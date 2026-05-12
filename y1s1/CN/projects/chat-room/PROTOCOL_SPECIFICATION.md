# Chat Room Application-Layer Protocol Specification

## Protocol Overview

The Chat Room Protocol (CRP) is a text-based, stateful protocol that operates
over TCP. It uses JSON-formatted messages for structured communication between
clients and server.

## Message Format

All messages follow a standard JSON format:

```json
{
  "type": "MESSAGE_TYPE",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "payload": {
    // Message-specific data
  }
}
```

### Message Components

- **type**: Identifies the message category (required)
- **timestamp**: ISO format timestamp of message creation (required)
- **payload**: Message-specific data structure (required)

## Message Types

### 1. Authentication Messages

#### CONNECT Request (Client → Server)

```json
{
  "type": "CONNECT",
  "timestamp": "2024-11-06 14:30:00",
  "payload": {
    "username": "alice",
    "protocol_version": "1.0"
  }
}
```

#### CONNECT_ACK Response (Server → Client)

```json
{
  "type": "CONNECT_ACK",
  "timestamp": "2024-11-06 14:30:01",
  "payload": {
    "status": "SUCCESS",
    "user_id": "user_123",
    "message": "Welcome to the chat room!",
    "online_users": ["bob", "charlie"]
  }
}
```

#### CONNECT_NACK Response (Server → Client)

```json
{
  "type": "CONNECT_NACK",
  "timestamp": "2024-11-06 14:30:01",
  "payload": {
    "status": "ERROR",
    "error_code": "USERNAME_TAKEN",
    "message": "Username already in use"
  }
}
```

### 2. Chat Messages

#### CHAT_MESSAGE (Client → Server)

```json
{
  "type": "CHAT_MESSAGE",
  "timestamp": "2024-11-06 14:31:00",
  "payload": {
    "sender": "alice",
    "content": "Hello everyone!",
    "message_id": "msg_456"
  }
}
```

#### CHAT_BROADCAST (Server → All Clients)

```json
{
  "type": "CHAT_BROADCAST",
  "timestamp": "2024-11-06 14:31:01",
  "payload": {
    "sender": "alice",
    "content": "Hello everyone!",
    "message_id": "msg_456"
  }
}
```

### 3. Private Messages

#### PRIVATE_MESSAGE (Client → Server)

```json
{
  "type": "PRIVATE_MESSAGE",
  "timestamp": "2024-11-06 14:32:00",
  "payload": {
    "sender": "alice",
    "recipient": "bob",
    "content": "Hi Bob, how are you?",
    "message_id": "msg_789"
  }
}
```

#### PRIVATE_DELIVERY (Server → Recipient)

```json
{
  "type": "PRIVATE_DELIVERY",
  "timestamp": "2024-11-06 14:32:01",
  "payload": {
    "sender": "alice",
    "content": "Hi Bob, how are you?",
    "message_id": "msg_789"
  }
}
```

### 4. User Management

#### USER_JOIN (Server → All Clients)

```json
{
  "type": "USER_JOIN",
  "timestamp": "2024-11-06 14:33:00",
  "payload": {
    "username": "david",
    "message": "david has joined the chat"
  }
}
```

#### USER_LEAVE (Server → All Clients)

```json
{
  "type": "USER_LEAVE",
  "timestamp": "2024-11-06 14:34:00",
  "payload": {
    "username": "charlie",
    "message": "charlie has left the chat"
  }
}
```

#### LIST_USERS (Client → Server)

```json
{
  "type": "LIST_USERS",
  "timestamp": "2024-11-06 14:35:00",
  "payload": {}
}
```

#### USER_LIST (Server → Client)

```json
{
  "type": "USER_LIST",
  "timestamp": "2024-11-06 14:35:01",
  "payload": {
    "users": ["alice", "bob", "david"],
    "count": 3
  }
}
```

### 5. Control Messages

#### DISCONNECT (Client → Server)

```json
{
  "type": "DISCONNECT",
  "timestamp": "2024-11-06 14:36:00",
  "payload": {
    "reason": "User initiated"
  }
}
```

#### PING (Client ↔ Server)

```json
{
  "type": "PING",
  "timestamp": "2024-11-06 14:37:00",
  "payload": {}
}
```

#### PONG (Server ↔ Client)

```json
{
  "type": "PONG",
  "timestamp": "2024-11-06 14:37:01",
  "payload": {}
}
```

#### ERROR (Server → Client)

```json
{
  "type": "ERROR",
  "timestamp": "2024-11-06 14:38:00",
  "payload": {
    "error_code": "INVALID_FORMAT",
    "message": "Message format is invalid",
    "details": "Missing required field: username"
  }
}
```

## Protocol State Machine

### Client States

1. **DISCONNECTED**: Initial state, not connected to server
2. **CONNECTING**: Connection attempt in progress
3. **CONNECTED**: Successfully connected and authenticated
4. **DISCONNECTING**: Graceful disconnect in progress

### Server States (per client)

1. **WAITING**: Waiting for client connection
2. **AUTHENTICATING**: Processing client authentication
3. **ACTIVE**: Client is authenticated and active
4. **DISCONNECTING**: Client is disconnecting

## Client Actions and Behaviors

### Connection Flow

1. **Establish TCP Connection**: Connect to server on designated port
2. **Send CONNECT**: Authenticate with username
3. **Wait for Response**: Handle CONNECT_ACK or CONNECT_NACK
4. **Enter Chat Mode**: Begin sending/receiving messages

### Message Handling

1. **Send Chat Messages**: Format and send CHAT_MESSAGE
2. **Send Private Messages**: Format and send PRIVATE_MESSAGE
3. **Process Incoming**: Handle all incoming message types
4. **Display Messages**: Show formatted messages to user

### User Interface Actions

1. **Message Input**: Accept user input for chat messages
2. **Command Processing**: Handle special commands (/quit, /users, /msg)
3. **Status Display**: Show connection status and errors
4. **Message Display**: Format and display received messages

## Server Actions and Behaviors

### Client Management

1. **Accept Connections**: Listen for and accept new client connections
2. **Authenticate Users**: Process CONNECT requests and validate usernames
3. **Maintain User List**: Track connected users and their states
4. **Handle Disconnections**: Clean up when clients disconnect

### Message Routing

1. **Broadcast Messages**: Forward chat messages to all connected clients
2. **Private Message Delivery**: Route private messages to specific recipients
3. **System Notifications**: Send join/leave notifications
4. **Error Handling**: Send appropriate error responses

### Session Management

1. **Connection Tracking**: Monitor client connection states
2. **Heartbeat Monitoring**: Use PING/PONG for connection health
3. **Graceful Shutdown**: Handle server shutdown cleanly
4. **Resource Cleanup**: Clean up resources when clients disconnect

## Error Handling

### Client Error Scenarios

- **Connection Refused**: Server not available
- **Authentication Failed**: Username taken or invalid
- **Network Errors**: Connection lost or timeout
- **Protocol Errors**: Invalid message format

### Server Error Scenarios

- **Invalid Messages**: Malformed JSON or missing fields
- **User Not Found**: Private message to non-existent user
- **Duplicate Username**: Username already in use
- **Resource Limits**: Too many connections

## Security Considerations

1. **Input Validation**: Validate all incoming message fields
2. **Rate Limiting**: Prevent message flooding
3. **Username Validation**: Ensure valid username format
4. **Message Sanitization**: Clean message content for display

## Protocol Extensions

The protocol is designed for extensibility:

- **File Transfer**: Add FILE_TRANSFER message type
- **Chat Rooms**: Add room-based messaging
- **User Roles**: Add admin/moderator capabilities
- **Message History**: Add persistent message storage
