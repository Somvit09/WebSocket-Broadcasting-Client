import asyncio, typer
from server import WebSocketServer
from client import WebSocketClient
from logger_init import logger

app = typer.Typer(help="WebSocket Broadcast CLI (Server & Client)")

@app.command()
def start():
    """
    Start the WebSocket broadcast server.
    The server listens for WebSocket connections, registers clients by user ID,
    and handles message broadcasting and disconnections.
    """
    try:
        server = WebSocketServer()
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("WebSocket server interrupted and shutting down.")

@app.command()
def connect(user_id: str = typer.Option(..., "--user-id", "-u", help="Unique user ID")):
    """
    Connect a client to the WebSocket server.

    The client registers using the provided user ID, sends and receives broadcast messages,
    and supports graceful disconnection with /exit.
    """
    try:
        logger.info(f"Connecting as client with user_id: {user_id}")
        client = WebSocketClient(user_id=user_id)
        asyncio.run(client.connect())
    except KeyboardInterrupt:
        logger.warning("Client manually interrupted.")

if __name__ == "__main__":
    app()
