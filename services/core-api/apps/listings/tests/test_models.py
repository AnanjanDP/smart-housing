from django.test import TestCase
from apps.users.models import User
from apps.listings.models import Listing

class ListingModelTest(TestCase):
    def test_create_listing(self):
        owner = User.objects.create_user(email='landlord@test.com', username='landlord', password='password', role='LANDLORD')
        listing = Listing.objects.create(
            owner=owner,
            title='Downtown Loft',
            description='Nice loft',
            address='123 Main St',
            city='San Francisco',
            state='CA',
            zip_code='94101',
            price=2500.00
        )
        self.assertEqual(listing.title, 'Downtown Loft')
        self.assertEqual(listing.owner, owner)
