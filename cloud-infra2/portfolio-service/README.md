# Portfolio Service

**Service**: Portfolio & Customer Management  
**Technology**: FastAPI, SQLAlchemy, PostgreSQL, Alembic  
**Port**: 8000  
**Status**: Production-Ready

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Purpose & Responsibilities](#purpose--responsibilities)
3. [API Endpoints](#api-endpoints)
4. [Architecture](#architecture)
5. [Port Mappings](#port-mappings)
6. [Database Schema](#database-schema)
7. [Folder Structure](#folder-structure)
8. [Technology Stack](#technology-stack)
9. [Environment Variables](#environment-variables)
10. [Docker Setup](#docker-setup)
11. [Local Development](#local-development)
12. [Database Migrations](#database-migrations)
13. [Service Communication](#service-communication)
14. [Deployment](#deployment)
15. [Scalability Notes](#scalability-notes)

---

## Service Overview

The **Portfolio Service** is a FastAPI microservice that manages customer portfolios, assets, and allocations. It provides authentication, customer account management, and portfolio lifecycle operations with complete audit trails.

### Key Attributes

- **Framework**: FastAPI (async, fast, production-ready)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic for schema versioning
- **Authentication**: JWT token-based
- **Data Validation**: Pydantic models
- **API Documentation**: Auto-generated Swagger UI
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging with context

---

## Purpose & Responsibilities

### Primary Responsibilities

1. **Authentication & Authorization**
   - User login/logout
   - JWT token generation and validation
   - Password hashing and verification
   - Session management

2. **Customer Management**
   - Create customer accounts
   - Update customer profiles
   - Retrieve customer information
   - Customer data validation
   - Customer deactivation

3. **Portfolio Management**
   - Create portfolios (per customer)
   - Read portfolio details
   - Update portfolio allocations
   - Delete portfolios
   - Portfolio validation rules

4. **Asset Management**
   - Asset CRUD operations
   - Asset allocation tracking
   - Cost basis tracking
   - Asset classification
   - Rebalancing support

5. **Portfolio History & Audit**
   - Historical portfolio snapshots
   - Change tracking and audit trail
   - Performance calculations
   - Historical comparison

6. **Data Persistence**
   - Reliable database operations
   - ACID transaction support
   - Data consistency enforcement
   - Backup-ready schema

### Not a Responsibility

- ❌ Market data analysis (Market Service handles this)
- ❌ Risk calculations (Market Service handles this)
- ❌ Real-time market data (Market Service handles this)
- ❌ User interface (Frontend Service handles this)

---

## API Endpoints

### Authentication Endpoints

```
POST   /api/v1/auth/login
       Request: { "email": "user@example.com", "password": "***" }
       Response: { "token": "eyJ...", "expires_in": 3600 }
       Status: 200 OK or 401 Unauthorized

POST   /api/v1/auth/logout
       Headers: Authorization: Bearer <token>
       Response: { "status": "logged_out" }
       Status: 200 OK

POST   /api/v1/auth/refresh
       Headers: Authorization: Bearer <token>
       Response: { "token": "eyJ...", "expires_in": 3600 }
       Status: 200 OK or 401 Unauthorized
```

### Customer Endpoints

```
POST   /api/v1/customers
       Create new customer account
       Request: { "email": "user@example.com", "name": "John Doe", "password": "***" }
       Response: { "id": 1, "email": "...", "created_at": "..." }
       Status: 201 Created

GET    /api/v1/customers/{customer_id}
       Get customer details
       Headers: Authorization: Bearer <token>
       Response: { "id": 1, "email": "...", "name": "...", "created_at": "..." }
       Status: 200 OK or 404 Not Found

PUT    /api/v1/customers/{customer_id}
       Update customer profile
       Headers: Authorization: Bearer <token>
       Request: { "name": "Updated Name", "email": "newemail@example.com" }
       Response: { "id": 1, "email": "...", "name": "..." }
       Status: 200 OK

DELETE /api/v1/customers/{customer_id}
       Deactivate customer account
       Headers: Authorization: Bearer <token>
       Response: { "status": "deactivated" }
       Status: 204 No Content
```

### Portfolio Endpoints

```
GET    /api/v1/portfolio/{customer_id}
       List all portfolios for customer
       Headers: Authorization: Bearer <token>
       Response: [{ "id": 1, "name": "Main Portfolio", "assets": [...] }, ...]
       Status: 200 OK

POST   /api/v1/portfolio
       Create new portfolio
       Headers: Authorization: Bearer <token>
       Request: { "customer_id": 1, "name": "New Portfolio", "description": "..." }
       Response: { "id": 2, "customer_id": 1, "name": "New Portfolio" }
       Status: 201 Created

GET    /api/v1/portfolio/{portfolio_id}
       Get portfolio details
       Headers: Authorization: Bearer <token>
       Response: { "id": 1, "customer_id": 1, "name": "...", "total_value": 10000.00, "assets": [...] }
       Status: 200 OK

PUT    /api/v1/portfolio/{portfolio_id}
       Update portfolio (allocation, rebalance)
       Headers: Authorization: Bearer <token>
       Request: { "name": "Updated Name", "assets": [...] }
       Response: { "id": 1, "customer_id": 1, "assets": [...], "updated_at": "..." }
       Status: 200 OK

DELETE /api/v1/portfolio/{portfolio_id}
       Delete portfolio
       Headers: Authorization: Bearer <token>
       Response: { "status": "deleted" }
       Status: 204 No Content

GET    /api/v1/portfolio/{portfolio_id}/history
       Get portfolio history
       Headers: Authorization: Bearer <token>
       Query Params: ?limit=100&offset=0
       Response: [{ "date": "2024-01-01", "value": 10000.00, "assets": [...] }, ...]
       Status: 200 OK
```

### Health & Status

```
GET    /health
       Service health check
       Response: { "status": "ok", "version": "1.0.0" }
       Status: 200 OK
```

---

## Architecture

### Service Architecture

```
Client (Frontend)
    ↓ (HTTPS via ALB)
FastAPI Application
    ├── API Router Layer
    │   ├── /auth router
    │   ├── /customers router
    │   └── /portfolio router
    │
    ├── Authentication Layer
    │   ├── JWT token validation
    │   ├── Password hashing (bcrypt)
    │   └── Permission checks
    │
    ├── Service Layer
    │   ├── AuthService
    │   ├── CustomerService
    │   └── PortfolioService
    │
    ├── ORM Layer (SQLAlchemy)
    │   ├── Session management
    │   └── Query abstraction
    │
    └── Database Layer
        └── PostgreSQL
            ├── customers table
            ├── portfolios table
            ├── assets table
            ├── allocations table
            └── audit_logs table
```

### Request Processing Flow

```
1. HTTP Request arrives at ALB
2. ALB routes to Flask on port 8000
3. FastAPI middleware chain processes request
4. JWT token validation (if protected route)
5. Route handler executes business logic
6. SQLAlchemy ORM performs database operations
7. Response serialized via Pydantic model
8. HTTP Response sent back to client
9. ALB returns response to client
```

---

## Port Mappings

### Local Development

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Portfolio Service | 8000 | HTTP | API server |
| Swagger UI | 8000/docs | HTTP | Interactive API docs |
| ReDoc | 8000/redoc | HTTP | Alternative API docs |

### Docker Compose

**Port Mapping**:
```yaml
portfolio-service:
  ports:
    - "8000:8000"  # Host:Container
```

### Production (AWS)

| Component | Port | Source | Destination |
|-----------|------|--------|-------------|
| ALB (HTTPS) | 443 | Internet | ALB |
| ALB path routing | N/A | ALB | Portfolio Service on port 8000 |
| Portfolio Service | 8000 | ALB | EC2 instance |
| PostgreSQL | 5432 | Portfolio Service | RDS instance |

---

## Database Schema

### Tables

#### customers

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

**Purpose**: Store customer account information and authentication credentials  
**Indexes**: email (unique), is_active, created_at

#### portfolios

```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Purpose**: Store customer portfolios  
**Indexes**: customer_id, is_active, created_at

#### assets

```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    quantity DECIMAL(12,4) NOT NULL,
    cost_basis DECIMAL(15,2),
    current_value DECIMAL(15,2),
    asset_type VARCHAR(50),  -- stock, bond, etf, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Track individual assets within portfolios  
**Indexes**: portfolio_id, symbol, asset_type

#### allocations

```sql
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    allocation_date DATE NOT NULL,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    percentage DECIMAL(5,2) NOT NULL,  -- 0-100%
    target_value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Track historical allocation targets  
**Indexes**: portfolio_id, allocation_date

#### portfolio_history

```sql
CREATE TABLE portfolio_history (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    snapshot_date DATE NOT NULL,
    total_value DECIMAL(15,2),
    asset_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Store portfolio snapshots for historical analysis  
**Indexes**: portfolio_id, snapshot_date

#### audit_logs

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    action VARCHAR(100) NOT NULL,  -- CREATE, UPDATE, DELETE
    resource_type VARCHAR(50) NOT NULL,  -- customer, portfolio, asset
    resource_id INTEGER,
    changes TEXT,  -- JSON of changes
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Track all changes for compliance and debugging  
**Indexes**: customer_id, resource_type, created_at

---

## Folder Structure

```
portfolio-service/
├── app/
│   ├── __init__.py                Main application module
│   ├── main.py                    FastAPI app, startup/shutdown hooks
│   ├── config.py                  Configuration management
│   ├── database.py                Database connection and session factory
│   ├── seed.py                    Seed data for testing
│   │
│   ├── models/                    SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── customer.py            Customer model
│   │   ├── portfolio.py           Portfolio model
│   │   ├── asset.py               Asset model
│   │   └── audit_log.py           Audit log model
│   │
│   ├── schemas/                   Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── customer.py            Customer schemas
│   │   ├── portfolio.py           Portfolio schemas
│   │   ├── asset.py               Asset schemas
│   │   └── auth.py                Auth schemas
│   │
│   ├── routers/                   API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                Authentication routes
│   │   ├── customers.py           Customer routes
│   │   ├── portfolios.py          Portfolio routes
│   │   └── health.py              Health check route
│   │
│   └── services/                  Business logic layer
│       ├── __init__.py
│       ├── auth_service.py        Authentication logic
│       ├── customer_service.py    Customer logic
│       ├── portfolio_service.py   Portfolio logic
│       └── asset_service.py       Asset logic
│
├── alembic/                       Database migration tool
│   ├── env.py                     Migration environment config
│   ├── script.py.mako             Migration template
│   └── versions/
│       └── 001_initial_schema.py  Initial schema migration
│
├── Dockerfile                     Container definition
├── entrypoint.sh                  Container startup script
├── requirements.txt               Python dependencies
├── alembic.ini                    Alembic configuration
└── README.md                      This file
```

### Key Files

**`app/main.py`**: FastAPI application entry point
- App initialization
- Middleware configuration
- Route registration
- Startup/shutdown handlers

**`app/config.py`**: Configuration management
- Database connection strings
- JWT settings
- CORS configuration
- API settings

**`app/models/`**: SQLAlchemy ORM models
- Define database tables
- Relationships between models
- Indexes and constraints

**`app/schemas/`**: Pydantic models for validation
- Request validation
- Response serialization
- API documentation

**`app/routers/`**: API endpoints
- Route definitions
- Request/response handling
- Error handling

**`app/services/`**: Business logic
- Authentication logic
- Portfolio operations
- Data validation rules
- Cross-cutting concerns

**`alembic/versions/`**: Database migrations
- Schema changes
- Data migrations
- Reversible changes

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI | Async web framework |
| **Language** | Python 3.10+ | Application code |
| **ORM** | SQLAlchemy 2.x | Database abstraction |
| **Migrations** | Alembic | Schema versioning |
| **Database** | PostgreSQL 16 | Relational data |
| **Validation** | Pydantic | Request validation |
| **Auth** | PyJWT | JWT tokens |
| **Hashing** | bcrypt | Password hashing |
| **Testing** | pytest | Unit tests |
| **Container** | Docker | Application containerization |

---

## Environment Variables

### Local Development (`.env`)

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=intelliwealth
DATABASE_URL=postgresql://postgres:dev_password@postgres:5432/intelliwealth

# JWT Configuration
JWT_SECRET_KEY=your_secret_key_here_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Configuration
PORTFOLIO_SERVICE_PORT=8000
PORTFOLIO_SERVICE_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

### Production (`.env.prod`)

```bash
# Database Configuration (from AWS Secrets Manager in production)
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/intelliwealth

# JWT Configuration
JWT_SECRET_KEY=production_secret_key_with_high_entropy
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8

# API Configuration
PORTFOLIO_SERVICE_PORT=8000
PORTFOLIO_SERVICE_CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

---

## Docker Setup

### Build Docker Image

**Local Development**:
```bash
docker build -f portfolio-service/Dockerfile -t intelliwealth-portfolio:dev .
```

**Production**:
```bash
docker build -f portfolio-service/Dockerfile -t intelliwealth-portfolio:latest .
```

### Dockerfile Overview

**Multi-stage build pattern**:

**Stage 1: Builder**
- Python 3.11 slim image
- Install dependencies
- Compile Python packages

**Stage 2: Runtime**
- Python 3.11 slim image (smaller)
- Copy from builder
- Run application
- Minimal attack surface

### Image Details

- **Base**: python:3.11-slim (small, secure)
- **Size**: ~500 MB
- **Port**: 8000
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

2. **Check logs**:
   ```bash
   docker compose logs -f portfolio-service
   ```

3. **Access Swagger UI**:
   ```
   http://localhost:8000/docs
   ```

4. **Stop services**:
   ```bash
   docker compose down
   ```

### Development Workflow

**File Watching**: Docker volume mounts `portfolio-service/app/` so changes reload automatically.

**Database Access**:
```bash
docker compose exec postgres psql -U postgres -d intelliwealth
# Inside psql
\dt              # List tables
SELECT * FROM customers;  # Query data
\q               # Quit
```

### Testing

**Run tests in container**:
```bash
docker compose exec portfolio-service pytest
docker compose exec portfolio-service pytest app/tests/ -v
docker compose exec portfolio-service pytest app/tests/ -v --cov=app
```

### Debugging

**View service logs**:
```bash
docker compose logs portfolio-service
docker compose logs portfolio-service -f    # Follow
```

**Shell access**:
```bash
docker compose exec portfolio-service bash
```

**Database debugging**:
```bash
docker compose exec postgres psql -U postgres -d intelliwealth
```

---

## Database Migrations

### Alembic Setup

Alembic tracks schema changes and enables version control of the database.

**Current Schema Version**:
```bash
docker compose exec portfolio-service alembic current
```

**Migration History**:
```bash
docker compose exec portfolio-service alembic history
```

### Creating New Migrations

**Auto-detect model changes**:
```bash
docker compose exec portfolio-service alembic revision --autogenerate -m "describe_change"
```

**Manual migration**:
```bash
docker compose exec portfolio-service alembic revision -m "describe_change"
```

### Applying Migrations

**Apply latest migrations**:
```bash
docker compose exec portfolio-service alembic upgrade head
```

**Apply specific version**:
```bash
docker compose exec portfolio-service alembic upgrade 001
```

**Rollback one migration**:
```bash
docker compose exec portfolio-service alembic downgrade -1
```

**Rollback to specific version**:
```bash
docker compose exec portfolio-service alembic downgrade 000
```

### Migration Safety

- **Always review migrations** before applying
- **Test in staging environment** first
- **Backup production database** before migrations
- **Have rollback plan** ready

---

## Service Communication

### Frontend → Portfolio Service

**HTTP Method**: POST/GET/PUT/DELETE  
**Protocol**: HTTPS (via ALB in production)  
**Base URL**: `/api/v1` → portfolio-service:8000  
**Authentication**: Bearer Token (JWT)

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

### Portfolio Service → PostgreSQL

**Connection**: Direct TCP/IP connection  
**Port**: 5432  
**Authentication**: PostgreSQL username/password  
**Connection String**: `postgresql://user:pass@host:5432/database`

**Connection Pool** (SQLAlchemy):
- Pool Size: 20 connections
- Max Overflow: 40 connections
- Pool Timeout: 30 seconds
- Auto-recycle: 3600 seconds

### Inter-Service Communication (Optional)

**Portfolio Service → Market Service** (if needed):
- HTTP/HTTPS
- Port: 8001
- Service-to-service authentication (optional)

---

## Deployment

### Production Build

1. **Build Docker image**:
   ```bash
   docker build -f portfolio-service/Dockerfile \
     -t your_registry/intelliwealth-portfolio:v1.0.0 .
   ```

2. **Push to registry**:
   ```bash
   docker push your_registry/intelliwealth-portfolio:v1.0.0
   ```

3. **Deploy on EC2**:
   ```bash
   docker pull your_registry/intelliwealth-portfolio:v1.0.0
   docker compose -f docker-compose.prod.yml up -d
   ```

### Health Checks

**ALB Health Check**:
```
Path: /health
Port: 8000
Interval: 30 seconds
Healthy Threshold: 2 consecutive successes
Unhealthy Threshold: 3 consecutive failures
```

### Monitoring

**CloudWatch Metrics**:
- Container CPU usage
- Container memory usage
- Application errors (HTTP 5xx)
- Request latency
- Database connection pool

**Application Logs**:
- All requests logged
- Errors with stack traces
- Performance metrics
- Audit trail (audit_logs table)

---

## Scalability Notes

### Current Architecture

**Single Instance** (suitable for development):
- One EC2 instance running portfolio-service
- Shared PostgreSQL RDS instance

### Scaling for Production

**Horizontal Scaling**:

1. **Auto Scaling Group**
   - Minimum: 2 instances
   - Desired: 2-3 instances
   - Maximum: 5-10 instances
   - Scale-up trigger: CPU > 70%
   - Scale-down trigger: CPU < 40%

2. **Load Balancing**
   - ALB distributes requests
   - Health checks ensure only healthy instances receive traffic
   - Automatic replacement of failed instances

3. **Database**
   - RDS Multi-AZ for high availability
   - Read replicas for scaling read-heavy workloads
   - Connection pooling in application layer
   - Query optimization and indexing

4. **Performance**
   - API response caching (Redis)
   - Database query caching
   - Connection pooling
   - Asynchronous operations (FastAPI)

### Future Improvements

- [ ] Database read replicas
- [ ] Redis caching layer for frequently accessed data
- [ ] API rate limiting and throttling
- [ ] Request queuing for peak load
- [ ] Distributed tracing (AWS X-Ray)
- [ ] Database query optimization
- [ ] Async background jobs (Celery)

---

**Last Updated**: May 2026  
**Maintainer**: Backend Infrastructure Team
