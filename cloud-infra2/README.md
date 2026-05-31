# IntelliWealth Cloud Infrastructure
## Enterprise Cloud Deployment Platform

**Version**: 1.0.0  
**Last Updated**: May 2026  
**Status**: Production-Ready Architecture

---

## ⚡ Quick Navigation

- **[Enterprise README](README_ENTERPRISE.md)** - Comprehensive cloud architecture & deployment guide
- **[Docker Setup](#docker-setup)** - Local development (below)
- **[Service Documentation](#services)** - Individual microservice guides
- **[AWS Deployment](docs/deployment-guide.md)** - Production AWS setup

---

IntelliWealth is an **enterprise-grade microservices platform** designed for **secure cloud deployment on AWS infrastructure**. The platform provides portfolio management, market intelligence, and asset allocation analysis with a focus on **production-ready cloud architecture**, **high availability**, and **secure networking**.

## Architecture Overview

For comprehensive architecture details including AWS cloud deployment design, **[see the Enterprise README](README_ENTERPRISE.md)**.

### Basic Service Architecture

```
Browser (localhost:3000)
    ↓
Nginx Frontend Container
    ↓ (/api/v1/*)
    ├─→ Portfolio Service (port 8000)
    └─→ Market Service (port 8001)
        ↓
    PostgreSQL Database
    Redis Cache (Market Service)
```

## Services

| Service | Technology | Local URL | Details |
| --- | --- | --- | --- |
| **frontend** | React, Vite, TypeScript, Nginx | http://localhost:3000 | [Frontend README](frontend/README.md) |
| **portfolio-service** | FastAPI, SQLAlchemy, PostgreSQL | http://localhost:8000/docs | [Service README](portfolio-service/README.md) |
| **market-service** | FastAPI, Redis, PostgreSQL | http://localhost:8001/docs | [Service README](market-service/README.md) |
| postgres | PostgreSQL 16 Alpine | localhost:5432 | Database |
| redis | Redis 7 Alpine | localhost:6379 | Cache |

## Prerequisites

- Docker Desktop
- Docker Compose v2
- Git

No local Node.js or Python installation is required for the Docker workflow.

## Local Development

### Quick Start

```bash
# Clone and navigate
git clone <repository-url>
cd cloud-infra

# Create environment file
cp .env.example .env

# Start all services (builds if necessary)
docker compose up --build -d

# Verify services
docker compose ps
```

### Access Services

```
Frontend:       http://localhost:3000
Portfolio API:  http://localhost:8000/docs  (Swagger UI)
Market API:     http://localhost:8001/docs  (Swagger UI)
```

### Useful Commands

```bash
# Start services
docker compose up -d

# Rebuild containers
docker compose up --build -d

# View logs
docker compose logs -f [service-name]

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# Check service status
docker compose ps

# Execute command in container
docker compose exec [service] bash
```

## Health Checks

Each service exposes a health check endpoint:

```bash
curl http://localhost:3000/health
curl http://localhost:8000/health
curl http://localhost:8001/health
```

Expected response:
```json
{"status": "ok"}
```

## Environment Configuration

For **local development**, Docker Compose uses defaults from `.env`. Create one from the example:

```bash
cp .env.example .env
```

**Key Variables**:
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: JWT token signing key
- `VITE_API_BASE_URL`: Frontend API endpoint (`/api/v1`)

**Important**: Never commit real `.env` or production secrets to version control.

For **production AWS deployment**, secrets should be stored in:
- AWS Secrets Manager (database credentials)
- AWS Systems Manager Parameter Store (configuration)
- Environment variables injected at EC2 runtime

## API Routing

Frontend is configured with `VITE_API_BASE_URL=/api/v1`. In local Docker development, Nginx proxies API requests:

| Route | Service | Port |
| --- | --- | --- |
| `/api/v1/auth` | portfolio-service | 8000 |
| `/api/v1/customers` | portfolio-service | 8000 |
| `/api/v1/portfolio` | portfolio-service | 8000 |
| `/api/v1/market` | market-service | 8001 |

## Production Deployment

For **comprehensive AWS deployment guide** with infrastructure setup, security, networking, and step-by-step deployment instructions, **[see Deployment Guide](docs/deployment-guide.md)** and **[AWS Infrastructure](docs/aws-infrastructure.md)**.

### Quick Production Steps

1. **Build and push Docker images**:
   ```bash
   export DOCKERHUB_USERNAME=your-username
   export IMAGE_TAG=v1.0.0
   ./scripts/build-and-push.sh
   ```

2. **Setup AWS infrastructure** (via Terraform):
   ```bash
   cd terraform
   terraform apply
   ```

3. **Deploy on EC2** (via docker-compose files):
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   docker compose -f docker-compose.frontend.prod.yml up -d
   ```

4. **Validate** health checks and monitor CloudWatch logs

## Repository Structure

```
cloud-infra/
├── docker/                         PostgreSQL initialization scripts
├── docs/                           Complete documentation
│   ├── architecture.md
│   ├── deployment-guide.md
│   ├── aws-infrastructure.md
│   ├── security.md
│   ├── networking.md
│   ├── service-flow.md
│   └── api-documentation.md
├── frontend/                       React/Vite frontend + Nginx
├── portfolio-service/              Portfolio management microservice
├── market-service/                 Market intelligence microservice
├── scripts/                        Build and deployment scripts
├── terraform/                      Infrastructure as Code (AWS)
├── docker-compose.yml              Local development stack
├── docker-compose.prod.yml         Production backend stack
├── docker-compose.frontend.prod.yml Production frontend stack
├── .env.example                    Local environment template
├── .env.prod.example               Production environment template
├── README.md                       This file (quick start guide)
└── README_ENTERPRISE.md            Comprehensive architecture guide
```

## Documentation Index

| Document | Purpose |
|----------|---------|
| **[README_ENTERPRISE.md](README_ENTERPRISE.md)** | Complete architecture, AWS deployment, infrastructure design |
| **[docs/deployment-guide.md](docs/deployment-guide.md)** | Step-by-step production deployment |
| **[docs/aws-infrastructure.md](docs/aws-infrastructure.md)** | AWS resource setup and configuration |
| **[docs/networking.md](docs/networking.md)** | VPC, subnets, routing, security groups |
| **[docs/security.md](docs/security.md)** | Security architecture and best practices |
| **[docs/architecture.md](docs/architecture.md)** | System design patterns |
| **[docs/service-flow.md](docs/service-flow.md)** | Service communication and integration |
| **[frontend/README.md](frontend/README.md)** | Frontend service documentation |
| **[portfolio-service/README.md](portfolio-service/README.md)** | Portfolio service documentation |
| **[market-service/README.md](market-service/README.md)** | Market service documentation |
| **[docker/README.md](docker/README.md)** | Docker and containerization |
| **[terraform/README.md](terraform/README.md)** | Infrastructure as Code setup |
| **[scripts/README.md](scripts/README.md)** | Build and deployment scripts |
