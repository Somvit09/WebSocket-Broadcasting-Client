import asyncio
import json, os
import websockets
from dotenv import load_dotenv
from logger_init import logger
from typing import Optional
from websockets import WebSocketClientProtocol

load_dotenv()


class WebSocketClient:
    def __init__(self, user_id: str):
        self.WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT")
        self.WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
        self.uri = f"ws://{self.WEBSOCKET_HOST}:{self.WEBSOCKET_PORT}"
        self.connection: Optional[WebSocketClientProtocol] = None
        self.queue = asyncio.Queue()
        self.user_id = user_id

    async def connect(self):
        try:
            self.connection = await websockets.connect(self.uri)
            logger.info(f"Websocket client connected to WebSocket server at {self.uri}")
            logger.info("Started listening.")

            # Register this client with its user_id
            await self.send({"type": "join", "user_id": self.user_id})
            logger.info(f"Connected as {self.user_id}")

            await asyncio.gather(self.listen(), self.process_queue(), self.user_input_loop())
        except Exception as e:
            logger.error(f"Error connecting to WebSocket server: {e}")

    async def send(self, message: dict):
        if self.connection:
            try:
                await self.connection.send(json.dumps(message))
                logger.info(f"Sent message: {message}")
            except Exception as e:
                logger.error(f"Error sending message: {e}")
        else:
            logger.error("WebSocket client connection is not established")

    async def broadcast(self, payload: str):
        message = {
            "type": "broadcast",
            "payload": payload,
            "user_id": self.user_id
        }
        await self.send(message)

    async def listen(self):
        while True:
            try:
                message = await self.connection.recv()
                parsed: dict = json.loads(message)
                msg_type = parsed.get("type")

                if msg_type == "user_joined":
                    logger.info(f"[SYSTEM] {parsed.get('message')}")

                elif msg_type == "user_left":
                    logger.info(f"[SYSTEM] {parsed.get('message')}")

                elif msg_type == "broadcast":
                    sender = parsed.get("from", "Unknown")
                    logger.info(f"[{sender}] {parsed.get('message')}")

                elif msg_type == "notification":
                    logger.info(f"[NOTIFICATION] {parsed.get('payload')}")

                elif msg_type == "hello":
                    logger.info(f"[SERVER] Hello message: {parsed.get('payload')}")

                elif msg_type == "unknown":
                    logger.warning(f"[SERVER] Unknown message type received: {parsed}")

                elif "error" in parsed:
                    logger.error(f"[ERROR] {parsed['error']}")

                else:
                    logger.info(f"[INFO] Received message: {parsed}")

                # Optionally queue all messages for further processing
                await self.queue.put(parsed)
            except websockets.ConnectionClosed:
                logger.info("WebSocket client connection closed")
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")

    async def interactive_input(self):
        while True:
            msg = await asyncio.to_thread(input, f"[{self.user_id}] > ")
            if msg.strip().lower() == "/exit":
                await self.send({"type": "disconnect", "user_id": self.user_id})
                await self.close()
                break
            else:
                await self.broadcast(msg)

    async def process_queue(self):
        while True:
            try:
                message = await self.queue.get()
                if message:
                    return message
                else:
                    logger.debug("No message in queue.")
            except Exception as e:
                logger.error(f"Error processing message from queue: {e}")

    async def receive(self):
        try:
            return await self.queue.get()
        except Exception as e:
            logger.error(f"Error in receive(): {e}")
            return None

    async def user_input_loop(self):
        loop = asyncio.get_event_loop()
        while True:
            user_input = await loop.run_in_executor(None, input, f"[{self.user_id}] > ")
            if user_input.strip().lower() == "/exit":
                logger.info("Closing connection...")
                await self.close()
                break
            elif user_input.strip():
                await self.broadcast(user_input.strip())


    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("WebSocket client connection closed")