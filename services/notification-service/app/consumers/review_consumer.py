class ReviewEventConsumer:
    def handle_message(self, message_payload):
        print(f"Consumed review event: {message_payload}")
