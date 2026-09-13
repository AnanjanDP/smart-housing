class NotificationProducer:
    def publish_notification_event(self, event_type: str, data: dict):
        payload = {"event_type": event_type, "data": data}
        print(f"[KAFKA PRODUCER MOCK] Published notification event: {payload}")
