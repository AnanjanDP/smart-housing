"""Publishing domain events to Kafka through a transactional outbox.

`publish_event` does not talk to Kafka. It stores the event in the database inside the caller's
transaction, so an event is recorded if and only if the change that caused it was committed. Events are
then delivered by `dispatch_pending`, which runs right after the commit (for low latency) and again from
the `relay_outbox` command (which retries until the broker accepts them). Delivery is at least once and in
order, so consumers must tolerate duplicates; every event carries a unique `event_id` for that.
"""
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from django.db import transaction

logger = logging.getLogger(__name__)

SEND_TIMEOUT_SECONDS = 5
DEFAULT_BATCH_SIZE = 100

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
                acks='all',
                retries=3,
                max_block_ms=2000,
            )
        except Exception as e:
            logger.warning("Kafka producer initialization failed: %s", e)
            _producer = False
    return _producer if _producer else None


def reset_kafka_producer():
    """Forget a producer that failed so the next attempt reconnects."""
    global _producer
    _producer = None


def publish_event(topic: str, payload: Dict[str, Any], correlation_id: Optional[str] = None):
    """Record a domain event for delivery. Call it inside the transaction that makes the change."""
    from apps.notifications.models import OutboxEvent

    event_type = payload.get("event_type", "DOMAIN_EVENT")
    envelope = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id or payload.get("correlation_id") or str(uuid.uuid4()),
        "payload": payload,
    }
    event = OutboxEvent.objects.create(topic=topic, envelope=envelope)

    def _deliver_now():
        try:
            dispatch_pending()
        except Exception:
            # Not fatal: the event is safely stored and the relay will deliver it.
            logger.warning("Immediate delivery of outbox events failed; the relay will retry", exc_info=True)

    transaction.on_commit(_deliver_now)  # runs at once when no transaction is open
    return event


def dispatch_pending(producer=None, batch_size: int = DEFAULT_BATCH_SIZE) -> int:
    """Send unsent events, oldest first. Stops at the first failure so order is kept. Returns how many were sent."""
    from django.utils import timezone as dj_timezone
    from apps.notifications.models import OutboxEvent

    producer = producer or get_kafka_producer()
    if producer is None:
        return 0

    sent = 0
    with transaction.atomic():
        # Rows are locked while being sent, so concurrent relays never send the same event twice.
        pending = (
            OutboxEvent.objects.select_for_update(skip_locked=True)
            .filter(published_at__isnull=True)
            .order_by('created_at')[:batch_size]
        )
        for event in pending:
            try:
                producer.send(event.topic, value=event.envelope).get(timeout=SEND_TIMEOUT_SECONDS)
            except Exception as exc:
                event.attempts += 1
                event.last_error = str(exc)[:500]
                event.save(update_fields=['attempts', 'last_error'])
                logger.error("Could not publish %s to %s (attempt %d): %s",
                             event.envelope.get('event_type'), event.topic, event.attempts, exc)
                reset_kafka_producer()
                break
            event.published_at = dj_timezone.now()
            event.save(update_fields=['published_at'])
            sent += 1
    return sent
