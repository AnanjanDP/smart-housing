import uuid
from django.db import models
from django.conf import settings

class RoommateProfile(models.Model):
    class SleepSchedule(models.TextChoices):
        EARLY_BIRD = 'EARLY_BIRD', 'Early Bird'
        NIGHT_OWL = 'NIGHT_OWL', 'Night Owl'
        FLEXIBLE = 'FLEXIBLE', 'Flexible'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roommate_profile')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, default=2500.00)
    move_in_date = models.DateField(null=True, blank=True)
    cleanliness_level = models.IntegerField(default=3)  # Scale 1-5
    sleep_schedule = models.CharField(max_length=20, choices=SleepSchedule.choices, default=SleepSchedule.FLEXIBLE)
    smoking_allowed = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=True)
    preferred_location = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Roommate Profile - {self.user.email}"
