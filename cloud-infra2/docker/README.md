# Docker Setup & Containerization

**Purpose**: Container definitions and orchestration for local development and production deployment  
**Status**: Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Docker Compose Files](#docker-compose-files)
3. [Container Images](#container-images)
4. [Local Development Stack](#local-development-stack)
5. [Production Deployment Stack](#production-deployment-stack)
6. [Docker Compose Commands](#docker-compose-commands)
7. [Networking](#networking)
8. [Volumes](#volumes)
9. [Environment Configuration](#environment-configuration)
10. [Troubleshooting](#troubleshooting)

---

## Overview

IntelliWealth uses Docker containers for consistent deployment across development, testing, and production environments. All services are containerized and orchestrated using Docker Compose.

### Containerization Strategy

- **Local Development**: `docker-compose.yml` - Full stack with all services
- **Production Backend**: `docker-compose.prod.yml` - Backend services only
- **Production Frontend**: `docker-compose.frontend.prod.yml` - Frontend only
- **Multi-stage builds**: Optimize image sizes, separate build and runtime

### Key Components

| Service | Docker Image | Base | Size | Purpose |
|---------|-------------|------|------|---------|
| frontend | intelliwealth-frontend | nginx:alpine | ~100 MB | Static web server + reverse proxy |
| portfolio-service | intelliwealth-portfolio | python:3.11-slim | ~500 MB | Portfolio microservice |
| market-service | intelliwealth-market | python:3.11-slim | ~500 MB | Market data microservice |
| postgres | postgres:16-alpine | postgres | ~150 MB | Relational database |
| redis | redis:7-alpine | redis | ~50 MB | Cache datastore |

---

## Docker Compose Files

### docker-compose.yml (Local Development)

**Purpose**: Complete local development environment with all services, database, and cache.

**Services**:
- `frontend` - React application (port 3000)
- `portfolio-service` - Portfolio microservice (port 8000)
- `market-service` - Market microservice (port 8001)
- `postgres` - PostgreSQL database (port 5432)
- `redis` - Redis cache (port 6379)

**Key Features**:
- Development-optimized Nginx configuration
- Volume mounts for hot reload
- Health checks enabled
- Network isolation
- Automatic database initialization

**Usage**:
```bash
# Build and start all services
docker compose up --build -d

# View logs
docker compose logs -f [service]

# Stop all services
docker compose down

# Clean up volumes
docker compose down -v
```

### docker-compose.prod.yml (Production Backend)

**Purpose**: Backend services for production EC2 deployment.

**Services**:
- `portfolio-service` - Portfolio microservice
- `market-service` - Market microservice
- `redis` - Redis cache (optional, can use ElastiCache)

**Excludes**:
- Frontend (served separately or via CDN)
- PostgreSQL (uses RDS)
- Redis (can use ElastiCache)

**Key Features**:
- Production-optimized settings
- Environment variable injection
- Logging configuration
- Resource limits
- Restart policies

**Usage**:
```bash
# Deploy backend services
docker compose -f docker-compose.prod.yml up -d

# View service status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### docker-compose.frontend.prod.yml (Production Frontend)

**Purpose**: Frontend service for production EC2 deployment.

**Services**:
- `frontend` - Nginx web server serving static files

**Features**:
- Production Nginx configuration
- Static file serving
- Reverse proxy configuration
- Cache headers
- Gzip compression

**Usage**:
```bash
# Deploy frontend
docker compose -f docker-compose.frontend.prod.yml up -d

# Verify running
docker compose -f docker-compose.frontend.prod.yml ps
```

---

## Container Images

### Frontend Image

**Dockerfile**: `frontend/Dockerfile`  
**Build Args**: `VITE_API_BASE_URL=/api/v1`

**Multi-stage Build**:

**Stage 1: Builder**
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
ARG VITE_API_BASE_URL=/api/v1
RUN npm run build
```

**Stage 2: Runtime**
```dockerfile
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**Image Characteristics**:
- Size: ~100 MB
- Base: nginx:alpine (lightweight)
- Build time: ~2 minutes
- Startup time: < 1 second

**Build**:
```bash
docker build -f frontend/Dockerfile -t intelliwealth-frontend:latest .
```

### Portfolio Service Image

**Dockerfile**: `portfolio-service/Dockerfile`

**Multi-stage Build**:

**Stage 1: Builder**
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /build
COPY portfolio-service/requirements.txt .
RUN pip install --user -r requirements.txt
```

**Stage 2: Runtime**
```dockerfile
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY portfolio-service/ /app
WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
```

**Image Characteristics**:
- Size: ~500 MB
- Base: python:3.11-slim
- Build time: ~3 minutes
- Dependencies: FastAPI, SQLAlchemy, Alembic

**Build**:
```bash
docker build -f portfolio-service/Dockerfile -t intelliwealth-portfolio:latest .
```

### Market Service Image

**Dockerfile**: `market-service/Dockerfile`

**Multi-stage Build**: Similar to portfolio service, includes scientific libraries (NumPy, SciPy)

**Image Characteristics**:
- Size: ~500 MB
- Base: python:3.11-slim
- Build time: ~3 minutes
- Dependencies: FastAPI, SQLAlchemy, NumPy, SciPy, Redis

**Build**:
```bash
docker build -f market-service/Dockerfile -t intelliwealth-market:latest .
```

### PostgreSQL Image

**Base**: `postgres:16-alpine`  
**Size**: ~150 MB  
**Configuration**: Initialization scripts from `docker/init.sql`

**Features**:
- PostgreSQL 16
- Alpine Linux (minimal)
- Auto-initialization script
- Volume for data persistence

**Initialization**:
```dockerfile
COPY docker/init.sql /docker-entrypoint-initdb.d/
```

### Redis Image

**Base**: `redis:7-alpine`  
**Size**: ~50 MB  
**Configuration**: Default settings suitable for caching

**Features**:
- Redis 7
- Alpine Linux (minimal)
- In-memory data store
- Optional persistence

---

## Local Development Stack

### Full Stack Architecture

```
┌─────────────────────────────────────────────────┐
│         Docker Compose Network (bridge)          │
├─────────────────────────────────────────────────┤
│                                                 │
│  Host Network (localhost)                       │
│  ├─ :3000   → frontend container:80            │
│  ├─ :8000   → portfolio-service:8000           │
│  ├─ :8001   → market-service:8001              │
│  ├─ :5432   → postgres:5432                    │
│  └─ :6379   → redis:6379                       │
│                                                 │
│  Container Network (internal Docker network)    │
│  ├─ frontend → Nginx reverse proxy              │
│  ├─ portfolio-service → FastAPI                 │
│  ├─ market-service → FastAPI                    │
│  ├─ postgres → PostgreSQL                       │
│  └─ redis → Redis                               │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Port Mappings (Local Development)

| Host Port | Container | Service | Purpose |
|-----------|-----------|---------|---------|
| 3000 | frontend:80 | Frontend | Web UI |
| 8000 | portfolio-service:8000 | Portfolio Service | API |
| 8001 | market-service:8001 | Market Service | API |
| 5432 | postgres:5432 | PostgreSQL | Database |
| 6379 | redis:6379 | Redis | Cache |

### Networking

**Docker Compose Network**: `cloud-infra_default` (bridge)

**Service Names** (container hostnames):
- `frontend` - Frontend service
- `portfolio-service` - Portfolio service
- `market-service` - Market service
- `postgres` - PostgreSQL database
- `redis` - Redis cache

**Inter-Container Communication**:
```
portfolio-service → postgres:5432
market-service → postgres:5432
market-service → redis:6379
frontend → portfolio-service:8000 (via Nginx)
frontend → market-service:8001 (via Nginx)
```

### Volumes

**Development Volumes**:

| Volume | Container Path | Purpose | Persistent |
|--------|-----------------|---------|-----------|
| `postgres_data` | /var/lib/postgresql/data | Database storage | Yes |
| `frontend/src` | /app/src | Source code (hot reload) | Host mount |
| `portfolio-service/app` | /app/app | Source code (hot reload) | Host mount |
| `market-service/app` | /app/app | Source code (hot reload) | Host mount |

**Volume Commands**:
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect postgres_data

# Remove volume
docker volume rm postgres_data

# Clear all unused volumes
docker volume prune
```

---

## Production Deployment Stack

### EC2 Instance Setup

**Prerequisites**:
- Amazon Linux 2 or Ubuntu 22.04 LTS
- Docker Engine 24.x+
- Docker Compose v2
- IAM role with ECR/ECS permissions

### Deployment Process

1. **Pull Docker Images**:
   ```bash
   docker pull your_registry/intelliwealth-frontend:v1.0.0
   docker pull your_registry/intelliwealth-portfolio:v1.0.0
   docker pull your_registry/intelliwealth-market:v1.0.0
   ```

2. **Create Compose Files**:
   ```bash
   # Copy compose files to EC2
   scp docker-compose.prod.yml ec2-user@instance:/home/ec2-user/
   scp docker-compose.frontend.prod.yml ec2-user@instance:/home/ec2-user/
   ```

3. **Set Environment Variables**:
   ```bash
   # Create .env.prod file with production secrets
   cp .env.prod.example .env.prod
   # Edit .env.prod with actual values from AWS Secrets Manager
   ```

4. **Start Services**:
   ```bash
   # Backend services
   docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
   
   # Frontend service
   docker compose -f docker-compose.frontend.prod.yml --env-file .env.prod up -d
   ```

5. **Verify Health**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   curl http://localhost/health
   ```

### Production Networking

**EC2 Instance → RDS**:
- Connection string from AWS Systems Manager Parameter Store
- Security group allows 5432 from EC2
- SSL/TLS encrypted connection recommended

**EC2 Instance → ElastiCache Redis**:
- ElastiCache endpoint injected via environment variable
- Security group allows 6379 from EC2
- Authentication via Redis auth token

**ALB → EC2**:
- ALB forwards requests to EC2 on ports 80, 8000, 8001
- Health checks on `/health` endpoints
- Target group deregistration on health check failure

---

## Docker Compose Commands

### Building

```bash
# Build all services
docker compose build

# Build specific service
docker compose build frontend

# Build with no cache
docker compose build --no-cache

# Build with build args
docker compose build --build-arg VITE_API_BASE_URL=/api/v1
```

### Running

```bash
# Start all services (build if necessary)
docker compose up --build -d

# Start without rebuilding
docker compose up -d

# Start specific service
docker compose up -d portfolio-service

# Run in foreground (see logs)
docker compose up
```

### Monitoring

```bash
# List running containers
docker compose ps

# View logs for all services
docker compose logs

# View logs for specific service
docker compose logs portfolio-service

# Follow logs in real-time
docker compose logs -f

# View last N lines
docker compose logs --tail 50

# View logs since timestamp
docker compose logs --since 2024-01-15T10:00:00
```

### Maintenance

```bash
# Stop all services
docker compose stop

# Restart services
docker compose restart portfolio-service

# Stop and remove containers
docker compose down

# Remove containers, volumes, and networks
docker compose down -v

# Pause/unpause
docker compose pause
docker compose unpause
```

### Debugging

```bash
# Execute command in container
docker compose exec portfolio-service bash

# View container stats
docker compose stats

# Inspect service
docker compose logs portfolio-service | head -100

# Check if service is healthy
docker compose ps | grep portfolio-service
```

---

## Networking

### Docker Network Types

**Bridge Network** (default for Compose):
- Each container gets an internal IP
- Containers communicate by service name (DNS)
- Port mapping bridges host to container

### DNS Resolution

**Container to Container**:
```
portfolio-service → postgres:5432
                 (resolved via Docker DNS: 127.0.0.11:53)
```

**Host to Container**:
```
localhost:8000 → portfolio-service:8000
               (mapped port)
```

### Custom Network Configuration

**Hostname Resolution**:
```yaml
services:
  portfolio-service:
    hostname: portfolio-service
    networks:
      - app-network
    environment:
      DATABASE_HOST: postgres  # Resolved via DNS
```

---

## Volumes

### Volume Types

**Named Volumes** (persistent storage):
```yaml
volumes:
  postgres_data:
    driver: local
```

**Bind Mounts** (host directory):
```yaml
volumes:
  - ./portfolio-service/app:/app/app  # Source:Destination
```

### Managing Volumes

**Backup Database**:
```bash
# Create backup
docker compose exec postgres pg_dump -U postgres intelliwealth > backup.sql

# Restore backup
docker compose exec -T postgres psql -U postgres intelliwealth < backup.sql
```

**View Volume Size**:
```bash
# List volumes with size info
docker volume ls

# Inspect specific volume
docker volume inspect postgres_data
```

---

## Environment Configuration

### Environment Files

**Local Development** (`.env`):
```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=intelliwealth
DATABASE_URL=postgresql://postgres:dev_password@postgres:5432/intelliwealth

# Redis
REDIS_URL=redis://redis:6379/0

# Services
JWT_SECRET_KEY=your_dev_secret_key
VITE_API_BASE_URL=/api/v1
```

**Production** (`.env.prod`):
```bash
# Stored in AWS Secrets Manager / Systems Manager Parameter Store
# Injected at runtime
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=...
```

### Passing Environment Variables

**Via docker-compose**:
```yaml
services:
  portfolio-service:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
```

**Via .env file**:
```bash
docker compose --env-file .env.prod up -d
```

**Via command line**:
```bash
docker compose -e DATABASE_URL=postgresql://... up -d
```

---

## Troubleshooting

### Common Issues

**Services Won't Start**:
```bash
# Check logs
docker compose logs portfolio-service

# Common causes:
# - Port already in use
# - Volume permission issues
# - Missing environment variables
# - Database connection failure
```

**Database Connection Failures**:
```bash
# Test PostgreSQL connection
docker compose exec portfolio-service \
  psql -h postgres -U postgres -d intelliwealth -c "SELECT 1;"

# Check if postgres is running
docker compose ps postgres

# View postgres logs
docker compose logs postgres
```

**Redis Connection Failures**:
```bash
# Test Redis connection
docker compose exec market-service redis-cli -h redis ping

# Check if redis is running
docker compose ps redis

# Monitor Redis operations
docker compose exec redis redis-cli MONITOR
```

**Nginx Routing Issues**:
```bash
# Check Nginx configuration
docker compose exec frontend nginx -t

# View Nginx access logs
docker compose logs frontend

# Test routing
curl -v http://localhost:3000/api/v1/health
```

**Permission Denied Errors**:
```bash
# Fix volume permissions
docker compose down
docker volume rm postgres_data
docker compose up -d

# Or set explicit permissions
sudo chown $USER:$USER ./portfolio-service/app
```

**Out of Disk Space**:
```bash
# Clean up unused images, containers, volumes
docker system prune -a --volumes

# Check disk usage
docker system df
```

### Health Check Verification

```bash
# Check if health endpoints are responding
curl http://localhost:3000/health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Expected response
{"status": "ok"}
```

---

## Best Practices

### Development

1. **Use volume mounts** for source code to enable hot reload
2. **Use .env.example** as template, don't commit real .env
3. **Keep Dockerfiles minimal** with multi-stage builds
4. **Use Alpine Linux** as base image (smaller, more secure)
5. **Tag images properly** (version numbers, timestamps)

### Production

1. **Never use `latest` tag** - use specific versions
2. **Build images in CI/CD pipeline** - not on EC2
3. **Push images to private registry** - not Docker Hub
4. **Scan images for vulnerabilities** before pushing
5. **Use read-only root filesystem** where possible
6. **Set resource limits** (CPU, memory)
7. **Enable restart policies** for fault tolerance
8. **Use environment variables** for secrets, not env files

### Security

1. **Don't run containers as root** - use non-root users
2. **Minimize attack surface** - use minimal base images
3. **Keep dependencies updated** - regular security patches
4. **Use secrets management** - AWS Secrets Manager
5. **Enable container logging** - CloudWatch integration
6. **Network policies** - Restrict inter-container communication

---

**Last Updated**: May 2026  
**Maintainer**: Infrastructure Team
