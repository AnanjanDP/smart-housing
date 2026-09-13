#!/usr/bin/env python
import os
import sys
import uuid

# Configure Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
    from apps.users.models import User
    from apps.listings.models import Listing
    from apps.roommates.models import RoommateProfile
    from apps.reviews.models import Review
except ImportError as e:
    print(f"Skipping Django model seeding: {e}")
    sys.exit(0)

def seed_data():
    print("Seeding database with sample users and listings...")
    
    # 1. Create Landlord
    landlord, created = User.objects.get_or_create(
        email='landlord@staymatch.com',
        defaults={
            'username': 'landlord_john',
            'first_name': 'John',
            'last_name': 'Landlord',
            'role': User.Role.LANDLORD,
            'phone_number': '+14155550199'
        }
    )
    if created:
        landlord.set_password('Password123!')
        landlord.save()

    # 2. Create Tenant
    tenant, created = User.objects.get_or_create(
        email='tenant@staymatch.com',
        defaults={
            'username': 'tenant_alice',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'role': User.Role.TENANT,
            'phone_number': '+14155550188'
        }
    )
    if created:
        tenant.set_password('Password123!')
        tenant.save()

    # 3. Create Sample Listings
    sample_listings = [
        {
            'title': 'Luxury High-rise Studio in Downtown',
            'description': 'Modern studio apartment with floor-to-ceiling windows, city views, in-unit laundry, and gym access.',
            'address': '100 Market St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94105',
            'price': 2600.00,
            'bedrooms': 1,
            'bathrooms': 1.0,
            'amenities': {'gym': True, 'wifi': True, 'parking': True, 'pets_allowed': True}
        },
        {
            'title': 'Cozy 2BR Flat near University',
            'description': 'Spacious 2 bedroom apartment ideal for students or young professionals. Close to public transit and parks.',
            'address': '450 University Ave',
            'city': 'Palo Alto',
            'state': 'CA',
            'zip_code': '94301',
            'price': 3400.00,
            'bedrooms': 2,
            'bathrooms': 1.5,
            'amenities': {'wifi': True, 'balcony': True, 'washer_dryer': True}
        }
    ]

    for data in sample_listings:
        listing, _ = Listing.objects.get_or_create(
            title=data['title'],
            owner=landlord,
            defaults=data
        )

    # 4. Create Roommate Profile
    RoommateProfile.objects.get_or_create(
        user=tenant,
        defaults={
            'budget_min': 1500.00,
            'budget_max': 2200.00,
            'cleanliness_level': 4,
            'sleep_schedule': RoommateProfile.SleepSchedule.EARLY_BIRD,
            'smoking_allowed': False,
            'pets_allowed': True,
            'preferred_location': 'San Francisco'
        }
    )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
