from app.services.notification_service import NotificationService

class ListingEventConsumer:
    def handle_message(self, message_payload):
        print(f"Consumed listing event: {message_payload}")
        NotificationService.process_listing_event(message_payload)
