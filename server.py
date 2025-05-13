import asyncio
import json, os
import websockets
from dotenv import load_dotenv
from logger_init import logger
from websockets import WebSocketClientProtocol

load_dotenv()


class WebSocketServer:
    def __init__(self):
        self.clients = dict()
        self.WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT")
        self.WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
        self.stop_event = asyncio.Event()

    async def register(self, websocket: WebSocketClientProtocol, user_id: str):
        if user_id in self.clients:
            logger.warning(f"user_id {user_id} already connected. Disconnecting old session.")
            old_ws: WebSocketClientProtocol = self.clients[user_id]
            await old_ws.close(reason="Duplicate login")
        self.clients[user_id] = websocket
        logger.info(f"New client connected: {websocket.remote_address} with user_id: {user_id}")
        logger.info(f"Current clients: {self.clients}")
        await self.notify_all({
            "type": "user_joined",
            "user_id": user_id,
            "message": f"{user_id} has connected."
        }, exclude=user_id)

    async def unregister(self, user_id: str):
        websocket: WebSocketClientProtocol = self.clients.pop(user_id, None)
        if websocket:
            logger.info(f"Current clients: {self.clients}")
            logger.info(f"Client disconnected: {websocket.remote_address} with user_id: {user_id}")
            await self.notify_all({
                "type": "user_left",
                "user_id": user_id,
                "message": f"{user_id} has disconnected."
            }, exclude=user_id)
        else:
            logger.info(f"Client with user_id: {user_id} not found in clients")

    async def handler(self, websocket: WebSocketClientProtocol):
        user_id = None
        try:
            async for message in websocket:
                try:
                    data: dict = json.loads(message)
                    if data.get("type") == "join":
                        user_id = data.get("user_id")
                        if not user_id:
                            await websocket.send(json.dumps({
                                "error": "Missing user_id in join request"
                            }))
                            continue
                        await self.register(websocket, user_id)
                        continue

                    # Handle message types
                    if data.get("type") == "hello":
                        await websocket.send(json.dumps({
                            "status": "hello",
                            "payload": "Hello, client!"
                        }))
                    elif data.get("type") == "broadcast":
                        logger.info(f"Broadcasting message from {user_id}: {data}")
                        await self.broadcast(data, sender_id=user_id)
                    elif data.get("type") == "disconnect":
                        await self.broadcast({
                            "type": "notification",
                            "payload": f"{user_id} has left the chat"
                        }, sender_id=user_id)
                        await websocket.close(reason="Client requested disconnect")
                        break
                    else:
                        await websocket.send(json.dumps({
                            "status": "unknown",
                            "payload": "Unknown message type"
                        }))

                except json.JSONDecodeError:
                    logger.error("Received invalid JSON from client.")
                    await websocket.send(json.dumps({
                        "error": "Invalid message format. Must be JSON."
                    }))
                except Exception as e:
                    logger.error(f"Unexpected error while handling message: {e}")
                    await websocket.send(json.dumps({
                        "error": "Server error occurred while processing your message."
                    }))
        except websockets.exceptions.ConnectionClosedError:
            logger.warning(f"Client forcibly disconnected: {websocket.remote_address}")
        except websockets.exceptions.ConnectionClosedOK:
            logger.warning(f"Client disconnected gracefully: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"Unexpected error during WebSocket communication: {e}")
        finally:
            if user_id:
                await self.unregister(user_id)
                logger.info(f"User unregistered. Id: {user_id}")
            else:
                logger.warning("Client disconnected before registering.")


    async def start(self):
        logger.info(f"Starting WebSocket server on {self.WEBSOCKET_HOST}:{self.WEBSOCKET_PORT}")
        async with websockets.serve(self.handler, self.WEBSOCKET_HOST, self.WEBSOCKET_PORT, ping_interval=20, ping_timeout=20):
            logger.info(f"WebSocket server started on {self.WEBSOCKET_HOST}:{self.WEBSOCKET_PORT}")
            await self.stop_event.wait()

    async def stop(self):
        logger.info("Shutting down WebSocket server...")
        self.stop_event.set()

    async def broadcast(self, message: dict, sender_id: str = None):
        if sender_id not in self.clients:
            logger.warning(f"Sender {sender_id} not registered. Ignoring broadcast.")
            return
        for uid, client in self.clients.items():
            if uid != sender_id:
                try:
                    await client.send(json.dumps({"from": sender_id, "message": message.get("payload")}))
                except Exception as e:
                    logger.error(f"Error sending message to {uid}: {e}")

    async def notify_all(self, message: dict, exclude: str = None):
        for uid, client in self.clients.items():
            if uid != exclude:
                try:
                    await client.send(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error notifying {uid}: {e}")