# Security Design

**Security Architecture, Best Practices, and Compliance**

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Network Security](#network-security)
3. [Access Control](#access-control)
4. [Data Protection](#data-protection)
5. [Secrets Management](#secrets-management)
6. [Compliance & Audit](#compliance--audit)
7. [Security Hardening](#security-hardening)
8. [Incident Response](#incident-response)

---

## Security Overview

### Security Layers

```
┌─────────────────────────────────────────────────┐
│  Layer 7 (Application)                          │
│  - Input validation                             │
│  - API authentication (JWT)                     │
│  - Authorization checks                         │
│  - Rate limiting                                │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│  Layer 4 (Transport)                            │
│  - TLS 1.2+ (HTTPS)                             │
│  - Certificate management (ACM)                 │
│  - Port filtering                               │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│  Layer 3 (Network)                              │
│  - VPC isolation                                │
│  - Security groups (stateful firewall)          │
│  - Network ACLs (stateless firewall)            │
│  - Private/Public subnets                       │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│  Layer 2 (Infrastructure)                       │
│  - IAM roles and policies                       │
│  - Encryption at rest (KMS)                     │
│  - EBS encryption                               │
│  - RDS encryption                               │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│  Layer 1 (Physical)                             │
│  - AWS data center security                     │
│  - Hardware isolation                           │
│  - Environmental controls                       │
└─────────────────────────────────────────────────┘
```

### Security Principles

1. **Least Privilege**: Minimal necessary permissions
2. **Defense in Depth**: Multiple security layers
3. **Assume Breach**: Design for potential compromise
4. **Encryption**: Protect data in transit and at rest
5. **Audit**: Log and monitor all access
6. **Automation**: Automated security checks
7. **Updates**: Regular patching and updates

---

## Network Security

### VPC Isolation

**Network Boundaries**:
- Custom VPC (10.0.0.0/16)
- Isolated from other VPCs (unless explicitly peered)
- All traffic filtered by security groups

**Internet Access Control**:
- Inbound: Only via ALB on ports 80/443
- Outbound: Private instances via NAT Gateway only
- No direct internet access to databases

### Security Groups

#### ALB Security Group

**Purpose**: Control internet-facing load balancer

**Inbound**:
```
Port 80 (HTTP) from 0.0.0.0/0
  → Redirects to HTTPS (443)

Port 443 (HTTPS) from 0.0.0.0/0
  → Forwarded to backend services
```

**Outbound**:
```
All traffic to 0.0.0.0/0
  → Can reach backend EC2 instances
  → Can reach external services (if needed)
```

#### EC2 Security Group

**Purpose**: Protect application servers

**Inbound Rules** (Least Privilege):
```
Port 80 (HTTP) from ALB SG
  → Nginx web server

Port 8000 (TCP) from ALB SG
  → Portfolio Service (FastAPI)

Port 8001 (TCP) from ALB SG
  → Market Service (FastAPI)

Port 22 (SSH) from Admin IP (CRITICAL: Restrict)
  → SSH access (SSH key authentication only)
```

**Outbound Rules**:
```
Port 443 (HTTPS) to 0.0.0.0/0
  → Docker image pulls from registry
  → Python package downloads
  → External API calls

Port 5432 (TCP) to RDS SG
  → Database queries
```

#### RDS Security Group

**Purpose**: Protect database

**Inbound Rules** (Highly Restricted):
```
Port 5432 (TCP) from EC2 SG only
  → PostgreSQL connections from application servers only
  → NO public access
```

**Outbound**:
```
None
  → Database initiates no outbound connections
```

#### Redis Security Group (Optional)

**Inbound Rules**:
```
Port 6379 (TCP) from EC2 SG only
  → Redis connections from application servers only
```

**Outbound**:
```
None
  → Cache initiates no outbound connections
```

### Network ACLs

**Default NACL Configuration**:
- Allow all inbound/outbound traffic within VPC
- Stateless (explicitly defined rules)
- Less commonly customized than security groups
- Applied at subnet level

**Custom Rules** (if implemented):
```
Public Subnet NACL:
  Inbound:  80 (HTTP), 443 (HTTPS) from 0.0.0.0/0
  Outbound: Ephemeral ports to 0.0.0.0/0

Private Subnet NACL:
  Inbound:  1024-65535 (ephemeral) from ALB
  Outbound: All to 0.0.0.0/0

Database Subnet NACL:
  Inbound:  5432 from Private EC2 SG
  Outbound: Minimal
```

---

## Access Control

### IAM Roles & Policies

#### EC2 Instance Role

**Purpose**: Allow EC2 instances to access AWS services

**Permissions Needed**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:intelliwealth/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:us-east-1:ACCOUNT:parameter/intelliwealth/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:ACCOUNT:log-group:/aws/ec2/intelliwealth/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Deployment Role

**Purpose**: Allow CI/CD pipeline to deploy infrastructure

**Permissions**:
- EC2, VPC, ALB management
- RDS operations
- IAM role creation
- CloudWatch access

```bash
# Minimum permissions
- ec2:*
- rds:*
- elasticache:*
- elbv2:*
- iam:CreateRole
- iam:PutRolePolicy
- iam:PassRole
```

### Authentication

#### API Authentication (JWT)

**Frontend → Backend Flow**:

```
1. User Login Request
   POST /api/v1/auth/login
   Body: { email, password }
   ↓
2. Portfolio Service validates credentials
   Checks against PostgreSQL
   ↓
3. Generate JWT Token
   Payload: { user_id, email, exp: now + 24h }
   Signed with HS256 secret
   ↓
4. Return token to frontend
   { access_token, token_type, expires_in }
   ↓
5. Frontend stores token (localStorage or sessionStorage)
   ↓
6. Subsequent requests include token
   Header: Authorization: Bearer <token>
   ↓
7. Backend validates token
   Checks signature and expiration
   Extracts user_id from payload
```

#### SSH Access

**Requirements**:
- SSH key pair in AWS
- Private key stored securely
- Public key on EC2 instances
- Key authentication only (no password)

**Best Practices**:
- Restrict SSH to admin IPs only
- Use short-lived credentials
- Audit all SSH sessions
- Disable root login
- Disable password authentication

```bash
# Recommended SSH config
Host ec2-instance
  HostName ec2-instance-ip
  User ec2-user
  IdentityFile ~/.ssh/intelliwealth-key.pem
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
```

---

## Data Protection

### Encryption in Transit

**HTTPS/TLS Configuration**:

| Component | Protocol | Version | Certificate |
|-----------|----------|---------|-------------|
| Frontend → ALB | HTTPS | TLS 1.2+ | ACM (public certificate) |
| ALB → EC2 | HTTP | Not encrypted | Internal only, not over internet |
| EC2 → RDS | Unencrypted | TCP | Internal VPC, optional upgrade |

**TLS Configuration** (ALB):
```
- Minimum TLS version: 1.2
- Cipher suites: Recommended by AWS
- Certificate: ACM managed (auto-renewal)
- HSTS: Consider enabling (for browsers)
```

### Encryption at Rest

#### RDS PostgreSQL

**Encryption**:
- Enabled by default
- AWS KMS managed keys
- Automatic backup encryption

```bash
# Verify RDS encryption
aws rds describe-db-instances \
  --db-instance-identifier intelliwealth-db \
  --query 'DBInstances[0].StorageEncrypted'
# Expected output: true
```

#### EBS Volumes

**Encryption**:
- EC2 root volumes: Enabled
- Additional volumes: Enabled by default

```bash
# Verify EBS encryption
aws ec2 describe-volumes \
  --filters Name=attachment.instance-id,Values=i-xxxxxxxx \
  --query 'Volumes[0].Encrypted'
# Expected output: True
```

#### Secrets & Credentials

**Where to Store**:
- ❌ NOT in code/images
- ❌ NOT in environment files checked into git
- ✅ AWS Secrets Manager
- ✅ AWS Systems Manager Parameter Store
- ✅ Environment variables injected at runtime

**Example Secret**:
```bash
# Store in Secrets Manager
aws secretsmanager create-secret \
  --name intelliwealth/prod/db-password \
  --secret-string 'P@ssw0rd!SecurePassword'

# Retrieve in application
aws secretsmanager get-secret-value \
  --secret-id intelliwealth/prod/db-password \
  --query SecretString
```

---

## Secrets Management

### Environment Variables

**Never Check In**:
```
DATABASE_URL=postgresql://user:pass@host:5432/db
API_KEY=sk_live_xxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=aws_secret_xxxxxxxxxx
JWT_SECRET=your_jwt_signing_secret
```

**Instead**:

**Option 1: AWS Secrets Manager**
```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='intelliwealth/prod/db-password')
password = secret['SecretString']
```

**Option 2: AWS Parameter Store**
```python
import boto3
client = boto3.client('ssm')
param = client.get_parameter(Name='/intelliwealth/prod/db-password', WithDecryption=True)
password = param['Parameter']['Value']
```

**Option 3: Environment Variables**
```bash
# At deployment time
export DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id intelliwealth/prod/db-password \
  --query SecretString)

# Application reads from $DB_PASSWORD
```

### Rotating Secrets

**RDS Master Password Rotation**:
```bash
# Modify RDS instance
aws rds modify-db-instance \
  --db-instance-identifier intelliwealth-db \
  --master-user-password NewSecurePassword123! \
  --apply-immediately

# Update application secrets
aws secretsmanager update-secret \
  --secret-id intelliwealth/prod/db-password \
  --secret-string 'NewSecurePassword123!'
```

---

## Compliance & Audit

### Logging

#### Application Logs

**Location**: CloudWatch Logs
```
/aws/ec2/intelliwealth/frontend
/aws/ec2/intelliwealth/portfolio-service
/aws/ec2/intelliwealth/market-service
```

**Content**:
- Request/response logs
- Error messages
- User actions
- Performance metrics

#### Database Logs

**PostgreSQL Logs**:
```sql
-- Enable logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = 'on';
SELECT pg_reload_conf();
```

**Monitor for**:
- Slow queries
- Failed authentication attempts
- Schema changes

#### Access Logs

**ALB Access Logs**:
```
type time elb client:port target:port request_processing_time target_processing_time response_time elb_status_code target_status_code received_bytes sent_bytes "request" "user_agent" "ssl_cipher" "ssl_protocol" target_group_arn trace_id domain_name chosen_cert_arn
```

#### VPC Flow Logs

**Monitor for**:
- Unusual traffic patterns
- Failed connections to databases
- Blocked security group rules

### Audit Trail

**AWS CloudTrail** (if enabled):
- Who did what and when
- API calls to AWS services
- Deployment actions

### Data Retention

| Log Type | Retention | Location |
|----------|-----------|----------|
| CloudWatch Logs | 30+ days | CloudWatch |
| RDS Backups | 30 days | AWS RDS |
| Database Logs | 7 days | PostgreSQL logs |
| ALB Access Logs | Variable | S3 (optional) |

---

## Security Hardening

### EC2 Hardening

```bash
# Update all packages
sudo yum update -y

# Enable firewall (if needed)
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Restrict SSH
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Harden network stack
sudo sysctl -w net.ipv4.tcp_syncookies=1
sudo sysctl -w net.ipv4.conf.all.rp_filter=1
sudo sysctl -w net.ipv4.icmp_echo_ignore_broadcasts=1
```

### Docker Security

**Image Scanning**:
```bash
# Scan images for vulnerabilities
docker scan intelliwealth-frontend:latest
```

**Container Restrictions**:
```yaml
# docker-compose.yml
services:
  portfolio-service:
    security_opt:
      - no-new-privileges:true
    read_only: true  # Read-only root filesystem
    cap_drop:
      - ALL         # Drop all capabilities
    cap_add:
      - NET_BIND_SERVICE  # Only needed capability
```

### RDS Hardening

**Enhanced Monitoring**:
```
Enabled with 1-minute granularity
Monitors: CPU, Memory, Disk I/O, Network
Alerts on anomalies
```

**Backup Encryption**:
```
Enabled by default
30-day retention
Encrypted with KMS
```

**Multi-AZ**:
```
Synchronous replication to standby
Automatic failover in < 2 minutes
```

---

## Incident Response

### Detection

**What to Monitor**:
- CloudWatch Alarms
- Application error rates
- Database connection failures
- Security group rule violations
- Unusual traffic patterns

### Response Playbooks

#### Database Breach Suspected

```
1. Immediately
   - Revoke all database credentials
   - Rotate RDS master password
   - Review recent database audit logs
   - Check for unauthorized schema changes

2. Short-term (1-4 hours)
   - Restore from clean backup
   - Identify compromise vector
   - Patch vulnerability
   - Redeployment of instances

3. Medium-term (1-7 days)
   - Full security audit
   - Code review for SQL injection
   - Update application secrets
   - Notify affected users if data accessed
```

#### Unauthorized API Access

```
1. Immediately
   - Revoke compromised API tokens
   - Review API logs
   - Identify source IP/user
   - Block offending IP in security group (if applicable)

2. Short-term
   - Invalidate all sessions
   - Force password reset for users
   - Review API access patterns
   - Increase rate limiting

3. Medium-term
   - Implement stricter authentication
   - Add geo-blocking if applicable
   - Multi-factor authentication
```

#### Service Unavailability (Potential DDoS)

```
1. Immediately
   - Enable ALB access logging
   - Check CloudWatch metrics
   - Identify traffic patterns
   - Contact AWS Support

2. Short-term
   - Consider AWS Shield Standard (free)
   - Implement AWS WAF if available
   - Rate limit per IP
   - Geographic restrictions (if applicable)

3. Medium-term
   - Auto Scaling optimization
   - CDN integration (CloudFront)
   - DDoS mitigation strategy
```

---

## Security Checklist

Before deploying to production:

### Network
- [ ] VPC created with private subnets
- [ ] Security groups configured with least privilege
- [ ] No database exposed to public internet
- [ ] No SSH access from 0.0.0.0/0
- [ ] ALB configured with HTTPS only
- [ ] ACM certificate provisioned and valid

### Access Control
- [ ] IAM roles created for EC2
- [ ] No hardcoded credentials in images
- [ ] SSH key pair created and secured
- [ ] RDS master password strong (20+ chars)
- [ ] JWT secret configured

### Data Protection
- [ ] RDS encryption enabled
- [ ] EBS encryption enabled
- [ ] Secrets in Secrets Manager
- [ ] Database backups enabled
- [ ] Log retention configured

### Monitoring & Logging
- [ ] CloudWatch Logs enabled
- [ ] Alarms for critical metrics
- [ ] ALB access logging enabled
- [ ] VPC Flow Logs enabled (optional)
- [ ] CloudTrail enabled (optional)

---

**Last Updated**: May 2026  
**Owner**: Security & Compliance Team
