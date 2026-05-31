# API And Data Flow

## Frontend API Base

```text
VITE_API_BASE_URL=/api/v1
```

## Local Routing

In local Docker Compose, frontend Nginx uses `frontend/nginx.dev.conf`:

```text
/api/v1/auth       -> portfolio-service:8000
/api/v1/customers  -> portfolio-service:8000
/api/v1/portfolio  -> portfolio-service:8000
/api/v1/market     -> market-service:8001
```

## Production Routing

Production frontend Nginx does not proxy API calls. Route API paths before traffic reaches the frontend container.

## Data Stores

```text
portfolio-service -> PostgreSQL
market-service    -> PostgreSQL
market-service    -> Redis
```
