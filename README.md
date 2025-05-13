# WebSocket Broadcasting System

This project demonstrates a WebSocket server-client architecture that allows real-time message broadcasting between multiple clients.

## 🔗 Project URL

Project on Roadmap.sh: [https://roadmap.sh/projects/broadcast-server](https://roadmap.sh/projects/broadcast-server)


## Features

- Real-time communication between clients using WebSockets
- User registration with `user_id`
- Message broadcasting to all connected clients
- Graceful handling of disconnects
- Logging for server and client activities

## Technologies

- Python 3.12+
- `websockets`
- `asyncio`
- `dotenv`
- Custom logging setup

## Installation

### For Linux based systems
- Clone this project from github.
  ```
  git clone git@github.com:Somvit09/WebSocket-Broadcasting-Client.git
  ```
- Make a virtual ENV.
  ```
  python3 -m venv your-venv-name
  ```
- Activate
  ```
  source your-venv/bin/activate
  ```
- Install all necessary packages from requirements.txt.
  ```
  pip install -r requirements.txt
  ```

### For Windows based systems
- Clone this project from github.
  ```
  git clone git@github.com:Somvit09/WebSocket-Broadcasting-Client.git
  ```
- Make a virtual ENV.
  ```
  python -m venv your-venv-name
  ```
- Activate
  ```
  .\your-venv-name\Scripts\activate
  ```
- Install all necessary packages from requirements.txt.
  ```
  pip install -r requirements.txt
  ```

## Environment Variables

Create a `.env` file in the root directory and set:

```env
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8765
```

## Running the Server

```bash
python .\broadcast-server.py start
```

## Running a Client

```bash
python .\broadcast-server.py connect --user-id=<YourUserID>
```

Once connected, you can type messages to broadcast. Use `/exit` to disconnect.

## Graceful Shutdown

Clients and the server handle disconnection cleanly. Keyboard interrupts (e.g. `Ctrl+C`) may still raise minor warnings in Windows but do not impact functionality.

