# Chat Room Application - Complete Documentation

## Overview

This is a network application implementing a multi-client chat room system using
socket programming. The application demonstrates client-server architecture with
a custom application-layer protocol running over TCP.

## Project Structure

```
socket_programming/
├── server.py                    # Chat server implementation
├── client.py                    # Chat client implementation
├── PROJECT_PROPOSAL.md          # Application objectives and requirements
├── PROTOCOL_SPECIFICATION.md    # Detailed protocol documentation
├── README.md                    # This documentation file
└── demo/                        # Demo materials (to be created)
```

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## Quick Start

### Starting the Server

1. Open a terminal in the project directory
2. Run the server:
   ```bash
   python3 server.py
   ```
3. The server will start on `localhost:8888` by default
4. You should see: `Chat Server started on localhost:8888`

### Connecting Clients

1. Open another terminal (for each client)
2. Run the client:
   ```bash
   python3 client.py
   ```
3. Enter a username when prompted
4. Start chatting!

### Command Line Options

#### Server Options

```bash
# Default usage
python3 server.py

# The server uses hardcoded localhost:8888
# To modify, edit the ChatServer() initialization in main()
```

#### Client Options

```bash
# Default connection (localhost:8888)
python3 client.py

# Connect to different host/port
python3 client.py --host 192.168.1.100 --port 9999
```

## Client Commands

Once connected, use these commands in the client:

| Command                 | Description             | Example                   |
| ----------------------- | ----------------------- | ------------------------- |
| `/help`                 | Show available commands | `/help`                   |
| `/users`                | List online users       | `/users`                  |
| `/msg <user> <message>` | Send private message    | `/msg alice Hello there!` |
| `/ping`                 | Ping the server         | `/ping`                   |
| `/quit`                 | Exit the chat           | `/quit`                   |

## Features Demonstration

### 1. Multi-Client Support

- Start the server
- Connect multiple clients with different usernames
- Observe join notifications

### 2. Public Chat

- Type messages without commands
- See messages broadcast to all users
- Messages show sender and timestamp

### 3. Private Messaging

- Use `/msg username message` to send private messages
- Only the recipient sees the message
- Error handling for non-existent users

### 4. User Management

- `/users` command shows all online users
- Join/leave notifications for all users
- Graceful handling of disconnections

### 5. Protocol Logging

- Server logs all protocol messages
- Client shows sent/received message types
- Detailed error reporting

## Architecture Details

### Server Architecture

- **Main Thread**: Accepts new client connections
- **Client Threads**: One thread per connected client
- **Thread-Safe**: Uses proper synchronization for shared data
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals

### Client Architecture

- **Main Thread**: Handles user input and commands
- **Receive Thread**: Continuously listens for server messages
- **Non-Blocking UI**: User can type while receiving messages

### Protocol Features

- **JSON-Based**: Human-readable message format
- **Timestamp**: All messages include timestamps
- **Error Handling**: Comprehensive error codes and messages
- **Extensible**: Easy to add new message types

## Testing Scenarios

### Basic Functionality Test

1. Start server
2. Connect 2-3 clients
3. Send public messages
4. Send private messages
5. Use `/users` command
6. Disconnect clients gracefully

### Error Handling Test

1. Try duplicate usernames
2. Send private message to non-existent user
3. Forcefully close client (Ctrl+C)
4. Send invalid JSON (requires manual testing)

### Stress Testing

1. Connect many clients (10+)
2. Send rapid messages
3. Test server stability

## Example Session

### Server Output

```
2024-11-06 14:30:00 - INFO - Chat Server started on localhost:8888
2024-11-06 14:30:00 - INFO - Waiting for client connections...
2024-11-06 14:30:15 - INFO - New client connection from ('127.0.0.1', 54321)
2024-11-06 14:30:16 - INFO - ← Received from ('127.0.0.1', 54321): CONNECT
2024-11-06 14:30:16 - INFO - Connection request from ('127.0.0.1', 54321) for username: alice
2024-11-06 14:30:16 - INFO - → Sent to alice: CONNECT_ACK
2024-11-06 14:30:16 - INFO - User alice connected successfully from ('127.0.0.1', 54321)
```

### Client Output

```
=== Chat Room Client ===
Enter your username to connect:
Username: alice
[INFO] Connected to server at localhost:8888
[SENT] CONNECT: {'username': 'alice', 'protocol_version': '1.0'}
[RECV] CONNECT_ACK at 2024-11-06 14:30:16
[SUCCESS] Welcome to the chat room, alice!
[INFO] You are the only user online

Welcome to the chat room! Type /help for commands.
Connected as: alice
alice> Hello everyone!
[SENT] CHAT_MESSAGE: {'sender': 'alice', 'content': 'Hello everyone!', 'message_id': 'msg_1699281017'}

💬 alice: Hello everyone!

alice> /users
[SENT] LIST_USERS: {}
[RECV] USER_LIST at 2024-11-06 14:30:20

👥 Online users (1): alice
```

## Implementation Highlights

### Server Features

- **Thread-per-client model** for handling multiple connections
- **JSON message parsing** with error handling
- **Broadcast messaging** to all connected clients
- **User session management** with authentication
- **Graceful cleanup** on client disconnection
- **Comprehensive logging** for debugging and monitoring

### Client Features

- **Threaded architecture** for simultaneous send/receive
- **Command-line interface** with intuitive commands
- **Real-time message display** with proper formatting
- **Error handling** and user feedback
- **Configurable connection parameters**

### Protocol Implementation

- **Stateful connections** with proper session management
- **Message typing** for different communication patterns
- **Error codes** for comprehensive error handling
- **Extensible design** for future enhancements

## Troubleshooting

### Common Issues

1. **"Address already in use" error**

   - Wait a few seconds and try again
   - Another server instance may be running

2. **"Connection refused" error**

   - Ensure server is running
   - Check host/port settings

3. **Username already taken**

   - Choose a different username
   - Previous connection may not have cleaned up

4. **Client freezes**
   - Use Ctrl+C to force quit
   - Check network connectivity

### Debug Mode

For detailed debugging, modify the logging level in `server.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Educational Objectives Met

This project demonstrates:

1. **Socket Programming**: TCP client-server implementation
2. **Protocol Design**: Custom application-layer protocol
3. **Threading**: Concurrent client handling
4. **Network Programming**: Real-world networking concepts
5. **Error Handling**: Robust error management
6. **Software Architecture**: Clean, maintainable code structure

## Future Enhancements

Possible extensions to this project:

- Chat rooms/channels
- File transfer capability
- User authentication with passwords
- Message persistence/history
- Web-based client interface
- Encryption for secure communication
- Administrative features (kick/ban users)

## Conclusion

This chat room application successfully demonstrates socket programming concepts
and provides a solid foundation for understanding network application
development. The implementation showcases proper protocol design, error
handling, and concurrent programming techniques essential for building robust
network applications.
