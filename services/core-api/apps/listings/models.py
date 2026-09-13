import uuid
from django.db import models
from django.conf import settings

class Listing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    is_available = models.BooleanField(default=True)
    amenities = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - ${self.price}/mo ({self.city})"
