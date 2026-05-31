# Documentation Index

**IntelliWealth Cloud Infrastructure - Complete Documentation**

---

## Documentation Structure

This documentation provides comprehensive guidance on deploying and maintaining IntelliWealth on AWS.

### Core Documentation

1. **[Architecture](architecture.md)** - System design patterns and high-level architecture
2. **[AWS Infrastructure](aws-infrastructure.md)** - AWS resource configuration and setup
3. **[Networking Design](networking.md)** - VPC, subnets, routing, and network segmentation
4. **[Security Design](security.md)** - Security groups, encryption, compliance, and best practices
5. **[Deployment Guide](deployment-guide.md)** - Step-by-step production deployment process
6. **[Service Communication](service-flow.md)** - API contracts and inter-service communication
7. **[API Documentation](api-documentation.md)** - REST API specifications

### Service-Specific Documentation

- **[Frontend Service](../frontend/README.md)** - React/Vite frontend application
- **[Portfolio Service](../portfolio-service/README.md)** - Portfolio management microservice
- **[Market Service](../market-service/README.md)** - Market intelligence microservice

### Infrastructure & DevOps

- **[Docker Setup](../docker/README.md)** - Container configuration and orchestration
- **[Terraform Setup](../terraform/README.md)** - Infrastructure as Code
- **[Scripts & Automation](../scripts/README.md)** - Build and deployment scripts

### Getting Started

**New to IntelliWealth?**
1. Start with [README.md](../README.md) - Quick overview
2. Read [README_ENTERPRISE.md](../README_ENTERPRISE.md) - Comprehensive architecture guide
3. Review [Architecture](architecture.md) - Understand system design
4. Check [Deployment Guide](deployment-guide.md) - Deploy to production

**Setting up locally?**
1. Follow [README.md](../README.md) - Local development setup
2. Review [Docker Setup](../docker/README.md) - Container orchestration
3. Check service-specific READMEs for detailed configuration

**Managing AWS infrastructure?**
1. Review [AWS Infrastructure](aws-infrastructure.md) - Resource configuration
2. Check [Terraform Setup](../terraform/README.md) - IaC deployment
3. Read [Networking Design](networking.md) - Network topology
4. Review [Security Design](security.md) - Security architecture

---

## Quick Reference

### Architecture Overview

```
Browser
  ↓
HTTPS
  ↓
Route53 (DNS)
  ↓
ALB (Port 443)
  ↓
EC2 Instances (Port 80)
  ├─ Frontend (Nginx)
  ├─ Portfolio Service (FastAPI:8000)
  └─ Market Service (FastAPI:8001)
  ↓
PostgreSQL (RDS)
Redis (ElastiCache)
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Compute | EC2 with Auto Scaling |
| Database | PostgreSQL 16 on RDS (Multi-AZ) |
| Cache | Redis 7 on ElastiCache |
| Load Balancing | Application Load Balancer (ALB) |
| DNS | Route53 |
| Certificates | ACM SSL/TLS |
| Containerization | Docker & Docker Compose |
| IaC | Terraform |

### Key Features

- ✅ Multi-AZ deployment (2 availability zones)
- ✅ Auto Scaling (min 2, desired 2, max 4 instances)
- ✅ Load Balancing (ALB with health checks)
- ✅ Database HA (RDS Multi-AZ with automatic failover)
- ✅ Network Segmentation (security groups, private subnets)
- ✅ Encryption (TLS in transit, EBS/RDS at rest)
- ✅ Infrastructure as Code (Terraform)
- ✅ Container Orchestration (Docker Compose)

---

## Common Tasks

### Local Development

```bash
# Start all services
docker compose up --build -d

# View logs
docker compose logs -f [service]

# Access applications
# Frontend: http://localhost:3000
# Portfolio API: http://localhost:8000/docs
# Market API: http://localhost:8001/docs
```

### Production Deployment

```bash
# 1. Build and push Docker images
./scripts/build-and-push.sh

# 2. Deploy infrastructure
cd terraform && terraform apply

# 3. Deploy services on EC2
# (via docker-compose.prod.yml)
```

### Health Monitoring

```bash
# Check service health
curl http://localhost/health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Monitor logs
docker compose logs -f

# Check container status
docker compose ps
```

### Database Operations

```bash
# Access PostgreSQL
docker compose exec postgres psql -U postgres -d intelliwealth

# Create backup
docker compose exec postgres pg_dump -U postgres intelliwealth > backup.sql

# Restore backup
docker compose exec -T postgres psql -U postgres intelliwealth < backup.sql
```

---

## Security Checklist

- [ ] VPC with isolated subnets
- [ ] Security groups with least privilege rules
- [ ] HTTPS/TLS enabled on ALB
- [ ] Database encryption (at rest and in transit)
- [ ] Secrets in AWS Secrets Manager
- [ ] No hardcoded credentials in code/images
- [ ] Regular backups enabled
- [ ] CloudWatch monitoring and alarms
- [ ] IAM roles for EC2 instances
- [ ] Security group audit log (VPC Flow Logs)

---

## Troubleshooting

### Common Issues

**Services won't start**
- Check logs: `docker compose logs [service]`
- Verify ports aren't in use: `lsof -i :[port]`
- Check environment variables: `docker compose config`

**Database connection failures**
- Verify PostgreSQL is running: `docker compose ps postgres`
- Test connection: `docker compose exec postgres psql -U postgres -d intelliwealth -c "SELECT 1;"`
- Check network: `docker network ls`

**API errors**
- Check service logs: `docker compose logs portfolio-service`
- Verify health endpoints: `curl http://localhost:8000/health`
- Check Nginx routing: `docker compose logs frontend`

### Getting Help

1. Check the relevant README in this documentation
2. Review service-specific logs
3. Check AWS CloudWatch metrics (production)
4. Review error messages and stack traces carefully

---

## Performance Optimization

### Database
- Connection pooling (SQLAlchemy)
- Query optimization with indexes
- Read replicas for scaling (future)

### Caching
- Redis for market data (5-minute TTL)
- API response caching
- Browser cache headers

### Infrastructure
- ALB health checks (auto-recovery)
- Auto Scaling based on CPU
- Multi-AZ for failover
- EBS gp3 volumes for performance

---

## Compliance & Audit

### Logging
- CloudWatch Logs for all services
- Database audit logs
- API request logging
- Deployment audit trail

### Backup Strategy
- RDS automatic backups (30-day retention)
- Manual snapshots for releases
- Point-in-time recovery enabled

### Monitoring
- CloudWatch metrics for all components
- Health checks on all services
- Alarms for critical metrics
- Log aggregation and analysis

---

## Document Maintenance

Last Updated: May 2026  
Version: 1.0.0

### How to Update Documentation

1. Modify relevant .md files
2. Update this index if adding new documentation
3. Keep diagrams synchronized with reality
4. Include timestamps and version info
5. Review changes before committing

---

## External Resources

- [AWS Documentation](https://docs.aws.amazon.com)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [PostgreSQL Documentation](https://www.postgresql.org/docs)
- [Docker Documentation](https://docs.docker.com)

---

**For questions or updates, please contact the Infrastructure Team.**
