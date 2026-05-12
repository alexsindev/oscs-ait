#!/usr/bin/env python3
"""
Chat Room Client Implementation
Implements the Chat Room Protocol (CRP) as specified in PROTOCOL_SPECIFICATION.md
"""

import socket
import threading
import json
import sys
import time
from datetime import datetime
from typing import Optional

class ChatClient:
    """Chat Room Client implementing CRP protocol"""
    
    def __init__(self, host: str = 'localhost', port: int = 6142):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.username: Optional[str] = None
        self.user_id: Optional[str] = None
        self.connected = False
        self.running = False
        
    def create_message(self, msg_type: str, payload: dict) -> dict:
        """Create a standardized protocol message"""
        message = {
            "type": msg_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": payload
        }

        print(f"-----> {message}")
        return message
    
    def send_message(self, message: dict) -> bool:
        """Send a JSON message to the server"""
        try:
            if not self.socket:
                print("[ERROR] Not connected to server")
                return False
            message_str = json.dumps(message) + '\n'
            self.socket.send(message_str.encode('utf-8'))
            # print(f"[SENT] {message['type']}: {message['payload']}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False
    
    def connect_to_server(self, username: str) -> bool:
        """Connect to the chat server"""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            print(f"[INFO] Connected to server at {self.host}:{self.port}")
            
            # Send connection request
            connect_msg = self.create_message("CONNECT", {
                "username": username,
                "protocol_version": "1.0"
            })

            if not self.send_message(connect_msg):
                return False
            
            # Wait for response
            response = self.receive_message()
            if not response:
                print("[ERROR] No response from server")
                return False

            print("<----- ", response)

            if response['type'] == 'CONNECT_ACK':
                payload = response['payload']
                self.username = username
                self.user_id = payload.get('user_id')
                self.connected = True
                
                # print(f"[SUCCESS] {payload.get('message', 'Connected successfully')}")
                
                online_users = payload.get('online_users', [])
                if online_users:
                    print(f"[INFO] Online users: {', '.join(online_users)}")
                else:
                    print("[INFO] You are the only user online")
                
                return True
            
            elif response['type'] == 'CONNECT_NACK':
                payload = response['payload']
                # print(f"[ERROR] Connection failed: {payload.get('message', 'Unknown error')}")
                return False
            
            else:
                print(f"[ERROR] Unexpected response: {response['type']}")
                return False
        
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            return False
    
    def receive_message(self) -> Optional[dict]:
        """Receive and parse a JSON message from the server"""
        try:
            if not self.socket:
                return None
            data = self.socket.recv(1024).decode('utf-8').strip()
            if not data:
                return None
            
            message = json.loads(data)
            return message
        
        except json.JSONDecodeError:
            print("[ERROR] Received invalid JSON from server")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to receive message: {e}")
            return None
    
    def handle_incoming_messages(self):
        """Handle incoming messages from the server"""
        while self.running and self.connected:
            try:
                message = self.receive_message()
                if not message:
                    break

                print("<-----", message)
                
                msg_type = message['type']
                payload = message['payload']
                timestamp = message.get('timestamp', '')
                
                # print(f"[RECV] {msg_type} at {timestamp}")
                
                if msg_type == 'CHAT_BROADCAST':
                    sender = payload.get('sender')
                    content = payload.get('content')
                    # print(f"\n💬 {sender}: {content}")
                
                elif msg_type == 'PRIVATE_DELIVERY':
                    sender = payload.get('sender')
                    content = payload.get('content')
                    # print(f"\n📩 Private from {sender}: {content}")
                
                elif msg_type == 'USER_JOIN':
                    username = payload.get('username')
                    # print(f"\n✅ {username} joined the chat")
                
                elif msg_type == 'USER_LEAVE':
                    username = payload.get('username')
                    # print(f"\n❌ {username} left the chat")
                
                elif msg_type == 'USER_LIST':
                    users = payload.get('users', [])
                    count = payload.get('count', 0)
                    # print(f"\n👥 Online users ({count}): {', '.join(users)}")
                
                elif msg_type == 'ERROR':
                    error_code = payload.get('error_code')
                    message_text = payload.get('message')
                    details = payload.get('details', '')
                    # print(f"\n❗ Error [{error_code}]: {message_text}")
                    if details:
                        print(f"   Details: {details}")
                
                elif msg_type == 'PONG':
                    print("[INFO] Pong received from server")
                
                else:
                    print(f"\n[UNKNOWN] {msg_type}: {payload}")
                
                # Show prompt again
                print(f"\n{self.username}> ", end='', flush=True)
            
            except Exception as e:
                if self.running:
                    print(f"\n[ERROR] Error receiving message: {e}")
                break
        
        print("\n[INFO] Message handler stopped")
    
    def send_chat_message(self, content: str):
        """Send a public chat message"""
        message = self.create_message("CHAT_MESSAGE", {
            "sender": self.username,
            "content": content,
            "message_id": f"msg_{int(time.time())}"
        })
        self.send_message(message)
    
    def send_private_message(self, recipient: str, content: str):
        """Send a private message"""
        message = self.create_message("PRIVATE_MESSAGE", {
            "sender": self.username,
            "recipient": recipient,
            "content": content,
            "message_id": f"msg_{int(time.time())}"
        })
        self.send_message(message)
    
    def request_user_list(self):
        """Request list of online users"""
        message = self.create_message("LIST_USERS", {})
        self.send_message(message)
    
    def send_ping(self):
        """Send ping to server"""
        message = self.create_message("PING", {})
        self.send_message(message)
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.connected:
            message = self.create_message("DISCONNECT", {
                "reason": "User initiated disconnect"
            })
            self.send_message(message)
            
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("[INFO] Disconnected from server")
    
    def show_help(self):
        """Show available commands"""
        print("\n=== Chat Commands ===")
        print("/help           - Show this help")
        print("/users          - List online users")
        print("/msg <user> <message> - Send private message")
        print("/ping           - Ping the server")
        print("/quit           - Exit the chat")
        print("===================\n")
    
    def parse_command(self, input_text: str) -> bool:
        """Parse and execute chat commands"""
        if not input_text.startswith('/'):
            return False
        
        parts = input_text[1:].split(' ', 2)
        command = parts[0].lower()
        
        if command == 'help':
            self.show_help()
        
        elif command == 'users':
            self.request_user_list()
        
        elif command == 'msg':
            if len(parts) < 3:
                print("[ERROR] Usage: /msg <username> <message>")
            else:
                recipient = parts[1]
                message = parts[2]
                self.send_private_message(recipient, message)
                # print(f"[SENT] Private message to {recipient}")
        
        elif command == 'ping':
            self.send_ping()
        
        elif command == 'quit':
            return True  # Signal to quit
        
        else:
            print(f"[ERROR] Unknown command: /{command}")
            print("Type /help for available commands")
        
        return False
    
    def run(self):
        """Main client loop"""
        print("=== Chat Room Client ===")
        print("Enter your username to connect:")
        
        # Get username
        while True:
            username = input("Username: ").strip()
            if username and len(username) >= 2:
                break
            print("Username must be at least 2 characters long")
        
        # Connect to server
        if not self.connect_to_server(username):
            print("Failed to connect to server")
            return
        
        self.running = True
        
        # Start message receiving thread
        receive_thread = threading.Thread(target=self.handle_incoming_messages, daemon=True)
        receive_thread.start()
        
        print(f"\nWelcome to the chat room! Type /help for commands.")
        print(f"Connected as: {self.username}")
        
        # Main input loop
        try:
            while self.running and self.connected:
                try:
                    user_input = input(f"{self.username}> ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Check if it's a command
                    if user_input.startswith('/'):
                        should_quit = self.parse_command(user_input)
                        if should_quit:
                            break
                    else:
                        # Send as chat message
                        self.send_chat_message(user_input)
                
                except EOFError:
                    # Handle Ctrl+D
                    break
                except KeyboardInterrupt:
                    # Handle Ctrl+C
                    break
        
        except Exception as e:
            print(f"[ERROR] Client error: {e}")
        
        finally:
            self.disconnect()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Chat Room Client')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=6142, help='Server port (default: 6142)')
    
    args = parser.parse_args()
    
    client = ChatClient(args.host, args.port)
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n[INFO] Client interrupted by user")
    except Exception as e:
        print(f"[ERROR] Client error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()