import asyncio
import json
import logging
import re
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

from app.core.auth import ChatAuthError, verify_access_token
from app.core.config import settings
from app.services.chat_access import can_join

logger = logging.getLogger(__name__)

ws_router = APIRouter()

# Close codes (4000-4999 are reserved for applications)
CLOSE_UNAUTHENTICATED = 4401
CLOSE_FORBIDDEN = 4403
CLOSE_ROOM_FULL = 4429
CLOSE_TOO_BIG = 1009
CLOSE_SERVER_ERROR = 1011

AUTH_TIMEOUT_SECONDS = 5.0
MAX_FRAME_CHARS = 8192
MAX_TEXT_CHARS = 2000
MAX_NAME_CHARS = 60
MAX_CLIENT_ID_CHARS = 64
MAX_CONNECTIONS_PER_ROOM = 10
RATE_LIMIT_MESSAGES = 10
RATE_LIMIT_WINDOW_SECONDS = 10.0
MAX_RATE_VIOLATIONS = 20
SEND_TIMEOUT_SECONDS = 5.0

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def lookup_listing_owner(listing_id: str) -> Optional[str]:
    from app.repositories.listing_repository import ListingRepository

    return ListingRepository().fetch_listing_owner(listing_id)


class Connection:
    def __init__(self, websocket: WebSocket, user_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.sent_at: Deque[float] = deque()
        self.violations = 0

    def allow_message(self, now: float) -> bool:
        while self.sent_at and now - self.sent_at[0] > RATE_LIMIT_WINDOW_SECONDS:
            self.sent_at.popleft()
        if len(self.sent_at) >= RATE_LIMIT_MESSAGES:
            self.violations += 1
            return False
        self.sent_at.append(now)
        return True


class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, List[Connection]] = {}

    def room_size(self, room_id: str) -> int:
        return len(self.rooms.get(room_id, []))

    def add(self, room_id: str, connection: Connection) -> None:
        self.rooms.setdefault(room_id, []).append(connection)
        logger.info("Chat connection joined room %s (%d connected)", room_id, self.room_size(room_id))

    def remove(self, room_id: str, connection: Connection) -> None:
        members = self.rooms.get(room_id)
        if not members:
            return
        if connection in members:
            members.remove(connection)
        if not members:
            del self.rooms[room_id]

    async def _send(self, connection: Connection, message: dict) -> bool:
        try:
            await asyncio.wait_for(connection.websocket.send_json(message), SEND_TIMEOUT_SECONDS)
            return True
        except Exception as exc:
            logger.warning("Dropping an unresponsive chat connection: %s", exc)
            return False

    async def broadcast(self, room_id: str, message: dict) -> None:
        members = list(self.rooms.get(room_id, []))
        results = await asyncio.gather(*(self._send(c, message) for c in members))
        for connection, ok in zip(members, results):
            if not ok:
                self.remove(room_id, connection)


manager = ConnectionManager()


def origin_allowed(websocket: WebSocket) -> bool:
    """Browsers always send Origin; reject cross-site pages. Non-browser clients send none."""
    origin = websocket.headers.get("origin")
    if origin is None:
        return True
    allowed = settings.allowed_origins()
    return "*" in allowed or origin in allowed


def clean_text(value, limit: int) -> str:
    return _CONTROL_CHARS.sub("", value).strip()[:limit] if isinstance(value, str) else ""


async def authenticate(websocket: WebSocket) -> Optional[str]:
    """The first frame must be {"type": "auth", "token": <access token>}, sent within a few seconds."""
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), AUTH_TIMEOUT_SECONDS)
        frame = json.loads(raw)
        if not isinstance(frame, dict) or frame.get("type") != "auth":
            return None
        return verify_access_token(frame.get("token"))
    except (asyncio.TimeoutError, ValueError, ChatAuthError, WebSocketDisconnect):
        return None


@ws_router.websocket("/ws/chat/{room_id}")
async def websocket_chat_endpoint(websocket: WebSocket, room_id: str):
    if not origin_allowed(websocket):
        await websocket.close(code=CLOSE_FORBIDDEN)
        return

    await websocket.accept()

    user_id = await authenticate(websocket)
    if user_id is None:
        await websocket.close(code=CLOSE_UNAUTHENTICATED)
        return

    try:
        permitted = await run_in_threadpool(can_join, user_id, room_id, lookup_listing_owner)
    except Exception as exc:
        logger.error("Chat room authorisation failed for room %s: %s", room_id, exc)
        await websocket.close(code=CLOSE_SERVER_ERROR)
        return
    if not permitted:
        await websocket.close(code=CLOSE_FORBIDDEN)
        return

    if manager.room_size(room_id) >= MAX_CONNECTIONS_PER_ROOM:
        await websocket.close(code=CLOSE_ROOM_FULL)
        return

    connection = Connection(websocket, user_id)
    manager.add(room_id, connection)
    try:
        await websocket.send_json({
            "type": "connection_established",
            "room_id": room_id,
            "user_id": user_id,
            "status": "connected",
        })
        while True:
            data_text = await websocket.receive_text()
            if len(data_text) > MAX_FRAME_CHARS:
                await websocket.close(code=CLOSE_TOO_BIG)
                return
            try:
                data = json.loads(data_text)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue

            text = clean_text(data.get("text"), MAX_TEXT_CHARS)
            if not text:
                continue

            if not connection.allow_message(time.monotonic()):
                await websocket.send_json({"type": "error", "code": "rate_limited"})
                if connection.violations >= MAX_RATE_VIOLATIONS:
                    await websocket.close(code=CLOSE_ROOM_FULL)
                    return
                continue

            client_id = data.get("id")
            await manager.broadcast(room_id, {
                "type": "chat_message",
                "room_id": room_id,
                "id": uuid.uuid4().hex,
                "client_id": client_id if isinstance(client_id, (str, int)) and len(str(client_id)) <= MAX_CLIENT_ID_CHARS else None,
                # Who sent it comes from the verified token, never from the message.
                "sender_id": user_id,
                "sender_name": clean_text(data.get("sender_name"), MAX_NAME_CHARS) or "User",
                "text": text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.error("WebSocket error in room %s: %s", room_id, exc)
    finally:
        manager.remove(room_id, connection)
        logger.info("Chat connection left room %s", room_id)
