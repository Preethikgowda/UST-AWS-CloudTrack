# Service Communication

## Local Docker Flow

```text
Browser
  -> frontend:3000
  -> nginx.dev.conf proxies /api/v1/* by path
  -> portfolio-service:8000
  -> market-service:8001
```

## Service Routes

```text
/api/v1/auth       -> portfolio-service
/api/v1/customers  -> portfolio-service
/api/v1/portfolio  -> portfolio-service
/api/v1/market     -> market-service
```

## Data Flow

```text
portfolio-service -> PostgreSQL
market-service    -> PostgreSQL
market-service    -> Redis
```

## Production Shape

The production frontend container serves static files only. It does not proxy APIs.

In an EC2 deployment, route `/api/v1/*` traffic before it reaches the frontend container, for example with a load balancer or reverse proxy.
