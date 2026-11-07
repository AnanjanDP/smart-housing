"""Remembers which events have been handled, so a redelivered event does not send a second email.

Protocol: `claim` before processing (a short-lived "processing" marker), `complete` after success (a 24h
"done" marker), `release` after a failure so the retry can claim again. A crash between claim and
complete leaves only the short marker, which expires, so the event is processed again rather than lost.

If Redis is unreachable the store lets events through (and logs it): a duplicate email is better than
silence. Delivery is at-least-once.
"""
import logging
import os

logger = logging.getLogger(__name__)

NEW = "new"
DONE = "done"
BUSY = "busy"

PROCESSING_TTL_SECONDS = 60
DONE_TTL_SECONDS = 24 * 3600


class RedisIdempotencyStore:
    def __init__(self, client=None, url=None):
        self._client = client
        self._url = url or os.getenv('REDIS_URL', 'redis://redis:6379/0')

    def _redis(self):
        if self._client is None:
            import redis
            self._client = redis.Redis.from_url(self._url, socket_connect_timeout=2, socket_timeout=2)
        return self._client

    @staticmethod
    def _key(event_id: str) -> str:
        return f"notification:event:{event_id}"

    def claim(self, event_id: str) -> str:
        if not event_id:
            return NEW
        try:
            client = self._redis()
            key = self._key(event_id)
            if client.set(key, "processing", nx=True, ex=PROCESSING_TTL_SECONDS):
                return NEW
            state = client.get(key)
            if isinstance(state, bytes):
                state = state.decode()
            if state == "done":
                return DONE
            if state is None:  # expired between the two calls
                return self.claim(event_id)
            return BUSY
        except Exception as exc:
            logger.warning("Idempotency store unavailable, processing without a duplicate check: %s", exc)
            return NEW

    def complete(self, event_id: str) -> None:
        try:
            self._redis().set(self._key(event_id), "done", ex=DONE_TTL_SECONDS)
        except Exception as exc:
            logger.warning("Could not record event %s as processed: %s", event_id, exc)

    def release(self, event_id: str) -> None:
        try:
            self._redis().delete(self._key(event_id))
        except Exception as exc:
            logger.warning("Could not release event %s: %s", event_id, exc)
