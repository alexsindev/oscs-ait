
# Chat Room Application - Demo Instructions

## Demo Preparation

### 1. Terminal Setup
- **Terminal 1**: Server (keep visible)
- **Terminal 2**: Client 1 (alice)
- **Terminal 3**: Client 2 (bob)
- **Terminal 4**: Client 3 (charlie) - optional

### 2. Demo Script

#### Phase 1: Server Startup
```bash
# Terminal 1
cd /Users/alex/Desktop/MSCS/CN/socket_programming
python3 server.py
```
**Show**: Server starting, listening for connections

#### Phase 2: First Client Connection
```bash
# Terminal 2
python3 client.py
# Enter username: alice
```
**Show**: 
- Connection protocol messages
- Welcome message
- Server logs showing client connection

#### Phase 3: Second Client Connection
```bash
# Terminal 3
python3 client.py
# Enter username: bob
```
**Show**:
- Join notification to alice
- User list showing both users
- Server handling multiple clients

#### Phase 4: Public Chat Demonstration
```
# In alice's client:
alice> Hello everyone! This is a test message.

# In bob's client:
bob> Hi alice! Nice to meet you.
bob> How does this chat room work?

# In alice's client:
alice> It uses TCP sockets and a custom protocol!
```
**Show**: Real-time message broadcasting

#### Phase 5: User Management
```
# In any client:
/users
```
**Show**: List of online users

#### Phase 6: Private Messaging
```
# In alice's client:
/msg bob This is a private message just for you!

# In bob's client:
/msg alice Thanks! This is private too.
```
**Show**: Private message delivery, not visible to others

#### Phase 7: Error Handling Demo
```bash
# Terminal 4 (new client)
python3 client.py
# Enter username: alice  (already taken)
```
**Show**: Username conflict error handling

```
# In any client:
/msg nonexistent_user Hello there
```
**Show**: User not found error

#### Phase 8: Command Demonstration
```
# In any client:
/help
/ping
/users
```
**Show**: Various protocol commands

#### Phase 9: Graceful Disconnection
```
# In bob's client:
/quit
```
**Show**: 
- Client disconnect protocol
- Leave notification to remaining users
- Server cleanup

#### Phase 10: Force Disconnect Handling
```
# In alice's client: Press Ctrl+C
```
**Show**: Server detecting and handling abrupt disconnection

#### Phase 11: Server Shutdown
```
# In server terminal: Press Ctrl+C
```
**Show**: Graceful server shutdown, client cleanup

## Key Demo Points to Highlight

### 1. Protocol Implementation
- JSON-based messages
- Structured request/response
- Proper error handling
- Message timestamps

### 2. Network Programming
- TCP socket usage
- Client-server architecture
- Concurrent client handling
- Thread safety

### 3. Real-time Communication
- Instant message delivery
- Broadcasting to multiple clients
- Private messaging
- User presence awareness

### 4. Robustness
- Error handling and recovery
- Graceful disconnections
- Server stability with multiple clients
- Protocol validation

### 5. User Experience
- Intuitive commands
- Clear status messages
- Real-time feedback
- Helpful error messages

## Technical Architecture Explanation

### Server Components
1. **Main Accept Loop**: Listens for new connections
2. **Client Handler Threads**: One per connected client
3. **Message Router**: Distributes messages based on type
4. **User Manager**: Tracks connected users and sessions

### Client Components
1. **Connection Manager**: Handles server connection
2. **Message Sender**: Processes user input and commands
3. **Message Receiver**: Handles incoming server messages
4. **User Interface**: Command-line interface with threading

### Protocol Features
1. **Message Types**: CONNECT, CHAT_MESSAGE, PRIVATE_MESSAGE, etc.
2. **Error Handling**: Comprehensive error codes and messages
3. **State Management**: Connection states and user sessions
4. **Extensibility**: Easy to add new message types

## Video Recording Tips

1. **Screen Layout**: Arrange terminals for clear visibility
2. **Timing**: Pause between actions for clarity
3. **Narration**: Explain what's happening at each step
4. **Documentation**: Show relevant code sections
5. **Testing**: Practice the demo beforehand

## Presentation Structure

1. **Introduction** (2 min)
   - Project overview and objectives
   - Why TCP was chosen

2. **Protocol Design** (3 min)
   - Show PROTOCOL_SPECIFICATION.md
   - Explain message format and types

3. **Live Demo** (10 min)
   - Follow the demo script above
   - Highlight key features

4. **Code Walkthrough** (5 min)
   - Show server.py key functions
   - Show client.py architecture
   - Explain threading model

5. **Q&A** (5 min)
   - Answer questions about implementation
   - Discuss potential improvements

## Files to Submit

1. **Source Code**:
   - server.py
   - client.py

2. **Documentation**:
   - PROJECT_PROPOSAL.md
   - PROTOCOL_SPECIFICATION.md
   - README.md

3. **Demo Materials**:
   - This demo script
   - Video recording of working application
   - Presentation slides (optional)

Remember: The goal is to demonstrate understanding of socket programming, protocol design, and network application development!
