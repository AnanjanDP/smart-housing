from django.test import TestCase
from datetime import date
from apps.users.models import User
from apps.listings.models import Listing
from apps.applications.models import Application

class ApplicationModelTest(TestCase):
    def test_create_application(self):
        tenant = User.objects.create_user(email='ap@test.com', username='ap', password='p', role='TENANT')
        landlord = User.objects.create_user(email='ld@test.com', username='ld', password='p', role='LANDLORD')
        listing = Listing.objects.create(owner=landlord, title='Studio', address='A', city='SF', state='CA', zip_code='1', price=1000)
        
        app = Application.objects.create(applicant=tenant, listing=listing, move_in_date=date.today())
        self.assertEqual(app.status, 'PENDING')
        self.assertEqual(app.listing, listing)
