import json
import logging
import os
import time
from typing import Any, Dict

from app.consumers.application_consumer import ApplicationEventConsumer
from app.consumers.listing_consumer import ListingEventConsumer
from app.consumers.processor import EventProcessor
from app.consumers.review_consumer import ReviewEventConsumer
from app.core.idempotency import RedisIdempotencyStore

logger = logging.getLogger(__name__)

TOPICS = ['listing_events', 'application_events', 'review_events']
GROUP_ID = 'notification-service-group'
DLQ_SEND_TIMEOUT_SECONDS = 10


class NotificationKafkaConsumerRunner:
    def __init__(self, idempotency=None):
        self.listing_consumer = ListingEventConsumer()
        self.application_consumer = ApplicationEventConsumer()
        self.review_consumer = ReviewEventConsumer()
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
        self.dlq_topic = os.getenv('KAFKA_DLQ_TOPIC', 'dlq_events')
        self._dlq_producer = None
        self.processor = EventProcessor(
            dispatch=self._dispatch_event,
            idempotency=idempotency or RedisIdempotencyStore(),
            send_to_dlq=self._send_to_dlq,
        )

    def _dispatch_event(self, topic: str, payload: Dict[str, Any]):
        if topic == 'listing_events':
            self.listing_consumer.handle_message(payload)
        elif topic == 'application_events':
            self.application_consumer.handle_message(payload)
        elif topic == 'review_events':
            self.review_consumer.handle_message(payload)
        else:
            raise ValueError(f"no handler for topic '{topic}'")

    def _send_to_dlq(self, topic: str, raw_payload: Any, error_message: str):
        """Park a message that cannot be processed. Raises if the write fails, so the message is not lost."""
        try:
            if self._dlq_producer is None:
                from kafka import KafkaProducer
                self._dlq_producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    acks='all',
                    max_block_ms=5000,
                )
            self._dlq_producer.send(self.dlq_topic, {
                "original_topic": topic,
                "payload": raw_payload,
                "error": error_message,
                "failed_at": time.time(),
            }).get(timeout=DLQ_SEND_TIMEOUT_SECONDS)
        except Exception:
            self._dlq_producer = None
            logger.critical("Could not write to the dead-letter topic; the message will be redelivered", exc_info=True)
            raise
        logger.error("Routed message from [%s] to dead-letter topic [%s]: %s", topic, self.dlq_topic, error_message)

    def _new_consumer(self):
        from kafka import KafkaConsumer
        return KafkaConsumer(
            *TOPICS,
            bootstrap_servers=self.bootstrap_servers,
            group_id=GROUP_ID,
            auto_offset_reset='earliest',
            # Offsets are committed by hand, only after a message is finished with. An automatic
            # commit could mark a message as done before (or even though) it was processed.
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )

    def start_listening(self):
        while True:
            consumer = None
            try:
                logger.info("Connecting to Kafka at %s...", self.bootstrap_servers)
                consumer = self._new_consumer()
                logger.info("Connected. Listening for events.")
                for message in consumer:
                    self.processor.process(message.topic, message.value)
                    consumer.commit()
            except Exception as err:
                # Includes failures to dead-letter: the offset was not committed, so the message returns.
                logger.error("Kafka consumer error (%s). Reconnecting in 5 seconds...", err)
                time.sleep(5)
            finally:
                if consumer is not None:
                    try:
                        consumer.close(autocommit=False)
                    except Exception:
                        pass
