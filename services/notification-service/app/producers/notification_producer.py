import os
import json
import logging

logger = logging.getLogger(__name__)

class NotificationProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=5000
            )
            logger.info("Kafka Producer initialized in notification service.")
        except Exception as e:
            logger.warning(f"Failed to connect Kafka Producer to {self.bootstrap_servers}: {e}")
            self.producer = None

    def publish_notification_event(self, event_type: str, data: dict, topic: str = "staymatch.notifications"):
        payload = {"event_type": event_type, "data": data}
        if self.producer:
            try:
                self.producer.send(topic, value=payload)
                self.producer.flush()
                logger.info(f"Published notification event '{event_type}' to topic '{topic}'")
                return True
            except Exception as e:
                logger.error(f"Error sending message to Kafka topic '{topic}': {e}")

        logger.info(f"[DEV KAFKA EVENT LOG] Published notification event: {payload}")
        return True

