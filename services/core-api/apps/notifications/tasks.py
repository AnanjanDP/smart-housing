import logging
from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=300,
    acks_late=True,
    reject_on_worker_lost=True
)
def send_notification_email_task(self, recipient_id: str, title: str, message: str):
    """
    Celery background task for transactional notification execution.
    Follows Rule 3: Retry parameters, backoff strategies, and direct DB state updates.
    """
    logger.info("Executing notification email background task", extra={
        "recipient_id": recipient_id,
        "task_id": self.request.id
    })
    
    try:
        from apps.notifications.models import Notification
        from apps.users.models import User

        with transaction.atomic():
            user = User.objects.get(id=recipient_id)
            notification = Notification.objects.create(
                recipient=user,
                title=title,
                message=message
            )
            logger.info("Notification created successfully", extra={"notification_id": str(notification.id)})
            return {"status": "SUCCESS", "notification_id": str(notification.id)}

    except Exception as exc:
        logger.error(f"Failed to execute notification task for recipient {recipient_id}: {exc}")
        raise self.retry(exc=exc)
