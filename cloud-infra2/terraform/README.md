# Terraform - Infrastructure as Code

**Purpose**: Define and manage AWS infrastructure using Terraform  
**Region**: us-east-1 (Multi-AZ)  
**Status**: Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [File Structure](#file-structure)
5. [Configuration](#configuration)
6. [Variables](#variables)
7. [Deployment](#deployment)
8. [AWS Resources](#aws-resources)
9. [Networking](#networking)
10. [Security Groups](#security-groups)
11. [Auto Scaling](#auto-scaling)
12. [Monitoring](#monitoring)
13. [Maintenance](#maintenance)
14. [Disaster Recovery](#disaster-recovery)

---

## Overview

This Terraform configuration provisions a **production-grade AWS infrastructure** for IntelliWealth on a custom VPC with:

- **Availability**: Multi-AZ deployment across 2 availability zones
- **Compute**: Auto Scaling Group for EC2 instances
- **Database**: RDS PostgreSQL with Multi-AZ failover
- **Cache**: ElastiCache Redis (optional)
- **Load Balancing**: Application Load Balancer (ALB) with HTTPS
- **DNS**: Route53 integration
- **Security**: Security groups, IAM roles, encryption

### Infrastructure Topology

```
┌─────────────────────────────────────────────────────────┐
│                  AWS Account (us-east-1)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Route53                                                │
│  (yourdomain.com)                                       │
│    ↓ (DNS resolution)                                   │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │        Application Load Balancer (ALB)            │ │
│  │  - Port 443 (HTTPS)                               │ │
│  │  - Port 80 (HTTP redirect)                        │ │
│  │  - ACM Certificate                                │ │
│  └───────────┬─────────────────────────┬─────────────┘ │
│              │                         │               │
│    ┌─────────▼──────────┐   ┌──────────▼──────────┐  │
│    │  Availability      │   │  Availability       │  │
│    │  Zone 1a           │   │  Zone 1b            │  │
│    │  (us-east-1a)      │   │  (us-east-1b)       │  │
│    ├────────────────────┤   ├─────────────────────┤  │
│    │ Public Subnet      │   │ Public Subnet       │  │
│    │ 10.0.1.0/24        │   │ 10.0.2.0/24         │  │
│    │                    │   │                     │  │
│    │ ┌──────────────┐  │   │ ┌──────────────┐   │  │
│    │ │ NAT Gateway  │  │   │ │ NAT Gateway  │   │  │
│    │ └──────────────┘  │   │ └──────────────┘   │  │
│    │                    │   │                     │  │
│    ├────────────────────┤   ├─────────────────────┤  │
│    │ Private App        │   │ Private App         │  │
│    │ Subnet             │   │ Subnet              │  │
│    │ 10.0.11.0/24       │   │ 10.0.12.0/24        │  │
│    │                    │   │                     │  │
│    │ ┌──────────────┐  │   │ ┌──────────────┐   │  │
│    │ │  EC2-1       │  │   │ │  EC2-2       │   │  │
│    │ │  (auto-      │  │   │ │  (auto-      │   │  │
│    │ │   scaled)    │  │   │ │   scaled)    │   │  │
│    │ └──────────────┘  │   │ └──────────────┘   │  │
│    │                    │   │                     │  │
│    ├────────────────────┤   ├─────────────────────┤  │
│    │ Private DB         │   │ Private DB          │  │
│    │ Subnet             │   │ Subnet              │  │
│    │ 10.0.21.0/24       │   │ 10.0.22.0/24        │  │
│    │                    │   │                     │  │
│    │ ┌──────────────┐  │   │ ┌──────────────┐   │  │
│    │ │ RDS Primary  │  │   │ │ RDS Standby  │   │  │
│    │ └──────────────┘  │   │ └──────────────┘   │  │
│    │                    │   │                     │  │
│    └────────────────────┘   └─────────────────────┘  │
│                                                       │
│  ┌───────────────────────────────────────────────────┐ │
│  │   ElastiCache Redis Cluster (optional)           │ │
│  │   - Multi-AZ                                      │ │
│  │   - Automatic failover                           │ │
│  └───────────────────────────────────────────────────┘ │
│                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Local Requirements

1. **Terraform** 1.5.0 or higher
   ```bash
   terraform version  # Should be >= 1.5.0
   ```

2. **AWS CLI** 2.x configured with credentials
   ```bash
   aws configure
   aws sts get-caller-identity  # Verify authentication
   ```

3. **AWS Account**
   - Proper IAM permissions (VPC, EC2, RDS, ALB, etc.)
   - Budget alerts configured (recommended)

4. **SSH Key Pair** in AWS
   - For EC2 instance access
   - Created in AWS Console or via CLI

### AWS Permissions Required

Minimum IAM policy for Terraform execution:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "rds:*",
        "elasticache:*",
        "elbv2:*",
        "route53:*",
        "acm:*",
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:GetRole",
        "iam:PassRole",
        "iam:CreateInstanceProfile",
        "iam:AddRoleToInstanceProfile"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## File Structure

```
terraform/
├── main.tf                Main configuration file
├── variables.tf           Input variable definitions
├── outputs.tf             Output values
├── versions.tf            Provider and version requirements
├── terraform.tfvars       Variable values (DO NOT COMMIT)
├── terraform.tfvars.example Example variable template
└── README.md              This file
```

### File Descriptions

**`versions.tf`**: Provider versions and requirements
- Terraform version constraint
- AWS provider version

**`variables.tf`**: Input variable declarations
- Variable names, types, descriptions
- Default values (if any)
- Validation rules

**`main.tf`**: Resource definitions
- VPC and networking
- Subnets and route tables
- EC2 instances and Auto Scaling
- RDS PostgreSQL
- ALB and target groups
- Security groups

**`outputs.tf`**: Output values
- ALB DNS name
- RDS endpoint
- EC2 instance IPs
- VPC information

**`terraform.tfvars`**: Variable values (LOCAL ONLY)
- AWS region
- CIDR blocks
- Instance types
- Database credentials
- **NEVER COMMIT** - contains secrets

---

## Configuration

### Step 1: Initialize Terraform

```bash
cd terraform

# Initialize Terraform (download providers)
terraform init

# Expected output
# Terraform has been successfully configured!
```

### Step 2: Create terraform.tfvars

```bash
# Copy example
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Required Variables** in `terraform.tfvars`:

```hcl
aws_region                    = "us-east-1"
environment                   = "production"
project_name                  = "intelliwealth"

# VPC Configuration
vpc_cidr_block               = "10.0.0.0/16"
availability_zones           = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs          = ["10.0.1.0/24", "10.0.2.0/24"]
private_app_subnet_cidrs     = ["10.0.11.0/24", "10.0.12.0/24"]
private_db_subnet_cidrs      = ["10.0.21.0/24", "10.0.22.0/24"]

# EC2 Configuration
instance_type                = "t3.medium"
key_name                     = "your-ec2-key-pair"
min_size                     = 2
desired_capacity             = 2
max_size                     = 4

# Database Configuration
db_instance_class            = "db.t3.small"
db_allocated_storage         = 100
db_engine_version            = "16.1"
db_username                  = "postgres"
db_password                  = "strong_password_here"

# Domain Configuration
domain_name                  = "yourdomain.com"
certificate_arn              = "arn:aws:acm:us-east-1:..."
```

### Step 3: Validate Configuration

```bash
# Validate syntax
terraform validate

# Expected output
# Success! The configuration is valid.
```

### Step 4: Plan Deployment

```bash
# Preview changes
terraform plan -out=tfplan

# Review output carefully
# Shows all resources that will be created
```

---

## Variables

### Input Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aws_region` | string | "us-east-1" | AWS region |
| `environment` | string | "production" | Environment name |
| `project_name` | string | "intelliwealth" | Project name |
| `vpc_cidr_block` | string | "10.0.0.0/16" | VPC CIDR range |
| `availability_zones` | list | ["us-east-1a", "us-east-1b"] | Availability zones |
| `instance_type` | string | "t3.medium" | EC2 instance type |
| `db_instance_class` | string | "db.t3.small" | RDS instance class |
| `db_allocated_storage` | number | 100 | RDS storage in GB |
| `db_username` | string | "postgres" | RDS master user |
| `db_password` | string | "" | RDS master password |

### Output Values

| Output | Description |
|--------|-------------|
| `vpc_id` | VPC ID |
| `alb_dns_name` | ALB DNS name (for Route53) |
| `rds_endpoint` | RDS endpoint address |
| `rds_port` | RDS port number |
| `security_group_ids` | Security group IDs |
| `autoscaling_group_name` | Auto Scaling Group name |

---

## Deployment

### Full Deployment (from scratch)

```bash
cd terraform

# 1. Initialize
terraform init

# 2. Plan
terraform plan -out=tfplan

# 3. Review plan output
# Carefully review all resources to be created

# 4. Apply
terraform apply tfplan

# 5. Copy outputs for later use
terraform output > ../deployment-outputs.txt
```

### Partial Deployment (specific resources)

```bash
# Deploy only VPC and networking
terraform apply -target=aws_vpc.main

# Deploy only EC2
terraform apply -target=aws_autoscaling_group.app
```

### Updating Deployment

```bash
# Modify variables in terraform.tfvars

# Plan changes
terraform plan

# Apply changes
terraform apply
```

---

## AWS Resources

### VPC & Networking

**VPC**: `intelliwealth-vpc`
- CIDR: 10.0.0.0/16
- DNS resolution enabled
- DNS hostnames enabled

**Internet Gateway**: `intelliwealth-igw`
- Attached to VPC
- Routes external traffic

**NAT Gateways**: 2 (one per AZ)
- Elastic IPs allocated
- Route private traffic outbound

### Subnets (Multi-AZ)

| Subnet | CIDR | AZ | Type | Purpose |
|--------|------|-----|------|---------|
| Public-1a | 10.0.1.0/24 | us-east-1a | Public | NAT Gateway |
| Public-1b | 10.0.2.0/24 | us-east-1b | Public | NAT Gateway |
| AppPrivate-1a | 10.0.11.0/24 | us-east-1a | Private | EC2 (Frontend, Backend) |
| AppPrivate-1b | 10.0.12.0/24 | us-east-1b | Private | EC2 (Frontend, Backend) |
| DbPrivate-1a | 10.0.21.0/24 | us-east-1a | Private | RDS Primary |
| DbPrivate-1b | 10.0.22.0/24 | us-east-1b | Private | RDS Standby |

### Application Load Balancer

**ALB**: `intelliwealth-alb`
- Scheme: Internet-facing
- Ports: 80 (HTTP redirect) and 443 (HTTPS)
- Listeners:
  - 80 → 443 redirect
  - 443 → Target Groups based on path

**Target Groups**:
- `frontend-tg` (port 80) - Frontend instances
- `portfolio-tg` (port 8000) - Portfolio service
- `market-tg` (port 8001) - Market service

### EC2 Auto Scaling

**Auto Scaling Group**: `intelliwealth-asg`
- Min: 2 instances
- Desired: 2 instances
- Max: 4 instances
- Instance type: t3.medium (configurable)
- Availability zones: us-east-1a, us-east-1b
- Health check: ELB (30 second interval)
- Termination policy: Default
- Scaling policies:
  - Scale up if CPU > 70%
  - Scale down if CPU < 40%

### RDS PostgreSQL

**DB Instance**: `intelliwealth-db`
- Engine: PostgreSQL 16
- Instance class: db.t3.small (configurable)
- Storage: 100 GB gp3 (auto-scaling enabled)
- Multi-AZ: Enabled
  - Primary: AppPrivate-1a subnet
  - Standby: AppPrivate-1b subnet
- Backup retention: 30 days
- Enhanced monitoring: Enabled (1-minute granularity)
- Performance Insights: Enabled
- Encryption: Enabled (AWS KMS)

### ElastiCache Redis (Optional)

**Redis Cluster**: `intelliwealth-redis`
- Engine: Redis 7
- Node type: cache.t3.micro
- Number of cache nodes: 2 (Multi-AZ)
- Automatic failover: Enabled
- Encryption in transit: Enabled (TLS)
- Encryption at rest: Enabled (KMS)
- Subnet group: Private DB subnets
- Security group: Redis SG (6379 from App SG)

---

## Networking

### Route Tables

**Public Route Table**:
```
Destination    | Target
───────────────|────────────────
10.0.0.0/16    | Local
0.0.0.0/0      | Internet Gateway
```

**Private Route Table (1a)**:
```
Destination    | Target
───────────────|────────────────
10.0.0.0/16    | Local
0.0.0.0/0      | NAT Gateway 1a
```

**Private Route Table (1b)**:
```
Destination    | Target
───────────────|────────────────
10.0.0.0/16    | Local
0.0.0.0/0      | NAT Gateway 1b
```

### DNS Resolution

**Route53 Record**:
```
Name: yourdomain.com
Type: A (Alias)
Target: ALB DNS name
Evaluate Target Health: Yes
```

---

## Security Groups

### ALB Security Group
```
Inbound:
  - 80 (HTTP) from 0.0.0.0/0
  - 443 (HTTPS) from 0.0.0.0/0

Outbound:
  - All traffic to 0.0.0.0/0
```

### EC2 Security Group
```
Inbound:
  - 80 (HTTP) from ALB SG
  - 8000 (Portfolio) from ALB SG
  - 8001 (Market) from ALB SG
  - 22 (SSH) from Admin IP (optional)

Outbound:
  - All traffic to 0.0.0.0/0
```

### RDS Security Group
```
Inbound:
  - 5432 (PostgreSQL) from EC2 SG only

Outbound:
  - None (typically)
```

### Redis Security Group (Optional)
```
Inbound:
  - 6379 (Redis) from EC2 SG only

Outbound:
  - None (typically)
```

---

## Auto Scaling

### Scaling Policies

**Target Tracking (CPU)**:
- Target: 70% average CPU
- Scale-up: +1 instance when CPU > 70%
- Scale-down: -1 instance when CPU < 40%
- Cooldown: 300 seconds

**Lifecycle Hooks** (optional):
- Before terminating: Drain connections (30 second grace period)
- After launching: Run initialization scripts

### Monitoring Scaling

```bash
# View Auto Scaling Group
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names intelliwealth-asg

# View scaling history
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name intelliwealth-asg

# View desired capacity changes
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name intelliwealth-asg \
  --desired-capacity 3
```

---

## Monitoring

### CloudWatch Metrics

**EC2 Metrics**:
- CPU Utilization
- Network In/Out
- EBS Read/Write Ops

**RDS Metrics**:
- CPU Utilization
- Database Connections
- IOPS
- Storage Used
- Replica Lag

**ALB Metrics**:
- Request Count
- Target Response Time
- HTTP 4xx/5xx Errors
- Active Connections

---

## Maintenance

### Updating Infrastructure

```bash
# 1. Update variables in terraform.tfvars
# Example: change instance type
# instance_type = "t3.large"

# 2. Plan changes
terraform plan

# 3. Review changes carefully
# Terraform will show what will be modified/replaced

# 4. Apply changes
terraform apply
```

### Scaling Up/Down

```bash
# Increase desired capacity
terraform apply -var="desired_capacity=3"

# Decrease desired capacity
terraform apply -var="desired_capacity=2"
```

### Backup & Recovery

**RDS Snapshots**:
```bash
# Automatic snapshots (30-day retention)
aws rds describe-db-snapshots \
  --db-instance-identifier intelliwealth-db

# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier intelliwealth-db \
  --db-snapshot-identifier intelliwealth-snapshot-$(date +%Y%m%d)

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier intelliwealth-db-restored \
  --db-snapshot-identifier intelliwealth-snapshot-20240115
```

---

## Disaster Recovery

### RTO (Recovery Time Objective)

| Component | RTO | Method |
|-----------|-----|--------|
| EC2 | < 5 min | Auto Scaling Group recreates failed instances |
| RDS | < 2 min | Multi-AZ automatic failover |
| Redis | < 1 min | Multi-AZ automatic failover |
| ALB | < 1 min | AWS managed |

### RPO (Recovery Point Objective)

| Component | RPO |
|-----------|-----|
| RDS | 5 minutes (backup frequency) |
| EC2 | Stateless (no recovery needed) |
| Redis | Configurable (default 60 sec snapshots) |

### Failover Testing

```bash
# Test RDS failover
aws rds reboot-db-instance \
  --db-instance-identifier intelliwealth-db \
  --force-failover

# Monitor failover (2 minutes typical)
aws rds describe-db-instances \
  --db-instance-identifier intelliwealth-db
```

---

## Cleanup (Destroy Infrastructure)

```bash
# ⚠️ WARNING: This will delete all infrastructure

# Plan destruction
terraform plan -destroy

# Destroy infrastructure
terraform destroy

# Confirm deletion by typing "yes"
```

---

**Last Updated**: May 2026  
**Maintainer**: Infrastructure Team

---

## Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Best Practices](https://docs.aws.amazon.com/general/latest/gr/aws-best-practices.html)
- [Terraform Best Practices](https://www.terraform.io/language/settings/terraform-cloud)

Set these vars (for example in `terraform.tfvars`):

```hcl
enable_default_vpc_rds_peering = true
existing_rds_sg_id             = "sg-xxxxxxxxxxxxxxxxx"
# OR
existing_rds_instance_identifier = "your-rds-identifier"
```

Optional: if your RDS subnets do not use default VPC main route table, set explicit route table IDs:

```hcl
default_vpc_route_table_ids = ["rtb-aaaa", "rtb-bbbb"]
```

## Existing ACM / Existing 443 Listener Modes

If you already have an ACM cert and/or HTTPS listener:

```hcl
create_acm_certificate      = false
existing_acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/..."

create_https_listener       = false
existing_https_listener_arn = "arn:aws:elasticloadbalancing:..."
```
