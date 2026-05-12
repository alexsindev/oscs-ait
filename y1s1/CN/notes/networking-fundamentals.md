# Networking Fundamentals

## The Internet Architecture

The internet is a network of networks connected by routers. End systems (hosts)
connect to the internet via access networks (DSL, cable, fiber, WiFi, cellular).

### Network Edge vs. Core

- **Edge**: End hosts running applications
- **Core**: Mesh of interconnected routers forwarding packets

### Packet vs. Circuit Switching

| | Packet Switching | Circuit Switching |
|---|---|---|
| Resources | Shared, on-demand | Reserved end-to-end |
| Overhead | Per-packet headers | Call setup |
| Efficiency | Higher (statistical multiplexing) | Lower (idle capacity wasted) |
| Example | Internet | Traditional telephony (PSTN) |

---

## The Layered Model

### OSI Model (7 layers)

```
7  Application   HTTP, DNS, SMTP, FTP
6  Presentation  Encryption, compression, encoding
5  Session       Session management
4  Transport     TCP, UDP (port numbers, reliability)
3  Network       IP, ICMP, routing
2  Data Link     Ethernet, ARP, MAC addresses
1  Physical      Bits on wire/fibre/radio
```

### TCP/IP Stack (4 layers used in practice)

```
Application   → HTTP, DNS, FTP, SMTP
Transport     → TCP, UDP
Internet      → IP (IPv4/IPv6)
Network Access→ Ethernet, WiFi (combines OSI layers 1-2)
```

Each layer adds a header to the payload as data travels down (encapsulation)
and strips it on the way up (de-capsulation).

---

## Application Layer

### HTTP

HTTP is a stateless, text-based request/response protocol over TCP (port 80 / 443).

**Request format:**
```
GET /index.html HTTP/1.1
Host: www.example.com
Connection: close
```

**Response format:**
```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234

<html>...</html>
```

**Key HTTP versions:**
- HTTP/1.0: One TCP connection per request
- HTTP/1.1: Persistent connections, pipelining, `Host` header required
- HTTP/2: Binary framing, multiplexing, header compression

**HTTP Methods:** GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH

**Common Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | OK |
| 301 | Moved Permanently |
| 304 | Not Modified (cache hit) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

**Cookies:** Server sends `Set-Cookie: id=abc` in response; client echoes
`Cookie: id=abc` in future requests. Used for session state on a stateless protocol.

**Caching:** `Cache-Control`, `ETag`, `If-None-Match`, `Last-Modified`,
`If-Modified-Since` headers enable conditional GETs.

### DNS

The Domain Name System maps hostnames to IP addresses.

**Hierarchy:**
```
.                       (root)
├── com
│   └── google
│       └── www         → 142.250.x.x
└── org
    └── wikipedia
        └── en          → 208.80.x.x
```

**Record types:**

| Type | Purpose |
|------|---------|
| A | hostname → IPv4 |
| AAAA | hostname → IPv6 |
| CNAME | alias → canonical name |
| MX | mail server for domain |
| NS | nameserver for domain |
| TXT | arbitrary text (SPF, DKIM) |

**Resolution flow (iterative):**
1. Browser cache → OS resolver cache
2. Local recursive resolver (ISP)
3. Root nameserver → TLD nameserver → Authoritative nameserver

**DNS runs over UDP port 53** (small queries). Falls back to TCP for large
responses (zone transfers, DNSSEC).

### SMTP / Email

- Client → server: TCP port 25 (SMTP)
- Retrieval: POP3 (port 110) or IMAP (port 143)
- Commands: `HELO`, `MAIL FROM:`, `RCPT TO:`, `DATA`, `QUIT`
- MIME headers extend ASCII email to support attachments and Unicode

---

## Transport Layer

### UDP

- Connectionless, unreliable, unordered
- No handshake, no congestion control
- Low overhead: 8-byte header (src port, dst port, length, checksum)
- Used for: DNS, DHCP, streaming media, VoIP, online games

### TCP

- Connection-oriented, reliable, ordered byte stream
- 3-way handshake: SYN → SYN-ACK → ACK
- 4-way teardown: FIN → ACK → FIN → ACK
- Flow control: receiver advertises **receive window** (`rwnd`)
- Congestion control: sender maintains `cwnd`, uses AIMD

**TCP Header fields (key ones):**
- Source/Destination Port (16-bit each)
- Sequence Number: byte offset in stream
- Acknowledgement Number: next expected byte
- Flags: SYN, ACK, FIN, RST, PSH, URG
- Window Size: receive buffer space available

**Congestion Control (Reno):**

```
Slow Start:     cwnd doubles each RTT until ssthresh
Congestion Avoidance: cwnd +1 MSS per RTT (linear)
Loss detected (timeout): ssthresh = cwnd/2, cwnd = 1 (restart SS)
Loss detected (3x dup ACK): ssthresh = cwnd/2, cwnd = ssthresh (Fast Recovery)
```

**Multiplexing / Demultiplexing:**
- Each TCP/UDP segment carries (src IP, src port, dst IP, dst port)
- OS uses this 4-tuple to demux to the correct socket

---

## Network Layer

### IPv4

- 32-bit addresses (e.g. `192.168.1.1`)
- Written as 4 decimal octets: `A.B.C.D`
- CIDR notation: `192.168.1.0/24` — 24 bits network, 8 bits host → 254 hosts

**Subnetting:**
- Subnet mask `/24` = `255.255.255.0`
- Network address: host bits all 0
- Broadcast: host bits all 1
- Usable: 2^(host bits) − 2

**Special addresses:**
- `127.0.0.1` — loopback
- `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` — private (RFC 1918)
- `0.0.0.0/0` — default route

**Fragmentation:** Routers fragment packets too large for the next link's MTU.
Reassembly happens at the destination.

### NAT

Network Address Translation maps private IP:port pairs to a single public IP.
The NAT router rewrites src/dst addresses and maintains a translation table.

### Routing

- **Distance Vector (RIP):** Each router tells neighbours its distance to every
  destination; count-to-infinity problem.
- **Link State (OSPF, IS-IS):** Each router floods the entire topology; runs
  Dijkstra locally.
- **BGP (path vector):** Inter-AS routing on the internet; policies override
  shortest path.

### ICMP

Internet Control Message Protocol carries error and diagnostic messages.
`ping` uses ICMP Echo Request / Reply. `traceroute` uses TTL expiry messages.

---

## Link Layer

### Ethernet (IEEE 802.3)

- Frame: Preamble | Dest MAC | Src MAC | EtherType | Payload | CRC
- MAC address: 48-bit, written as `AA:BB:CC:DD:EE:FF`
- CSMA/CD for half-duplex (legacy); full-duplex switches eliminate collisions

### ARP

Address Resolution Protocol maps IP → MAC within a subnet.
Host broadcasts "Who has 192.168.1.1?" → owner replies with its MAC.
Results cached in the ARP table (usually 20 min TTL).

### Switches

- Operate at Layer 2, forward frames by MAC address table
- Self-learning: populate table from source MAC of incoming frames
- Spanning Tree Protocol (STP) prevents Layer-2 loops

---

## Socket Programming

A socket is a software abstraction of a communication endpoint in the OS.
It exposes a file-like interface: open, read/write, close.

### TCP Socket Lifecycle

**Server:**
```python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 8888))          # bind to port
s.listen(5)                 # backlog queue of 5
conn, addr = s.accept()     # blocks until client connects
data = conn.recv(1024)      # read from connection
conn.send(b'response')
conn.close()
```

**Client:**
```python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8888))
s.send(b'hello')
data = s.recv(1024)
s.close()
```

### UDP Socket Lifecycle

```python
# Server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 9999))
data, addr = s.recvfrom(1024)
s.sendto(b'reply', addr)

# Client
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'hello', ('localhost', 9999))
data, addr = s.recvfrom(1024)
```

### Threading for Concurrent Clients

The standard pattern is **thread-per-client**: the main thread accepts connections
and spawns a daemon thread to handle each one.

```python
while True:
    conn, addr = server_socket.accept()
    t = threading.Thread(target=handle_client, args=(conn,), daemon=True)
    t.start()
```

### Application-Layer Protocol Design

When building a custom protocol over TCP:
1. Define a **message format** (JSON, binary, delimited text)
2. Define **message types** with clear semantics
3. Handle **framing** — TCP is a stream, not a message protocol. Use
   newline delimiters, length prefixes, or similar to delineate messages.
4. Define a **state machine** for the connection lifecycle
5. Handle **errors** explicitly with error codes

**Example JSON framing (newline-delimited):**
```python
# Send
msg = json.dumps({"type": "PING", "payload": {}}) + '\n'
sock.send(msg.encode())

# Receive
data = sock.recv(4096).decode().strip()
msg = json.loads(data)
```
