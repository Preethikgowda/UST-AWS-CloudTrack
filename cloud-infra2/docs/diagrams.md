# Architecture Diagrams

**Mermaid Diagrams for IntelliWealth Architecture**

---

## System Architecture Diagram

```mermaid
graph TB
    subgraph Internet["Internet"]
        Browser["🌐 Browser<br/>React SPA"]
    end
    
    subgraph DNS["DNS & SSL"]
        Route53["Route53<br/>yourdomain.com"]
        ACM["ACM Certificate<br/>yourdomain.com"]
    end
    
    subgraph AWS["AWS Cloud - us-east-1"]
        subgraph ALB_Layer["Load Balancing Layer"]
            ALB["Application Load Balancer<br/>Port: 80, 443<br/>HTTPS Termination"]
        end
        
        subgraph Public_Subnets["Public Subnets<br/>10.0.1.0/24, 10.0.2.0/24"]
            IGW["Internet Gateway"]
            NAT1["NAT Gateway 1a"]
            NAT2["NAT Gateway 1b"]
        end
        
        subgraph Compute_1a["AZ 1a - Private App Subnet<br/>10.0.11.0/24"]
            EC2_1["EC2 Instance 1<br/>Frontend + Backend<br/>Port: 80, 8000, 8001"]
        end
        
        subgraph Compute_1b["AZ 1b - Private App Subnet<br/>10.0.12.0/24"]
            EC2_2["EC2 Instance 2<br/>Frontend + Backend<br/>Port: 80, 8000, 8001"]
        end
        
        subgraph Database_1a["AZ 1a - Private DB Subnet<br/>10.0.21.0/24"]
            RDS_Primary["RDS PostgreSQL Primary<br/>Port: 5432"]
        end
        
        subgraph Database_1b["AZ 1b - Private DB Subnet<br/>10.0.22.0/24"]
            RDS_Standby["RDS PostgreSQL Standby<br/>Port: 5432<br/>Multi-AZ Replica"]
        end
        
        subgraph Cache["Cache Layer"]
            Redis["ElastiCache Redis<br/>Port: 6379<br/>Multi-AZ Optional"]
        end
    end
    
    Browser -->|HTTPS| Route53
    Route53 -->|DNS Resolution| ALB
    ACM -->|Certificate| ALB
    
    ALB -->|Path: /| EC2_1
    ALB -->|Path: /| EC2_2
    ALB -->|Path: /api/v1/*| EC2_1
    ALB -->|Path: /api/v1/*| EC2_2
    
    EC2_1 -->|SQL| RDS_Primary
    EC2_2 -->|SQL| RDS_Primary
    
    RDS_Primary -->|Replication| RDS_Standby
    
    EC2_1 -->|Cache Get/Set| Redis
    EC2_2 -->|Cache Get/Set| Redis
    
    EC2_1 -->|Outbound| NAT1
    EC2_2 -->|Outbound| NAT2
    
    NAT1 -->|Internet| IGW
    NAT2 -->|Internet| IGW
```

---

## Microservice Communication Flow

```mermaid
graph LR
    subgraph Frontend["Frontend Service<br/>React + Nginx<br/>Port 80"]
        React["React App<br/>TypeScript"]
        API_Client["API Client<br/>Axios/Fetch"]
    end
    
    subgraph Portfolio["Portfolio Service<br/>FastAPI<br/>Port 8000"]
        Auth["Auth Router<br/>/auth/*"]
        Customer["Customer Router<br/>/customers/*"]
        PortfolioAPI["Portfolio Router<br/>/portfolio/*"]
        Service["Service Layer<br/>Business Logic"]
    end
    
    subgraph Market["Market Service<br/>FastAPI<br/>Port 8001"]
        QuoteAPI["Quote Router<br/>/market/*"]
        RiskAPI["Risk Router<br/>/risk/*"]
        SectorAPI["Sector Router<br/>/sectors/*"]
        MarketService["Service Layer<br/>Risk Calculations"]
    end
    
    subgraph Database["PostgreSQL 16"]
        CustomerDB["customers table"]
        PortfolioDB["portfolios table"]
        AssetDB["assets table"]
        MarketDB["market_data table"]
    end
    
    subgraph Cache["Redis 7"]
        QuoteCache["quote:{symbol}"]
        HistoryCache["history:{symbol}"]
        RiskCache["risk:{portfolio_id}"]
    end
    
    React -->|GET /api/v1/auth/login<br/>POST /api/v1/auth/login| API_Client
    API_Client -->|HTTP/JSON| Auth
    API_Client -->|HTTP/JSON| Customer
    API_Client -->|HTTP/JSON| PortfolioAPI
    API_Client -->|HTTP/JSON| QuoteAPI
    
    Auth -->|Verify| Service
    Customer -->|CRUD| Service
    PortfolioAPI -->|CRUD| Service
    QuoteAPI -->|Fetch| MarketService
    RiskAPI -->|Calculate| MarketService
    SectorAPI -->|Aggregate| MarketService
    
    Service -->|SELECT/INSERT/UPDATE| CustomerDB
    Service -->|SELECT/INSERT/UPDATE| PortfolioDB
    Service -->|SELECT/INSERT/UPDATE| AssetDB
    
    MarketService -->|SELECT| MarketDB
    
    MarketService -->|GET/SET| QuoteCache
    MarketService -->|GET/SET| HistoryCache
    Service -->|GET/SET| RiskCache
```

---

## AWS Deployment Architecture

```mermaid
graph TB
    subgraph UserRegion["User Location"]
        Users["👥 Users<br/>Global"]
    end
    
    subgraph AWSRegion["AWS Region: us-east-1"]
        subgraph Route53["DNS & Global"]
            R53["Route53<br/>yourdomain.com<br/>Failover Policy"]
        end
        
        subgraph LoadBalancing["Load Balancing"]
            ELB["Application Load Balancer<br/>Internet-facing<br/>HTTPS:443<br/>HTTP:80→443<br/>Multi-AZ"]
            TargetFront["Target Group<br/>Frontend:80"]
            TargetPort["Target Group<br/>Portfolio:8000"]
            TargetMarket["Target Group<br/>Market:8001"]
        end
        
        subgraph AZ_1a["Availability Zone 1a"]
            PublicSN_1a["Public Subnet<br/>10.0.1.0/24"]
            PrivateSN_1a["Private App Subnet<br/>10.0.11.0/24"]
            DBSubnet_1a["Private DB Subnet<br/>10.0.21.0/24"]
            
            NAT_1a["NAT Gateway"]
            EC2_1a["EC2 Instance<br/>t3.medium<br/>80,8000,8001"]
            RDS_1a["RDS Primary<br/>PostgreSQL"]
        end
        
        subgraph AZ_1b["Availability Zone 1b"]
            PublicSN_1b["Public Subnet<br/>10.0.2.0/24"]
            PrivateSN_1b["Private App Subnet<br/>10.0.12.0/24"]
            DBSubnet_1b["Private DB Subnet<br/>10.0.22.0/24"]
            
            NAT_1b["NAT Gateway"]
            EC2_1b["EC2 Instance<br/>t3.medium<br/>80,8000,8001"]
            RDS_1b["RDS Standby<br/>PostgreSQL"]
        end
        
        subgraph Storage["Data & Cache"]
            RDS_Cluster["RDS PostgreSQL Cluster<br/>db.t3.small<br/>100GB gp3<br/>Multi-AZ"]
            Redis["ElastiCache Redis<br/>cache.t3.micro<br/>Multi-AZ<br/>Port 6379"]
        end
        
        subgraph Monitoring["Monitoring & Logging"]
            CloudWatch["CloudWatch<br/>Logs & Metrics"]
            CloudTrail["CloudTrail<br/>API Audit"]
            Alarms["CloudWatch Alarms<br/>CPU, Network, Errors"]
        end
    end
    
    Users -->|HTTPS| R53
    R53 -->|A Record Alias| ELB
    
    ELB -->|Path: /| TargetFront
    ELB -->|Path: /api/v1/portfolio| TargetPort
    ELB -->|Path: /api/v1/market| TargetMarket
    
    TargetFront --> EC2_1a
    TargetFront --> EC2_1b
    TargetPort --> EC2_1a
    TargetPort --> EC2_1b
    TargetMarket --> EC2_1a
    TargetMarket --> EC2_1b
    
    EC2_1a --> RDS_Cluster
    EC2_1b --> RDS_Cluster
    EC2_1a --> Redis
    EC2_1b --> Redis
    
    EC2_1a --> NAT_1a
    EC2_1b --> NAT_1b
    
    EC2_1a --> CloudWatch
    EC2_1b --> CloudWatch
    ELB --> CloudWatch
    RDS_Cluster --> CloudWatch
    
    EC2_1a -.->|Optional| CloudTrail
    EC2_1b -.->|Optional| CloudTrail
```

---

## Network Segmentation & Security Groups

```mermaid
graph TB
    subgraph Internet["Internet<br/>0.0.0.0/0"]
        Client["Client Requests"]
    end
    
    subgraph ALB_SG["ALB Security Group<br/>Inbound: 80, 443<br/>Outbound: All"]
        ALB["Application Load<br/>Balancer"]
    end
    
    subgraph VPC["VPC 10.0.0.0/16"]
        subgraph PublicNet["Public Subnets"]
            PublicSG["Public SG"]
            IGW["Internet<br/>Gateway"]
            NAT["NAT<br/>Gateways"]
        end
        
        subgraph PrivateAppNet["Private App Subnets<br/>10.0.11.0/24, 10.0.12.0/24"]
            EC2_SG["EC2 Security Group<br/>Inbound from ALB SG:<br/>80, 8000, 8001<br/>Outbound: All"]
            EC2["EC2<br/>Instances"]
        end
        
        subgraph PrivateDBNet["Private DB Subnets<br/>10.0.21.0/24, 10.0.22.0/24"]
            RDS_SG["RDS Security Group<br/>Inbound from EC2 SG:<br/>5432 PostgreSQL<br/>Outbound: None"]
            RDS["RDS<br/>PostgreSQL"]
        end
        
        subgraph PrivateCacheNet["Private Cache Subnets"]
            Redis_SG["Redis Security Group<br/>Inbound from EC2 SG:<br/>6379<br/>Outbound: None"]
            Redis["Redis<br/>Cache"]
        end
    end
    
    Client -->|HTTP/HTTPS| ALB_SG
    ALB_SG -->|Rule: Allow 80,443<br/>from 0.0.0.0/0| ALB
    
    ALB -->|Route traffic| EC2_SG
    EC2_SG -->|Allow 80,8000,8001<br/>from ALB SG| EC2
    
    EC2 -->|Query 5432| RDS_SG
    RDS_SG -->|Allow 5432<br/>from EC2 SG| RDS
    
    EC2 -->|Query 6379| Redis_SG
    Redis_SG -->|Allow 6379<br/>from EC2 SG| Redis
    
    EC2 -->|Outbound Internet| NAT
    NAT -->|Translate to<br/>Elastic IP| IGW
    IGW -->|Route to<br/>Internet| Internet
```

---

## Request Flow Through System

```mermaid
sequenceDiagram
    participant Browser
    participant Route53
    participant ALB
    participant EC2_Frontend
    participant EC2_Backend
    participant RDS
    participant Redis
    
    Browser->>Route53: 1. Resolve yourdomain.com
    Route53-->>Browser: ALB IP Address
    
    Browser->>ALB: 2. HTTPS Request GET /api/v1/portfolio
    ALB->>ALB: 3. TLS Termination<br/>Path-based Routing
    
    alt Path matches /api/v1/portfolio
        ALB->>EC2_Backend: 4. HTTP GET /portfolio/list<br/>Authorization: Bearer token
    end
    
    EC2_Backend->>EC2_Backend: 5. FastAPI Handler<br/>Validate JWT Token
    
    EC2_Backend->>Redis: 6. Check Cache<br/>portfolio:{user_id}
    alt Cache Hit
        Redis-->>EC2_Backend: Return cached data
    else Cache Miss
        EC2_Backend->>RDS: 7. SELECT portfolios<br/>WHERE customer_id = ?
        RDS-->>EC2_Backend: Portfolio records
        EC2_Backend->>Redis: 8. SET portfolio:{user_id}<br/>TTL: 30min
    end
    
    EC2_Backend->>EC2_Backend: 9. Transform to JSON<br/>Add metadata
    EC2_Backend-->>ALB: 10. HTTP 200 OK<br/>JSON response
    
    ALB-->>Browser: 11. HTTPS 200 OK<br/>TLS Encrypted<br/>JSON response
    
    Browser->>Browser: 12. Parse JSON<br/>Update React State<br/>Render UI
```

---

## Security Architecture

```mermaid
graph TB
    subgraph Outside["External Threats"]
        DDoS["DDoS Attacks"]
        Malware["Malicious Requests"]
    end
    
    subgraph Layer1["Layer 1: Network Edge"]
        AWS_Shield["AWS Shield Standard<br/>DDoS Protection"]
        Route53_HC["Route53 Health Check<br/>Failover"]
    end
    
    subgraph Layer2["Layer 2: Load Balancer"]
        ALB_SG["ALB Security Group<br/>Whitelist Ports:<br/>80, 443"]
        ALB_WAF["WAF Rules<br/>SQL Injection<br/>XSS Prevention"]
        HTTPS["HTTPS/TLS 1.2+<br/>ACM Certificates<br/>Encryption"]
    end
    
    subgraph Layer3["Layer 3: Network"]
        EC2_SG["EC2 Security Group<br/>Only from ALB<br/>Ports 80,8000,8001"]
        VPC_Net["VPC Network<br/>Private Subnets<br/>No Public IP"]
        NAT["NAT Gateway<br/>Outbound Only"]
    end
    
    subgraph Layer4["Layer 4: Application"]
        Auth["JWT Authentication<br/>HS256 Signing<br/>24h Expiration"]
        Input_Val["Input Validation<br/>Pydantic Schemas<br/>Type Checking"]
        RateLimit["Rate Limiting<br/>Per User<br/>Per IP"]
    end
    
    subgraph Layer5["Layer 5: Data"]
        RDS_SG["RDS Security Group<br/>Only from EC2<br/>Port 5432"]
        RDS_Enc["RDS Encryption<br/>AWS KMS<br/>At Rest"]
        Backup["Backup Strategy<br/>30-day Retention<br/>Cross-AZ"]
    end
    
    subgraph Layer6["Layer 6: Monitoring"]
        CloudWatch["CloudWatch Monitoring<br/>Logs & Metrics"]
        Alarms["CloudWatch Alarms<br/>CPU, Errors,<br/>Anomalies"]
        Audit["CloudTrail Audit<br/>API Activity Log"]
    end
    
    Outside -->|Attack Vector| Layer1
    Layer1 -->|Block| Layer2
    Layer2 -->|Block| Layer3
    Layer3 -->|Block| Layer4
    Layer4 -->|Validate| Layer5
    Layer5 -->|Monitor| Layer6
```

---

## CI/CD Deployment Pipeline

```mermaid
graph LR
    subgraph Source["Source Code"]
        GitHub["GitHub Repository<br/>main branch"]
    end
    
    subgraph Build["Build Stage"]
        trigger["Webhook Trigger<br/>on push"]
        test["Run Tests<br/>pytest, npm test"]
        build_img["Build Images<br/>docker build"]
        scan["Security Scan<br/>trivy"]
    end
    
    subgraph Registry["Container Registry"]
        DockerHub["Docker Hub<br/>intelliwealth:v1.0.0"]
    end
    
    subgraph Deploy["Deployment Stage"]
        terraform["Terraform Apply<br/>Infrastructure"]
        pull_img["Pull Images<br/>EC2 Instances"]
        deploy["Deploy Containers<br/>docker compose up"]
        health["Health Checks<br/>API Endpoints"]
    end
    
    subgraph Production["Production"]
        ALB["Load Balancer"]
        EC2["EC2 Instances<br/>Auto Scaling"]
        RDS["PostgreSQL<br/>Multi-AZ"]
    end
    
    GitHub -->|Push Event| trigger
    trigger -->|Run| test
    test -->|On Success| build_img
    build_img -->|Scan| scan
    scan -->|On Success| DockerHub
    
    DockerHub -->|Pull| pull_img
    terraform -->|Provision| EC2
    pull_img -->|Deploy| deploy
    deploy -->|Verify| health
    
    EC2 -->|Update| ALB
    EC2 -->|Connect| RDS
```

---

**Last Updated**: May 2026  
**Diagrams Created**: System Architecture, Service Communication, AWS Deployment, Network Security, Request Flow, Security Layers, CI/CD Pipeline
