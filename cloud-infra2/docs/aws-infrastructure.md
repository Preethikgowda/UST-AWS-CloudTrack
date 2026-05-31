# AWS Infrastructure Documentation

**Complete AWS Deployment Architecture for IntelliWealth**

---

## Table of Contents

1. [Infrastructure Overview](#infrastructure-overview)
2. [VPC Architecture](#vpc-architecture)
3. [Network Topology](#network-topology)
4. [Resource Configuration](#resource-configuration)
5. [Deployment Architecture](#deployment-architecture)
6. [High Availability](#high-availability)
7. [Disaster Recovery](#disaster-recovery)
8. [Cost Optimization](#cost-optimization)

---

## Infrastructure Overview

### AWS Services Used

| Service | Purpose | Details |
|---------|---------|---------|
| **VPC** | Network isolation | Custom CIDR 10.0.0.0/16, multi-AZ |
| **EC2** | Compute | t3.medium, Auto Scaling Group |
| **RDS** | Database | PostgreSQL 16, Multi-AZ, 100GB |
| **ElastiCache** | Caching | Redis 7, optional, Multi-AZ |
| **ALB** | Load balancing | Internet-facing, HTTPS, path-based routing |
| **Route53** | DNS | Domain management, health checks |
| **ACM** | TLS/SSL | HTTPS certificates, auto-renewal |
| **CloudWatch** | Monitoring | Logs, metrics, alarms |
| **IAM** | Access control | Roles, policies for EC2 |
| **EBS** | Storage | gp3 volumes with auto-scaling |

---

## VPC Architecture

### VPC Design

**VPC: intelliwealth-vpc**
- **CIDR Block**: 10.0.0.0/16 (65,536 IP addresses)
- **DNS Resolution**: Enabled
- **DNS Hostnames**: Enabled
- **Tenancy**: Default (shared hardware)

### Subnets

#### Public Subnets (NAT Gateways)

| Subnet | CIDR | AZ | Purpose | Route Table |
|--------|------|-----|---------|-------------|
| public-1a | 10.0.1.0/24 | us-east-1a | NAT Gateway 1a | public-rt |
| public-1b | 10.0.2.0/24 | us-east-1b | NAT Gateway 1b | public-rt |

**Route Table: public-rt**
```
Destination    | Target
─────────────────────────────────
10.0.0.0/16    | Local
0.0.0.0/0      | Internet Gateway
```

#### Private Application Subnets

| Subnet | CIDR | AZ | Purpose | Route Table |
|--------|------|-----|---------|-------------|
| private-app-1a | 10.0.11.0/24 | us-east-1a | EC2 instances | private-rt-1a |
| private-app-1b | 10.0.12.0/24 | us-east-1b | EC2 instances | private-rt-1b |

**Route Table: private-rt-1a**
```
Destination    | Target
─────────────────────────────────
10.0.0.0/16    | Local
0.0.0.0/0      | NAT Gateway 1a
```

**Route Table: private-rt-1b**
```
Destination    | Target
─────────────────────────────────
10.0.0.0/16    | Local
0.0.0.0/0      | NAT Gateway 1b
```

#### Private Database Subnets

| Subnet | CIDR | AZ | Purpose | Route Table |
|--------|------|-----|---------|-------------|
| private-db-1a | 10.0.21.0/24 | us-east-1a | RDS Primary | private-db-rt |
| private-db-1b | 10.0.22.0/24 | us-east-1b | RDS Standby | private-db-rt |

**Route Table: private-db-rt**
```
Destination    | Target
─────────────────────────────────
10.0.0.0/16    | Local
```
(No outbound internet access for database)

### Internet Gateway

**Gateway: intelliwealth-igw**
- Attached to VPC
- Routes external traffic from public subnets
- Enables EC2 instances in public subnets to reach the internet

### NAT Gateways

**NAT Gateway 1a** (in public-1a)
- Elastic IP allocated
- Routes outbound traffic from private-app-1a to internet
- Single point of failure for 1a instances

**NAT Gateway 1b** (in public-1b)
- Elastic IP allocated
- Routes outbound traffic from private-app-1b to internet
- Single point of failure for 1b instances

---

## Network Topology

### Visual Architecture

```
                    ┌──────────────────────────────────────────┐
                    │            Internet (0.0.0.0/0)           │
                    └─────────────────┬──────────────────────────┘
                                      │
                    ┌─────────────────▼──────────────────────────┐
                    │         Route53 (DNS)                      │
                    │     yourdomain.com → ALB IP              │
                    └─────────────────┬──────────────────────────┘
                                      │ HTTPS
                    ┌─────────────────▼──────────────────────────┐
                    │  Application Load Balancer (ALB)          │
                    │  Ports: 80 (HTTP→HTTPS), 443 (HTTPS)      │
                    │  ACM Certificate: yourdomain.com          │
                    │  ┌────────────────────────────────────┐   │
                    │  │ Listener 80 → Listener 443         │   │
                    │  │ Listener 443:                      │   │
                    │  │  / → Frontend TG (port 80)        │   │
                    │  │  /api/v1/portfolio → Port 8000    │   │
                    │  │  /api/v1/market → Port 8001       │   │
                    │  └────────────────────────────────────┘   │
                    │  Availability Zones: us-east-1a, us-east-1b │
                    └─────────────────┬──────────────────────────┘
                                      │
                ┌─────────────────────┴─────────────────────────┐
                │                                               │
    ┌───────────▼──────────┐                        ┌──────────▼──────────┐
    │  Availability Zone   │                        │ Availability Zone   │
    │      us-east-1a      │                        │     us-east-1b      │
    ├──────────────────────┤                        ├─────────────────────┤
    │                      │                        │                     │
    │  Public Subnet       │                        │ Public Subnet       │
    │  10.0.1.0/24        │                        │ 10.0.2.0/24        │
    │  ┌────────────────┐  │                        │ ┌───────────────┐   │
    │  │  NAT Gateway   │  │                        │ │ NAT Gateway   │   │
    │  │  Elastic IP    │  │                        │ │ Elastic IP    │   │
    │  └────────────────┘  │                        │ └───────────────┘   │
    │                      │                        │                     │
    ├──────────────────────┤                        ├─────────────────────┤
    │                      │                        │                     │
    │  Private App Subnet  │                        │ Private App Subnet  │
    │  10.0.11.0/24       │                        │ 10.0.12.0/24       │
    │  ┌────────────────┐  │                        │ ┌───────────────┐   │
    │  │  EC2 Instance  │  │                        │ │ EC2 Instance  │   │
    │  │  (Frontend)    │  │                        │ │ (Frontend)    │   │
    │  │  :80           │  │                        │ │ :80           │   │
    │  └────────────────┘  │                        │ └───────────────┘   │
    │  ┌────────────────┐  │                        │ ┌───────────────┐   │
    │  │  EC2 Instance  │  │                        │ │ EC2 Instance  │   │
    │  │  (Backend)     │  │                        │ │ (Backend)     │   │
    │  │  :8000,:8001   │  │                        │ │ :8000,:8001   │   │
    │  └────────────────┘  │                        │ └───────────────┘   │
    │                      │                        │                     │
    ├──────────────────────┤                        ├─────────────────────┤
    │                      │                        │                     │
    │  Private DB Subnet   │                        │ Private DB Subnet   │
    │  10.0.21.0/24       │                        │ 10.0.22.0/24       │
    │  ┌────────────────┐  │                        │ ┌───────────────┐   │
    │  │  RDS Primary   │  │                        │ │ RDS Standby   │   │
    │  │  Port 5432     │  │                        │ │ Port 5432     │   │
    │  └────────────────┘  │                        │ └───────────────┘   │
    │                      │                        │                     │
    └──────────────────────┘                        └─────────────────────┘
    │
    │ RDS Replication (continuous)
    │
    ┌─────────────────────────────────────────────────────────┐
    │        RDS Database (Multi-AZ Configuration)            │
    │  Engine: PostgreSQL 16                                  │
    │  Primary in 1a ↔ Standby in 1b (automatic failover)    │
    │  Storage: 100 GB gp3 (auto-scaling)                    │
    │  Backups: 30-day retention                             │
    └─────────────────────────────────────────────────────────┘

    Optional:
    ┌─────────────────────────────────────────────────────────┐
    │     ElastiCache Redis (Multi-AZ Configuration)          │
    │  Engine: Redis 7                                         │
    │  Nodes: 2 (one per AZ)                                   │
    │  Port: 6379 (accessible from private subnets)           │
    └─────────────────────────────────────────────────────────┘
```

---

## Resource Configuration

### EC2 Instances

**Auto Scaling Group Configuration**

| Parameter | Value |
|-----------|-------|
| Name | intelliwealth-asg |
| Min Size | 2 |
| Desired Capacity | 2 |
| Max Size | 4 |
| Instance Type | t3.medium (2 vCPU, 4 GB RAM) |
| AMI | Ubuntu 22.04 LTS |
| Root Volume | 50 GB (gp3) |
| Availability Zones | us-east-1a, us-east-1b |
| Subnets | private-app-1a, private-app-1b |
| Health Check | ELB (30 sec interval) |
| Unhealthy Threshold | 3 failures |

**Scaling Policies**

| Metric | Target | Action |
|--------|--------|--------|
| CPU Utilization | 70% (target tracking) | Scale up if > 70%, down if < 40% |
| Cooldown | 300 seconds | Prevent rapid scaling |

**EC2 Security Group**

| Direction | Port | Protocol | Source | Purpose |
|-----------|------|----------|--------|---------|
| Inbound | 80 | TCP | ALB SG | Frontend web server |
| Inbound | 8000 | TCP | ALB SG | Portfolio service |
| Inbound | 8001 | TCP | ALB SG | Market service |
| Inbound | 22 | TCP | Admin IP | SSH access (optional) |
| Outbound | All | All | 0.0.0.0/0 | Outbound internet access |

### RDS PostgreSQL

**Instance Configuration**

| Parameter | Value |
|-----------|-------|
| Identifier | intelliwealth-db |
| Engine | PostgreSQL 16.1 |
| Instance Class | db.t3.small (2 vCPU, 2 GB RAM) |
| Storage | 100 GB (gp3, auto-scaling) |
| Multi-AZ | Enabled |
| Backup Retention | 30 days |
| Preferred Backup Window | 03:00-04:00 UTC |
| Preferred Maintenance Window | sun:04:00-sun:05:00 UTC |
| Encryption | Enabled (AWS KMS) |
| Enhanced Monitoring | 1-minute granularity |
| Performance Insights | Enabled |

**Database Configuration**

| Parameter | Value |
|-----------|-------|
| Database Name | intelliwealth |
| Master Username | postgres |
| Master Password | (from AWS Secrets Manager) |
| Port | 5432 |
| Subnet Group | private-db-1a, private-db-1b |
| Security Group | rds-sg (5432 from ec2-sg) |

**RDS Security Group**

| Direction | Port | Protocol | Source | Purpose |
|-----------|------|----------|--------|---------|
| Inbound | 5432 | TCP | EC2 SG | PostgreSQL access |
| Outbound | - | - | - | None |

### Application Load Balancer

**ALB Configuration**

| Parameter | Value |
|-----------|-------|
| Name | intelliwealth-alb |
| Scheme | internet-facing |
| Type | Application |
| Subnets | public-1a, public-1b |
| Security Groups | alb-sg |
| Availability Zones | us-east-1a, us-east-1b |

**Listeners**

| Port | Protocol | Target | Action |
|------|----------|--------|--------|
| 80 | HTTP | - | Redirect to 443 |
| 443 | HTTPS | Multiple | Path-based routing |

**Target Groups**

| Name | Port | Protocol | HC Path | HC Interval |
|------|------|----------|---------|-------------|
| frontend-tg | 80 | HTTP | /health | 30s |
| portfolio-tg | 8000 | HTTP | /health | 30s |
| market-tg | 8001 | HTTP | /health | 30s |

**Path-Based Routing**

```
/ (root) → frontend-tg
/api/v1/auth → portfolio-tg
/api/v1/customers → portfolio-tg
/api/v1/portfolio → portfolio-tg
/api/v1/market → market-tg
```

**ALB Security Group**

| Direction | Port | Protocol | Source | Purpose |
|-----------|------|----------|--------|---------|
| Inbound | 80 | TCP | 0.0.0.0/0 | HTTP from internet |
| Inbound | 443 | TCP | 0.0.0.0/0 | HTTPS from internet |
| Outbound | All | All | 0.0.0.0/0 | To target groups |

---

## Deployment Architecture

### Deployment Flow

```
┌─────────────────────────────────┐
│  1. Terraform Initialization    │
│     - AWS credentials           │
│     - Terraform backend         │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  2. Create VPC & Networking     │
│     - VPC with CIDR 10.0.0.0/16 │
│     - 6 Subnets across 2 AZs    │
│     - Internet Gateway          │
│     - NAT Gateways              │
│     - Route tables              │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  3. Create Security Groups      │
│     - ALB SG                    │
│     - EC2 SG                    │
│     - RDS SG                    │
│     - Redis SG                  │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  4. Create ALB                  │
│     - Internet-facing           │
│     - Multi-AZ                  │
│     - Target groups             │
│     - HTTPS listener            │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  5. Create RDS Database         │
│     - PostgreSQL 16             │
│     - Multi-AZ setup            │
│     - Backup enabled            │
│     - Encryption enabled        │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  6. Create Auto Scaling Group   │
│     - Launch template           │
│     - Min 2, Desired 2, Max 4   │
│     - Scaling policies          │
│     - Health checks             │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  7. Create Optional Resources   │
│     - ElastiCache Redis         │
│     - CloudWatch alarms         │
│     - IAM roles                 │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  8. Configure Route53 DNS       │
│     - Create A record           │
│     - Point to ALB              │
│     - Health checks             │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  9. Deploy Containers to EC2    │
│     - Pull Docker images        │
│     - Start services            │
│     - Configure environment     │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  10. Validate Deployment        │
│      - Health checks            │
│      - ALB health               │
│      - Database connectivity    │
│      - API endpoints            │
└─────────────────────────────────┘
```

---

## High Availability

### Multi-AZ Architecture

```
┌────────────────────────────────────────────────────────┐
│              Availability Zone 1a (us-east-1a)         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  EC2 Instance (Frontend + Backend Services)           │
│  Auto Scaling Group Member                            │
│  ↓                                                     │
│  PostgreSQL Primary (RDS)                            │
│                                                        │
└────────────────────────────────────────────────────────┘
  ↔ Continuous Replication
┌────────────────────────────────────────────────────────┐
│              Availability Zone 1b (us-east-1b)         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  EC2 Instance (Frontend + Backend Services)           │
│  Auto Scaling Group Member                            │
│  ↓                                                     │
│  PostgreSQL Standby (RDS)                            │
│                                                        │
└────────────────────────────────────────────────────────┘

Benefits:
- Automatic failover if one AZ goes down
- Automatic instance replacement via ASG
- Database failover in < 2 minutes
- Minimum 99.95% availability (AWS SLA)
```

### Failover Scenarios

**EC2 Instance Fails**:
1. ALB health check detects failure (after 3 consecutive failures)
2. ASG removes instance from target group
3. ASG launches replacement instance
4. New instance joins target group
5. Recovery time: ~5 minutes

**Entire AZ Fails**:
1. ALB health check detects all instances in AZ are down
2. Traffic automatically routes to remaining AZ
3. ASG scales up to desired capacity if needed
4. Recovery time: ~5 minutes

**RDS Primary Fails**:
1. RDS detects failure
2. Promotes standby to new primary
3. Updates connection string (route via RDS endpoint)
4. Applications automatically connect to new primary
5. Recovery time: < 2 minutes

**Database Disk Full**:
1. Auto-scaling enabled on RDS
2. Automatically increases storage
3. No downtime during scaling
4. Monitoring alerts on growth rate

---

## Disaster Recovery

### Backup Strategy

**Automatic RDS Snapshots**
- Frequency: Daily
- Retention: 30 days
- Automatic backup window: 03:00-04:00 UTC
- Multi-AZ snapshot replication

**Manual Snapshots**
- Before major deployments
- For archival purposes
- Named with timestamp

**Point-in-Time Recovery**
- Available for 30 days
- Recover to any specific time
- Creates new RDS instance

### Recovery Procedures

**Restore from RDS Snapshot**

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier intelliwealth-db-restored \
  --db-snapshot-identifier intelliwealth-snapshot-20240115
```

**Restore from Point-in-Time**

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier intelliwealth-db \
  --target-db-instance-identifier intelliwealth-db-restored \
  --restore-time 2024-01-15T10:00:00Z
```

### RTO & RPO

| Component | RTO | RPO | Method |
|-----------|-----|-----|--------|
| EC2 | < 5 min | Stateless | Auto Scaling |
| RDS | < 2 min | 5 min | Multi-AZ failover |
| ALB | < 1 min | No data loss | AWS managed |
| Redis | < 1 min | Configurable | Multi-AZ failover |

---

## Cost Optimization

### Current Costs (Estimate)

| Service | Instance | Cost/Month |
|---------|----------|-----------|
| EC2 | 2x t3.medium | ~$60 |
| RDS | db.t3.small | ~$40 |
| Data Transfer | ~1 TB | ~$100 |
| ALB | 1x ALB | ~$16 |
| ElastiCache | cache.t3.micro (optional) | ~$20 |
| **Total** | | ~$240/month |

### Cost Saving Options

1. **Reserved Instances** (1-3 year commitment)
   - Savings: 30-70% on EC2 costs
   - Estimated: $18-40/month for 2x t3.medium

2. **Spot Instances** (interruptible, 70% discount)
   - For non-critical workloads
   - Mix with On-Demand for reliability

3. **Smaller Instances** (dev/staging)
   - t3.small instead of t3.medium
   - Savings: ~$30/month

4. **Consolidate Services** (single instance)
   - Run all services on one EC2
   - Requires careful resource planning

---

**Last Updated**: May 2026  
**Architect**: Cloud Infrastructure Team
