# Scripts & Automation

**Purpose**: Build, deployment, and operational scripts  
**Status**: Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Build Scripts](#build-scripts)
3. [Deployment Scripts](#deployment-scripts)
4. [Operational Scripts](#operational-scripts)
5. [CI/CD Integration](#cicd-integration)
6. [Security Considerations](#security-considerations)

---

## Overview

This directory contains shell scripts for automating build, deployment, and operational tasks:

- **Building**: Docker image compilation
- **Publishing**: Registry uploads
- **Deployment**: Infrastructure provisioning
- **Maintenance**: Health checks, backups

### Script Conventions

- Scripts use Bash 5.0+
- Error handling with `set -e`
- Logging with timestamp prefixes
- Environment variable validation
- Dry-run modes where possible

---

## Build Scripts

### build-and-push.sh

**Purpose**: Build Docker images and push to registry  
**Location**: `scripts/build-and-push.sh`

#### Usage

```bash
export DOCKERHUB_USERNAME=your_username
export IMAGE_TAG=v1.0.0
./scripts/build-and-push.sh
```

#### Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DOCKERHUB_USERNAME` | Yes | - | Docker Hub username |
| `IMAGE_TAG` | Yes | - | Image version tag |
| `REGISTRY` | No | docker.io | Container registry |
| `DRY_RUN` | No | false | Preview without pushing |

#### Process

1. **Validate Prerequisites**
   - Check Docker is installed and running
   - Verify environment variables
   - Confirm registry authentication

2. **Build Frontend Image**
   ```bash
   docker build -f frontend/Dockerfile \
     --build-arg VITE_API_BASE_URL=/api/v1 \
     -t intelliwealth-frontend:${IMAGE_TAG} .
   ```

3. **Build Portfolio Service Image**
   ```bash
   docker build -f portfolio-service/Dockerfile \
     -t intelliwealth-portfolio:${IMAGE_TAG} .
   ```

4. **Build Market Service Image**
   ```bash
   docker build -f market-service/Dockerfile \
     -t intelliwealth-market:${IMAGE_TAG} .
   ```

5. **Tag for Registry**
   ```bash
   docker tag intelliwealth-frontend:${IMAGE_TAG} \
     ${REGISTRY}/${DOCKERHUB_USERNAME}/intelliwealth-frontend:${IMAGE_TAG}
   ```

6. **Push to Registry**
   ```bash
   docker push ${REGISTRY}/${DOCKERHUB_USERNAME}/intelliwealth-frontend:${IMAGE_TAG}
   ```

#### Success Indicators

```
✓ Frontend image built successfully
✓ Portfolio service image built successfully
✓ Market service image built successfully
✓ All images pushed to registry
```

#### Troubleshooting

**Authentication Failed**:
```bash
docker login
# Enter credentials when prompted
```

**Build Failed**:
```bash
# Check Docker daemon
docker ps

# View build logs
docker build -f frontend/Dockerfile --verbose .
```

**Push Failed**:
```bash
# Verify registry access
docker tag test-image:latest ${REGISTRY}/${USER}/test-image:latest
docker push ${REGISTRY}/${USER}/test-image:latest
```

---

## Deployment Scripts

### deploy.sh (Terraform)

**Purpose**: Deploy infrastructure to AWS  
**Location**: `terraform/` (typically automated via CI/CD)

#### Usage

```bash
cd terraform

# Initialize
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan
```

#### Steps

1. **Validate AWS Credentials**
   ```bash
   aws sts get-caller-identity
   ```

2. **Initialize Terraform**
   ```bash
   terraform init
   ```

3. **Validate Configuration**
   ```bash
   terraform validate
   ```

4. **Plan Deployment**
   ```bash
   terraform plan -out=tfplan
   ```

5. **Apply Changes**
   ```bash
   terraform apply tfplan
   ```

6. **Export Outputs**
   ```bash
   terraform output > deployment-outputs.txt
   ```

#### Outputs

Terraform provides critical deployment information:

```
alb_dns_name = "intelliwealth-alb-12345.us-east-1.elb.amazonaws.com"
rds_endpoint = "intelliwealth-db.123456.us-east-1.rds.amazonaws.com"
rds_port = 5432
vpc_id = "vpc-12345678"
security_groups = ["sg-12345678", "sg-87654321"]
```

### EC2 Deployment (docker-compose)

**Purpose**: Deploy containers to EC2 instances

#### Process

1. **SSH into EC2 Instance**
   ```bash
   ssh -i your-key.pem ec2-user@instance-public-ip
   ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/cloud-infra.git
   cd cloud-infra
   ```

3. **Create Environment File**
   ```bash
   # Retrieve from AWS Secrets Manager
   aws secretsmanager get-secret-value \
     --secret-id intelliwealth/prod \
     --query SecretString \
     --output text > .env.prod
   ```

4. **Deploy Services**
   ```bash
   # Backend services
   docker compose -f docker-compose.prod.yml \
     --env-file .env.prod up -d
   
   # Frontend service
   docker compose -f docker-compose.frontend.prod.yml \
     --env-file .env.prod up -d
   ```

5. **Verify Health**
   ```bash
   curl http://localhost/health
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   ```

---

## Operational Scripts

### Health Check Script

**Purpose**: Monitor service health  
**Location**: `scripts/health-check.sh` (create if needed)

```bash
#!/bin/bash

# Health check endpoints
FRONTEND_HEALTH="http://localhost:3000/health"
PORTFOLIO_HEALTH="http://localhost:8000/health"
MARKET_HEALTH="http://localhost:8001/health"

echo "Checking Frontend..."
curl -s ${FRONTEND_HEALTH} | jq .

echo "Checking Portfolio Service..."
curl -s ${PORTFOLIO_HEALTH} | jq .

echo "Checking Market Service..."
curl -s ${MARKET_HEALTH} | jq .
```

**Usage**:
```bash
bash scripts/health-check.sh
```

### Database Backup Script

**Purpose**: Backup RDS PostgreSQL  
**Location**: `scripts/backup-database.sh` (create if needed)

```bash
#!/bin/bash

RDS_INSTANCE="intelliwealth-db"
BACKUP_NAME="intelliwealth-backup-$(date +%Y%m%d-%H%M%S)"

echo "Creating RDS snapshot: ${BACKUP_NAME}"

aws rds create-db-snapshot \
  --db-instance-identifier ${RDS_INSTANCE} \
  --db-snapshot-identifier ${BACKUP_NAME}

echo "Snapshot creation initiated"
```

**Usage**:
```bash
bash scripts/backup-database.sh
```

### Logs Collection Script

**Purpose**: Collect application logs  
**Location**: `scripts/collect-logs.sh` (create if needed)

```bash
#!/bin/bash

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_DIR="./logs-${TIMESTAMP}"

mkdir -p ${LOG_DIR}

# Docker Compose logs
docker compose logs frontend > ${LOG_DIR}/frontend.log
docker compose logs portfolio-service > ${LOG_DIR}/portfolio-service.log
docker compose logs market-service > ${LOG_DIR}/market-service.log
docker compose logs postgres > ${LOG_DIR}/postgres.log
docker compose logs redis > ${LOG_DIR}/redis.log

# System logs (if applicable)
docker compose exec postgres pg_dump -U postgres intelliwealth > ${LOG_DIR}/database-dump.sql

echo "Logs collected to ${LOG_DIR}"
```

---

## CI/CD Integration

### GitHub Actions Example

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Docker
        run: echo ${{ secrets.DOCKERHUB_TOKEN }} | docker login -u ${{ secrets.DOCKERHUB_USERNAME }} --password-stdin
      
      - name: Build and Push Images
        run: |
          export DOCKERHUB_USERNAME=${{ secrets.DOCKERHUB_USERNAME }}
          export IMAGE_TAG=${{ github.sha }}
          ./scripts/build-and-push.sh
      
      - name: Deploy Infrastructure
        run: |
          cd terraform
          terraform init
          terraform apply -auto-approve
      
      - name: Deploy to EC2
        run: |
          # SSH into EC2 and deploy
          ssh -i ${{ secrets.EC2_KEY }} \
              ec2-user@${{ secrets.EC2_INSTANCE }} \
              'cd cloud-infra && git pull && docker-compose pull && docker-compose up -d'
```

---

## Security Considerations

### Secrets Management

**Never**:
- Commit `.env` or credential files
- Store secrets in scripts
- Log sensitive information
- Hardcode API keys or passwords

**Do**:
- Use AWS Secrets Manager
- Use AWS Systems Manager Parameter Store
- Inject secrets at runtime via environment variables
- Rotate credentials regularly

### Script Security

```bash
# Use set -e to exit on error
set -e

# Use set -u to fail on undefined variables
set -u

# Avoid eval and dynamic code execution
# Validate all inputs

# Use proper quoting
echo "${VARIABLE}" # Good
echo $VARIABLE     # Bad - whitespace issues
```

### Audit Logging

All deployment scripts should log actions:

```bash
# Log with timestamp
LOG_FILE="./deployment-$(date +%Y%m%d-%H%M%S).log"

exec 1> >(tee -a ${LOG_FILE})
exec 2> >(tee -a ${LOG_FILE} >&2)

echo "Deployment started at $(date)" >> ${LOG_FILE}
```

---

## Best Practices

1. **Test Before Deploying**
   - Test scripts in development environment first
   - Validate all inputs
   - Use dry-run modes

2. **Idempotency**
   - Scripts should be safe to run multiple times
   - Check if resource exists before creating
   - Don't fail if already done

3. **Error Handling**
   - Check return codes
   - Provide meaningful error messages
   - Exit early on critical failures

4. **Documentation**
   - Document all variables and options
   - Provide usage examples
   - List prerequisites

5. **Version Control**
   - Track script changes
   - Use semantic versioning for releases
   - Tag stable versions

---

**Last Updated**: May 2026  
**Maintainer**: DevOps Team
