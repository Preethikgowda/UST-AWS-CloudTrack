# Networking Design

**VPC Architecture, Routing, and Network Segmentation**

---

## Table of Contents

1. [VPC Architecture](#vpc-architecture)
2. [Subnets & Routing](#subnets--routing)
3. [Internet Connectivity](#internet-connectivity)
4. [Network Segmentation](#network-segmentation)
5. [Traffic Flow](#traffic-flow)
6. [Network Monitoring](#network-monitoring)

---

## VPC Architecture

### Custom VPC Design

**VPC Name**: intelliwealth-vpc  
**CIDR Block**: 10.0.0.0/16  
**Region**: us-east-1  
**Availability Zones**: us-east-1a, us-east-1b

### IP Address Allocation

```
10.0.0.0/16 (Total: 65,536 addresses)
├── 10.0.0.0/18    (16,384 addresses) - Reserved for future use
├── 10.0.64.0/18   (16,384 addresses) - Reserved for future use
│
├── Public Subnets (2 × /24 = 512 addresses)
│   ├── 10.0.1.0/24   (256 addresses)  - us-east-1a public
│   └── 10.0.2.0/24   (256 addresses)  - us-east-1b public
│
├── Private App Subnets (2 × /24 = 512 addresses)
│   ├── 10.0.11.0/24  (256 addresses)  - us-east-1a private
│   └── 10.0.12.0/24  (256 addresses)  - us-east-1b private
│
└── Private DB Subnets (2 × /24 = 512 addresses)
    ├── 10.0.21.0/24  (256 addresses)  - us-east-1a private
    └── 10.0.22.0/24  (256 addresses)  - us-east-1b private
```

### Subnet Allocation Details

| Subnet | CIDR | Usable IPs | AZ | Type | Purpose |
|--------|------|-----------|-----|------|---------|
| public-1a | 10.0.1.0/24 | 251 | us-east-1a | Public | NAT Gateway |
| public-1b | 10.0.2.0/24 | 251 | us-east-1b | Public | NAT Gateway |
| private-app-1a | 10.0.11.0/24 | 251 | us-east-1a | Private | EC2 Instances |
| private-app-1b | 10.0.12.0/24 | 251 | us-east-1b | Private | EC2 Instances |
| private-db-1a | 10.0.21.0/24 | 251 | us-east-1a | Private | RDS Primary |
| private-db-1b | 10.0.22.0/24 | 251 | us-east-1b | Private | RDS Standby |

*Usable IPs exclude AWS-reserved addresses (network, broadcast, gateway, DNS, future)*

---

## Subnets & Routing

### Public Subnets (NAT Subnets)

**Purpose**: Host NAT Gateways for outbound traffic from private subnets

**Characteristics**:
- Direct route to Internet Gateway
- Elastic IPs for NAT Gateways
- No EC2 instances deployed here
- Enable auto-assign public IP: No

**Associations**:
- Internet Gateway → 0.0.0.0/0
- Local route → 10.0.0.0/16

### Route Table: public-rt

```
Destination      Prefix        Target              Status
─────────────────────────────────────────────────────────
10.0.0.0/16      10.0.0.0/16   Local              active
0.0.0.0/0        default       igw-xxxxxxxxx      active
```

**Internet Gateway**: intelliwealth-igw
- Attached to intelliwealth-vpc
- Provides internet connectivity for public subnets

---

### Private Application Subnets

**Purpose**: Host EC2 instances (Frontend, Portfolio Service, Market Service)

**Characteristics**:
- No direct internet access
- Outbound via NAT Gateway in same AZ
- No public IP addresses (internal only)
- Enable auto-assign public IP: No

**Associations**:
- NAT Gateway in same AZ for outbound traffic

### Route Table: private-rt-1a

```
Destination      Prefix        Target                          Status
──────────────────────────────────────────────────────────────────
10.0.0.0/16      10.0.0.0/16   Local                          active
0.0.0.0/0        default       nat-xxxxxxxxx (in public-1a)   active
```

### Route Table: private-rt-1b

```
Destination      Prefix        Target                          Status
──────────────────────────────────────────────────────────────────
10.0.0.0/16      10.0.0.0/16   Local                          active
0.0.0.0/0        default       nat-xxxxxxxxx (in public-1b)   active
```

---

### Private Database Subnets

**Purpose**: Host RDS PostgreSQL database

**Characteristics**:
- No internet access (no route to IGW or NAT)
- Only internal VPC communication
- RDS multi-AZ configured across both subnets
- Enable auto-assign public IP: No

**Associations**:
- RDS Subnet Group (multi-AZ)

### Route Table: private-db-rt

```
Destination      Prefix        Target    Status
──────────────────────────────────────────
10.0.0.0/16      10.0.0.0/16   Local    active
```

*No internet route - database only accessible from within VPC*

---

## Internet Connectivity

### Inbound Traffic (Public → Private)

```
Internet (Client)
    ↓ HTTPS
Route53 DNS Resolution
    ↓
ALB (Internet-facing)
    └─ Public Subnets (10.0.1.0/24, 10.0.2.0/24)
    ↓
Application Load Balancer
    ├─ Health Check
    ├─ TLS Termination
    └─ Path-based Routing
    ↓
EC2 Instances (Private App Subnets)
    ├─ Frontend (Nginx port 80)
    ├─ Portfolio Service (FastAPI port 8000)
    └─ Market Service (FastAPI port 8001)
    ↓
RDS / Redis (Private DB Subnets)
```

### Outbound Traffic (Private → Public)

```
EC2 Instances (Private App Subnets)
    ↓ Outbound Request (e.g., Docker pull, package updates)
NAT Gateway (in Public Subnet, same AZ)
    ├─ Translates private IP → Elastic IP
    └─ Connection state maintained
    ↓
Internet Gateway
    ↓
Internet (0.0.0.0/0)
```

### ALB Placement

**ALB Subnets**: public-1a, public-1b

**Rationale**:
- Internet-facing endpoint needs public IP
- Automatically assigned Elastic IPs by AWS
- Directly connected to Internet Gateway
- Redundancy across both AZs

**Note**: ALB itself is internet-facing, but it routes traffic to private EC2 instances

---

## Network Segmentation

### Security Group Hierarchy

```
┌──────────────────────────────────────────────────────────┐
│                   Internet (0.0.0.0/0)                   │
└────────────────┬─────────────────────────────────────────┘
                 │ HTTPS Port 443
                 │
        ┌────────▼──────────┐
        │  ALB Security     │
        │  Group (alb-sg)   │
        │                   │
        │  Inbound:         │
        │  - 80 (HTTP)      │
        │  - 443 (HTTPS)    │
        │  From: 0.0.0.0/0  │
        │                   │
        │  Outbound:        │
        │  - All to ALL     │
        └────────┬──────────┘
                 │
                 ├─────────────────┬───────────────┐
                 │                 │               │
        ┌────────▼──────────┐  ┌────▼────────┐  ┌─▼─────────────┐
        │  EC2 Security     │  │ EC2 Security │  │ EC2 Security  │
        │  Group (ec2-sg)   │  │ Group (ec2   │  │ Group (ec2    │
        │                   │  │ -sg)         │  │ -sg)          │
        │  Inbound:         │  │              │  │               │
        │  - 80 (HTTP)      │  │ Inbound:     │  │ Inbound:      │
        │  - 8000 (Portfolio)  │ - 80, 8000   │  │ - 80, 8000    │
        │  - 8001 (Market)  │  │ - 8001       │  │ - 8001        │
        │  - 22 (SSH)       │  │ From: alb-sg │  │ From: alb-sg  │
        │  From: alb-sg     │  │              │  │               │
        │                   │  │ Outbound:    │  │ Outbound:     │
        │  Outbound:        │  │ - All to ALL │  │ - All to ALL  │
        │  - All to ALL     │  │              │  │               │
        │                   │  │              │  │               │
        └────────┬──────────┘  └────┬─────────┘  └─┬──────────────┘
                 │                  │              │
                 ├──────────────────┼──────────────┤
                 │                  │              │
        ┌────────▼──────────────────▼──────────────▼───────────┐
        │              RDS Security Group (rds-sg)            │
        │                                                      │
        │  Inbound:                                           │
        │  - 5432 (PostgreSQL) From: ec2-sg only             │
        │                                                      │
        │  Outbound:                                          │
        │  - None                                             │
        └──────────────────────────────────────────────────────┘
```

### Security Group Rules

#### ALB Security Group (alb-sg)

| Direction | Protocol | Port(s) | CIDR | Description |
|-----------|----------|---------|------|-------------|
| Inbound | TCP | 80 | 0.0.0.0/0 | HTTP from Internet |
| Inbound | TCP | 443 | 0.0.0.0/0 | HTTPS from Internet |
| Outbound | All | All | 0.0.0.0/0 | To target groups |

#### EC2 Security Group (ec2-sg)

| Direction | Protocol | Port(s) | Source | Description |
|-----------|----------|---------|--------|-------------|
| Inbound | TCP | 80 | alb-sg | Frontend (Nginx) |
| Inbound | TCP | 8000 | alb-sg | Portfolio Service |
| Inbound | TCP | 8001 | alb-sg | Market Service |
| Inbound | TCP | 22 | 0.0.0.0/0 | SSH (optional, restrict to admin IP) |
| Outbound | All | All | 0.0.0.0/0 | Internet access (Docker, pip, etc) |

#### RDS Security Group (rds-sg)

| Direction | Protocol | Port(s) | Source | Description |
|-----------|----------|---------|--------|-------------|
| Inbound | TCP | 5432 | ec2-sg | PostgreSQL from EC2 |
| Outbound | None | N/A | N/A | No outbound needed |

#### Redis Security Group (redis-sg) - Optional

| Direction | Protocol | Port(s) | Source | Description |
|-----------|----------|---------|--------|-------------|
| Inbound | TCP | 6379 | ec2-sg | Redis from EC2 |
| Outbound | None | N/A | N/A | No outbound needed |

---

## Traffic Flow

### Request Flow (Frontend to User)

```
1. User Types URL: https://yourdomain.com
   ↓
2. Browser DNS Query → Route53
   (yourdomain.com → 54.123.45.67)
   ↓
3. Browser HTTPS Connection to ALB
   Target: 54.123.45.67:443
   ↓
4. ALB TLS Handshake
   Certificate: yourdomain.com (from ACM)
   ↓
5. ALB Receives HTTPS Request
   ↓
6. ALB Listener (port 443)
   Rule: / → frontend-tg
   ↓
7. ALB Forwards to EC2 (HTTP)
   Target: 10.0.11.5:80 (or 10.0.12.5:80)
   ↓
8. EC2 Nginx Container
   Receives HTTP request
   ↓
9. Nginx Routes to React App
   Returns HTML/CSS/JS
   ↓
10. ALB Returns to Client (HTTPS)
    ↓
11. Browser Renders Page
```

### Internal Service Communication

```
Frontend (Browser)
    ↓ HTTPS to ALB
ALB (Internet-facing)
    │ Path: /api/v1/portfolio
    ↓
Portfolio Service Target Group
    │ Sends request to EC2:8000
    ↓
EC2 (Private App Subnet)
    │ Portfolio Service (FastAPI)
    │
    ├─→ RDS PostgreSQL
    │   (10.0.21.4:5432)
    │   Query: SELECT * FROM portfolios
    │   ↓ Response
    │
    └─→ Redis Cache (optional)
        (cached market data)
```

### Database Access Pattern

```
EC2 Instance (Private App Subnet)
    Application (Django/FastAPI)
    ↓ 
    SQLAlchemy ORM
    ↓
    Connection String: postgresql://user:pass@rds-endpoint:5432/intelliwealth
    ↓
    EC2 SG allows → 5432 to RDS SG
    ↓
    RDS PostgreSQL (Private DB Subnet)
    ↓
    Query Execution
    ↓
    Response → EC2
```

---

## Network Monitoring

### VPC Flow Logs

**Purpose**: Capture network traffic for analysis and troubleshooting

**Enable for**:
- VPC (all ENIs)
- Individual subnets
- Specific security groups

**Traffic Captured**:
- Source/destination IP and port
- Protocol (TCP/UDP)
- Packets/bytes transferred
- Accepted or rejected traffic

**Example Flow Log Entry**:
```
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
2 123456789012 eni-1a2b3c4d 10.0.11.5 10.0.21.4 50923 5432 6 2 120 1612345678 1612345680 ACCEPT OK
```

### CloudWatch Network Metrics

| Metric | Description | Normal Range |
|--------|-------------|--------------|
| NetworkIn | Bytes received by instance | Variable |
| NetworkOut | Bytes transmitted | Variable |
| NetworkPacketsIn | Packets received | Variable |
| NetworkPacketsOut | Packets transmitted | Variable |
| BytesProcessed | ALB bytes processed | Variable |
| RequestCount | ALB request count | Depends on traffic |

### DNS Monitoring

**Route53 Health Checks**:
- Monitor ALB endpoint
- Failover to backup if needed
- CloudWatch metrics for DNS queries

---

## Network Best Practices

### Design Principles

✅ **Do**:
- Use private subnets for compute and database
- Route all inbound traffic through ALB
- Restrict security groups to minimum required ports
- Separate subnets by function (public, app, database)
- Use VPC Flow Logs for troubleshooting
- Monitor network metrics via CloudWatch

❌ **Don't**:
- Expose RDS directly to public subnet
- Allow SSH from 0.0.0.0/0 (always restrict)
- Disable VPC Flow Logs in production
- Mix subnets across AZs unnecessarily
- Hardcode IP addresses in security groups
- Use default VPC for production workloads

---

**Last Updated**: May 2026  
**Architect**: Network Infrastructure Team
