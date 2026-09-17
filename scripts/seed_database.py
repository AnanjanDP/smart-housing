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
    print("Production mode active: Skipping fake listing and roommate seeding.")

if __name__ == '__main__':
    seed_data()

