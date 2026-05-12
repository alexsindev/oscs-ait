# Full Stack Application Development

## REST API Design

REST (Representational State Transfer) is an architectural style for building
network APIs over HTTP.

### Core Constraints

1. **Uniform interface** — resources identified by URIs; standard HTTP methods
2. **Stateless** — no server-side session; each request contains all needed info
3. **Client-server** — UI and data storage concerns are separated
4. **Cacheable** — responses indicate cacheability
5. **Layered system** — client can't tell if it's talking to the origin server

### Resource Design

- Use nouns, not verbs: `/users`, `/projects`, `/enrollments`
- Nest for ownership: `/users/{id}/posts`
- Use HTTP verbs for the operation:

| Method | Path | Action |
|--------|------|--------|
| GET | `/users` | List all users |
| POST | `/users` | Create a user |
| GET | `/users/{id}` | Get one user |
| PUT | `/users/{id}` | Full replace |
| PATCH | `/users/{id}` | Partial update |
| DELETE | `/users/{id}` | Delete user |

### HTTP Status Codes for APIs

| Code | Meaning | Typical Use |
|------|---------|-------------|
| 200 | OK | GET success |
| 201 | Created | POST success |
| 204 | No Content | DELETE / PUT success with no body |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing / invalid token |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate (e.g. email already registered) |
| 422 | Unprocessable Entity | FastAPI / Pydantic validation failure |
| 500 | Internal Server Error | Unhandled exception |

---

## Authentication with JWT

JSON Web Tokens carry claims as a signed Base64-encoded payload.

### Structure

```
header.payload.signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJzdWIiOiJ1c2VyXzEyMyIsImV4cCI6MTcwMDAwMDAwMH0
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

- **Header:** algorithm (`HS256`, `RS256`) and token type
- **Payload:** claims — `sub` (subject), `exp` (expiry), `iat` (issued at),
  custom fields (`role`, `user_id`)
- **Signature:** `HMAC_SHA256(base64(header) + "." + base64(payload), secret)`

### Flow

```
1. POST /auth/login  { username, password }
2. Server verifies password hash (bcrypt)
3. Server issues JWT: { access_token, token_type: "bearer" }
4. Client stores token (memory or localStorage)
5. Client sends: Authorization: Bearer <token>
6. Server middleware decodes and validates token on each request
```

### FastAPI JWT Pattern

```python
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return db.query(User).filter(User.id == user_id).first()
```

---

## FastAPI

FastAPI is a modern Python web framework built on Starlette and Pydantic.

### Application Structure

```python
# app/main.py
from fastapi import FastAPI
from app.api.v1 import routes_auth, routes_users

app = FastAPI(title="My API")

app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(routes_users.router, prefix="/api/v1/users", tags=["users"])
```

### Route Definition

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

    class Config:
        from_attributes = True  # allows ORM object → Pydantic
```

### SQLAlchemy ORM Models

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
```

---

## Node.js / Express

### Basic Express Server

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// Middleware
app.use((req, res, next) => {
  console.log(`${req.method} ${req.path}`);
  next();
});

// Route
app.get('/api/users', async (req, res) => {
  const users = await User.find();
  res.json(users);
});

app.listen(3000, () => console.log('Server on port 3000'));
```

### JWT Middleware (Express)

```javascript
const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
};
```

### Mongoose (MongoDB ODM)

```javascript
const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email:    { type: String, required: true, unique: true },
  password: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', UserSchema);

// Usage
const user = await User.findOne({ email: req.body.email });
const users = await User.find({ role: 'admin' }).populate('projects');
```

---

## React

React is a component-based JavaScript library for building UIs.

### Component Anatomy

```jsx
import { useState, useEffect } from 'react';

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/users')
      .then(r => r.json())
      .then(data => { setUsers(data); setLoading(false); });
  }, []);   // empty deps → run once on mount

  if (loading) return <p>Loading...</p>;

  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}
```

### Custom Hook Pattern

```jsx
// hooks/useAuth.js
export function useAuth() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const login = async (email, password) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const { access_token } = await res.json();
    localStorage.setItem('token', access_token);
    setToken(access_token);
  };

  const logout = () => { localStorage.removeItem('token'); setToken(null); };

  return { token, login, logout, isAuthenticated: !!token };
}
```

### React Router (v6)

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"         element={<Home />} />
        <Route path="/login"    element={<Login />} />
        <Route path="/projects" element={
          isAuthenticated ? <Projects /> : <Navigate to="/login" />
        } />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## WebSockets

WebSocket provides a persistent, full-duplex channel over a single TCP connection.

### Server (Node.js `ws` library)

```javascript
const { WebSocketServer } = require('ws');
const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws, req) => {
  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    // Broadcast to all connected clients
    wss.clients.forEach(client => {
      if (client.readyState === ws.OPEN) {
        client.send(JSON.stringify({ type: 'broadcast', data: msg }));
      }
    });
  });

  ws.on('close', () => console.log('Client disconnected'));
});
```

### Client (React)

```jsx
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8080');

  ws.onopen = () => console.log('Connected');
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    setMessages(prev => [...prev, msg]);
  };
  ws.onclose = () => console.log('Disconnected');

  return () => ws.close();   // cleanup on unmount
}, []);
```

**Key points:**
- `ws://` for unencrypted, `wss://` for TLS (required in production)
- Server must handle `Upgrade` HTTP header during handshake
- Heartbeat/ping-pong keeps idle connections alive through proxies

---

## Docker

### Dockerfile (Node.js)

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS production
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Dockerfile (Python / FastAPI)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose (multi-service)

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
    depends_on: [db]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

**Key commands:**
```bash
docker compose up -d          # start in background
docker compose logs -f api    # tail logs
docker compose down -v        # stop and remove volumes
docker exec -it api bash      # shell into running container
```

---

## CI/CD with GitLab CI

```yaml
# .gitlab-ci.yml
stages: [build, deploy]

build:
  stage: build
  image: docker:24
  services: [docker:24-dind]
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  only: [main]
  script:
    - ssh $DEPLOY_USER@$DEPLOY_HOST "
        docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA &&
        docker compose up -d --no-deps api"
```
