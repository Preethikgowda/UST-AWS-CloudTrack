# Market Service

**Service**: Market Intelligence & Risk Analysis  
**Technology**: FastAPI, SQLAlchemy, PostgreSQL, Redis, Alembic  
**Port**: 8001  
**Status**: Production-Ready

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Purpose & Responsibilities](#purpose--responsibilities)
3. [API Endpoints](#api-endpoints)
4. [Architecture](#architecture)
5. [Port Mappings](#port-mappings)
6. [Database Schema](#database-schema)
7. [Caching Strategy](#caching-strategy)
8. [Folder Structure](#folder-structure)
9. [Technology Stack](#technology-stack)
10. [Environment Variables](#environment-variables)
11. [Docker Setup](#docker-setup)
12. [Local Development](#local-development)
13. [Caching & Redis](#caching--redis)
14. [Service Communication](#service-communication)
15. [Deployment](#deployment)
16. [Scalability Notes](#scalability-notes)

---

## Service Overview

The **Market Service** provides real-time market intelligence, risk analysis, and sector data for portfolio analysis. It aggregates market data, calculates risk metrics, and caches frequently accessed data using Redis for high performance.

### Key Attributes

- **Framework**: FastAPI (async, high performance)
- **Database**: PostgreSQL for persistent market data
- **Cache**: Redis for real-time data caching
- **Data Aggregation**: Market data from multiple sources
- **Risk Analysis**: Quantitative risk calculations
- **Performance**: Sub-second response times via caching
- **Scalability**: Horizontal scaling with shared Redis cache

---

## Purpose & Responsibilities

### Primary Responsibilities

1. **Market Data Management**
   - Fetch and store market prices
   - Historical price tracking
   - Market data aggregation
   - Data freshness validation
   - Multi-source data reconciliation

2. **Risk Metrics Calculation**
   - Portfolio volatility analysis
   - Value at Risk (VaR) calculations
   - Sharpe ratio calculations
   - Maximum drawdown analysis
   - Beta and correlation analysis

3. **Sector Analysis**
   - Sector classification
   - Sector performance tracking
   - Portfolio sector distribution
   - Sector allocation recommendations

4. **Caching & Performance**
   - Redis caching for frequently accessed data
   - Cache invalidation strategy
   - TTL-based expiration
   - Cache hit rate optimization

5. **Data Analytics**
   - Price trends and patterns
   - Volatility measures
   - Performance attribution
   - Correlation analysis

### Not a Responsibility

- ❌ Portfolio management (Portfolio Service handles this)
- ❌ Customer authentication (Portfolio Service handles this)
- ❌ User interface (Frontend Service handles this)
- ❌ Real-time market data feeds (external providers handle this)

---

## API Endpoints

### Market Data Endpoints

```
GET    /api/v1/market/data/{symbol}
       Get current market data for a security
       Headers: Authorization: Bearer <token>
       Query Params: ?include_history=false&days=30
       Response: {
         "symbol": "AAPL",
         "current_price": 150.25,
         "open": 149.00,
         "high": 151.50,
         "low": 149.00,
         "volume": 45000000,
         "timestamp": "2024-01-15T16:00:00Z",
         "historical_prices": [...]
       }
       Status: 200 OK

GET    /api/v1/market/data
       List market data for multiple symbols
       Headers: Authorization: Bearer <token>
       Query Params: ?symbols=AAPL,MSFT,GOOGL&days=1
       Response: [
         { "symbol": "AAPL", "current_price": 150.25, ... },
         { "symbol": "MSFT", "current_price": 380.50, ... },
         ...
       ]
       Status: 200 OK
```

### Risk Metrics Endpoints

```
GET    /api/v1/market/risk/{portfolio_id}
       Get risk metrics for a portfolio
       Headers: Authorization: Bearer <token>
       Response: {
         "portfolio_id": 1,
         "volatility": 0.18,
         "sharpe_ratio": 1.25,
         "max_drawdown": -0.15,
         "var_95": -0.045,
         "beta": 1.05,
         "correlation_with_market": 0.92,
         "calculated_at": "2024-01-15T16:00:00Z"
       }
       Status: 200 OK

POST   /api/v1/market/risk/calculate
       Calculate risk metrics for a hypothetical portfolio
       Headers: Authorization: Bearer <token>
       Request: {
         "assets": [
           { "symbol": "AAPL", "weight": 0.40 },
           { "symbol": "MSFT", "weight": 0.30 },
           { "symbol": "GOOGL", "weight": 0.30 }
         ],
         "time_horizon_days": 250
       }
       Response: {
         "portfolio_volatility": 0.16,
         "sharpe_ratio": 1.35,
         "expected_return": 0.08,
         ...
       }
       Status: 200 OK
```

### Sector Endpoints

```
GET    /api/v1/market/sectors
       List all sectors and performance
       Headers: Authorization: Bearer <token>
       Response: [
         {
           "sector": "Technology",
           "symbol": "XLK",
           "ytd_return": 0.25,
           "performance_1y": 0.15,
           "volatility": 0.18
         },
         ...
       ]
       Status: 200 OK

GET    /api/v1/market/portfolio/{portfolio_id}/sectors
       Get sector allocation for portfolio
       Headers: Authorization: Bearer <token>
       Response: {
         "portfolio_id": 1,
         "sectors": [
           { "sector": "Technology", "percentage": 45.0 },
           { "sector": "Healthcare", "percentage": 30.0 },
           { "sector": "Financials", "percentage": 25.0 }
         ]
       }
       Status: 200 OK
```

### Analytics Endpoints

```
GET    /api/v1/market/analytics
       Get market-wide analytics
       Headers: Authorization: Bearer <token>
       Response: {
         "market_index": "SPY",
         "current_level": 450.25,
         "ytd_return": 0.18,
         "volatility": 0.15,
         "correlation_matrix": {...},
         "sector_performance": [...]
       }
       Status: 200 OK
```

### Health Check

```
GET    /health
       Service health and dependencies
       Response: {
         "status": "ok",
         "version": "1.0.0",
         "redis_connected": true,
         "database_connected": true
       }
       Status: 200 OK
```

---

## Architecture

### Service Architecture

```
Client (Frontend)
    ↓ (HTTPS via ALB)
FastAPI Application (Market Service)
    ├── API Router Layer
    │   ├── /market/data router
    │   ├── /market/risk router
    │   ├── /market/sectors router
    │   └── /market/analytics router
    │
    ├── Caching Layer (Redis)
    │   ├── Check cache for data
    │   ├── Cache hits for market data
    │   ├── Cache misses fetch from DB
    │   └── Cache invalidation
    │
    ├── Service Layer
    │   ├── MarketDataService
    │   ├── RiskService
    │   ├── SectorService
    │   └── AnalyticsService
    │
    ├── ORM Layer (SQLAlchemy)
    │   ├── Session management
    │   └── Query abstraction
    │
    ├── Data Aggregation
    │   └── External market data sources
    │
    └── Database Layer
        ├── PostgreSQL
        ├── market_data table
        ├── risk_metrics table
        ├── sector_data table
        └── price_history table
```

### Caching Strategy

```
Request for Market Data
    ↓
Check Redis Cache
    ├─ Cache Hit
    │   └─ Return cached data + 200 response
    │
    └─ Cache Miss
        ├─ Query PostgreSQL
        ├─ Calculate metrics if needed
        ├─ Store in Redis (TTL: 5-60 min depending on data)
        └─ Return data + 200 response
```

---

## Port Mappings

### Local Development

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Market Service | 8001 | HTTP | API server |
| Swagger UI | 8001/docs | HTTP | Interactive API docs |
| Redis | 6379 | TCP | Cache server |

### Docker Compose

**Port Mapping**:
```yaml
market-service:
  ports:
    - "8001:8001"  # Host:Container
redis:
  ports:
    - "6379:6379"  # Host:Container (development only)
```

### Production (AWS)

| Component | Port | Source | Destination |
|-----------|------|--------|-------------|
| ALB (HTTPS) | 443 | Internet | ALB |
| ALB path routing | N/A | ALB | Market Service on port 8001 |
| Market Service | 8001 | ALB | EC2 instance |
| PostgreSQL | 5432 | Market Service | RDS instance |
| Redis | 6379 | Market Service | ElastiCache instance |

---

## Database Schema

### Tables

#### market_data

```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    current_price DECIMAL(15,2) NOT NULL,
    open_price DECIMAL(15,2),
    high_price DECIMAL(15,2),
    low_price DECIMAL(15,2),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(10,2),
    dividend_yield DECIMAL(10,4),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE
);
```

**Purpose**: Store current market data for securities  
**Indexes**: symbol (unique), last_updated, is_active

#### price_history

```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(15,2),
    close_price DECIMAL(15,2),
    high_price DECIMAL(15,2),
    low_price DECIMAL(15,2),
    volume BIGINT,
    adjusted_close DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);
```

**Purpose**: Historical price data for technical analysis  
**Indexes**: symbol, date, created_at

#### risk_metrics

```sql
CREATE TABLE risk_metrics (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    calculation_date DATE NOT NULL,
    volatility DECIMAL(10,4),
    sharpe_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    value_at_risk_95 DECIMAL(10,4),
    beta DECIMAL(10,4),
    correlation_matrix TEXT,  -- JSON
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, calculation_date)
);
```

**Purpose**: Risk calculations and metrics  
**Indexes**: portfolio_id, calculation_date, calculated_at

#### sector_data

```sql
CREATE TABLE sector_data (
    id SERIAL PRIMARY KEY,
    sector_name VARCHAR(100) NOT NULL UNIQUE,
    sector_symbol VARCHAR(10),  -- e.g., XLK, XLV
    ytd_return DECIMAL(10,4),
    performance_1y DECIMAL(10,4),
    performance_5y DECIMAL(10,4),
    volatility DECIMAL(10,4),
    dividend_yield DECIMAL(10,4),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Sector-level performance and metrics  
**Indexes**: sector_name, last_updated

#### sector_allocations

```sql
CREATE TABLE sector_allocations (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    sector_name VARCHAR(100) NOT NULL,
    percentage DECIMAL(5,2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Portfolio sector distribution  
**Indexes**: portfolio_id, calculated_at

---

## Caching Strategy

### Redis Cache Architecture

**Cache Key Patterns**:

```
market:data:{symbol}              # Market data for symbol (TTL: 5 min)
market:data:all                   # All market data (TTL: 10 min)
market:price:history:{symbol}     # Historical prices (TTL: 1 hour)
market:risk:{portfolio_id}        # Risk metrics (TTL: 30 min)
market:sectors                    # Sector data (TTL: 60 min)
market:analytics                  # Market analytics (TTL: 15 min)
```

### Cache Invalidation

**Time-Based (TTL)**:
- Market data: 5 minutes (prices change frequently)
- Risk metrics: 30 minutes (calculated less frequently)
- Sector data: 60 minutes (stable, changes infrequently)

**Event-Based**:
- Portfolio updated → Invalidate risk metrics for that portfolio
- Market data refreshed → Invalidate related cache entries

**Manual**:
```bash
# Clear specific cache
REDIS-CLI DEL market:data:AAPL

# Clear all market cache
REDIS-CLI DEL market:*

# Flush entire cache (development only)
REDIS-CLI FLUSHDB
```

### Cache Performance

**Expected Performance**:
- Cache Hit: ~1-5ms response time
- Cache Miss: ~100-500ms response time (database query)
- Hit Rate Target: 80%+ for market data

**Monitoring**:
- Cache hit/miss rates
- Average response time
- Cache memory usage

---

## Folder Structure

```
market-service/
├── app/
│   ├── __init__.py                Main application module
│   ├── main.py                    FastAPI app, startup/shutdown hooks
│   ├── config.py                  Configuration management
│   ├── database.py                Database connection
│   ├── redis_client.py            Redis connection and cache methods
│   ├── seed.py                    Seed data for testing
│   │
│   ├── models/                    SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── market_data.py         Market data model
│   │   ├── price_history.py       Historical prices model
│   │   ├── risk_metrics.py        Risk metrics model
│   │   ├── sector_data.py         Sector data model
│   │   └── sector_allocation.py   Portfolio sector allocation
│   │
│   ├── schemas/                   Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── market_data.py         Market data schemas
│   │   ├── risk_metrics.py        Risk metric schemas
│   │   └── sector.py              Sector schemas
│   │
│   ├── routers/                   API route handlers
│   │   ├── __init__.py
│   │   ├── market.py              Market data routes
│   │   ├── risk.py                Risk metrics routes
│   │   ├── sectors.py             Sector routes
│   │   ├── analytics.py           Analytics routes
│   │   └── health.py              Health check route
│   │
│   └── services/                  Business logic layer
│       ├── __init__.py
│       ├── market_service.py      Market data logic
│       ├── risk_engine.py         Risk calculation engine
│       ├── sector_service.py      Sector logic
│       ├── cache_service.py       Cache management
│       └── analytics_service.py   Analytics logic
│
├── alembic/                       Database migration tool
│   ├── env.py                     Migration environment config
│   └── versions/
│       └── 001_market_schema.py   Initial schema migration
│
├── Dockerfile                     Container definition
├── entrypoint.sh                  Container startup script
├── requirements.txt               Python dependencies
├── alembic.ini                    Alembic configuration
└── README.md                      This file
```

### Key Files

**`app/redis_client.py`**: Redis connection and caching
- Connection pooling
- Cache get/set operations
- TTL management
- Cache invalidation

**`app/services/risk_engine.py`**: Quantitative risk calculations
- Volatility calculations
- Sharpe ratio computation
- VaR calculations
- Correlation analysis

**`app/services/cache_service.py`**: Cache management
- Cache warming
- Cache invalidation logic
- Key generation
- TTL strategies

**`app/routers/market.py`**: Market data API routes
- Symbol lookup
- Price history retrieval
- Market data streaming (optional WebSocket)

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI | Async web framework |
| **Language** | Python 3.10+ | Application code |
| **ORM** | SQLAlchemy 2.x | Database abstraction |
| **Database** | PostgreSQL 16 | Market data storage |
| **Cache** | Redis 7 | High-speed caching |
| **Validation** | Pydantic | Request validation |
| **Auth** | PyJWT | JWT tokens |
| **Math** | NumPy, SciPy | Risk calculations |
| **Testing** | pytest | Unit tests |
| **Container** | Docker | Containerization |

---

## Environment Variables

### Local Development (`.env`)

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=intelliwealth
DATABASE_URL=postgresql://postgres:dev_password@postgres:5432/intelliwealth

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0

# Service Configuration
MARKET_SERVICE_PORT=8001
MARKET_SERVICE_CORS_ORIGINS=http://localhost:3000,http://localhost:8001

# Market Data Configuration
MARKET_DATA_UPDATE_INTERVAL_MINUTES=5
RISK_CALC_INTERVAL_HOURS=1

# Logging
LOG_LEVEL=INFO
```

### Production (`.env.prod`)

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/intelliwealth

# Redis Configuration (ElastiCache)
REDIS_HOST=elasticache-endpoint.amazonaws.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_AUTH_TOKEN=your_redis_auth_token

# Service Configuration
MARKET_SERVICE_PORT=8001
MARKET_SERVICE_CORS_ORIGINS=https://yourdomain.com

# Market Data Configuration
MARKET_DATA_UPDATE_INTERVAL_MINUTES=5
RISK_CALC_INTERVAL_HOURS=1

# Logging
LOG_LEVEL=INFO
```

---

## Docker Setup

### Build Docker Image

**Local Development**:
```bash
docker build -f market-service/Dockerfile -t intelliwealth-market:dev .
```

**Production**:
```bash
docker build -f market-service/Dockerfile -t intelliwealth-market:latest .
```

### Dockerfile Overview

**Multi-stage build**:

**Stage 1: Builder**
- Python 3.11 slim image
- Install dependencies including NumPy, SciPy
- Compile packages

**Stage 2: Runtime**
- Python 3.11 slim image
- Copy from builder
- Run with gunicorn/uvicorn

### Image Details

- **Base**: python:3.11-slim
- **Size**: ~500 MB (includes scientific libraries)
- **Port**: 8001
- **Entrypoint**: `entrypoint.sh`

---

## Local Development

### Prerequisites

- Docker Desktop 4.10+
- Docker Compose v2
- Git

**No local Python installation required.**

### Quick Start

1. **Start the full stack**:
   ```bash
   docker compose up --build -d
   ```

2. **Check Market Service logs**:
   ```bash
   docker compose logs -f market-service
   ```

3. **Access Swagger UI**:
   ```
   http://localhost:8001/docs
   ```

4. **Monitor Redis**:
   ```bash
   docker compose exec redis redis-cli
   # Inside redis-cli
   > INFO
   > KEYS market:*
   > GET market:data:AAPL
   > MONITOR    # Watch all operations
   ```

### Development Workflow

**File Watching**: Docker volume mounts `market-service/app/` for hot reload.

**Database Access**:
```bash
docker compose exec postgres psql -U postgres -d intelliwealth
\dt                    # List tables
SELECT * FROM market_data;
```

**Redis Access**:
```bash
docker compose exec redis redis-cli
> DBSIZE
> KEYS *
> INFO stats
```

---

## Caching & Redis

### Redis Client Usage

**Basic Operations**:
```python
from app.redis_client import cache

# Get data
data = cache.get("market:data:AAPL")

# Set data with TTL
cache.set("market:data:AAPL", data, ttl=300)  # 5 minutes

# Delete data
cache.delete("market:data:AAPL")

# Delete pattern
cache.delete_pattern("market:data:*")
```

### Cache Warming

**Pre-load cache on startup**:
```bash
# Manual cache warming
docker compose exec market-service python -m app.cache_warmer

# Automatic on service start via entrypoint.sh
```

### Cache Monitoring

**Redis Memory Usage**:
```bash
docker compose exec redis redis-cli INFO memory
docker compose exec redis redis-cli INFO stats  # Hit rate
```

**Cache Hit Rate**:
```
hit_rate = hits / (hits + misses)
```

---

## Service Communication

### Frontend → Market Service

**HTTP Method**: GET/POST  
**Protocol**: HTTPS (via ALB in production)  
**Base URL**: `/api/v1` → market-service:8001  
**Authentication**: Bearer Token (JWT)

**Example Request**:
```bash
curl -X GET http://localhost:8001/api/v1/market/data/AAPL \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Market Service ↔ PostgreSQL

**Connection**: Direct TCP/IP  
**Port**: 5432  
**Connection Pool**: 20 connections, max overflow 40

### Market Service ↔ Redis

**Connection**: Direct TCP  
**Port**: 6379  
**Protocol**: RESP (Redis Serialization Protocol)
**Connection Pool**: 50 connections (default)

### Market Service ↔ Portfolio Service (if needed)

**Communication**: HTTP REST API  
**Purpose**: Retrieve portfolio composition for risk calculations  
**Port**: 8000

---

## Deployment

### Production Build

1. **Build Docker image**:
   ```bash
   docker build -f market-service/Dockerfile \
     -t your_registry/intelliwealth-market:v1.0.0 .
   ```

2. **Push to registry**:
   ```bash
   docker push your_registry/intelliwealth-market:v1.0.0
   ```

3. **Deploy on EC2**:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

### Health Checks

**ALB Health Check**:
```
Path: /health
Port: 8001
Interval: 30 seconds
Healthy Threshold: 2
Unhealthy Threshold: 3
```

**Expected Response**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "redis_connected": true,
  "database_connected": true
}
```

### Monitoring

**CloudWatch Metrics**:
- Container CPU/memory
- Redis memory usage
- Cache hit rate
- Request latency
- Error rate

**Application Logs**:
- Market data updates
- Risk calculations
- Cache operations
- API requests

---

## Scalability Notes

### Current Architecture

**Single Instance** (suitable for development):
- One EC2 instance
- Shared PostgreSQL RDS
- Shared Redis (single node)

### Scaling for Production

**Horizontal Scaling**:

1. **Application Instances**
   - Auto Scaling Group (min 2, desired 2, max 5)
   - Scale trigger: CPU > 70%
   - Health checks ensure availability

2. **Database**
   - RDS Multi-AZ
   - Read replicas for scaling reads
   - Connection pooling

3. **Redis Cluster**
   - ElastiCache Multi-AZ
   - Automatic failover
   - Sharding for large datasets
   - Persistence (RDB/AOF)

4. **Data Pipeline**
   - Background job for market data updates
   - Batch risk calculations
   - Async cache warming
   - Message queue (optional: SQS)

### Performance Optimization

- **Cache Warmup**: Pre-load frequently accessed data
- **Query Optimization**: Index critical columns
- **Batch Operations**: Aggregate requests
- **Data Compression**: Redis compression
- **Async Processing**: Background tasks for expensive calculations

### Future Improvements

- [ ] ElastiCache Redis Cluster for horizontal scaling
- [ ] Read replicas for market data queries
- [ ] Background job queue (Celery + RabbitMQ)
- [ ] Time-series database (InfluxDB) for price history
- [ ] Real-time WebSocket updates
- [ ] Machine learning models for risk prediction
- [ ] Distributed tracing (AWS X-Ray)
- [ ] Custom CloudWatch dashboards

---

**Last Updated**: May 2026  
**Maintainer**: Data & Analytics Team
