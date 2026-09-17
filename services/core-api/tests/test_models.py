from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.listings.models import Listing
from apps.roommates.models import RoommateProfile
from apps.applications.models import Application

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(
            username='landlord_user',
            email='landlord@example.com',
            password='Password123!',
            role='landlord'
        )
        self.tenant = User.objects.create_user(
            username='tenant_user',
            email='tenant@example.com',
            password='Password123!',
            role='tenant'
        )

    def test_user_creation(self):
        self.assertEqual(self.landlord.role, 'landlord')
        self.assertEqual(self.tenant.role, 'tenant')
        self.assertTrue(self.landlord.check_password('Password123!'))

    def test_listing_creation(self):
        listing = Listing.objects.create(
            owner=self.landlord,
            title='Sunny Studio Flat',
            description='Modern studio in city center.',
            address='123 Main St',
            city='San Francisco',
            state='CA',
            zip_code='94105',
            price=2500.00,
            bedrooms=1,
            bathrooms=1.0,
            is_available=True
        )
        self.assertEqual(listing.title, 'Sunny Studio Flat')
        self.assertEqual(listing.price, 2500.00)
        self.assertTrue(listing.is_available)

    def test_roommate_profile_creation(self):
        profile = RoommateProfile.objects.create(
            user=self.tenant,
            bio='Software engineer looking for quiet roommate',
            cleanliness_level=5,
            budget_max=3000.00,
            preferred_location='San Francisco'
        )
        self.assertEqual(profile.cleanliness_level, 5)
        self.assertEqual(profile.preferred_location, 'San Francisco')

    def test_housing_application_creation(self):
        listing = Listing.objects.create(
            owner=self.landlord,
            title='2BR Flat',
            address='456 Park Ave',
            city='Palo Alto',
            state='CA',
            zip_code='94301',
            price=3200.00,
            bedrooms=2,
            bathrooms=2.0
        )
        application = Application.objects.create(
            applicant=self.tenant,
            listing=listing,
            status=Application.Status.PENDING,
            move_in_date='2026-10-01'
        )
        self.assertEqual(application.status, Application.Status.PENDING)
        self.assertEqual(application.applicant, self.tenant)


