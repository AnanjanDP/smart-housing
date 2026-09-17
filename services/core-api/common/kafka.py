import json
import logging
import os
from typing import Dict, Any

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

def publish_event(topic: str, payload: Dict[str, Any]):
    producer = get_kafka_producer()
    if producer:
        try:
            producer.send(topic, value=payload)
            producer.flush()
            logger.info(f"Published event to topic '{topic}': {payload}")
        except Exception as e:
            logger.error(f"Failed to publish event to topic '{topic}': {e}")
    else:
        logger.info(f"[Kafka Offline] Event for '{topic}': {payload}")
