import uuid
from django.db import models
from django.conf import settings

class Interaction(models.Model):
    class Action(models.TextChoices):
        VIEW = 'VIEW', 'View'
        SAVE = 'SAVE', 'Save'
        CLICK = 'CLICK', 'Click'
        APPLY = 'APPLY', 'Apply'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions')
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='user_interactions')
    action = models.CharField(max_length=20, choices=Action.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.action} on {self.listing.title}"
