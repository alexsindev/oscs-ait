# Full Stack Application Development (FSAD)

## Course Overview

Covers the full development lifecycle of modern web applications — from
RESTful API design and database integration, through to React front-ends,
real-time features (WebSockets), containerisation (Docker), and CI/CD
pipelines (GitLab CI).

## Topics

- REST API design: resources, HTTP verbs, status codes, versioning
- Backend frameworks: Node.js/Express, FastAPI (Python)
- Authentication: JWT, bcrypt, middleware patterns
- MongoDB / Mongoose ODM
- React: components, hooks, routing (React Router), state management
- Real-time: WebSocket (ws library), Socket.IO concepts
- Docker: Dockerfile, docker-compose, multi-service stacks
- CI/CD: GitLab CI pipelines, Docker Hub deployment

## Contents

```
FSAD/
├── notes/
│   └── fullstack-fundamentals.md
└── projects/
    ├── fastapi-backend/         FastAPI + PostgreSQL + JWT (semester assignment)
    └── project-tracker/         React + Node.js + MongoDB + WebSocket (final exam)
```

## Projects

### FastAPI Backend (`fastapi-backend/`)

A RESTful API built with Python / FastAPI. Features:
- JWT-based authentication (`/auth/login`, `/auth/register`)
- Role-based access (admin / student)
- Resources: Users, Courses, Enrollments, Posts, Feedback
- PostgreSQL via SQLAlchemy ORM
- Dockerised: `docker-compose.yml` starts the API + Postgres

**Quick start:**
```bash
cp .env.example .env   # fill in DB credentials
docker compose up -d
```

### Project Tracker — Final Exam (`project-tracker/`)

Full-stack SPA with:
- **Backend:** Node.js / Express, MongoDB (Mongoose), JWT auth, WebSocket server
- **Frontend:** React (Vite), React Router, WebSocket client for live updates
- **Deploy:** Docker multi-stage build; GitLab CI pushes images to Docker Hub

**Architecture:**
```
browser  ←HTTP→  React (Vite)  ←REST→  Express API  ←→  MongoDB
                                ←WS──→  ws server
```
