# Architecture

IntelliWealth is a Docker-based microservice application.

```text
Browser
  |
  v
Frontend container
React static build served by Nginx
  |
  | /api/v1/*
  v
Backend services
  |
  | SQL
  v
PostgreSQL

Market service also uses Redis as a cache.
```

## Services

### Frontend

```text
Path: frontend/
Port: 80 in container, 3000 locally
Tech: React, Vite, TypeScript, Nginx
```

Production Nginx serves static files only. It does not proxy backend APIs.

### Portfolio Service

```text
Path: portfolio-service/
Port: 8000
Tech: FastAPI, SQLAlchemy, Alembic, PostgreSQL
```

Routes:

```text
/api/v1/auth
/api/v1/customers
/api/v1/portfolio
```

### Market Service

```text
Path: market-service/
Port: 8001
Tech: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis
```

Routes:

```text
/api/v1/market
```

## Data Stores

### PostgreSQL

Local development uses a PostgreSQL container. Production injects a `DATABASE_URL` that can point to an external database.

### Redis

Redis is used by `market-service` as an ephemeral cache.

## Docker Compose Files

```text
docker-compose.yml
```

Local full stack: frontend, portfolio-service, market-service, postgres, redis.

```text
docker-compose.prod.yml
```

Backend production stack: portfolio-service, market-service, redis.

```text
docker-compose.frontend.prod.yml
```

Frontend production stack: frontend only.
