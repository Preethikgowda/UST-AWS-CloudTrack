# IntelliWealth Cloud Infrastructure
## Enterprise Cloud Deployment Platform

**Version**: 1.0.0  
**Last Updated**: May 2026  
**Status**: Production-Ready Architecture

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Business Problem](#business-problem)
3. [Solution Architecture](#solution-architecture)
4. [Microservices Architecture](#microservices-architecture)
5. [Technology Stack](#technology-stack)
6. [System Architecture](#system-architecture)
7. [AWS Deployment Architecture](#aws-deployment-architecture)
8. [Infrastructure Design](#infrastructure-design)
9. [Security & Compliance](#security--compliance)
10. [Local Development Setup](#local-development-setup)
11. [Docker Containerization](#docker-containerization)
12. [Production Deployment](#production-deployment)
13. [Operations & Monitoring](#operations--monitoring)
14. [Service Communication Flow](#service-communication-flow)
15. [Future Roadmap](#future-roadmap)

---

## Project Overview

**IntelliWealth** is an enterprise-grade microservices platform designed for **secure cloud deployment on AWS infrastructure**. The platform provides portfolio management, market intelligence, and asset allocation analysis with a focus on **production-ready cloud architecture**, **high availability**, **multi-AZ deployment**, and **secure networking**.

### Key Attributes
- ✅ **Microservices Architecture** - Independent, scalable services
- ✅ **Container-Based Deployment** - Docker & Docker Compose orchestration
- ✅ **AWS-Native Infrastructure** - Custom VPC, RDS, ALB, EC2 Auto Scaling
- ✅ **Multi-AZ Redundancy** - High availability across availability zones
- ✅ **Enterprise Security** - Security groups, SSL/TLS, least privilege networking
- ✅ **Infrastructure as Code** - Terraform automation for reproducible deployments
- ✅ **Production-Grade** - Health checks, monitoring, logging architecture

### Business Problem

Organizations require secure, scalable portfolio management solutions with:
- **Real-time market data analysis** without manual refresh
- **Decoupled service architecture** for independent scaling
- **Cloud-native infrastructure** with failover and disaster recovery
- **Compliance-ready networking** with security segmentation
- **Zero-trust architecture** with encrypted communication
- **Auto-scaling capabilities** to handle demand variations

### Solution Architecture

IntelliWealth solves these challenges through:
1. **Microservices decomposition** - Portfolio and Market services operate independently
2. **Cloud infrastructure** - AWS VPC with multi-AZ, RDS, ALB
3. **Container orchestration** - Docker Compose for local dev, EC2 for production
4. **API-first design** - Frontend communicates via RESTful APIs
5. **Infrastructure automation** - Terraform for repeatable deployments
6. **Security-by-design** - Network segmentation, SSL/TLS, least privilege access

---

## Microservices Architecture

### Core Services

#### 1. Frontend Service
**Purpose**: User-facing web application  
**Technology**: React, Vite, TypeScript, Nginx  
**Port**: 3000 (local), 80 (container)  
**Responsibility**: 
- Dashboard and UI presentation
- User authentication interface
- API request orchestration
- Real-time portfolio visualization

**Communication Pattern**: 
```
Browser → Nginx (reverse proxy) → Backend APIs
```

#### 2. Portfolio Service
**Purpose**: Portfolio and customer management  
**Technology**: FastAPI, SQLAlchemy, PostgreSQL  
**Port**: 8000  
**Responsibility**:
- Customer account management
- Portfolio CRUD operations
- Asset allocation tracking
- Portfolio history and audit
- Authentication/Authorization

**Endpoints**:
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/customers/{customer_id}
POST   /api/v1/customers
GET    /api/v1/portfolio/{customer_id}
POST   /api/v1/portfolio
PUT    /api/v1/portfolio/{portfolio_id}
DELETE /api/v1/portfolio/{portfolio_id}
```

#### 3. Market Service
**Purpose**: Market data and risk analysis  
**Technology**: FastAPI, SQLAlchemy, PostgreSQL, Redis  
**Port**: 8001  
**Responsibility**:
- Real-time market data aggregation
- Risk metrics calculation
- Sector analysis
- Caching layer (Redis)
- Data-intensive computations

**Endpoints**:
```
GET    /api/v1/market/data/{symbol}
GET    /api/v1/market/risk/{portfolio_id}
GET    /api/v1/market/sectors
GET    /api/v1/market/analytics
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Frontend** | React | Latest | UI framework |
| **Frontend Build** | Vite | Latest | Build tool |
| **Language** | TypeScript | Latest | Type-safe code |
| **Web Server** | Nginx | Alpine | Reverse proxy, static serving |
| **Backend** | FastAPI | Latest | Python async framework |
| **ORM** | SQLAlchemy | 2.x | Database abstraction |
| **Migrations** | Alembic | Latest | Schema versioning |
| **Database** | PostgreSQL | 16 Alpine | Primary datastore |
| **Cache** | Redis | 7 Alpine | Market data cache |
| **Containerization** | Docker | 24.x+ | Container runtime |
| **Orchestration** | Docker Compose | v2 | Local & production |
| **Infrastructure** | Terraform | 1.5+ | IaC |
| **Cloud Platform** | AWS | - | Production deployment |

---

## System Architecture

### Local Development Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Workstation                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Browser (localhost:3000)                                    │
│    ↓                                                          │
│  ┌─────────────────────────────────────────────┐             │
│  │        Frontend Container (Nginx)           │             │
│  │    Port 3000 → Container Port 80            │             │
│  │  Reverse Proxy: /api → Backend Services     │             │
│  └──────────────┬──────────────────────────────┘             │
│               ↙  ↘                                            │
│         /api/v1   /api/v1                                     │
│             ↓      ↓                                          │
│  ┌──────────────┐ ┌──────────────┐   ┌──────────────────┐  │
│  │   Portfolio  │ │    Market    │   │     Redis        │  │
│  │   Service    │ │   Service    │   │   (Cache)        │  │
│  │  Port 8000   │ │  Port 8001   │   │  Port 6379       │  │
│  └──────┬───────┘ └──────┬───────┘   └────────┬─────────┘  │
│         │                │                      │            │
│         └────────────────┼──────────────────────┘            │
│                          ↓                                    │
│         ┌────────────────────────────────┐                   │
│         │   PostgreSQL Database          │                   │
│         │   Port 5432                    │                   │
│         │   Volume: postgres_data        │                   │
│         └────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## AWS Deployment Architecture

### High-Level Deployment Topology

```
┌────────────────────────────────────────────────────────────────┐
│                        AWS Account                              │
│                    (us-east-1, Multi-AZ)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  Route53 (DNS)                            │ │
│  │          (yourdomain.com → ALB IP)                        │ │
│  └─────────────────────────┬─────────────────────────────────┘ │
│                            │ HTTPS/TLS                          │
│                            ↓                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │      Application Load Balancer (ALB)                      │ │
│  │  Port: 443 (HTTPS) + 80 (HTTP redirect)                  │ │
│  │  ACM Certificate: yourdomain.com                          │ │
│  │  Path-based routing:                                      │ │
│  │    /            → Frontend Target Group                   │ │
│  │    /api/v1/*    → Backend Target Groups                   │ │
│  └─────┬────────────────────────────────────────────┬────────┘ │
│        │                                            │           │
│  ┌─────▼──────────────────┐      ┌────────────────▼──────────┐ │
│  │   Availability Zone 1   │      │   Availability Zone 2     │ │
│  │     (us-east-1a)       │      │     (us-east-1b)          │ │
│  ├────────────────────────┤      ├───────────────────────────┤ │
│  │                         │      │                           │ │
│  │  Public Subnet          │      │  Public Subnet            │ │
│  │  CIDR: 10.0.1.0/24     │      │  CIDR: 10.0.2.0/24       │ │
│  │                         │      │                           │ │
│  │  ┌──────────────────┐  │      │  ┌──────────────────────┐ │ │
│  │  │  NAT Gateway 1   │  │      │  │  NAT Gateway 2       │ │ │
│  │  │  Elastic IP      │  │      │  │  Elastic IP          │ │ │
│  │  └──────────────────┘  │      │  └──────────────────────┘ │ │
│  │                         │      │                           │ │
│  ├─────────────────────────┤      ├───────────────────────────┤ │
│  │ Private App Subnet      │      │ Private App Subnet        │ │
│  │ CIDR: 10.0.11.0/24     │      │ CIDR: 10.0.12.0/24       │ │
│  │                         │      │                           │ │
│  │  ┌──────────┐          │      │  ┌──────────┐            │ │
│  │  │Frontend  │          │      │  │Frontend  │            │ │
│  │  │  EC2-1  │          │      │  │  EC2-2   │            │ │
│  │  │Port: 80 │          │      │  │Port: 80  │            │ │
│  │  └──────────┘          │      │  └──────────┘            │ │
│  │                         │      │                           │ │
│  │  ┌──────────┐          │      │  ┌──────────┐            │ │
│  │  │Portfolio │          │      │  │Portfolio │            │ │
│  │  │ Service  │          │      │  │ Service  │            │ │
│  │  │Port:8000 │          │      │  │Port:8000 │            │ │
│  │  └──────────┘          │      │  └──────────┘            │ │
│  │                         │      │                           │ │
│  │  ┌──────────┐          │      │  ┌──────────┐            │ │
│  │  │Market    │          │      │  │Market    │            │ │
│  │  │Service   │          │      │  │Service   │            │ │
│  │  │Port:8001 │          │      │  │Port:8001 │            │ │
│  │  └──────────┘          │      │  └──────────┘            │ │
│  │                         │      │                           │ │
│  ├─────────────────────────┤      ├───────────────────────────┤ │
│  │ Private DB Subnet       │      │ Private DB Subnet         │ │
│  │ CIDR: 10.0.21.0/24     │      │ CIDR: 10.0.22.0/24       │ │
│  │                         │      │                           │ │
│  └─────────────────────────┘      └───────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │   RDS PostgreSQL Multi-AZ Instance                        │ │
│  │   - Primary: AZ-1                                         │ │
│  │   - Standby: AZ-2                                         │ │
│  │   - Automatic failover enabled                           │ │
│  │   - Security Group: Port 5432 from App SG only           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │   ElastiCache Redis (Optional)                            │ │
│  │   - Multi-AZ with automatic failover                      │ │
│  │   - Port 6379 from App SG only                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### VPC Design

**Custom VPC: `intelliwealth-vpc`**
- **CIDR Block**: `10.0.0.0/16`
- **DNS Resolution**: Enabled
- **DNS Hostnames**: Enabled
- **Tenancy**: Default

**Subnets**

| Subnet | CIDR | AZ | Type | Route Table | Purpose |
|--------|------|-----|------|-------------|---------|
| Public-1a | 10.0.1.0/24 | us-east-1a | Public | IGW | NAT Gateway |
| Public-1b | 10.0.2.0/24 | us-east-1b | Public | IGW | NAT Gateway |
| AppPrivate-1a | 10.0.11.0/24 | us-east-1a | Private | NAT-1a | EC2 Instances |
| AppPrivate-1b | 10.0.12.0/24 | us-east-1b | Private | NAT-1b | EC2 Instances |
| DbPrivate-1a | 10.0.21.0/24 | us-east-1a | Private | None | RDS Primary |
| DbPrivate-1b | 10.0.22.0/24 | us-east-1b | Private | None | RDS Standby |

### Internet Connectivity

**Internet Gateway**: `intelliwealth-igw`
- Attached to VPC
- Handles all outbound/inbound internet traffic

**NAT Gateways**:
- **NAT-1a** (in Public-1a subnet)
  - Elastic IP: Assigned
  - Handles outbound traffic from AppPrivate-1a
  
- **NAT-1b** (in Public-1b subnet)
  - Elastic IP: Assigned
  - Handles outbound traffic from AppPrivate-1b

### Route Tables

**Public Route Table** (IGW)
```
Destination      | Target
─────────────────|─────────────
10.0.0.0/16      | Local
0.0.0.0/0        | Internet Gateway
```

**Private Route Table 1a** (NAT-1a)
```
Destination      | Target
─────────────────|─────────────
10.0.0.0/16      | Local
0.0.0.0/0        | NAT Gateway 1a
```

**Private Route Table 1b** (NAT-1b)
```
Destination      | Target
─────────────────|─────────────
10.0.0.0/16      | Local
0.0.0.0/0        | NAT Gateway 1b
```

---

## Infrastructure Design

### Compute Strategy

**Load Balancing**: Application Load Balancer (ALB)
- **Protocol**: HTTPS (443) and HTTP (80)
- **Certificate**: AWS ACM (SSL/TLS)
- **Health Checks**: Every 30 seconds
- **Path-based Routing**:
  - `/` → Frontend Target Group
  - `/api/v1/*` → Backend Target Groups

**Target Groups**:
1. **Frontend TG**: EC2 instances on port 80
2. **Portfolio Service TG**: EC2 instances on port 8000
3. **Market Service TG**: EC2 instances on port 8001

**EC2 Instances**:
- **Instance Type**: `t3.medium` or `t3.large`
- **AMI**: Ubuntu 22.04 LTS
- **Root Volume**: 50 GB (gp3)
- **Deployment**: Auto Scaling Group (min 2, desired 2, max 4)
- **Monitoring**: CloudWatch metrics, health checks

### Database Strategy

**RDS PostgreSQL**:
- **Engine**: PostgreSQL 16
- **Instance Class**: `db.t3.small` (scalable)
- **Storage**: 100 GB (gp3, auto-scaling enabled)
- **Multi-AZ**: Enabled
  - **Primary**: Private DB Subnet (AZ 1a)
  - **Standby**: Private DB Subnet (AZ 1b)
  - **Automatic Failover**: ~60 seconds
- **Backup**:
  - **Retention**: 30 days
  - **Backup Window**: 03:00-04:00 UTC
  - **Multi-AZ Snapshot**: Automated
- **Port**: 5432 (restricted to application security group)
- **Database**: `intelliwealth_db`

### Caching Strategy

**ElastiCache Redis** (Optional, recommended):
- **Engine**: Redis 7
- **Node Type**: `cache.t3.micro` or `cache.t3.small`
- **Port**: 6379
- **Multi-AZ**: Enabled (automatic failover)
- **Encryption**:
  - **In Transit**: TLS enabled
  - **At Rest**: Enabled
- **Security Group**: Restricted to application security group

---

## Security & Compliance

### Network Security

**Security Groups**

1. **ALB Security Group** (`alb-sg`)
   ```
   Inbound Rules:
   - Port 443 (HTTPS) from 0.0.0.0/0
   - Port 80 (HTTP) from 0.0.0.0/0
   
   Outbound Rules:
   - All traffic to 0.0.0.0/0
   ```

2. **Frontend EC2 Security Group** (`frontend-sg`)
   ```
   Inbound Rules:
   - Port 80 from alb-sg
   
   Outbound Rules:
   - All traffic to 0.0.0.0/0
   ```

3. **Backend Services Security Group** (`backend-sg`)
   ```
   Inbound Rules:
   - Port 8000 (Portfolio) from alb-sg
   - Port 8001 (Market) from alb-sg
   
   Outbound Rules:
   - All traffic to 0.0.0.0/0
   ```

4. **RDS Security Group** (`db-sg`)
   ```
   Inbound Rules:
   - Port 5432 (PostgreSQL) from backend-sg only
   
   Outbound Rules:
   - None (typically)
   ```

5. **ElastiCache Security Group** (`redis-sg`)
   ```
   Inbound Rules:
   - Port 6379 (Redis) from backend-sg only
   
   Outbound Rules:
   - None (typically)
   ```

### Application Security

- **JWT Token-based Authentication**: Stateless, secure
- **HTTPS/TLS Enforcement**: All client-server communication encrypted
- **CORS Configuration**: Restricted to known origins
- **SQL Injection Protection**: SQLAlchemy parameterized queries
- **Password Hashing**: bcrypt with salt (in application)
- **API Rate Limiting**: Per-IP rate limiting recommended
- **Secrets Management**:
  - AWS Secrets Manager for RDS credentials
  - Environment variables (not in code)
  - No hardcoded credentials in Docker images

### Compliance Considerations

- **Data at Rest**: PostgreSQL on RDS (EBS encrypted)
- **Data in Transit**: TLS 1.2+ (ALB to clients, application to database)
- **Audit Logging**: CloudWatch Logs, RDS audit
- **Access Control**: IAM roles for EC2 instances
- **Least Privilege**: Security groups restrict access by default

---

## Local Development Setup

### Prerequisites

| Tool | Minimum Version | Purpose |
|------|-----------------|---------|
| Docker Desktop | 4.10+ | Container runtime |
| Docker Compose | 2.0+ | Container orchestration |
| Git | 2.20+ | Version control |
| Bash/Shell | 5.0+ | Script execution |

**No local Python, Node.js, or database installation required.**

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cloud-infra
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker compose up --build -d
   ```

4. **Verify services are running**
   ```bash
   docker compose ps
   ```

5. **Access the application**
   ```
   Frontend:       http://localhost:3000
   Portfolio API:  http://localhost:8000/docs
   Market API:     http://localhost:8001/docs
   ```

### Health Checks

Verify all services are healthy:

```bash
curl http://localhost:3000/health
curl http://localhost:8000/health
curl http://localhost:8001/health
```

Expected response:
```json
{"status": "ok"}
```

### Environment Variables

**Local Development** (`.env`)

| Variable | Value | Purpose |
|----------|-------|---------|
| `POSTGRES_USER` | postgres | Database user |
| `POSTGRES_PASSWORD` | dev_password | Database password |
| `POSTGRES_DB` | intelliwealth | Database name |
| `DATABASE_URL` | postgresql://postgres:dev_password@postgres:5432/intelliwealth | Connection string |
| `REDIS_URL` | redis://redis:6379 | Redis connection |
| `JWT_SECRET_KEY` | your_secret_key_here | JWT signing key |
| `VITE_API_BASE_URL` | /api/v1 | API endpoint |

---

## Docker Containerization

### Image Strategy

All services are containerized and defined in Dockerfiles:

| Service | Dockerfile | Image Size | Build Time |
|---------|-----------|-----------|------------|
| Frontend | `frontend/Dockerfile` | ~100 MB | ~2 min |
| Portfolio | `portfolio-service/Dockerfile` | ~500 MB | ~3 min |
| Market | `market-service/Dockerfile` | ~500 MB | ~3 min |

### Docker Compose Files

**Development**: `docker-compose.yml`
- Full local development stack
- All services, database, cache
- Hot reload enabled where possible
- Exposed ports for local development

**Production Backend**: `docker-compose.prod.yml`
- Portfolio and Market services only
- Redis cache
- For EC2 deployment
- No frontend (served separately)

**Production Frontend**: `docker-compose.frontend.prod.yml`
- Frontend Nginx only
- Static build artifact
- For EC2 deployment

### Building Images

**Local Build**:
```bash
docker compose build
```

**Production Push to Registry**:
```bash
export DOCKERHUB_USERNAME=your_username
export IMAGE_TAG=v1.0.0
./scripts/build-and-push.sh
```

Images are tagged as:
- `your_username/intelliwealth-frontend:v1.0.0`
- `your_username/intelliwealth-portfolio-service:v1.0.0`
- `your_username/intelliwealth-market-service:v1.0.0`

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] AWS account with VPC created
- [ ] Route53 domain configured
- [ ] ACM certificate issued
- [ ] RDS PostgreSQL instance running
- [ ] ElastiCache Redis (optional) deployed
- [ ] EC2 security groups configured
- [ ] ALB created and target groups defined
- [ ] Container images pushed to registry

### Deployment Sequence

#### Phase 1: Infrastructure Setup (Terraform)
```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```

#### Phase 2: RDS Database
1. Create RDS PostgreSQL instance
2. Initialize schema using migration scripts
3. Create superuser account
4. Test connectivity from EC2 instances

#### Phase 3: EC2 Deployment
1. Launch EC2 instances in Auto Scaling Group
2. Configure security groups
3. Deploy Docker containers using docker-compose files
4. Verify service startup logs

#### Phase 4: ALB Configuration
1. Create ALB in public subnets
2. Configure target groups
3. Add health check endpoints
4. Test routing to each service

#### Phase 5: DNS & TLS
1. Create ACM certificate
2. Attach certificate to ALB listener
3. Configure Route53 CNAME records
4. Test HTTPS connectivity

#### Phase 6: Validation
1. Test frontend accessibility
2. Test API endpoints
3. Verify database connectivity
4. Check health check responses
5. Monitor CloudWatch metrics

### Production Deployment Flow

```
Infrastructure (Terraform)
        ↓
RDS Database (PostgreSQL)
        ↓
ElastiCache (Redis)
        ↓
EC2 Instances (Auto Scaling)
        ↓
Docker Container Deployment
        ↓
ALB Configuration
        ↓
Security Groups
        ↓
Route53 DNS
        ↓
ACM/TLS Certificates
        ↓
Health Check Validation
        ↓
Load Testing & Verification
        ↓
Production Ready
```

---

## Operations & Monitoring

### CloudWatch Monitoring

**EC2 Instance Metrics**:
- CPU Utilization
- Network In/Out
- Disk Read/Write

**RDS Metrics**:
- CPU Utilization
- Database Connections
- IOPS
- Storage Used
- Replica Lag (Multi-AZ)

**ALB Metrics**:
- Request Count
- Target Response Time
- HTTP 4xx/5xx Errors
- Active Connections

### Logging

**Application Logs**:
- CloudWatch Logs for container stdout/stderr
- Log Group: `/intelliwealth/frontend`
- Log Group: `/intelliwealth/portfolio-service`
- Log Group: `/intelliwealth/market-service`

**Database Logs**:
- RDS error log
- Slow query log (if enabled)

### Auto Scaling

**Scaling Policy**: Target Tracking
- **Metric**: Average CPU Utilization
- **Target**: 70%
- **Scale-up**: +1 instance when CPU > 70%
- **Scale-down**: -1 instance when CPU < 40%
- **Cooldown**: 300 seconds

---

## Service Communication Flow

### Request Flow Diagram

```
User (Browser)
  ↓
HTTPS → ALB (Route53 resolves to ALB IP)
  ↓
ALB Path-Based Routing
  ├─ / → Frontend Target Group
  │   └─ EC2 (Nginx on port 80)
  │       ├─ Serve static files
  │       └─ Proxy /api/* → Backend
  │
  └─ /api/* → Backend Target Groups
      ├─ /api/v1/auth → Portfolio Service (port 8000)
      ├─ /api/v1/customers → Portfolio Service (port 8000)
      ├─ /api/v1/portfolio → Portfolio Service (port 8000)
      └─ /api/v1/market → Market Service (port 8001)

Frontend Service (React)
  ↓ (API requests with JWT)
Backend Services (FastAPI)
  ├─ Portfolio Service → PostgreSQL
  └─ Market Service → PostgreSQL + Redis Cache
```

### Inter-Service Communication

**Frontend → Portfolio Service**:
- Protocol: HTTPS (via ALB)
- Authentication: JWT Bearer Token
- Data Format: JSON

**Portfolio Service → Market Service** (if applicable):
- Protocol: HTTP (internal)
- Port: 8001
- Authentication: Service-to-service token

**Services → PostgreSQL**:
- Protocol: TCP/IP
- Port: 5432
- Authentication: Username/Password (IAM role-based in production)

**Market Service → Redis**:
- Protocol: TCP
- Port: 6379
- Authentication: Password (if enabled)

---

## Future Roadmap

### Phase 2: Enhanced Observability
- [ ] Distributed tracing (AWS X-Ray)
- [ ] Application Performance Monitoring (APM)
- [ ] Custom CloudWatch dashboards
- [ ] Alerts & SNS notifications

### Phase 3: Advanced Security
- [ ] AWS WAF (Web Application Firewall) on ALB
- [ ] VPC Flow Logs analysis
- [ ] GuardDuty threat detection
- [ ] Secrets rotation automation

### Phase 4: Disaster Recovery
- [ ] Automated RDS backup to S3
- [ ] Cross-region replication
- [ ] Disaster recovery playbooks
- [ ] RTO/RPO definitions

### Phase 5: Cost Optimization
- [ ] Reserved Instances (RI) for predictable load
- [ ] Spot Instances for non-critical services
- [ ] RDS cost analysis
- [ ] Data transfer optimization

### Phase 6: Container Orchestration
- [ ] ECS Fargate migration
- [ ] EKS (Kubernetes) evaluation
- [ ] Container registry (ECR) integration
- [ ] Blue-green deployment strategy

### Phase 7: CI/CD Pipeline
- [ ] GitHub Actions / GitLab CI
- [ ] Automated testing in pipeline
- [ ] Containerized deployment
- [ ] Rollback automation

---

## Documentation Index

For more detailed information, see:

- **[Architecture Details](docs/architecture.md)** - System design patterns
- **[Networking Guide](docs/networking.md)** - VPC, subnets, routing
- **[Security Design](docs/security.md)** - Security groups, encryption, compliance
- **[AWS Infrastructure](docs/aws-infrastructure.md)** - AWS resource setup
- **[Deployment Guide](docs/deployment-guide.md)** - Step-by-step production deployment
- **[Service Communication](docs/service-flow.md)** - API contracts and integration
- **[API Documentation](docs/api-documentation.md)** - OpenAPI/Swagger specifications
- **[Frontend Service](frontend/README.md)** - React application details
- **[Portfolio Service](portfolio-service/README.md)** - Portfolio microservice
- **[Market Service](market-service/README.md)** - Market microservice
- **[Docker Setup](docker/README.md)** - Container configuration
- **[Terraform Setup](terraform/README.md)** - Infrastructure as Code
- **[Scripts](scripts/README.md)** - Automation and deployment scripts

---

## Support & Contribution

For issues, questions, or contributions:
1. Review relevant documentation sections above
2. Check service-specific READMEs
3. Review GitHub issues for known problems
4. Submit pull requests with detailed descriptions

---

**Last Updated**: May 2026  
**Maintained By**: Cloud Infrastructure Team
