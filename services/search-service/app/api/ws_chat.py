import json
import logging
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

ws_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Map room_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        logger.info(f"WebSocket connected to room {room_id}. Total connected: {len(self.active_connections[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        logger.info(f"WebSocket disconnected from room {room_id}")

    async def broadcast(self, message: dict, room_id: str, sender_ws: WebSocket = None):
        if room_id in self.active_connections:
            disconnected_sockets = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting WebSocket message: {e}")
                    disconnected_sockets.append(connection)
            for dead in disconnected_sockets:
                self.disconnect(dead, room_id)

manager = ConnectionManager()

@ws_router.websocket("/ws/chat/{room_id}")
async def websocket_chat_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        # Send initial confirmation connection frame
        await websocket.send_json({
            "type": "connection_established",
            "room_id": room_id,
            "status": "connected"
        })
        while True:
            data_text = await websocket.receive_text()
            try:
                data = json.loads(data_text)
            except json.JSONDecodeError:
                data = {"text": data_text, "sender": "user"}

            broadcast_payload = {
                "type": "chat_message",
                "room_id": room_id,
                "id": data.get("id"),
                "sender": data.get("sender", "user"),
                "sender_name": data.get("sender_name", "User"),
                "text": data.get("text", ""),
                "timestamp": data.get("timestamp")
            }

            await manager.broadcast(broadcast_payload, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
    except Exception as e:
        logger.error(f"WebSocket error in room {room_id}: {e}")
        manager.disconnect(websocket, room_id)
