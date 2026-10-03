import json
import logging
import os
import time
import uuid
from typing import Dict, Any
from app.consumers.listing_consumer import ListingEventConsumer
from app.consumers.application_consumer import ApplicationEventConsumer
from app.consumers.review_consumer import ReviewEventConsumer

logger = logging.getLogger(__name__)

class NotificationKafkaConsumerRunner:
    def __init__(self):
        self.listing_consumer = ListingEventConsumer()
        self.application_consumer = ApplicationEventConsumer()
        self.review_consumer = ReviewEventConsumer()
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
        self.dlq_topic = os.getenv('KAFKA_DLQ_TOPIC', 'dlq_events')
        self.max_retries = 3
        self._redis_client = None

    def _get_redis(self):
        if self._redis_client is None:
            try:
                import redis
                redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
                self._redis_client = redis.Redis.from_url(redis_url, socket_connect_timeout=1)
            except Exception as e:
                logger.warning(f"Redis initialization failed for idempotency check: {e}")
                self._redis_client = False
        return self._redis_client if self._redis_client else None

    def _is_duplicate_event(self, event_id: str) -> bool:
        redis_inst = self._get_redis()
        if not redis_inst or not event_id:
            return False
        try:
            dedup_key = f"processed_event:{event_id}"
            is_new = redis_inst.set(dedup_key, "1", nx=True, ex=86400)  # TTL 24h
            return not is_new
        except Exception as e:
            logger.warning(f"Idempotency check Redis error: {e}")
            return False

    def _send_to_dlq(self, topic: str, raw_payload: Any, error_message: str):
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                max_block_ms=2000
            )
            dlq_message = {
                "original_topic": topic,
                "payload": raw_payload,
                "error": error_message,
                "failed_at": time.time()
            }
            producer.send(self.dlq_topic, dlq_message)
            producer.flush()
            logger.error(f"Routed toxic message from topic [{topic}] to DLQ [{self.dlq_topic}]: {error_message}")
        except Exception as e:
            logger.critical(f"Failed to send message to DLQ: {e}")

    def _dispatch_event(self, topic: str, payload: Dict[str, Any]):
        if topic == 'listing_events':
            self.listing_consumer.handle_message(payload)
        elif topic == 'application_events':
            self.application_consumer.handle_message(payload)
        elif topic == 'review_events':
            self.review_consumer.handle_message(payload)

    def start_listening(self):
        from kafka import KafkaConsumer
        topics = ['listing_events', 'application_events', 'review_events']
        
        while True:
            try:
                logger.info(f"Connecting to Kafka at {self.bootstrap_servers}...")
                consumer = KafkaConsumer(
                    *topics,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id='notification-service-group',
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                )
                logger.info("Successfully connected to Kafka. Listening for events...")

                for message in consumer:
                    topic = message.topic
                    raw_event = message.value
                    
                    # Envelope extraction (supports uniform envelope and fallback raw payload)
                    if isinstance(raw_event, dict) and "payload" in raw_event and "event_id" in raw_event:
                        event_id = raw_event.get("event_id")
                        event_type = raw_event.get("event_type")
                        correlation_id = raw_event.get("correlation_id")
                        inner_payload = raw_event.get("payload", {})
                    else:
                        event_id = str(uuid.uuid4())
                        event_type = raw_event.get("event_type", "UNKNOWN") if isinstance(raw_event, dict) else "UNKNOWN"
                        correlation_id = str(uuid.uuid4())
                        inner_payload = raw_event

                    logger.info(
                        f"Received Kafka event '{event_type}' on topic [{topic}]",
                        extra={"event_id": event_id, "correlation_id": correlation_id}
                    )

                    # 1. Idempotency Check
                    if self._is_duplicate_event(event_id):
                        logger.warning(f"Skipping duplicate event [ID: {event_id}] on topic [{topic}]")
                        continue

                    # 2. Process with retry and DLQ routing
                    success = False
                    for attempt in range(1, self.max_retries + 1):
                        try:
                            self._dispatch_event(topic, inner_payload)
                            success = True
                            break
                        except Exception as err:
                            logger.warning(
                                f"Attempt {attempt}/{self.max_retries} failed for event [ID: {event_id}]: {err}"
                            )
                            time.sleep(1)

                    if not success:
                        logger.error(f"Event processing failed after {self.max_retries} attempts. Routing to DLQ.")
                        self._send_to_dlq(topic, raw_event, f"Failed after {self.max_retries} retries")

            except Exception as err:
                logger.error(f"Kafka consumer error ({err}). Reconnecting in 5 seconds...")
                time.sleep(5)
