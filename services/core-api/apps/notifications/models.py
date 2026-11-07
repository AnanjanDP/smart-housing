import uuid
from django.db import models
from django.conf import settings

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.title}"


class OutboxEvent(models.Model):
    """A domain event waiting to be sent to Kafka.

    The row is written in the same database transaction as the change it describes, so an event exists
    if and only if the change was committed. A relay (`manage.py relay_outbox`) publishes pending rows,
    in order, and retries until the broker accepts them.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=100)
    envelope = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['published_at', 'created_at'], name='outbox_pending_idx')]

    def __str__(self):
        return f"{self.topic}:{self.envelope.get('event_type')} ({'sent' if self.published_at else 'pending'})"
