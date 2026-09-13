from app.services.notification_service import NotificationService

class ApplicationEventConsumer:
    def handle_message(self, message_payload):
        print(f"Consumed application event: {message_payload}")
        NotificationService.process_application_event(message_payload)
