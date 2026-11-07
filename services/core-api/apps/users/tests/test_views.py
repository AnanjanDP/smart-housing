import time

import jwt
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from apps.users.models import User

SECRET = "t" * 40


class UserViewsTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_user_registration(self):
        url = reverse('user-register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Password123!',
            'role': 'TENANT'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    @override_settings(SUPABASE_JWT_SECRET=SECRET, SUPABASE_URL='')
    def test_oauth_oidc_login(self):
        token = jwt.encode(
            {
                'sub': 'google-123456',
                'email': 'google.user@example.com',
                'aud': 'authenticated',
                'exp': int(time.time()) + 600,
                'user_metadata': {'email_verified': True, 'full_name': 'Google User'},
                'app_metadata': {'provider': 'google'},
            },
            SECRET,
            algorithm='HS256',
        )
        response = self.client.post(reverse('oauth-login'), {'id_token': token}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'google.user@example.com')

    @override_settings(SUPABASE_JWT_SECRET=SECRET, SUPABASE_URL='', ALLOW_INSECURE_DEMO_OAUTH=False)
    def test_oauth_login_without_a_verified_token_is_refused(self):
        data = {'email': 'google.user@example.com', 'name': 'Google User', 'provider': 'google_oidc', 'sub': 'x'}
        response = self.client.post(reverse('oauth-login'), data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(User.objects.filter(email='google.user@example.com').exists())
