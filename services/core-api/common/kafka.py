import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from django.db import transaction

logger = logging.getLogger(__name__)

_producer = None

def get_kafka_producer():
    global _producer
    if _producer is None:
        try:
            from kafka import KafkaProducer
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
            _producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                max_block_ms=2000
            )
        except Exception as e:
            logger.warning(f"Kafka producer initialization failed: {e}")
            _producer = False
    return _producer if _producer else None

def publish_event(topic: str, payload: Dict[str, Any], correlation_id: str = None):
    """
    Publish structured domain event to Kafka.
    Enforces transaction.on_commit() in Django to prevent race conditions or ghost events.
    """
    event_type = payload.get("event_type", "DOMAIN_EVENT")
    event_envelope = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id or payload.get("correlation_id") or str(uuid.uuid4()),
        "payload": payload
    }

    def _do_publish():
        producer = get_kafka_producer()
        if producer:
            try:
                producer.send(topic, value=event_envelope)
                producer.flush()
                logger.info(f"Published Kafka event '{event_type}' [ID: {event_envelope['event_id']}] to topic '{topic}'")
            except Exception as e:
                logger.error(f"Failed to publish event '{event_type}' to topic '{topic}': {e}")
        else:
            logger.info(f"[Kafka Offline] Event for '{topic}': {event_envelope}")

    # Ensure events dispatch strictly AFTER the DB transaction commits
    if transaction.get_connection().in_atomic_block:
        transaction.on_commit(_do_publish)
    else:
        _do_publish()

