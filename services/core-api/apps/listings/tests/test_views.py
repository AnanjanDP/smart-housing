from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.listings.models import Listing

class ListingViewsTest(TestCase):
    def test_list_listings(self):
        url = reverse('listing-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
