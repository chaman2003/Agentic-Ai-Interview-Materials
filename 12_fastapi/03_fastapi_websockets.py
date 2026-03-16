"""
FastAPI WebSockets — Comprehensive Examples
===========================================
Covers:
  1. Basic echo WebSocket
  2. Broadcast chat server with room support
  3. Live dashboard (server pushes data to client)
  4. JWT authentication over WebSocket
  5. Binary data / JSON messaging
  6. Connection manager with rooms
  7. Redis pub/sub for multi-instance scaling (conceptual)

Run with:
    uvicorn 03_fastapi_websockets:app --reload --port 8001

Test with:  websocat ws://localhost:8001/ws/echo
            or the HTML test client at http://localhost:8001/test
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Query,
    HTTPException,
    Depends,
)
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="WebSocket Examples", version="1.0.0")

SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"


# ---------------------------------------------------------------------------
# 1. BASIC ECHO WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/ws/echo")
async def echo_endpoint(websocket: WebSocket):
    """
    Simplest possible WebSocket — echoes every message back to the sender.
    Demonstrates: accept(), receive_text(), send_text(), WebSocketDisconnect.
    """
    await websocket.accept()
    client_id = str(uuid.uuid4())[:8]
    print(f"[echo] Client {client_id} connected")
    try:
        while True:
            data = await websocket.receive_text()
            timestamp = datetime.utcnow().isoformat()
            await websocket.send_text(f"[{timestamp}] Echo: {data}")
    except WebSocketDisconnect:
        print(f"[echo] Client {client_id} disconnected")


# ---------------------------------------------------------------------------
# 2. CONNECTION MANAGER — the core building block for multi-client WS apps
# ---------------------------------------------------------------------------

class ConnectionManager:
    """
    Manages active WebSocket connections.
    Supports:
      - Global broadcast
      - Per-room broadcast
      - Personal messages
    """

    def __init__(self):
        # user_id -> WebSocket
        self.connections: Dict[str, WebSocket] = {}
        # room_id -> set of user_ids
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, room_id: str = "lobby"):
        await websocket.accept()
        self.connections[user_id] = websocket
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(user_id)
        print(f"[manager] {user_id} connected to room '{room_id}'")

    def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)
        for room_members in self.rooms.values():
            room_members.discard(user_id)
        print(f"[manager] {user_id} disconnected")

    async def send_personal(self, message: str, user_id: str):
        """Send a message to one specific user."""
        ws = self.connections.get(user_id)
        if ws:
            await ws.send_text(message)

    async def broadcast_to_room(self, message: str, room_id: str, exclude: str = None):
        """Broadcast to all users in a room, optionally excluding the sender."""
        members = self.rooms.get(room_id, set())
        dead = []
        for uid in members:
            if uid == exclude:
                continue
            ws = self.connections.get(uid)
            if ws:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append(uid)
        for uid in dead:
            self.disconnect(uid)

    async def broadcast_all(self, message: str):
        """Broadcast to every connected user."""
        dead = []
        for uid, ws in self.connections.items():
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(uid)
        for uid in dead:
            self.disconnect(uid)

    def get_room_members(self, room_id: str) -> List[str]:
        return list(self.rooms.get(room_id, set()))

    def user_count(self) -> int:
        return len(self.connections)


manager = ConnectionManager()


# ---------------------------------------------------------------------------
# 3. CHAT SERVER WITH ROOMS
# ---------------------------------------------------------------------------

@app.websocket("/ws/chat/{room_id}")
async def chat_endpoint(
    websocket: WebSocket,
    room_id: str,
    username: str = Query(..., description="Display name for chat"),
):
    """
    Multi-room chat server.
    - Join a named room via URL path param
    - Messages are broadcast to all room members
    - Supports JSON protocol: {"type": "message"|"ping", "text": "..."}
    """
    user_id = f"{username}_{uuid.uuid4().hex[:4]}"
    await manager.connect(websocket, user_id, room_id)

    # Announce arrival
    join_msg = json.dumps({
        "type": "system",
        "user": "System",
        "text": f"{username} joined room '{room_id}'",
        "timestamp": datetime.utcnow().isoformat(),
        "members": manager.get_room_members(room_id),
    })
    await manager.broadcast_to_room(join_msg, room_id)

    try:
        while True:
            raw = await websocket.receive_text()

            # Parse JSON protocol
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "text": "Invalid JSON"}))
                continue

            msg_type = payload.get("type", "message")

            if msg_type == "ping":
                # Heartbeat — respond with pong
                await websocket.send_text(json.dumps({"type": "pong"}))

            elif msg_type == "message":
                # Broadcast message to room
                outbound = json.dumps({
                    "type": "message",
                    "user": username,
                    "text": payload.get("text", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                })
                await manager.broadcast_to_room(outbound, room_id)

            elif msg_type == "private":
                # Private message to a specific user
                target = payload.get("to")
                if target:
                    dm = json.dumps({
                        "type": "private",
                        "from": username,
                        "text": payload.get("text", ""),
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    await manager.send_personal(dm, target)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        leave_msg = json.dumps({
            "type": "system",
            "user": "System",
            "text": f"{username} left room '{room_id}'",
            "timestamp": datetime.utcnow().isoformat(),
            "members": manager.get_room_members(room_id),
        })
        await manager.broadcast_to_room(leave_msg, room_id)


# ---------------------------------------------------------------------------
# 4. LIVE DASHBOARD — server pushes data to client
# ---------------------------------------------------------------------------

import random  # for simulated metrics

@app.websocket("/ws/dashboard")
async def dashboard_endpoint(websocket: WebSocket):
    """
    Server-side push pattern — server sends live metrics every second.
    Client doesn't send anything (read-only stream).
    Real use case: live charts, monitoring dashboards, stock tickers.
    """
    await websocket.accept()
    print("[dashboard] Client subscribed to live metrics")
    try:
        while True:
            # Simulate real-time metrics (in production: query Prometheus, Redis, DB)
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "active_users": manager.user_count(),
                "cpu_percent": round(random.uniform(10, 90), 1),
                "memory_mb": round(random.uniform(200, 800), 1),
                "requests_per_sec": round(random.uniform(50, 500), 1),
                "error_rate": round(random.uniform(0, 5), 2),
            }
            await websocket.send_json(metrics)
            await asyncio.sleep(1)  # Push every second
    except WebSocketDisconnect:
        print("[dashboard] Client unsubscribed")


# ---------------------------------------------------------------------------
# 5. AUTHENTICATED WebSocket (JWT via query param)
# ---------------------------------------------------------------------------

def create_test_token(user_id: int, username: str) -> str:
    """Helper to create a test JWT — for demo purposes only."""
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_ws_token(token: str) -> dict:
    """Decode and validate JWT for WebSocket auth."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


@app.websocket("/ws/secure")
async def secure_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Bearer token"),
):
    """
    Authenticated WebSocket.
    - Auth MUST happen before accept() — we close with 1008 if invalid
    - Token passed as query param: ws://host/ws/secure?token=<jwt>
    - Headers can't be set easily in browser WebSocket API, hence query param
    """
    # Validate BEFORE accept() — cleanest rejection point
    try:
        payload = decode_ws_token(token)
        user_id = payload["sub"]
        username = payload.get("username", "unknown")
    except ValueError:
        # 1008 = Policy Violation — standard code for auth rejection
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await websocket.accept()
    await websocket.send_json({
        "type": "auth_success",
        "user_id": user_id,
        "username": username,
        "message": "Authenticated successfully",
    })

    try:
        while True:
            data = await websocket.receive_json()
            # Process authenticated user's messages
            response = {
                "type": "response",
                "user": username,
                "echo": data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await websocket.send_json(response)
    except WebSocketDisconnect:
        print(f"[secure] Authenticated user {username} disconnected")


# ---------------------------------------------------------------------------
# 6. BINARY DATA — receive and send bytes (file chunks, images)
# ---------------------------------------------------------------------------

@app.websocket("/ws/binary")
async def binary_endpoint(websocket: WebSocket):
    """
    Binary WebSocket — useful for streaming file uploads/downloads,
    audio processing, or sending compressed data.
    """
    await websocket.accept()
    total_bytes = 0
    chunks = []

    try:
        while True:
            # receive_bytes() for binary frames; receive_text() for text frames
            message = await websocket.receive()

            if message["type"] == "websocket.receive":
                if "bytes" in message and message["bytes"]:
                    chunk = message["bytes"]
                    chunks.append(chunk)
                    total_bytes += len(chunk)
                    # Acknowledge each chunk
                    await websocket.send_json({
                        "status": "chunk_received",
                        "chunk_size": len(chunk),
                        "total_bytes": total_bytes,
                    })
                elif "text" in message:
                    cmd = json.loads(message["text"])
                    if cmd.get("type") == "upload_complete":
                        # Echo back a summary (in real app: save file)
                        await websocket.send_json({
                            "type": "upload_complete",
                            "total_bytes": total_bytes,
                            "chunks": len(chunks),
                        })
                        chunks = []
                        total_bytes = 0

            elif message["type"] == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        print(f"[binary] Client disconnected after {total_bytes} bytes")


# ---------------------------------------------------------------------------
# 7. HTTP ENDPOINT to issue test tokens (for testing auth WS)
# ---------------------------------------------------------------------------

class TokenRequest(BaseModel):
    user_id: int = 1
    username: str = "testuser"


@app.post("/auth/test-token")
async def get_test_token(req: TokenRequest):
    """
    Development-only endpoint to get a JWT for testing the secure WebSocket.
    Use:  POST /auth/test-token {"user_id": 1, "username": "alice"}
    Then: ws://localhost:8001/ws/secure?token=<returned_token>
    """
    token = create_test_token(req.user_id, req.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "ws_url": f"ws://localhost:8001/ws/secure?token={token}",
    }


# ---------------------------------------------------------------------------
# 8. STATS endpoint — HTTP endpoint showing current WS state
# ---------------------------------------------------------------------------

@app.get("/ws/stats")
async def websocket_stats():
    """HTTP endpoint to check live WebSocket connection stats."""
    return {
        "active_connections": manager.user_count(),
        "rooms": {
            room_id: list(members)
            for room_id, members in manager.rooms.items()
            if members
        },
    }


# ---------------------------------------------------------------------------
# 9. HTML TEST CLIENT — visit http://localhost:8001/test to try the chat
# ---------------------------------------------------------------------------

HTML_TEST_CLIENT = """
<!DOCTYPE html>
<html>
<head><title>WebSocket Test</title></head>
<body>
<h2>FastAPI WebSocket Test Client</h2>
<label>Room: <input id="room" value="general"/></label>
<label>Username: <input id="username" value="alice"/></label>
<button onclick="connect()">Connect</button>
<button onclick="disconnect()">Disconnect</button>
<hr/>
<input id="msg" placeholder="Type a message..." style="width:300px"/>
<button onclick="sendMsg()">Send</button>
<hr/>
<div id="log" style="height:300px;overflow-y:scroll;border:1px solid #ccc;padding:8px;font-family:monospace"></div>
<script>
let ws = null;
function log(msg, color='black') {
    const div = document.getElementById('log');
    div.innerHTML += `<div style="color:${color}">${new Date().toLocaleTimeString()}: ${msg}</div>`;
    div.scrollTop = div.scrollHeight;
}
function connect() {
    const room = document.getElementById('room').value;
    const user = document.getElementById('username').value;
    ws = new WebSocket(`ws://localhost:8001/ws/chat/${room}?username=${user}`);
    ws.onopen = () => log('Connected!', 'green');
    ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        const color = data.type === 'system' ? 'blue' : data.type === 'private' ? 'purple' : 'black';
        log(`[${data.type}] ${data.user || ''}: ${data.text}`, color);
    };
    ws.onclose = () => log('Disconnected', 'red');
    ws.onerror = (e) => log('Error: ' + e, 'red');
}
function disconnect() { if (ws) ws.close(); }
function sendMsg() {
    const text = document.getElementById('msg').value;
    if (ws && text) {
        ws.send(JSON.stringify({type: 'message', text}));
        document.getElementById('msg').value = '';
    }
}
document.getElementById('msg').addEventListener('keypress', e => { if (e.key === 'Enter') sendMsg(); });
</script>
</body>
</html>
"""

@app.get("/test", response_class=HTMLResponse)
async def test_client():
    """Serve a simple HTML WebSocket test client."""
    return HTMLResponse(content=HTML_TEST_CLIENT)


# ---------------------------------------------------------------------------
# 10. CONCEPTUAL: Redis pub/sub for scaling across multiple server instances
# ---------------------------------------------------------------------------

"""
SCALING WEBSOCKETS WITH REDIS PUB/SUB (conceptual — requires redis + aioredis)
==============================================================================

Problem: The ConnectionManager above stores connections in memory.
If you run 2 uvicorn workers, a message sent to worker-1 won't reach
clients connected to worker-2.

Solution: Use Redis as a message bus.

import aioredis

redis = aioredis.from_url("redis://localhost")

@app.websocket("/ws/scaled-chat/{room_id}")
async def scaled_chat(websocket: WebSocket, room_id: str, username: str = Query(...)):
    await websocket.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"room:{room_id}")

    async def receive_from_redis():
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"].decode())

    # Run redis listener concurrently with receiving from this client
    redis_task = asyncio.create_task(receive_from_redis())

    try:
        while True:
            data = await websocket.receive_text()
            # Publish to Redis — all server instances receive it
            await redis.publish(f"room:{room_id}", json.dumps({
                "user": username, "text": data,
                "timestamp": datetime.utcnow().isoformat()
            }))
    except WebSocketDisconnect:
        redis_task.cancel()
        await pubsub.unsubscribe(f"room:{room_id}")
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("03_fastapi_websockets:app", host="0.0.0.0", port=8001, reload=True)
