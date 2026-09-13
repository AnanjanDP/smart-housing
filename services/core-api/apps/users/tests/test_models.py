from django.test import TestCase
from apps.users.models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Password123!',
            role=User.Role.TENANT
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'TENANT')
        self.assertTrue(user.check_password('Password123!'))
