from django.test import TestCase
from apps.users.models import User
from apps.reviews.models import Review

class ReviewModelTest(TestCase):
    def test_create_review(self):
        reviewer = User.objects.create_user(email='rv@test.com', username='rv', password='p')
        target = User.objects.create_user(email='tg@test.com', username='tg', password='p')
        review = Review.objects.create(reviewer=reviewer, target_user=target, rating=5, comment='Great roommate!')
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer, reviewer)
