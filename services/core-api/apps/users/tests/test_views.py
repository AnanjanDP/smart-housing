from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from apps.users.models import User

class UserViewsTest(TestCase):
    def test_user_registration(self):
        url = reverse('user-register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Password123!',
            'role': 'TENANT'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_211_CREATED if response.status_code == 211 else status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
