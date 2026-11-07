import pytest

from app.consumers.application_consumer import ApplicationEventConsumer
from app.consumers.listing_consumer import ListingEventConsumer
from app.consumers.processor import DEAD_LETTERED, DUPLICATE, PROCESSED, EventProcessor, StillProcessingElsewhere
from app.consumers.review_consumer import ReviewEventConsumer
from app.core.idempotency import BUSY, DONE, NEW, RedisIdempotencyStore
from app.services.email_service import EmailDeliveryError, EmailService
from app.services.notification_service import InvalidEventError, NotificationService


class RecordingEmail:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    def send_email(self, to_email, subject, body, is_html=False):
        if self.fail:
            raise EmailDeliveryError("smtp down")
        self.sent.append((to_email, subject, body))


@pytest.fixture
def email():
    return RecordingEmail()


@pytest.fixture
def service(email):
    return NotificationService(email_service=email)


# ------------------------------------------------------------------ who gets which email
def test_a_new_listing_is_confirmed_to_its_owner(service, email):
    ListingEventConsumer(service).handle_message(
        {"event_type": "LISTING_CREATED", "title": "Studio", "city": "Pune", "price": 900, "owner_email": "owner@x.com"})
    [(to, subject, body)] = email.sent
    assert to == "owner@x.com"
    assert "Studio" in subject and "Pune" in body


def test_a_new_application_goes_to_the_owner(service, email):
    ApplicationEventConsumer(service).handle_message({
        "event_type": "APPLICATION_SUBMITTED", "listing_title": "Flat", "owner_email": "owner@x.com",
        "applicant_email": "tenant@x.com"})
    assert [to for to, _, _ in email.sent] == ["owner@x.com"]


def test_a_decision_goes_to_the_applicant(service, email):
    ApplicationEventConsumer(service).handle_message({
        "event_type": "APPLICATION_STATUS_UPDATED", "listing_title": "Flat", "status": "UNDER_REVIEW",
        "owner_email": "owner@x.com", "applicant_email": "tenant@x.com"})
    [(to, subject, body)] = email.sent
    assert to == "tenant@x.com"
    assert "Under Review" in subject and "under review" in body


def test_a_review_goes_to_the_person_reviewed(service, email):
    ReviewEventConsumer(service).handle_message({
        "event_type": "REVIEW_CREATED", "rating": 4, "listing_title": "Flat", "recipient_email": "owner@x.com"})
    [(to, _, body)] = email.sent
    assert to == "owner@x.com"
    assert "4-star" in body


@pytest.mark.parametrize("handler,event", [
    ("process_listing_event", {"event_type": "LISTING_CREATED", "title": "x"}),
    ("process_application_event", {"event_type": "APPLICATION_SUBMITTED"}),
    ("process_application_event", {"event_type": "APPLICATION_STATUS_UPDATED", "status": "APPROVED"}),
    ("process_application_event", {"event_type": "SOMETHING_ELSE"}),
    ("process_review_event", {"event_type": "REVIEW_CREATED"}),
])
def test_events_without_a_recipient_are_rejected_not_sent_to_a_made_up_address(service, email, handler, event):
    with pytest.raises(InvalidEventError):
        getattr(service, handler)(event)
    assert email.sent == []


def test_a_failed_email_surfaces_as_an_error(email):
    broken = NotificationService(email_service=RecordingEmail(fail=True))
    with pytest.raises(EmailDeliveryError):
        broken.process_listing_event({"title": "x", "owner_email": "owner@x.com"})


def test_smtp_failures_are_raised_by_the_email_service(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "127.0.0.1")
    monkeypatch.setenv("SMTP_PORT", "1")  # nothing listens here
    monkeypatch.setenv("SMTP_USER", "u")
    with pytest.raises(EmailDeliveryError):
        EmailService.send_email("a@b.c", "s", "b")


def test_without_smtp_configuration_nothing_is_sent_and_nothing_fails(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    EmailService.send_email("a@b.c", "s", "b")


# ------------------------------------------------------------------ idempotency store
class FakeRedis:
    def __init__(self):
        self.data = {}

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.data:
            return None
        self.data[key] = value.encode() if isinstance(value, str) else value
        return True

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        self.data.pop(key, None)


def test_the_first_claim_wins_and_a_finished_event_is_a_duplicate():
    store = RedisIdempotencyStore(client=FakeRedis())
    assert store.claim("e1") == NEW
    assert store.claim("e1") == BUSY  # still being processed
    store.complete("e1")
    assert store.claim("e1") == DONE


def test_a_released_claim_can_be_taken_again():
    store = RedisIdempotencyStore(client=FakeRedis())
    store.claim("e1")
    store.release("e1")
    assert store.claim("e1") == NEW


def test_the_store_lets_events_through_when_redis_is_down():
    class Down:
        def set(self, *a, **k):
            raise ConnectionError("redis down")

    store = RedisIdempotencyStore(client=Down())
    assert store.claim("e1") == NEW
    store.complete("e1")  # must not raise
    store.release("e1")


# ------------------------------------------------------------------ message processing
def envelope(event_id="evt-1", **payload):
    return {"event_id": event_id, "event_type": payload.get("event_type", "LISTING_CREATED"), "payload": payload}


class Harness:
    def __init__(self, dispatch=None, dlq_fails=False, store=None, **kwargs):
        self.handled, self.dead = [], []
        self.store = store or RedisIdempotencyStore(client=FakeRedis())
        self.sleeps = []

        def default_dispatch(topic, payload):
            self.handled.append((topic, payload))

        def dlq(topic, raw, error):
            if dlq_fails:
                raise RuntimeError("kafka down")
            self.dead.append((topic, raw, error))

        self.processor = EventProcessor(
            dispatch=dispatch or default_dispatch, idempotency=self.store, send_to_dlq=dlq,
            sleep=self.sleeps.append, **kwargs)


def test_a_message_is_processed_once():
    h = Harness()
    assert h.processor.process("listing_events", envelope(title="A")) == PROCESSED
    assert h.handled == [("listing_events", {"title": "A"})]


def test_a_redelivered_message_is_skipped():
    h = Harness()
    message = envelope(title="A")
    h.processor.process("listing_events", message)
    assert h.processor.process("listing_events", message) == DUPLICATE
    assert len(h.handled) == 1


def test_transient_failures_are_retried_until_they_succeed():
    attempts = []

    def flaky(topic, payload):
        attempts.append(1)
        if len(attempts) < 3:
            raise EmailDeliveryError("smtp down")

    h = Harness(dispatch=flaky)
    assert h.processor.process("listing_events", envelope(title="A")) == PROCESSED
    assert len(attempts) == 3
    assert len(h.sleeps) == 2


def test_a_message_that_keeps_failing_is_dead_lettered_and_can_be_replayed():
    def always_fails(topic, payload):
        raise EmailDeliveryError("smtp down")

    h = Harness(dispatch=always_fails)
    message = envelope(title="A")
    assert h.processor.process("listing_events", message) == DEAD_LETTERED
    [(topic, raw, error)] = h.dead
    assert topic == "listing_events" and raw == message and "smtp down" in error
    assert h.store.claim("evt-1") == NEW  # the claim was released, so a replay is processed, not skipped


def test_an_invalid_event_is_dead_lettered_without_retrying():
    calls = []

    def reject(topic, payload):
        calls.append(1)
        raise InvalidEventError("missing recipient")

    h = Harness(dispatch=reject)
    assert h.processor.process("listing_events", envelope(title="A")) == DEAD_LETTERED
    assert calls == [1]


def test_if_the_dead_letter_write_fails_the_error_propagates_so_the_offset_is_not_committed():
    def always_fails(topic, payload):
        raise RuntimeError("boom")

    h = Harness(dispatch=always_fails, dlq_fails=True)
    with pytest.raises(RuntimeError, match="kafka down"):
        h.processor.process("listing_events", envelope(title="A"))


def test_an_event_another_worker_is_still_handling_is_not_dropped():
    store = RedisIdempotencyStore(client=FakeRedis())
    store.claim("evt-1")  # another worker's claim that never completes
    h = Harness(store=store, busy_attempts=3)
    with pytest.raises(StillProcessingElsewhere):
        h.processor.process("listing_events", envelope(title="A"))
    assert h.handled == []
    assert len(h.sleeps) == 3


def test_messages_without_an_envelope_are_still_handled():
    h = Harness()
    assert h.processor.process("listing_events", {"event_type": "LISTING_CREATED", "title": "A"}) == PROCESSED
    assert h.handled[0][1]["title"] == "A"
