import logging
import time
import uuid
from typing import Any, Callable, Dict, Tuple

from app.core.idempotency import BUSY, DONE

logger = logging.getLogger(__name__)

PROCESSED = "processed"
DUPLICATE = "duplicate"
DEAD_LETTERED = "dead_lettered"


class StillProcessingElsewhere(Exception):
    """Another worker holds this event and did not finish; the offset must not be committed."""


def unwrap(raw_event: Any) -> Tuple[str, str, Dict[str, Any]]:
    """Return (event_id, event_type, payload) for an enveloped event or a bare payload."""
    if isinstance(raw_event, dict) and "payload" in raw_event and "event_id" in raw_event:
        return raw_event["event_id"], raw_event.get("event_type", "UNKNOWN"), raw_event.get("payload") or {}
    event_type = raw_event.get("event_type", "UNKNOWN") if isinstance(raw_event, dict) else "UNKNOWN"
    return str(uuid.uuid4()), event_type, raw_event if isinstance(raw_event, dict) else {}


class EventProcessor:
    """Handles one Kafka message: de-duplicate, process with retries, dead-letter on persistent failure.

    `process` returns normally only when the message is finished with (handled, skipped as a duplicate, or
    safely dead-lettered), which is exactly when its offset may be committed. If it raises, the offset must
    not be committed so the message is delivered again.
    """

    def __init__(self, dispatch: Callable[[str, Dict[str, Any]], None], idempotency, send_to_dlq: Callable,
                 max_retries: int = 3, retry_delay: float = 1.0, busy_wait: float = 2.0, busy_attempts: int = 30,
                 sleep: Callable[[float], None] = time.sleep):
        self.dispatch = dispatch
        self.idempotency = idempotency
        self.send_to_dlq = send_to_dlq
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.busy_wait = busy_wait
        self.busy_attempts = busy_attempts
        self.sleep = sleep

    def _claim(self, event_id: str) -> str:
        for _ in range(self.busy_attempts):
            state = self.idempotency.claim(event_id)
            if state != BUSY:
                return state
            self.sleep(self.busy_wait)
        raise StillProcessingElsewhere(event_id)

    def process(self, topic: str, raw_event: Any) -> str:
        event_id, event_type, payload = unwrap(raw_event)
        logger.info("Received %s on %s [%s]", event_type, topic, event_id)

        if self._claim(event_id) == DONE:
            logger.warning("Skipping duplicate event %s on %s", event_id, topic)
            return DUPLICATE

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self.dispatch(topic, payload)
            except Exception as exc:
                last_error = exc
                logger.warning("Attempt %d/%d failed for event %s: %s", attempt, self.max_retries, event_id, exc)
                if getattr(exc, "permanent", False):
                    break  # retrying cannot help
                if attempt < self.max_retries:
                    self.sleep(self.retry_delay)
                continue
            self.idempotency.complete(event_id)
            return PROCESSED

        # Release the claim first so a manual replay from the dead-letter topic is not mistaken for a duplicate.
        self.idempotency.release(event_id)
        # If the dead-letter write fails this raises, the offset stays uncommitted and the message returns.
        self.send_to_dlq(topic, raw_event, f"Failed: {last_error}")
        return DEAD_LETTERED
