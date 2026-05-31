# API Documentation

## Base URLs

```text
Portfolio Service: http://localhost:8000
Market Service:    http://localhost:8001
Frontend proxy:    http://localhost:3000/api/v1
```

## Portfolio Service

Swagger:

```text
http://localhost:8000/docs
```

Routes:

```text
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/customers
GET  /api/v1/customers/{id}
PUT  /api/v1/customers/{id}
POST /api/v1/portfolio
GET  /api/v1/portfolio
GET  /api/v1/portfolio/{id}
POST /api/v1/portfolio/add-asset
PUT  /api/v1/portfolio/update-asset/{id}
DELETE /api/v1/portfolio/remove-asset/{id}
GET  /api/v1/portfolio/allocation/{id}
GET  /api/v1/portfolio/history/{id}
POST /api/v1/portfolio/history/{id}/snapshot
```

## Market Service

Swagger:

```text
http://localhost:8001/docs
```

Routes:

```text
GET /api/v1/market/assets
GET /api/v1/market/trends
GET /api/v1/market/volatility
GET /api/v1/market/risk
GET /api/v1/market/sector-analysis
```

## Health

Both backend services expose:

```text
GET /health
GET /readiness
GET /liveness
```
