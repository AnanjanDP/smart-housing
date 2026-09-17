from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.listings.models import Listing
from apps.roommates.models import RoommateProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with initial users, listings, and roommate profiles.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding StayMatch database...")

        def get_or_create_user(email, username, role, password, bio=None, is_staff=False, is_superuser=False):
            user = User.objects.filter(email=email).first() or User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create(
                    email=email,
                    username=username,
                    role=role,
                    bio=bio or '',
                    is_staff=is_staff,
                    is_superuser=is_superuser
                )
                user.set_password(password)
                user.save()
            return user

        # 1. Admin User
        admin = get_or_create_user(
            email='admin@staymatch.com',
            username='admin',
            role=User.Role.ADMIN,
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )

        # 2. Landlord User
        landlord = get_or_create_user(
            email='landlord@staymatch.com',
            username='landlord_jane',
            role=User.Role.LANDLORD,
            password='LandlordPass123!',
            bio='Verified property owner managing high-end apartments.'
        )

        # 3. Tenant Users
        tenant1 = get_or_create_user(
            email='alex@staymatch.com',
            username='alex_dev',
            role=User.Role.TENANT,
            password='TenantPass123!',
            bio='Software engineer looking for quiet roommate near tech hubs.'
        )

        tenant2 = get_or_create_user(
            email='sarah@staymatch.com',
            username='sarah_design',
            role=User.Role.TENANT,
            password='TenantPass123!',
            bio='UX designer who enjoys cooking and clean spaces.'
        )

        # 4. Sample Listings
        listings_data = [
            {
                "title": "Luxury High-rise Studio in Downtown SF",
                "description": "Modern sunny studio apartment with floor-to-ceiling windows, gym, rooftop pool, and 24/7 concierge service.",
                "address": "450 Mission St",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94105",
                "price": 2600.00,
                "bedrooms": 1,
                "bathrooms": 1.0,
                "amenities": {"gym": True, "pool": True, "parking": True, "pet_friendly": True}
            },
            {
                "title": "Cozy 2BR Flat near University Park",
                "description": "Spacious 2 bedroom apartment ideal for students or working professionals. Close to Caltrain and downtown shops.",
                "address": "120 University Ave",
                "city": "Palo Alto",
                "state": "CA",
                "zip_code": "94301",
                "price": 3400.00,
                "bedrooms": 2,
                "bathrooms": 1.5,
                "amenities": {"wifi": True, "in_unit_laundry": True, "parking": True}
            },
            {
                "title": "Modern Loft in Downtown San Jose",
                "description": "Open concept loft with exposed brick walls, updated kitchen, high ceilings, and easy freeway access.",
                "address": "88 S 1st St",
                "city": "San Jose",
                "state": "CA",
                "zip_code": "95113",
                "price": 2200.00,
                "bedrooms": 1,
                "bathrooms": 1.0,
                "amenities": {"balcony": True, "ac": True, "dishwasher": True}
            }
        ]

        for item in listings_data:
            Listing.objects.get_or_create(
                owner=landlord,
                title=item['title'],
                defaults=item
            )

        # 5. Roommate Profiles
        RoommateProfile.objects.get_or_create(
            user=tenant1,
            defaults={
                'budget_min': 1200.00,
                'budget_max': 2000.00,
                'cleanliness_level': 4,
                'sleep_schedule': RoommateProfile.SleepSchedule.EARLY_BIRD,
                'pets_allowed': True,
                'preferred_location': 'San Francisco',
                'bio': 'Tech worker, clean and respectful.'
            }
        )

        RoommateProfile.objects.get_or_create(
            user=tenant2,
            defaults={
                'budget_min': 1400.00,
                'budget_max': 2200.00,
                'cleanliness_level': 5,
                'sleep_schedule': RoommateProfile.SleepSchedule.FLEXIBLE,
                'pets_allowed': False,
                'preferred_location': 'Palo Alto',
                'bio': 'Creative professional, quiet on weeknights.'
            }
        )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded!"))
