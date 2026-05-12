# AT70.05 - Backend Application

## Local Development Setup

1. Clone the repository
2. cd into the project directory
3. `uv sync` to create virtual environment and install dependencies
4. Create a `.env` file in the root directory
   ```env
   DATABASE_USER=devuser
   DATABASE_PASS=devpass
   DATABASE_HOST=localhost:5454
   DATABASE_DB=fastapi_db
   UVICORN_HOST=localhost
   UVICORN_PORT=8000
   JWT_SECRET_KEY=your_jwt_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   UPLOAD_DIRECTORY=./uploads
   SEED_DEFAULT_USERS=true
   ```
5. Start the PostgreSQL database:
   ```bash
   docker-compose -f docker-compose-db.yml up -d
   ```
6. Run the application (database tables will be created automatically):
   ```bash
   ./start-backend.sh
   # or manually:
   # uv run uvicorn app.main:app --reload --host localhost --port 8000
   ```

## Default Users (Development Only)

When `SEED_DEFAULT_USERS=true` in `.env`, the following users are created
automatically on startup if they don't exist:

| Role       | Email               | Password      |
| ---------- | ------------------- | ------------- |
| Admin      | admin@test.com      | admin123      |
| Teacher    | teacher@test.com    | teacher123    |
| Student    | student@test.com    | student123    |
| Instructor | instructor@test.com | instructor123 |
| Guest      | guest@test.com      | guest123      |

**Note:** Set `SEED_DEFAULT_USERS=false` in production or manually create secure
admin users.

You can also run the seeding script manually:

```bash
uv run python -m app.db.seed_users
```

## Pytest local run

- Make sure to have the virtual environment activated in the terminal and sample
  images in `tests/sample_images/` folder.
- Make sure `.env` file is properly set up with correct `DB_HOST` for local
  testing.
- Run the tests with:
  ```bash
  pytest -v
  ```

## API endpoints and role permissions

**Legend:**

- ✅ = Full access
- ❌ = No access
- 👤 = Only for own resources (e.g., students can only access their own data)
- ⚙️ = Visibility filtered by role (e.g., see only resources assigned to them)

### Authentication and Authorization

- Everyone can login, register, logout, and change their password of their own
  account.
- During registration, all new users are assigned the "guest" role and have
  their accounts marked as unapproved by default. An admin must approve the
  account and set the role before the user can access other functionalities.
- **But during development** for the scope of this course, this restriction is
  not enforced to facilitate testing by allowing all the users to select a role
  and access all functionalities immediately after registration.
- For **Frontend** registration page, users can select any role from dropdown
  menu except "Admin".
- For the student profile, students can later create and update their profiles
  after logging in, or Admins and Teachers can create and update student
  profiles for them.
- Logout will invalidate the JWT token by adding its jti to a blacklist. Good
  for auditing as well.
- Each user can only change their own password.

| Action | Endpoint                  | Description                 | Admin | Teacher | Instructor | Student | Guest |
| ------ | ------------------------- | --------------------------- | ----- | ------- | ---------- | ------- | ----- |
| POST   | `/auth/register`          | Register a new user         | 👤     | 👤       | 👤          | 👤       | 👤     |
| POST   | `/auth/login`             | Login and get access token  | 👤     | 👤       | 👤          | 👤       | 👤     |
| POST   | `/auth/logout`            | Logout and invalidate token | 👤     | 👤       | 👤          | 👤       | 👤     |
| POST   | `/auth/change_password`   | Change user password        | 👤     | 👤       | 👤          | 👤       | 👤     |
| PATCH  | `/auth/approve_user/{id}` | Approve user account        | ✅     | ❌       | ❌          | ❌       | ❌     |

### User Management

- Admins and Teachers can read all users at once for management purposes.
- Everyone can read their own user details.
- **Frontend** can use the `/users/me` endpoint to get the logged-in user's
  details along with their student profile if available.
- Everyone can read other users' details except Guests can only read their own
  details for privacy reasons.
- **Frontend** can use the `/users/{id}` endpoint to get other users' details
  along with their student profiles if available, with the access permissions.
- Editing users' details is restricted to Admins only, except users can update
  their own information.
- Deleting users is restricted to Admins only for prevention of accidental or
  malicious deletions.
- Reading users' details also automatically includes their student profiles if
  they have one.
- Most of student profile management endpoints are restricted to Admins and
  Teachers for API CRUD management purposes, getting student profiles can be
  done through user details endpoints.
- Student profiles can be created and updated by the respective students
  themselves, and also by Admins and Teachers.
- Deleting student profiles is restricted to Admins only.

| Action | Endpoint                             | Description                  | Admin | Teacher | Instructor | Student | Guest |
| ------ | ------------------------------------ | ---------------------------- | ----- | ------- | ---------- | ------- | ----- |
| GET    | `/users/`                            | Read all users               | ✅     | ✅       | ❌          | ❌       | ❌     |
| GET    | `/users/me`                          | Read self                    | ✅     | ✅       | ✅          | ✅       | ✅     |
| GET    | `/users/{id}`                        | Read user by ID              | ✅     | ✅       | ✅          | ✅       | 👤     |
| PATCH  | `/users/{id}`                        | Update user information      | ✅     | 👤       | 👤          | 👤       | 👤     |
| DELETE | `/users/{id}`                        | Delete user by ID            | ✅     | ❌       | ❌          | ❌       | ❌     |
| GET    | `/users/student_profiles`            | Read all student profiles    | ✅     | ✅       | ❌          | ❌       | ❌     |
| POST   | `/users/student_profiles`            | Create student profile       | ✅     | ✅       | ❌          | 👤       | ❌     |
| GET    | `/users/student_profiles/{id}`       | Read student profile by ID   | ✅     | ✅       | ❌          | 👤       | ❌     |
| PATCH  | `/users/student_profiles/{id}`       | Update student profile       | ✅     | ✅       | ❌          | 👤       | ❌     |
| DELETE | `/users/student_profiles/{id}`       | Delete student profile by ID | ✅     | ❌       | ❌          | ❌       | ❌     |
| GET    | `/users/user_profiles`               | Read all user profiles       | ✅     | ✅       | ❌          | ❌       | ❌     |
| POST   | `/users/user_profiles`               | Create user profile          | ✅     | ✅       | 👤          | 👤       | 👤     |
| GET    | `/users/user_profiles/{id}`          | Read user profile by ID      | ✅     | ✅       | 👤          | 👤       | 👤     |
| PATCH  | `/users/user_profiles/{id}`          | Update user profile          | ✅     | ✅       | 👤          | 👤       | 👤     |
| DELETE | `/users/user_profiles/{id}`          | Delete user profile by ID    | ✅     | ❌       | ❌          | ❌       | ❌     |
| POST   | `/users/profile-picture/upload`      | Upload profile picture       | ✅     | ✅       | ✅          | ✅       | ✅     |
| GET    | `/users/profile-pictures/{filename}` | Get profile picture (public) | ✅     | ✅       | ✅          | ✅       | ✅     |
| DELETE | `/users/profile-picture`             | Delete profile picture       | ✅     | ✅       | ✅          | ✅       | ✅     |

### Course Groups and Courses

- There is no sensitive data in this section, so everyone can read all courses
  and course groups.
- One course group can have multiple courses, one course belongs to one course
  group.
- Course group and course management (create, update, delete) is restricted to
  Admins and Teachers only.
- Won't allow deleting a course group if it still has courses assigned to it.
- Frontend can use the `/courses/groups` to get all course groups, then display
  the courses under each group with the `/courses/groups/{id}/courses` endpoint.

| Action | Endpoint                       | Description                    | Admin | Teacher | Instructor | Student | Guest |
| ------ | ------------------------------ | ------------------------------ | ----- | ------- | ---------- | ------- | ----- |
| GET    | `/courses/`                    | Read all courses               | ✅     | ✅       | ✅          | ✅       | ✅     |
| GET    | `/courses/teacher/me`          | Read courses created by me     | ✅     | ✅       | ❌          | ❌       | ❌     |
| POST   | `/courses/`                    | Create course                  | ✅     | ✅       | ❌          | ❌       | ❌     |
| GET    | `/courses/{id}`                | Read course by ID              | ✅     | ✅       | ✅          | ✅       | ✅     |
| DELETE | `/courses/{id}`                | Delete course by ID            | ✅     | ✅       | ❌          | ❌       | ❌     |
| PATCH  | `/courses/{id}`                | Update course by ID            | ✅     | ✅       | ❌          | ❌       | ❌     |
| GET    | `/courses/groups `             | Read all course groups         | ✅     | ✅       | ✅          | ✅       | ✅     |
| POST   | `/courses/groups`              | Create course group            | ✅     | ✅       | ❌          | ❌       | ❌     |
| GET    | `/courses/groups/{id}`         | Read course group by ID        | ✅     | ✅       | ✅          | ✅       | ✅     |
| DELETE | `/courses/groups/{id}`         | Delete course group by ID      | ✅     | ✅       | ❌          | ❌       | ❌     |
| PATCH  | `/courses/groups/{id}`         | Update course group by ID      | ✅     | ✅       | ❌          | ❌       | ❌     |
| GET    | `/courses/groups/{id}/courses` | Read courses in a course group | ✅     | ✅       | ✅          | ✅       | ✅     |

### Enrollments

- Most of these are just for mapping students into courses for filtering and
  potential visualization purposes, updating and deleting enrollments does not
  affect users, courses, posts, or feedbacks, since posts and feedbacks are
  linked to users directly.
- Only Admins and Teachers can read all enrollments at once for management
  purposes.
- Students and Instructors can enroll themselves in courses or let Teachers/Admins enroll them.
- Everyone except Guests can read enrollment details by ID, this is just
  enrollment status information.
- Admins and Teachers can update enrollment status and delete enrollments.
- Everyone except Guests can read any student's enrollments with their user ID
  for viewing their course participation.
- Everyone except Guests can read enrollments for a specific course for viewing
  course participation.

| Action | Endpoint                          | Description                | Admin | Teacher | Instructor | Student | Guest |
| ------ | --------------------------------- | -------------------------- | ----- | ------- | ---------- | ------- | ----- |
| GET    | `/enrollments/`                   | Read all enrollments       | ✅     | ✅       | ❌          | ❌       | ❌     |
| POST   | `/enrollments/`                   | Create enrollment          | ✅     | ✅       | 👤          | 👤       | ❌     |
| GET    | `/enrollments/{id}`               | Read enrollment by ID      | ✅     | ✅       | ✅          | ✅       | ❌     |
| PATCH  | `/enrollments/{id}`               | Update enrollment status   | ✅     | ✅       | ❌          | ❌       | ❌     |
| DELETE | `/enrollments/{id}`               | Delete enrollment by ID    | ✅     | ✅       | ❌          | ❌       | ❌     |
| GET    | `/enrollments/user/{user_id}`     | Read enrollments by user   | ✅     | ✅       | ✅          | ✅       | ❌     |
| GET    | `/enrollments/course/{course_id}` | Read enrollments by course | ✅     | ✅       | ✅          | ✅       | ❌     |

### Posts, Media, and Feedbacks

- Only Admins can read all posts at once for management purposes, some posts
  might not be suitable for all roles, even teachers, just in case, and fetching
  all posts of every users is not a common use case anyway.
- Only Admins and Students can create posts, since this is E-portfolio system
  for students' work.
- Admin can read any post by ID, while other roles have configurable or special
  permissions to read posts based on visibility settings.
- Admin and Teachers can update any post's visibility, Students can only update
  their own posts' visibility. Only admins can set `admins_only` visibility.
- Admin and Teachers can delete posts, while Students can only delete their own
  posts.
- Everyone can read posts by a specific user, with visibility filtering based on
  roles.
- **Frontend** can use the `/posts/user/{user_id}` endpoint to get all posts by
  a specific user, with visibility filtering automatically applied on the
  backend side based on the role of the requester.
- Each post can have multiple media files attached to it, and the media files
  are stored and served from the backend.
- **Frontend** can use the `/posts/media/{media_id}` endpoint to get the media
  file attached to a post by its media ID which automatically applies visibility
  filtering based on the role of the requester.
- All authenticated users (admin, teacher, instructor, student, guest) can create
  feedbacks for posts they have visibility access to. Post owners can also provide
  feedback on their own posts (treated as replies to other feedback).
- Only Admins and Teachers can read all feedbacks at once for management
  purposes.
- Only Admins and Teachers can delete feedbacks.
- Everyone can read feedbacks for a specific post, with visibility filtering
  based on roles.
- **Frontend** can use the `/feedbacks/post/{post_id}` endpoint to get all
  feedbacks for a specific post, with visibility filtering automatically applied
  on the backend side based on the role of the requester.
- **NOTE: Students can always access their own posts, feedbacks, and media files
  without restrictions, so they can fully manage their own E-portfolio.**

| Action | Endpoint                            | Description                                           | Admin | Teacher | Instructor | Student | Guest |
| ------ | ----------------------------------- | ----------------------------------------------------- | ----- | ------- | ---------- | ------- | ----- |
| GET    | `/posts/`                           | Read all posts                                        | ✅     | ❌       | ❌          | ❌       | ❌     |
| GET    | `/posts/course/{course_id}`         | Read posts by course (visibility filtered)            | ✅     | ⚙️       | ⚙️          | ⚙️       | ⚙️     |
| POST   | `/posts/`                           | Create a post                                         | ✅     | ❌       | ❌          | ✅       | ❌     |
| GET    | `/posts/{id}`                       | Read post by ID (visibility filtered)                 | ✅     | ⚙️       | ⚙️          | ⚙️       | ⚙️     |
| PATCH  | `/posts/{id}/visibility`            | Update post visibility                                | ✅     | ⚙️       | ❌          | 👤       | ❌     |
| PATCH  | `/posts/{post_id}/content`          | Update post title and/or text content                 | ✅     | ✅       | ❌          | 👤       | ❌     |
| DELETE | `/posts/{post_id}/media/{media_id}` | Delete post media by media ID                         | ✅     | ✅       | ❌          | 👤       | ❌     |
| DELETE | `/posts/{id}`                       | Delete post by ID                                     | ✅     | ✅       | ❌          | 👤       | ❌     |
| GET    | `/posts/user/{user_id}`             | Read posts by user (visibility filtered)              | ✅     | ⚙️       | ⚙️          | ⚙️       | ⚙️     |
| GET    | `/posts/media/{media_id}`           | Get post media file by media ID (visibility filtered) | ✅     | ⚙️       | ⚙️          | ⚙️       | ⚙️     |
| POST   | `/feedbacks/`                       | Create feedback                                       | ✅     | ✅       | ✅          | ✅       | ✅     |
| GET    | `/feedbacks/`                       | Read all feedbacks                                    | ✅     | ✅       | ❌          | ❌       | ❌     |
| DELETE | `/feedbacks/{id}`                   | Delete feedback by ID                                 | ✅     | ✅       | ❌          | ❌       | ❌     |
| GET    | `/feedbacks/post/{post_id}`         | Read feedbacks by post (visibility filtered)          | ✅     | ⚙️       | ⚙️          | ⚙️       | ⚙️     |

### Public Endpoints

- Public endpoints do not require authentication.
- These endpoints are designed for public-facing pages like project info.

| Action | Endpoint                | Description                   | Admin | Teacher | Instructor | Student | Guest | Public |
| ------ | ----------------------- | ----------------------------- | ----- | ------- | ---------- | ------- | ----- | ------ |
| GET    | `/public/user-profiles` | List users with user profiles | ✅     | ✅       | ✅          | ✅       | ✅     | ✅      |

## Production Deployment with Docker

This section covers deploying the complete Achievement Showcase system (Frontend + Backend + Database) using Docker Compose on a production server.

### Architecture Overview

The production deployment consists of three services running in a Docker network:
- **Frontend** (nginx): Publicly accessible on port 80/443
- **Backend** (FastAPI): Internal only, accessible via Docker network
- **Database** (PostgreSQL): Internal only, accessible via Docker network

### Prerequisites

1. **Docker and Docker Compose** installed on production server
   ```bash
   # Install Docker (Ubuntu/Debian)
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Pre-built Docker images** pushed to Docker Hub
   ```bash
   # On your development machine:
   
   # Build and push backend image
   cd AT70.05-Backend
   docker build -t yourusername/achievement-showcase-backend:latest .
   docker push yourusername/achievement-showcase-backend:latest
   
   # Build and push frontend image
   cd ../AT70.05-Frontend
   docker build -t yourusername/achievement-showcase-frontend:latest .
   docker push yourusername/achievement-showcase-frontend:latest
   ```

### Deployment Steps

#### 1. Prepare Production Environment

On your production server, create a deployment directory:

```bash
mkdir -p ~/achievement-showcase
cd ~/achievement-showcase
```

#### 2. Create Environment Configuration

Create a `.env` file with your production settings:

```bash
cat > .env << 'EOF'
# Database Configuration
DATABASE_USER=achievement_user
DATABASE_PASS=your_secure_database_password_here
DATABASE_DB=achievement_showcase

# JWT Configuration (CHANGE THESE IN PRODUCTION!)
JWT_SECRET_KEY=your_super_secure_random_jwt_secret_key_minimum_32_characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# User Seeding (false in production)
SEED_DEFAULT_USERS=false
EOF
```

**Security Notes:**
- Generate a strong JWT secret: `openssl rand -hex 32`
- Use strong database password: `openssl rand -base64 32`
- Never commit `.env` to version control
- Consider using Docker secrets for sensitive data

#### 3. Create Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database - Internal only
  db:
    image: postgres:16
    container_name: achievement-db
    environment:
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASS}
      POSTGRES_DB: ${DATABASE_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - achievement-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER} -d ${DATABASE_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API - Internal only (not exposed to host)
  backend:
    image: yourusername/achievement-showcase-backend:latest
    container_name: achievement-backend
    environment:
      DATABASE_USER: ${DATABASE_USER}
      DATABASE_PASS: ${DATABASE_PASS}
      DATABASE_HOST: db:5432
      DATABASE_DB: ${DATABASE_DB}
      UVICORN_HOST: 0.0.0.0
      UVICORN_PORT: 8000
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      JWT_ALGORITHM: ${JWT_ALGORITHM}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
      UPLOAD_DIRECTORY: /app/uploads
      SEED_DEFAULT_USERS: ${SEED_DEFAULT_USERS:-false}
    volumes:
      - backend_uploads:/app/uploads
    networks:
      - achievement-network
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  # Frontend - Publicly accessible
  frontend:
    image: yourusername/achievement-showcase-frontend:latest
    container_name: achievement-frontend
    ports:
      - "80:80"
      - "443:443"  # If using SSL
    networks:
      - achievement-network
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:80/health"\]
      interval: 30s
      timeout: 3s
      retries: 3

volumes:
  postgres_data:
    driver: local
  backend_uploads:
    driver: local

networks:
  achievement-network:
    driver: bridge
```

**Important:** Replace `yourusername` with your actual Docker Hub username in the image names.

#### 4. Start the Application

```bash
# Pull latest images and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

#### 5. Verify Deployment

```bash
# Check all containers are running
docker ps

# Test backend health (from within server)
curl http://localhost:8000/health

# Test frontend (from browser)
# Visit: http://your-server-ip
```

### Network Architecture

- **Frontend → Backend**: Uses internal Docker network name `http://backend:8000`
- **Backend → Database**: Uses internal Docker network name `db:5432`
- **External → Frontend**: Accessible via port 80/443 on host
- **External → Backend**: NOT accessible (no port mapping)
- **External → Database**: NOT accessible (no port mapping)

This setup ensures only the frontend is publicly accessible, while backend and database remain isolated within the Docker network.

### Management Commands

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# View logs for a specific service
docker-compose logs -f backend

# Execute commands in a container
docker exec -it achievement-backend bash

# Update to latest images
docker-compose pull
docker-compose up -d
```

### Monitoring

```bash
# View resource usage
docker stats

# Check health status
docker inspect --format='{{json .State.Health}}' achievement-backend
docker inspect --format='{{json .State.Health}}' achievement-frontend

# View backend logs
docker-compose logs -f backend --tail=100

# View frontend access logs
docker exec achievement-frontend cat /var/log/nginx/access.log
```

### Backup and Restore

#### Database Backup

```bash
# Create backup
docker exec achievement-db pg_dump -U ${DATABASE_USER} ${DATABASE_DB} > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
cat backup_20240101_120000.sql | docker exec -i achievement-db psql -U ${DATABASE_USER} ${DATABASE_DB}
```

#### Uploads Backup

```bash
# Backup uploads volume
docker run --rm -v achievement-showcase_backend_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore uploads
docker run --rm -v achievement-showcase_backend_uploads:/data -v $(pwd):/backup alpine tar xzf /backup/uploads_backup_20240101_120000.tar.gz -C /data
```

### SSL/HTTPS Setup

For production, you should enable HTTPS. Use one of these approaches:

#### Option 1: Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot

# Get certificate (temporary stop frontend)
docker-compose stop frontend
sudo certbot certonly --standalone -d your-domain.com

# Update docker-compose.yml to mount certificates
# Add under frontend.volumes:
#   - /etc/letsencrypt:/etc/letsencrypt:ro

# Restart with SSL enabled
docker-compose up -d
```

#### Option 2: Reverse Proxy (Recommended)

Use a reverse proxy like Traefik or nginx-proxy with automatic Let's Encrypt:

```yaml
# Add labels to frontend service
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.frontend.rule=Host(`your-domain.com`)"
  - "traefik.http.routers.frontend.entrypoints=websecure"
  - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
```

### Troubleshooting

#### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs backend

# Verify environment variables
docker-compose config
```

#### Database Connection Issues

```bash
# Test database connectivity
docker exec achievement-backend python -c "from app.database import engine; print(engine)"

# Check database logs
docker-compose logs db
```

#### Frontend Can't Reach Backend

1. Verify services are on same network: `docker network inspect achievement-showcase_achievement-network`
2. Check backend health: `docker exec achievement-backend curl http://localhost:8000/health`
3. Verify frontend environment: `docker exec achievement-frontend env | grep VITE_API_BASE_URL`

#### Out of Disk Space

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove old images
docker image prune -a

# Check volume sizes
docker system df -v
```

### Security Considerations

1. **Change default credentials**: Always use strong, unique passwords
2. **Regular updates**: Keep Docker images updated
   ```bash
   docker-compose pull
   docker-compose up -d
   ```
3. **Firewall**: Only expose necessary ports (80, 443)
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
4. **Monitoring**: Set up monitoring for unusual activity
5. **Backups**: Automate regular database and upload backups
6. **Logs**: Rotate logs to prevent disk space issues
   ```bash
   # Add to docker-compose.yml under each service:
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

### Updating the Application

```bash
# 1. Build new images on development machine
docker build -t yourusername/achievement-showcase-backend:latest .
docker push yourusername/achievement-showcase-backend:latest

# 2. On production server
cd ~/achievement-showcase
docker-compose pull
docker-compose up -d

# 3. Verify update
docker-compose ps
docker-compose logs -f
```

### Performance Optimization

1. **Resource Limits**: Add to docker-compose.yml
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
       reservations:
         cpus: '0.5'
         memory: 512M
   ```

2. **Database Tuning**: Add to db service
   ```yaml
   command:
     - "postgres"
     - "-c"
     - "shared_buffers=256MB"
     - "-c"
     - "max_connections=100"
   ```

3. **Nginx Caching**: Already configured in frontend image

### Support

For issues or questions:
1. Check service logs: `docker-compose logs service-name`
2. Verify health checks: `docker ps` (look for "healthy" status)
3. Test connectivity between services
4. Review environment variables: `docker-compose config`

