from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.applications.models import Application
from apps.listings.models import Listing
from apps.reviews.models import Review
from apps.roommates.models import RoommateProfile
from apps.users.models import User

LISTINGS = "/api/v1/listings/"
APPLICATIONS = "/api/v1/applications/"
PROFILES = "/api/v1/roommates/profiles/"
REVIEWS = "/api/v1/reviews/"


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])  # fast hashing, tests only
class PermissionTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        make = lambda email, name, role, **kw: User.objects.create_user(  # noqa: E731
            email=email, username=name, password="Sup3rSecret!pass", role=role, **kw)
        self.admin = make("admin@x.com", "admin", "ADMIN", is_staff=True, is_superuser=True)
        self.landlord = make("landlord@x.com", "landlord", "LANDLORD")
        self.other_landlord = make("landlord2@x.com", "landlord2", "LANDLORD")
        self.tenant = make("tenant@x.com", "tenant", "TENANT")
        self.other_tenant = make("tenant2@x.com", "tenant2", "TENANT")
        self.listing = self.make_listing(self.landlord)

    def make_listing(self, owner, **kw):
        data = dict(owner=owner, title="Flat", description="d", address="a", city="Pune", state="MH",
                    zip_code="1", price="1000", bedrooms=1)
        data.update(kw)
        return Listing.objects.create(**data)

    def as_user(self, user):
        self.client.force_authenticate(user)
        return self.client

    def listing_body(self, **kw):
        body = {"title": "New", "description": "d", "address": "a", "city": "Pune", "state": "MH",
                "zip_code": "1", "price": "100.00", "bedrooms": 1, "bathrooms": "1.0"}
        body.update(kw)
        return body


class ListingPermissionTests(PermissionTestCase):
    def test_anonymous_visitors_can_read_listings(self):
        self.assertEqual(self.client.get(LISTINGS).status_code, 200)

    def test_anonymous_visitors_cannot_create_listings(self):
        self.assertIn(self.client.post(LISTINGS, self.listing_body(), format="json").status_code, (401, 403))

    def test_tenants_cannot_publish_listings(self):
        response = self.as_user(self.tenant).post(LISTINGS, self.listing_body(), format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Listing.objects.count(), 1)

    def test_landlords_and_admins_can_publish_listings(self):
        self.assertEqual(self.as_user(self.landlord).post(LISTINGS, self.listing_body(), format="json").status_code, 201)
        self.assertEqual(self.as_user(self.admin).post(LISTINGS, self.listing_body(), format="json").status_code, 201)

    def test_published_listing_belongs_to_the_publisher(self):
        response = self.as_user(self.landlord).post(LISTINGS, self.listing_body(), format="json")
        self.assertEqual(Listing.objects.get(id=response.data["id"]).owner, self.landlord)

    def test_only_the_owner_can_edit_or_delete_a_listing(self):
        url = f"{LISTINGS}{self.listing.id}/"
        self.assertEqual(self.as_user(self.other_landlord).patch(url, {"price": "1.00"}, format="json").status_code, 403)
        self.assertEqual(self.as_user(self.tenant).delete(url).status_code, 403)
        self.assertEqual(self.as_user(self.landlord).patch(url, {"price": "2000.00"}, format="json").status_code, 200)
        self.assertEqual(self.as_user(self.landlord).delete(url).status_code, 204)


class ApplicationPermissionTests(PermissionTestCase):
    def apply(self, user=None, listing=None, **extra):
        body = {"listing": str((listing or self.listing).id), "move_in_date": "2030-01-01"}
        body.update(extra)
        return self.as_user(user or self.tenant).post(APPLICATIONS, body, format="json")

    def test_a_new_application_is_always_pending(self):
        response = self.apply(status="APPROVED")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "PENDING")

    def test_the_applicant_cannot_approve_their_own_application(self):
        application_id = self.apply().data["id"]
        response = self.as_user(self.tenant).patch(f"{APPLICATIONS}{application_id}/", {"status": "APPROVED"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Application.objects.get(id=application_id).status, "PENDING")

    def test_the_applicant_can_edit_their_own_notes_while_the_application_is_open(self):
        application_id = self.apply().data["id"]
        response = self.as_user(self.tenant).patch(f"{APPLICATIONS}{application_id}/", {"notes": "updated"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Application.objects.get(id=application_id).notes, "updated")

    def test_an_application_cannot_be_moved_to_another_listing(self):
        other = self.make_listing(self.other_landlord)
        application_id = self.apply().data["id"]
        response = self.as_user(self.tenant).patch(f"{APPLICATIONS}{application_id}/", {"listing": str(other.id)}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_the_landlord_decides_the_outcome(self):
        application_id = self.apply().data["id"]
        response = self.as_user(self.landlord).patch(f"{APPLICATIONS}{application_id}/", {"status": "APPROVED"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "APPROVED")

    def test_the_landlord_cannot_edit_the_applicants_details(self):
        application_id = self.apply().data["id"]
        for body in ({"notes": "x"}, {"move_in_date": "2031-01-01"}):
            response = self.as_user(self.landlord).patch(f"{APPLICATIONS}{application_id}/", body, format="json")
            self.assertEqual(response.status_code, 400, body)

    def test_a_decided_application_cannot_be_reopened_or_edited(self):
        application_id = self.apply().data["id"]
        self.as_user(self.landlord).patch(f"{APPLICATIONS}{application_id}/", {"status": "REJECTED"}, format="json")
        reopen = self.as_user(self.landlord).patch(f"{APPLICATIONS}{application_id}/", {"status": "PENDING"}, format="json")
        self.assertEqual(reopen.status_code, 400)
        edit = self.as_user(self.tenant).patch(f"{APPLICATIONS}{application_id}/", {"notes": "please"}, format="json")
        self.assertEqual(edit.status_code, 400)

    def test_other_users_cannot_see_or_change_the_application(self):
        application_id = self.apply().data["id"]
        for stranger in (self.other_tenant, self.other_landlord):
            client = self.as_user(stranger)
            self.assertEqual(client.get(f"{APPLICATIONS}{application_id}/").status_code, 404)
            self.assertEqual(client.patch(f"{APPLICATIONS}{application_id}/", {"status": "APPROVED"}, format="json").status_code, 404)
            self.assertEqual(client.delete(f"{APPLICATIONS}{application_id}/").status_code, 404)
            self.assertEqual(client.get(APPLICATIONS).data["count"], 0)

    def test_each_side_sees_only_their_own_applications(self):
        self.apply()
        self.apply(user=self.other_tenant)
        self.assertEqual(self.as_user(self.landlord).get(APPLICATIONS).data["count"], 2)
        self.assertEqual(self.as_user(self.tenant).get(APPLICATIONS).data["count"], 1)

    def test_a_landlord_who_also_applies_elsewhere_sees_both(self):
        other = self.make_listing(self.other_landlord)
        self.apply(user=self.tenant)
        self.apply(user=self.landlord, listing=other)
        self.assertEqual(self.as_user(self.landlord).get(APPLICATIONS).data["count"], 2)

    def test_owners_cannot_apply_to_their_own_listing(self):
        self.assertEqual(self.apply(user=self.landlord).status_code, 400)

    def test_unavailable_listings_cannot_be_applied_to(self):
        self.listing.is_available = False
        self.listing.save()
        self.assertEqual(self.apply().status_code, 400)

    def test_a_second_open_application_for_the_same_listing_is_refused(self):
        self.assertEqual(self.apply().status_code, 201)
        self.assertEqual(self.apply().status_code, 400)

    def test_reapplying_is_allowed_after_a_rejection(self):
        application_id = self.apply().data["id"]
        self.as_user(self.landlord).patch(f"{APPLICATIONS}{application_id}/", {"status": "REJECTED"}, format="json")
        self.assertEqual(self.apply().status_code, 201)

    def test_the_applicant_can_withdraw_an_open_application(self):
        application_id = self.apply().data["id"]
        self.assertEqual(self.as_user(self.tenant).delete(f"{APPLICATIONS}{application_id}/").status_code, 204)

    def test_the_landlord_cannot_delete_an_application(self):
        application_id = self.apply().data["id"]
        self.assertEqual(self.as_user(self.landlord).delete(f"{APPLICATIONS}{application_id}/").status_code, 403)
        self.assertTrue(Application.objects.filter(id=application_id).exists())

    def test_a_decided_application_cannot_be_deleted(self):
        application_id = self.apply().data["id"]
        self.as_user(self.landlord).patch(f"{APPLICATIONS}{application_id}/", {"status": "APPROVED"}, format="json")
        self.assertEqual(self.as_user(self.tenant).delete(f"{APPLICATIONS}{application_id}/").status_code, 403)

    def test_anonymous_requests_are_refused(self):
        self.assertEqual(self.client.get(APPLICATIONS).status_code, 401)


class RoommateProfilePermissionTests(PermissionTestCase):
    def setUp(self):
        super().setUp()
        self.profile = RoommateProfile.objects.create(user=self.tenant, bio="original")

    def test_profiles_are_readable_by_anyone(self):
        self.assertEqual(self.client.get(PROFILES).status_code, 200)

    def test_only_the_owner_can_edit_a_profile(self):
        url = f"{PROFILES}{self.profile.id}/"
        self.assertEqual(self.as_user(self.other_tenant).patch(url, {"bio": "defaced"}, format="json").status_code, 403)
        self.assertEqual(self.as_user(self.landlord).put(url, {"bio": "defaced"}, format="json").status_code, 403)
        self.assertEqual(self.as_user(self.tenant).patch(url, {"bio": "mine"}, format="json").status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "mine")

    def test_only_the_owner_can_delete_a_profile(self):
        url = f"{PROFILES}{self.profile.id}/"
        self.assertEqual(self.as_user(self.other_tenant).delete(url).status_code, 403)
        self.assertTrue(RoommateProfile.objects.filter(id=self.profile.id).exists())
        self.assertEqual(self.as_user(self.tenant).delete(url).status_code, 204)

    def test_creating_a_second_profile_is_a_clear_error_not_a_crash(self):
        response = self.as_user(self.tenant).post(PROFILES, {"bio": "again"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_a_user_can_create_their_first_profile(self):
        response = self.as_user(self.other_tenant).post(PROFILES, {"bio": "hi", "cleanliness_level": 4}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(RoommateProfile.objects.get(id=response.data["id"]).user, self.other_tenant)

    def test_cleanliness_must_be_between_one_and_five(self):
        for bad in (0, 6, 99, -1):
            response = self.as_user(self.other_tenant).post(PROFILES, {"cleanliness_level": bad}, format="json")
            self.assertEqual(response.status_code, 400, bad)

    def test_minimum_budget_cannot_exceed_maximum(self):
        response = self.as_user(self.other_tenant).post(
            PROFILES, {"budget_min": "5000", "budget_max": "1000"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_compatibility_still_works_between_two_profiles(self):
        mine = RoommateProfile.objects.create(user=self.other_tenant)
        response = self.as_user(self.other_tenant).get(f"{PROFILES}{self.profile.id}/compatibility/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("compatibility_score", response.data)
        self.assertIsNotNone(mine)


class ReviewPermissionTests(PermissionTestCase):
    def setUp(self):
        super().setUp()
        self.review = Review.objects.create(reviewer=self.tenant, listing=self.listing, rating=5, comment="great")

    def test_reviews_are_readable_by_anyone(self):
        self.assertEqual(self.client.get(REVIEWS).status_code, 200)

    def test_only_the_author_can_edit_a_review(self):
        url = f"{REVIEWS}{self.review.id}/"
        self.assertEqual(self.as_user(self.other_tenant).patch(url, {"rating": 1, "comment": "tampered"}, format="json").status_code, 403)
        self.assertEqual(self.as_user(self.landlord).patch(url, {"rating": 1}, format="json").status_code, 403)
        self.assertEqual(self.as_user(self.tenant).patch(url, {"rating": 4}, format="json").status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)

    def test_only_the_author_can_delete_a_review(self):
        url = f"{REVIEWS}{self.review.id}/"
        self.assertEqual(self.as_user(self.other_tenant).delete(url).status_code, 403)
        self.assertEqual(self.as_user(self.landlord).delete(url).status_code, 403)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
        self.assertEqual(self.as_user(self.tenant).delete(url).status_code, 204)

    def test_what_was_reviewed_cannot_be_changed(self):
        other = self.make_listing(self.other_landlord)
        response = self.as_user(self.tenant).patch(f"{REVIEWS}{self.review.id}/", {"listing": str(other.id)}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_a_user_can_review_a_listing_they_do_not_own(self):
        response = self.as_user(self.other_tenant).post(
            REVIEWS, {"listing": str(self.listing.id), "rating": 3, "comment": "ok"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.get(id=response.data["id"]).reviewer, self.other_tenant)

    def test_a_user_can_review_another_user(self):
        response = self.as_user(self.tenant).post(
            REVIEWS, {"target_user": str(self.landlord.id), "rating": 5, "comment": "good landlord"}, format="json")
        self.assertEqual(response.status_code, 201)

    def test_you_cannot_review_yourself_or_your_own_listing(self):
        me = self.as_user(self.landlord).post(
            REVIEWS, {"target_user": str(self.landlord.id), "rating": 5, "comment": "me"}, format="json")
        own = self.as_user(self.landlord).post(
            REVIEWS, {"listing": str(self.listing.id), "rating": 5, "comment": "mine"}, format="json")
        self.assertEqual((me.status_code, own.status_code), (400, 400))

    def test_a_review_needs_exactly_one_subject(self):
        none = self.as_user(self.other_tenant).post(REVIEWS, {"rating": 3, "comment": "?"}, format="json")
        both = self.as_user(self.other_tenant).post(
            REVIEWS, {"listing": str(self.listing.id), "target_user": str(self.landlord.id), "rating": 3, "comment": "?"},
            format="json")
        self.assertEqual((none.status_code, both.status_code), (400, 400))

    def test_the_same_subject_cannot_be_reviewed_twice(self):
        response = self.as_user(self.tenant).post(
            REVIEWS, {"listing": str(self.listing.id), "rating": 1, "comment": "again"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_ratings_outside_one_to_five_are_refused(self):
        for bad in (0, 6):
            response = self.as_user(self.other_tenant).post(
                REVIEWS, {"listing": str(self.listing.id), "rating": bad, "comment": "x"}, format="json")
            self.assertEqual(response.status_code, 400, bad)

    def test_anonymous_visitors_cannot_write_reviews(self):
        self.assertIn(self.client.post(REVIEWS, {"listing": str(self.listing.id), "rating": 5, "comment": "x"},
                                       format="json").status_code, (401, 403))
