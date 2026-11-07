from app.services.notification_service import NotificationService


class ListingEventConsumer:
    def __init__(self, service: NotificationService = None):
        self.service = service or NotificationService()

    def handle_message(self, message_payload):
        self.service.process_listing_event(message_payload)
