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

    def test_oauth_oidc_login(self):
        url = reverse('oauth-login')
        data = {
            'email': 'google.user@example.com',
            'name': 'Google User',
            'provider': 'google_oidc',
            'sub': 'google-123456'
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'google.user@example.com')

