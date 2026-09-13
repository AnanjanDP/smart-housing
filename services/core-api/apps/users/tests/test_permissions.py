from django.test import TestCase
from apps.users.permissions import IsUserSelf
from apps.users.models import User
from unittest.mock import Mock

class UserPermissionsTest(TestCase):
    def test_is_user_self_permission(self):
        user = User.objects.create_user(email='u1@test.com', username='u1', password='pass')
        user2 = User.objects.create_user(email='u2@test.com', username='u2', password='pass')
        perm = IsUserSelf()
        
        request = Mock()
        request.user = user
        
        self.assertTrue(perm.has_object_permission(request, None, user))
        self.assertFalse(perm.has_object_permission(request, None, user2))
