from django.test import TestCase
from apps.listings.filters import ListingFilter
from apps.listings.models import Listing
from apps.users.models import User

class ListingFilterTest(TestCase):
    def test_filter_by_city(self):
        user = User.objects.create_user(email='l1@test.com', username='l1', password='p')
        Listing.objects.create(owner=user, title='Apt 1', address='1', city='San Francisco', state='CA', zip_code='1', price=1000)
        Listing.objects.create(owner=user, title='Apt 2', address='2', city='New York', state='NY', zip_code='2', price=2000)
        
        f = ListingFilter({'city': 'San Francisco'}, queryset=Listing.objects.all())
        self.assertEqual(f.qs.count(), 1)
