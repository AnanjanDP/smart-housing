from django.test import TestCase
from django.urls import reverse

class HealthCheckTest(TestCase):
    def test_health_check_endpoint(self):
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
