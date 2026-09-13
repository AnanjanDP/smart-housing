from apps.notifications.models import Notification

class NotificationService:
    @staticmethod
    def send_notification(recipient, title, message):
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message
        )
