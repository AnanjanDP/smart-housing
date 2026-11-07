from unittest import mock

from django.core.management import call_command
from django.db import transaction
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase

from apps.listings.models import Listing
from apps.notifications.models import OutboxEvent
from apps.users.models import User
from common import kafka
from common.kafka import dispatch_pending, publish_event

FAST_HASH = override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])


class FakeFuture:
    def __init__(self, error=None):
        self.error = error

    def get(self, timeout=None):
        if self.error:
            raise self.error


class FakeProducer:
    def __init__(self, fail_on=()):
        self.sent = []
        self.fail_on = set(fail_on)

    def send(self, topic, value):
        if value["event_type"] in self.fail_on:
            return FakeFuture(RuntimeError("broker unavailable"))
        self.sent.append((topic, value))
        return FakeFuture()


def event(kind):
    return publish_event("test_events", {"event_type": kind})


class OutboxStorageTests(TestCase):
    def test_an_event_is_stored_with_a_complete_envelope(self):
        stored = event("THING_HAPPENED")
        envelope = OutboxEvent.objects.get(pk=stored.pk).envelope
        self.assertEqual(envelope["event_type"], "THING_HAPPENED")
        self.assertTrue(envelope["event_id"])
        self.assertTrue(envelope["correlation_id"])
        self.assertEqual(envelope["payload"], {"event_type": "THING_HAPPENED"})
        self.assertIsNone(stored.published_at)

    def test_an_event_is_not_recorded_if_the_change_is_rolled_back(self):
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                event("GHOST")
                raise RuntimeError("the change failed")
        self.assertEqual(OutboxEvent.objects.count(), 0)

    def test_publishing_never_fails_the_request_when_the_broker_is_down(self):
        with mock.patch.object(kafka, "get_kafka_producer", side_effect=RuntimeError("no broker")):
            with self.captureOnCommitCallbacks(execute=True):
                event("STILL_SAFE")
        self.assertEqual(OutboxEvent.objects.filter(published_at__isnull=True).count(), 1)


class OutboxDeliveryTests(TestCase):
    def test_pending_events_are_sent_oldest_first_and_marked(self):
        for kind in ("FIRST", "SECOND", "THIRD"):
            event(kind)
        producer = FakeProducer()
        self.assertEqual(dispatch_pending(producer=producer), 3)
        self.assertEqual([e["event_type"] for _, e in producer.sent], ["FIRST", "SECOND", "THIRD"])
        self.assertEqual(OutboxEvent.objects.filter(published_at__isnull=True).count(), 0)

    def test_sent_events_are_not_sent_again(self):
        event("ONCE")
        producer = FakeProducer()
        dispatch_pending(producer=producer)
        self.assertEqual(dispatch_pending(producer=producer), 0)
        self.assertEqual(len(producer.sent), 1)

    def test_a_failure_stops_delivery_so_order_is_kept_and_is_retried_later(self):
        for kind in ("A", "B", "C"):
            event(kind)
        flaky = FakeProducer(fail_on={"B"})
        self.assertEqual(dispatch_pending(producer=flaky), 1)
        self.assertEqual([e["event_type"] for _, e in flaky.sent], ["A"])  # C was not sent ahead of B

        failed = OutboxEvent.objects.get(envelope__event_type="B")
        self.assertEqual(failed.attempts, 1)
        self.assertIn("broker unavailable", failed.last_error)
        self.assertIsNone(failed.published_at)

        healthy = FakeProducer()
        self.assertEqual(dispatch_pending(producer=healthy), 2)
        self.assertEqual([e["event_type"] for _, e in healthy.sent], ["B", "C"])

    def test_without_a_broker_nothing_is_lost(self):
        event("WAITING")
        with mock.patch.object(kafka, "get_kafka_producer", return_value=None):
            self.assertEqual(dispatch_pending(), 0)
        self.assertEqual(OutboxEvent.objects.filter(published_at__isnull=True).count(), 1)

    def test_the_relay_command_publishes_pending_events(self):
        event("VIA_RELAY")
        producer = FakeProducer()
        with mock.patch.object(kafka, "get_kafka_producer", return_value=producer):
            call_command("relay_outbox", "--once")
        self.assertEqual(len(producer.sent), 1)


@FAST_HASH
class ServicesPublishEventsTests(APITestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(
            email="owner@example.com", username="owner", password="Sup3rSecret!pass", role="LANDLORD")
        self.tenant = User.objects.create_user(
            email="tenant@example.com", username="tenant", password="Sup3rSecret!pass", role="TENANT")
        self.listing = Listing.objects.create(
            owner=self.landlord, title="Sunny flat", description="d", address="a", city="Pune", state="MH",
            zip_code="1", price="1000", bedrooms=1)

    def events(self, kind):
        return [e.envelope["payload"] for e in OutboxEvent.objects.filter(envelope__event_type=kind)]

    def test_creating_a_listing_publishes_an_event_for_the_owner(self):
        self.client.force_authenticate(self.landlord)
        response = self.client.post("/api/v1/listings/", {
            "title": "Studio", "description": "d", "address": "a", "city": "Pune", "state": "MH",
            "zip_code": "1", "price": "900", "bedrooms": 1}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Studio")
        self.assertEqual(response.data["owner"]["id"], str(self.landlord.id))
        [created] = self.events("LISTING_CREATED")
        self.assertEqual(created["title"], "Studio")
        self.assertEqual(created["owner_email"], "owner@example.com")

    def test_applying_notifies_the_owner_with_real_addresses(self):
        self.client.force_authenticate(self.tenant)
        response = self.client.post(
            "/api/v1/applications/", {"listing": str(self.listing.id), "move_in_date": "2030-01-01"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "PENDING")
        [submitted] = self.events("APPLICATION_SUBMITTED")
        self.assertEqual(submitted["owner_email"], "owner@example.com")
        self.assertEqual(submitted["applicant_email"], "tenant@example.com")
        self.assertEqual(submitted["listing_title"], "Sunny flat")

    def test_a_decision_notifies_the_applicant(self):
        self.client.force_authenticate(self.tenant)
        application_id = self.client.post(
            "/api/v1/applications/", {"listing": str(self.listing.id), "move_in_date": "2030-01-01"},
            format="json").data["id"]
        self.client.force_authenticate(self.landlord)
        response = self.client.patch(f"/api/v1/applications/{application_id}/", {"status": "APPROVED"}, format="json")
        self.assertEqual(response.status_code, 200)
        [updated] = self.events("APPLICATION_STATUS_UPDATED")
        self.assertEqual(updated["status"], "APPROVED")
        self.assertEqual(updated["applicant_email"], "tenant@example.com")

    def test_editing_notes_without_a_decision_publishes_nothing(self):
        self.client.force_authenticate(self.tenant)
        application_id = self.client.post(
            "/api/v1/applications/", {"listing": str(self.listing.id), "move_in_date": "2030-01-01"},
            format="json").data["id"]
        self.client.patch(f"/api/v1/applications/{application_id}/", {"notes": "I have a cat"}, format="json")
        self.assertEqual(self.events("APPLICATION_STATUS_UPDATED"), [])

    def test_a_rejected_application_leaves_no_event(self):
        self.client.force_authenticate(self.landlord)  # owners cannot apply to their own listing
        response = self.client.post(
            "/api/v1/applications/", {"listing": str(self.listing.id), "move_in_date": "2030-01-01"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(OutboxEvent.objects.count(), 0)

    def test_a_review_notifies_the_listing_owner(self):
        self.client.force_authenticate(self.tenant)
        response = self.client.post(
            "/api/v1/reviews/", {"listing": str(self.listing.id), "rating": 5, "comment": "Lovely"}, format="json")
        self.assertEqual(response.status_code, 201)
        [created] = self.events("REVIEW_CREATED")
        self.assertEqual(created["recipient_email"], "owner@example.com")
        self.assertEqual(created["rating"], 5)
