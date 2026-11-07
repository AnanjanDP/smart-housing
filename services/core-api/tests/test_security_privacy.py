from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.applications.models import Application
from apps.listings.models import Listing
from apps.reviews.models import Review
from apps.roommates.models import RoommateProfile
from apps.users.models import User

PUBLIC_FIELDS = {"id", "username", "first_name", "last_name", "name", "avatar_url"}
PRIVATE_VALUES = ("landlord@private.example", "+91 99999 11111", "tenant@private.example", "+91 88888 22222")


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])  # fast hashing, tests only
class PrivacyTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.landlord = User.objects.create_user(
            email="landlord@private.example", username="landlord", password="Sup3rSecret!pass",
            role="LANDLORD", first_name="Jane", last_name="Doe", phone_number="+91 99999 11111", bio="private bio")
        self.tenant = User.objects.create_user(
            email="tenant@private.example", username="tenant", password="Sup3rSecret!pass",
            role="TENANT", first_name="Alex", phone_number="+91 88888 22222")
        self.listing = Listing.objects.create(
            owner=self.landlord, title="Flat", description="d", address="a", city="Pune", state="MH",
            zip_code="1", price="1000", bedrooms=1)
        self.profile = RoommateProfile.objects.create(user=self.tenant, bio="hi")
        Review.objects.create(reviewer=self.tenant, listing=self.listing, rating=5, comment="great")

    def assert_nothing_private(self, response):
        body = response.content.decode()
        for secret in PRIVATE_VALUES:
            self.assertNotIn(secret, body, secret)


class PublicEndpointPrivacyTests(PrivacyTestCase):
    def test_listing_list_does_not_reveal_the_owners_contact_details(self):
        response = self.client.get("/api/v1/listings/")
        self.assertEqual(response.status_code, 200)
        self.assert_nothing_private(response)
        self.assertEqual(set(response.data["results"][0]["owner"]), PUBLIC_FIELDS)

    def test_listing_detail_does_not_reveal_the_owners_contact_details(self):
        response = self.client.get(f"/api/v1/listings/{self.listing.id}/")
        self.assert_nothing_private(response)
        self.assertEqual(set(response.data["owner"]), PUBLIC_FIELDS)

    def test_owner_name_is_still_shown(self):
        owner = self.client.get(f"/api/v1/listings/{self.listing.id}/").data["owner"]
        self.assertEqual(owner["name"], "Jane Doe")
        self.assertEqual(owner["username"], "landlord")

    def test_roommate_profiles_do_not_reveal_contact_details(self):
        response = self.client.get("/api/v1/roommates/profiles/")
        self.assert_nothing_private(response)
        self.assertEqual(set(response.data["results"][0]["user"]), PUBLIC_FIELDS)

    def test_reviews_do_not_reveal_the_reviewers_contact_details(self):
        response = self.client.get("/api/v1/reviews/")
        self.assert_nothing_private(response)
        self.assertEqual(set(response.data["results"][0]["reviewer"]), PUBLIC_FIELDS)

    def test_compatibility_does_not_return_the_other_persons_email(self):
        RoommateProfile.objects.create(user=self.landlord)
        self.client.force_authenticate(self.landlord)
        response = self.client.get(f"/api/v1/roommates/profiles/{self.profile.id}/compatibility/")
        self.assertEqual(response.status_code, 200)
        self.assert_nothing_private(response)
        self.assertEqual(response.data["target_user"], "tenant")


class ParticipantPrivacyTests(PrivacyTestCase):
    def setUp(self):
        super().setUp()
        self.application = Application.objects.create(
            listing=self.listing, applicant=self.tenant, move_in_date="2030-01-01")

    def test_the_landlord_still_sees_how_to_contact_the_applicant(self):
        self.client.force_authenticate(self.landlord)
        applicant = self.client.get("/api/v1/applications/").data["results"][0]["applicant"]
        self.assertEqual(applicant["email"], "tenant@private.example")
        self.assertEqual(applicant["phone_number"], "+91 88888 22222")

    def test_an_application_never_exposes_the_landlords_contact_details(self):
        for user in (self.landlord, self.tenant):
            self.client.force_authenticate(user)
            result = self.client.get("/api/v1/applications/").data["results"][0]
            self.assertEqual(set(result["listing_detail"]["owner"]), PUBLIC_FIELDS)
            self.assertNotIn("landlord@private.example", str(result))
            self.assertNotIn("+91 99999 11111", str(result))

    def test_users_still_see_their_own_details(self):
        self.client.force_authenticate(self.tenant)
        me = self.client.get("/api/v1/users/me/").data
        self.assertEqual(me["email"], "tenant@private.example")
        self.assertEqual(me["phone_number"], "+91 88888 22222")
