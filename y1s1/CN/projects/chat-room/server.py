#!/usr/bin/env python3
"""
Chat Room Server Implementation
Implements the Chat Room Protocol (CRP) as specified in PROTOCOL_SPECIFICATION.md
"""

import socket
import threading
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ChatClient:
    """Represents a connected client"""
    def __init__(self, socket: socket.socket, address: tuple):
        self.socket = socket
        self.address = address
        self.username: Optional[str] = None
        self.user_id: Optional[str] = None
        self.connected_at = datetime.now()
        self.last_ping = datetime.now()
        
    def send_message(self, message: dict) -> bool:
        """Send a JSON message to the client"""
        try:
            print("---->", message)
            message_str = json.dumps(message) + '\n'
            self.socket.send(message_str.encode('utf-8'))
            # logger.info(f"→ Sent to {self.username or self.address}: {message['type']}")

            # print(f"SENT TO {self.username or self.address}: {message}")
            return True
        except Exception as e:
            # logger.error(f"Failed to send message to {self.username or self.address}: {e}")
            return False

class ChatServer:
    """Chat Room Server implementing CRP protocol"""
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        self.clients: Dict[str, ChatClient] = {}  # username -> ChatClient
        self.running = False
        self.message_counter = 0
        
    def create_message(self, msg_type: str, payload: dict) -> dict:
        """Create a standardized protocol message"""
        return {
            "type": msg_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": payload
        }
    
    def get_next_message_id(self) -> str:
        """Generate unique message ID"""
        self.message_counter += 1
        return f"msg_{self.message_counter}"
    
    def get_next_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{int(time.time())}"
    
    def broadcast_message(self, message: dict, exclude_client: Optional[str] = None):
        """Broadcast message to all connected clients except excluded one"""
        # logger.info(f"Broadcasting {message['type']} to {len(self.clients)} clients")
        
        disconnected_clients = []
        for username, client in self.clients.items():
            if username != exclude_client:
                if not client.send_message(message):
                    disconnected_clients.append(username)
        
        # Clean up disconnected clients
        for username in disconnected_clients:
            self.disconnect_client(username, "Connection lost during broadcast")
    
    def send_to_client(self, username: str, message: dict) -> bool:
        """Send message to specific client"""
        if username in self.clients:
            return self.clients[username].send_message(message)
        return False
    
    def handle_connect(self, client: ChatClient, payload: dict) -> bool:
        """Handle client connection request"""
        username = payload.get('username', '').strip()
        protocol_version = payload.get('protocol_version', '1.0')
        
        # logger.info(f"Connection request from {client.address} for username: {username}")
        
        # Validate username
        if not username or len(username) < 2 or len(username) > 20:
            response = self.create_message("CONNECT_NACK", {
                "status": "ERROR",
                "error_code": "INVALID_USERNAME",
                "message": "Username must be 2-20 characters long"
            })
            client.send_message(response)
            return False
        
        # Check if username is already taken
        if username in self.clients:
            response = self.create_message("CONNECT_NACK", {
                "status": "ERROR",
                "error_code": "USERNAME_TAKEN",
                "message": "Username already in use"
            })
            client.send_message(response)
            return False
        
        # Accept the connection
        client.username = username
        client.user_id = self.get_next_user_id()
        self.clients[username] = client
        
        # Send success response
        online_users = list(self.clients.keys())
        online_users.remove(username)  # Don't include the new user in the list
        
        response = self.create_message("CONNECT_ACK", {
            "status": "SUCCESS",
            "user_id": client.user_id,
            "message": f"Welcome to the chat room, {username}!",
            "online_users": online_users
        })
        client.send_message(response)
        
        # Notify other clients about new user
        join_message = self.create_message("USER_JOIN", {
            "username": username,
            "message": f"{username} has joined the chat"
        })
        self.broadcast_message(join_message, exclude_client=username)
        
        # logger.info(f"User {username} connected successfully from {client.address}")
        return True
    
    def handle_chat_message(self, client: ChatClient, payload: dict):
        """Handle public chat message"""
        if not client.username:
            return
        
        content = payload.get('content', '').strip()
        if not content:
            return
        
        message_id = self.get_next_message_id()
        
        # logger.info(f"Chat message from {client.username}: {content[:50]}...")
        
        # Broadcast to all clients
        broadcast_msg = self.create_message("CHAT_BROADCAST", {
            "sender": client.username,
            "content": content,
            "message_id": message_id
        })
        self.broadcast_message(broadcast_msg)
    
    def handle_private_message(self, client: ChatClient, payload: dict):
        """Handle private message"""
        if not client.username:
            return
        
        recipient = payload.get('recipient', '').strip()
        content = payload.get('content', '').strip()
        
        if not recipient or not content:
            return
        
        # logger.info(f"Private message from {client.username} to {recipient}")
        
        if recipient not in self.clients:
            error_msg = self.create_message("ERROR", {
                "error_code": "USER_NOT_FOUND",
                "message": f"User '{recipient}' not found",
                "details": "The recipient is not currently online"
            })
            client.send_message(error_msg)
            return
        
        message_id = self.get_next_message_id()
        
        # Send to recipient
        private_msg = self.create_message("PRIVATE_DELIVERY", {
            "sender": client.username,
            "content": content,
            "message_id": message_id
        })
        self.send_to_client(recipient, private_msg)
    
    def handle_list_users(self, client: ChatClient):
        """Handle request for user list"""
        if not client.username:
            return
        
        users = list(self.clients.keys())
        response = self.create_message("USER_LIST", {
            "users": users,
            "count": len(users)
        })
        client.send_message(response)
    
    def handle_ping(self, client: ChatClient):
        """Handle ping request"""
        if client.username:
            client.last_ping = datetime.now()
            pong_msg = self.create_message("PONG", {})
            client.send_message(pong_msg)
    
    def handle_disconnect(self, client: ChatClient, payload: dict):
        """Handle client disconnect request"""
        reason = payload.get('reason', 'Client initiated disconnect')
        # logger.info(f"Disconnect request from {client.username}: {reason}")
        self.disconnect_client(client.username, reason)
    
    def disconnect_client(self, username: str, reason: str = "Unknown"):
        """Disconnect a client and clean up"""
        if username not in self.clients:
            return
        
        client = self.clients[username]
        # logger.info(f"Disconnecting user {username}: {reason}")
        
        # Close socket
        try:
            client.socket.close()
        except:
            pass
        
        # Remove from clients list
        del self.clients[username]
        
        # Notify other clients
        leave_message = self.create_message("USER_LEAVE", {
            "username": username,
            "message": f"{username} has left the chat"
        })
        self.broadcast_message(leave_message)
    
    def handle_client(self, client: ChatClient):
        """Handle communication with a single client"""
        # logger.info(f"New client connection from {client.address}")
        
        try:
            while self.running:
                # Receive data
                data = client.socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                
                try:
                    # Parse JSON message
                    message = json.loads(data)
                    msg_type = message.get('type')
                    payload = message.get('payload', {})
                    
                    logger.info(f"<----: {message}")
                    
                    # Route message based on type
                    if msg_type == "CONNECT":
                        if not self.handle_connect(client, payload):
                            break
                    elif msg_type == "CHAT_MESSAGE":
                        self.handle_chat_message(client, payload)
                    elif msg_type == "PRIVATE_MESSAGE":
                        self.handle_private_message(client, payload)
                    elif msg_type == "LIST_USERS":
                        self.handle_list_users(client)
                    elif msg_type == "PING":
                        self.handle_ping(client)
                    elif msg_type == "DISCONNECT":
                        self.handle_disconnect(client, payload)
                        break
                    else:
                        # Unknown message type
                        error_msg = self.create_message("ERROR", {
                            "error_code": "UNKNOWN_MESSAGE_TYPE",
                            "message": f"Unknown message type: {msg_type}",
                            "details": "Supported types: CONNECT, CHAT_MESSAGE, PRIVATE_MESSAGE, LIST_USERS, PING, DISCONNECT"
                        })
                        client.send_message(error_msg)
                
                except json.JSONDecodeError:
                    # Invalid JSON
                    error_msg = self.create_message("ERROR", {
                        "error_code": "INVALID_FORMAT",
                        "message": "Invalid JSON format",
                        "details": "Message must be valid JSON"
                    })
                    client.send_message(error_msg)
                
                except Exception as e:
                    logger.error(f"Error handling message from {client.username or client.address}: {e}")
                    break
        
        except Exception as e:
            logger.error(f"Error in client handler for {client.address}: {e}")
        
        finally:
            # Clean up client connection
            if client.username:
                self.disconnect_client(client.username, "Client handler terminated")
            else:
                try:
                    client.socket.close()
                except:
                    pass
    
    def start(self):
        """Start the chat server"""
        try:
            # Create and bind socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            
            self.running = True
            
            logger.info(f"Chat Server started on {self.host}:{self.port}")
            logger.info("Waiting for client connections...")
            
            while self.running:
                try:
                    # Accept new connection
                    client_socket, client_address = self.socket.accept()
                    
                    # Create client object
                    client = ChatClient(client_socket, client_address)
                    
                    # Start client handler thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client,),
                        daemon=True
                    )
                    client_thread.start()
                
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
        
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the chat server"""
        logger.info("Stopping chat server...")
        self.running = False
        
        # Disconnect all clients
        for username in list(self.clients.keys()):
            self.disconnect_client(username, "Server shutdown")
        
        # Close server socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        logger.info("Chat server stopped")

def main():
    """Main function to start the server"""
    import signal
    import sys
    
    # Create server instance
    server = ChatServer()
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the server
        server.start()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.stop()

if __name__ == "__main__":
    main()