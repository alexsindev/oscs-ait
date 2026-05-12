# Computer Networks (CN)

## Course Overview

Covers the principles, protocols, and architecture of computer networks from the
application layer down to the link layer. Labs focus on hands-on Wireshark analysis
and socket programming.

## Topics

- Layered network architecture (OSI model, TCP/IP stack)
- Application layer: HTTP/1.1, DNS, SMTP, FTP
- Transport layer: TCP (reliability, congestion control), UDP
- Network layer: IP addressing, routing, NAT
- Link layer: Ethernet, ARP, switches
- Socket programming: TCP client-server, threading, custom application-layer protocols

## Contents

```
CN/
├── notes/
│   └── networking-fundamentals.md   Study notes covering all major topics
└── projects/
    └── chat-room/                   Multi-client TCP chat room (Python)
        ├── server.py
        ├── client.py
        ├── PROTOCOL_SPECIFICATION.md
        └── README.md
```

## Projects

### Chat Room — TCP Socket Programming

A multi-client chat room built on raw TCP sockets in Python. Implements a custom
JSON application-layer protocol (CRP) with:

- Authentication (CONNECT / CONNECT_ACK / CONNECT_NACK)
- Public broadcast messages
- Private direct messages
- User listing, PING/PONG keepalive
- Thread-per-client server architecture

See [projects/chat-room/README.md](projects/chat-room/README.md) for full docs.
