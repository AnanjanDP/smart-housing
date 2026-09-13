from django.test import TestCase
from apps.users.models import User
from apps.roommates.models import RoommateProfile
from apps.roommates.matching import RoommateMatcher

class RoommateMatcherTest(TestCase):
    def test_high_compatibility(self):
        u1 = User.objects.create_user(email='r1@test.com', username='r1', password='p')
        u2 = User.objects.create_user(email='r2@test.com', username='r2', password='p')
        
        p1 = RoommateProfile.objects.create(
            user=u1, budget_min=1000, budget_max=2000, cleanliness_level=4, 
            sleep_schedule='EARLY_BIRD', preferred_location='SF'
        )
        p2 = RoommateProfile.objects.create(
            user=u2, budget_min=1200, budget_max=1800, cleanliness_level=4, 
            sleep_schedule='EARLY_BIRD', preferred_location='SF'
        )

        score = RoommateMatcher.calculate_compatibility(p1, p2)
        self.assertGreaterEqual(score, 85.0)
