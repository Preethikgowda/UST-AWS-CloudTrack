# Service Communication Flow

**API Contracts and Inter-Service Communication**

---

## Table of Contents

1. [Overview](#overview)
2. [Frontend → Backend Communication](#frontend--backend-communication)
3. [Backend Service Communication](#backend-service-communication)
4. [Database Access Patterns](#database-access-patterns)
5. [Cache Integration](#cache-integration)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Monitoring Communication](#monitoring-communication)

---

## Overview

### Service Architecture

```
┌─────────────┐
│   Browser   │
│  (React)    │
└──────┬──────┘
       │ HTTPS
       │ JSON
       ▼
┌──────────────────────────────────────────┐
│  Application Load Balancer (ALB)         │
│  ├─ Path: / → Frontend (port 80)        │
│  ├─ Path: /api/v1/portfolio → Port 8000 │
│  └─ Path: /api/v1/market → Port 8001    │
└──┬────────────────────────────────────┬──┘
   │                                    │
   ▼                                    ▼
┌──────────────────┐          ┌──────────────────┐
│  Frontend Nginx  │          │  Backend Services │
│  (Port 80)       │          │                   │
│  - Static assets │          ├─ Portfolio (8000) │
│  - React SPA     │          └─ Market (8001)    │
│  - Routing       │
└──────────────────┘          ┌──────────────────┐
                              │  PostgreSQL RDS  │
                              │  Redis Cache     │
                              └──────────────────┘
```

---

## Frontend → Backend Communication

### Authentication Flow

```
1. User Submits Login Form
   ┌─────────────────────────────────┐
   │ POST /api/v1/auth/login         │
   │ Content-Type: application/json  │
   │ {                               │
   │   "email": "user@example.com",  │
   │   "password": "password123"     │
   │ }                               │
   └────────────┬────────────────────┘
                │
   2. Portfolio Service Validates
                │
                ▼
   ┌──────────────────────────────────┐
   │ Check email/password in DB       │
   │ Generate JWT token (exp: 24h)    │
   └────────────┬─────────────────────┘
                │
   3. Return Token to Frontend
                │
                ▼
   ┌──────────────────────────────────┐
   │ 200 OK                           │
   │ {                                │
   │   "access_token": "eyJhb...",   │
   │   "token_type": "bearer",        │
   │   "expires_in": 86400            │
   │ }                                │
   └──────────────────────────────────┘

4. Frontend Stores Token
   localStorage.setItem('auth_token', token)

5. Subsequent Requests Include Token
   GET /api/v1/portfolio/list
   Authorization: Bearer eyJhb...
```

### API Request/Response Pattern

**Request Headers**:
```http
GET /api/v1/portfolio/list
Host: yourdomain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json
User-Agent: Mozilla/5.0...
```

**Response Headers**:
```http
200 OK
Content-Type: application/json
Content-Length: 1234
Cache-Control: no-cache
Set-Cookie: session=abc123; Path=/; HttpOnly; Secure
```

**Response Body**:
```json
{
  "status": "success",
  "data": {
    "portfolios": [
      {
        "id": "port-123",
        "name": "Retirement Portfolio",
        "total_value": 250000,
        "cash": 15000,
        "assets": [...]
      }
    ]
  },
  "meta": {
    "timestamp": "2024-05-28T10:30:00Z",
    "version": "1.0.0"
  }
}
```

---

## Backend Service Communication

### Portfolio Service API

**Authentication Endpoints**:

```
POST /auth/login
  Request: { email, password }
  Response: { access_token, token_type, expires_in }
  Status: 200 | 401

POST /auth/logout
  Request: { token }
  Response: { message: "Logged out" }
  Status: 200 | 401

POST /auth/refresh
  Request: { refresh_token }
  Response: { access_token, expires_in }
  Status: 200 | 401
```

**Customer Endpoints**:

```
GET /customers/{customer_id}
  Response: Customer object
  Status: 200 | 404 | 401

PUT /customers/{customer_id}
  Request: Customer fields to update
  Response: Updated customer object
  Status: 200 | 400 | 401

DELETE /customers/{customer_id}
  Response: { message: "Customer deleted" }
  Status: 204 | 404 | 401
```

**Portfolio Endpoints**:

```
GET /portfolio/list
  Response: [Portfolio objects]
  Status: 200 | 401

POST /portfolio/create
  Request: { name, description, initial_investment }
  Response: { id, name, created_at }
  Status: 201 | 400 | 401

GET /portfolio/{portfolio_id}
  Response: Portfolio object with assets
  Status: 200 | 404 | 401

PUT /portfolio/{portfolio_id}
  Request: { name, description, target_allocation }
  Response: Updated portfolio
  Status: 200 | 400 | 401

DELETE /portfolio/{portfolio_id}
  Response: { message: "Portfolio deleted" }
  Status: 204 | 404 | 401
```

**Asset Endpoints**:

```
POST /portfolio/{portfolio_id}/assets
  Request: { symbol, quantity, purchase_price }
  Response: { asset_id, symbol, quantity }
  Status: 201 | 400 | 401

PUT /portfolio/{portfolio_id}/assets/{asset_id}
  Request: { quantity, purchase_price }
  Response: Updated asset
  Status: 200 | 400 | 401

DELETE /portfolio/{portfolio_id}/assets/{asset_id}
  Response: { message: "Asset deleted" }
  Status: 204 | 404 | 401
```

### Market Service API

**Market Data Endpoints**:

```
GET /market/quote/{symbol}
  Response: { symbol, price, change, volume }
  Status: 200 | 404
  Cache: Redis (5 minutes TTL)

GET /market/history/{symbol}?period=1d|1w|1m|1y
  Response: [{ timestamp, open, high, low, close, volume }]
  Status: 200 | 404
  Cache: Redis (1 hour TTL)

GET /market/search?query=apple
  Response: [{ symbol, name, type }]
  Status: 200
  Cache: Redis (1 day TTL)
```

**Risk Metrics Endpoints**:

```
GET /risk/{portfolio_id}
  Response: {
    volatility: 0.15,
    sharpe_ratio: 1.2,
    beta: 0.85,
    var_95: 5000,
    cvar_95: 6500
  }
  Status: 200 | 404
  Cache: Redis (30 minutes TTL)

GET /risk/{portfolio_id}/allocation
  Response: {
    equities: 60,
    bonds: 25,
    cash: 15
  }
  Status: 200 | 404
  Cache: Redis (30 minutes TTL)
```

**Sector Analysis Endpoints**:

```
GET /sectors
  Response: [{ sector, weight, performance }]
  Status: 200
  Cache: Redis (1 hour TTL)

GET /sectors/{sector_name}
  Response: { sector, stocks: [...], performance }
  Status: 200 | 404
  Cache: Redis (1 hour TTL)
```

---

## Database Access Patterns

### Portfolio Service Database Schema

```
┌─────────────────────┐
│    customers        │
├─────────────────────┤
│ id (PK)             │
│ email (UNIQUE)      │
│ password_hash       │
│ first_name          │
│ last_name           │
│ created_at          │
│ updated_at          │
└────────┬────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────┐
│   portfolios        │
├─────────────────────┤
│ id (PK)             │
│ customer_id (FK)    │
│ name                │
│ description         │
│ initial_value       │
│ current_value       │
│ created_at          │
│ updated_at          │
└────────┬────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────┐
│     assets          │
├─────────────────────┤
│ id (PK)             │
│ portfolio_id (FK)   │
│ symbol              │
│ quantity            │
│ purchase_price      │
│ current_price       │
│ created_at          │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐
│  portfolio_history  │
├─────────────────────┤
│ id (PK)             │
│ portfolio_id (FK)   │
│ snapshot_date       │
│ total_value         │
│ cash_balance        │
│ created_at          │
└─────────────────────┘
```

### Market Service Database Schema

```
┌──────────────────────┐
│   market_data        │
├──────────────────────┤
│ id (PK)              │
│ symbol               │
│ current_price        │
│ previous_close       │
│ day_high             │
│ day_low              │
│ volume               │
│ market_cap           │
│ pe_ratio             │
│ last_updated         │
└──────┬───────────────┘
       │
       │ 1:N
       │
       ▼
┌──────────────────────┐
│   price_history      │
├──────────────────────┤
│ id (PK)              │
│ symbol (FK)          │
│ timestamp            │
│ open                 │
│ high                 │
│ low                  │
│ close                │
│ volume               │
└──────────────────────┘

┌──────────────────────┐
│   risk_metrics       │
├──────────────────────┤
│ id (PK)              │
│ symbol               │
│ period               │
│ volatility           │
│ sharpe_ratio         │
│ beta                 │
│ var_95               │
│ last_calculated      │
└──────────────────────┘

┌──────────────────────┐
│   sector_data        │
├──────────────────────┤
│ id (PK)              │
│ sector_name          │
│ performance          │
│ stocks_in_sector     │
│ market_cap           │
│ last_updated         │
└──────────────────────┘
```

---

## Cache Integration

### Redis Cache Strategy

**Cache Keys Pattern**:

```
quote:{symbol}
  Type: String
  Value: JSON quote data
  TTL: 5 minutes
  Updated: On market data change

history:{symbol}:{period}
  Type: String
  Value: JSON price history array
  TTL: 1 hour
  Updated: Daily at market close

risk:{portfolio_id}
  Type: String
  Value: JSON risk metrics
  TTL: 30 minutes
  Updated: On portfolio change

sector:{sector_name}
  Type: String
  Value: JSON sector data
  TTL: 1 hour
  Updated: Hourly

session:{session_id}
  Type: String
  Value: User session data
  TTL: 24 hours
  Updated: On user action
```

**Cache Warming**:

```python
# On application startup
def warm_cache():
    # Pre-populate popular stocks
    popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    for symbol in popular_symbols:
        cache.set(f'quote:{symbol}', fetch_quote(symbol), ttl=300)
    
    # Pre-populate sectors
    for sector in SECTORS:
        cache.set(f'sector:{sector}', fetch_sector_data(sector), ttl=3600)

# Scheduled cache refresh
@scheduler.scheduled_job('interval', minutes=5)
def refresh_popular_quotes():
    for symbol in get_popular_symbols():
        quote = fetch_quote(symbol)
        cache.set(f'quote:{symbol}', quote, ttl=300)
```

**Cache Invalidation**:

```python
# When portfolio updated
def update_portfolio(portfolio_id, changes):
    # Update database
    portfolio = db.update_portfolio(portfolio_id, changes)
    
    # Invalidate cache
    cache.delete(f'risk:{portfolio_id}')
    cache.delete(f'allocation:{portfolio_id}')
    
    # Invalidate related caches
    for asset in portfolio.assets:
        cache.delete(f'quote:{asset.symbol}')

# When market data updated
def update_market_quote(symbol, quote_data):
    # Update database
    db.update_quote(symbol, quote_data)
    
    # Update cache
    cache.set(f'quote:{symbol}', quote_data, ttl=300)
    
    # Invalidate dependent caches
    cache.delete(f'history:{symbol}:*')  # Invalidate all time periods
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Validation failed",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ],
  "meta": {
    "timestamp": "2024-05-28T10:30:00Z",
    "request_id": "req-12345"
  }
}
```

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | User not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |
| 502 | Bad Gateway | Service unavailable |
| 503 | Service Unavailable | Temporary outage |

### Common Error Codes

```
INVALID_CREDENTIALS
  → Wrong email/password
  → HTTP 401

TOKEN_EXPIRED
  → JWT token past expiration
  → HTTP 401

INSUFFICIENT_FUNDS
  → Not enough cash for transaction
  → HTTP 400

PORTFOLIO_NOT_FOUND
  → Portfolio ID doesn't exist
  → HTTP 404

MARKET_DATA_UNAVAILABLE
  → External API down
  → HTTP 503

RATE_LIMIT_EXCEEDED
  → Too many requests
  → HTTP 429
```

---

## Rate Limiting

### Rate Limit Strategy

**By Endpoint**:

```
POST /auth/login: 5 requests/minute per IP
GET /market/quote: 100 requests/minute per user
POST /portfolio/create: 10 requests/hour per user
GET /portfolio/list: 1000 requests/hour per user
```

**Rate Limit Headers**:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1685347200

When limit exceeded:
HTTP 429 Too Many Requests
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1685347260
Retry-After: 60
```

**Implementation**:

```python
from functools import wraps
from redis import Redis

redis = Redis(host='redis', port=6379)

def rate_limit(max_requests, window_seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_current_user_id()
            key = f'ratelimit:{func.__name__}:{user_id}'
            
            # Get current count
            current = redis.get(key) or 0
            
            if int(current) >= max_requests:
                raise RateLimitExceeded()
            
            # Increment counter
            redis.incr(key)
            redis.expire(key, window_seconds)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.post('/auth/login')
@rate_limit(max_requests=5, window_seconds=60)
def login(credentials):
    # Login logic
    pass
```

---

## Monitoring Communication

### Request Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration:.3f}s"
    )
    
    return response
```

**Log Format**:

```
2024-05-28 10:30:45.123 | GET /api/v1/portfolio/list | status=200 | duration=0.245s | user_id=user-123 | request_id=req-abc123
2024-05-28 10:30:46.456 | POST /api/v1/market/quote/AAPL | status=200 | duration=0.098s | user_id=user-123 | request_id=req-def456
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram

request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

# Usage
@app.get('/portfolio/list')
@request_duration.labels(method='GET', endpoint='/portfolio/list').time()
def list_portfolios():
    request_count.labels(
        method='GET',
        endpoint='/portfolio/list',
        status=200
    ).inc()
    # Logic here
```

### Health Check Endpoints

```
GET /health
  Response: { status: "healthy", checks: {...} }
  Status: 200 | 503

GET /health/ready
  Response: { ready: true, dependencies: {...} }
  Status: 200 | 503

GET /metrics
  Response: Prometheus metrics
  Status: 200
```

---

**Last Updated**: May 2026  
**Owner**: API & Integration Team
