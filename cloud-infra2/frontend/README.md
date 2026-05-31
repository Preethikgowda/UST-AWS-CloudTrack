# Frontend Service

**Service**: Web Application & API Gateway  
**Technology**: React, Vite, TypeScript, Nginx  
**Port**: 3000 (local), 80 (container production)  
**Status**: Production-Ready

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Purpose & Responsibilities](#purpose--responsibilities)
3. [Architecture](#architecture)
4. [Port Mappings](#port-mappings)
5. [API Configuration](#api-configuration)
6. [Folder Structure](#folder-structure)
7. [Technology Stack](#technology-stack)
8. [Environment Variables](#environment-variables)
9. [Docker Setup](#docker-setup)
10. [Local Development](#local-development)
11. [Build & Deployment](#build--deployment)
12. [Service Communication](#service-communication)
13. [Scalability Notes](#scalability-notes)

---

## Service Overview

The **Frontend Service** is the user-facing web application layer for IntelliWealth. It provides a modern, responsive user interface for portfolio management, real-time market analysis, and asset allocation tracking.

### Key Attributes

- **Framework**: React with TypeScript for type safety
- **Build Tool**: Vite for fast development and optimized production builds
- **Styling**: CSS modules and component-based design
- **API Integration**: RESTful API client with JWT authentication
- **Web Server**: Nginx for static file serving and reverse proxy
- **Responsiveness**: Mobile-first, responsive design
- **Performance**: Optimized bundle sizes, lazy loading

---

## Purpose & Responsibilities

### Primary Responsibilities

1. **User Interface Presentation**
   - Dashboard with portfolio overview
   - Portfolio management pages
   - Asset allocation visualization
   - Market intelligence displays
   - User settings and profile

2. **Authentication & Authorization**
   - Login/logout flows
   - JWT token management
   - Session persistence
   - Protected routes with access control

3. **API Integration**
   - HTTP client for backend service calls
   - Request/response handling
   - Error handling and user feedback
   - Token refresh on expiration

4. **State Management**
   - User authentication state
   - Portfolio data caching
   - Market data updates
   - UI state management

5. **Real-time Updates**
   - Market data refresh
   - Portfolio balance updates
   - Risk metrics visualization
   - Sector allocation charts

### Not a Responsibility

- ❌ Direct database access (all via API)
- ❌ Business logic (Portfolio/Market services handle this)
- ❌ Data validation (handled by backend APIs)
- ❌ Cache management (relies on backend)

---

## Architecture

### Component Architecture

```
App.tsx (Root component)
├── Layout
│   ├── Navbar (navigation, user menu)
│   ├── Sidebar (menu, navigation)
│   └── PageContainer (main content area)
│
├── Pages
│   ├── Login (authentication)
│   ├── Dashboard (overview)
│   ├── PortfolioOverview (portfolio details)
│   ├── PortfolioHistory (historical data)
│   ├── AssetAllocation (asset breakdown)
│   ├── Admin (admin panel)
│   └── Profile (user settings)
│
├── Components
│   ├── ChartCard (reusable chart wrapper)
│   ├── MetricCard (metric display)
│   ├── StatWidget (statistic widget)
│   ├── TableCard (data table wrapper)
│   ├── SectionHeader (section titles)
│   └── ContentGrid (layout grid)
│
├── Auth
│   ├── AuthContext (state management)
│   ├── ProtectedRoute (route protection)
│
├── API
│   └── client.ts (HTTP client, API calls)
│
└── Types
    └── index.ts (TypeScript interfaces)
```

### Request Flow

```
User Interaction (Click, Submit)
    ↓
Component State Update
    ↓
API Client Call (src/api/client.ts)
    ↓
HTTP Request to Backend
    ↓
ALB / Nginx Routing
    ↓
Backend Service (Portfolio or Market)
    ↓
HTTP Response (JSON)
    ↓
State Management Update
    ↓
Component Re-render
    ↓
UI Update
```

---

## Port Mappings

### Local Development

| Service | Port | Protocol | URL |
|---------|------|----------|-----|
| Frontend Dev Server | 3000 | HTTP | http://localhost:3000 |
| Vite HMR | 3000 | WebSocket | ws://localhost:3000 |

### Production (Container)

| Service | Port | Protocol | Context |
|---------|------|----------|---------|
| Nginx (static) | 80 | HTTP | Container internal |
| Nginx (reverse proxy) | 80 | HTTP | Routes `/api/*` to backends |

### Production (AWS)

| Component | Port | Source | Destination |
|-----------|------|--------|-------------|
| ALB | 443 | Internet (clients) | HTTPS endpoint |
| ALB | 80 | Internet (clients) | HTTP redirect to 443 |
| Frontend EC2 | 80 | ALB | Nginx web server |
| Backend redirect | 8000/8001 | Frontend (via ALB) | Portfolio/Market services |

---

## API Configuration

### API Base URL

**Local Development** (`.env`):
```
VITE_API_BASE_URL=/api/v1
```

**Nginx Reverse Proxy** (`nginx.dev.conf`):
Routes `/api/v1/*` to backend services

- `/api/v1/auth` → portfolio-service:8000
- `/api/v1/customers` → portfolio-service:8000
- `/api/v1/portfolio` → portfolio-service:8000
- `/api/v1/market` → market-service:8001

### API Client (src/api/client.ts)

Centralized HTTP client for all backend communication:

```typescript
// Usage example
const response = await api.get('/auth/login', {
  email: 'user@example.com',
  password: 'password'
});

// Automatically includes:
// - Base URL
// - JWT token (Authorization header)
// - Error handling
// - Content-Type: application/json
```

### Authentication

**JWT Token Flow**:
1. User logs in → Backend returns JWT token
2. Token stored in localStorage
3. All subsequent requests include `Authorization: Bearer <token>`
4. Token refresh on expiration
5. Logout clears token

---

## Folder Structure

```
frontend/
├── src/
│   ├── App.tsx                  Root component
│   ├── main.tsx                 Vite entry point
│   ├── index.css                Global styles
│   ├── vite-env.d.ts            Vite type definitions
│   │
│   ├── api/
│   │   └── client.ts            HTTP client, API methods
│   │
│   ├── assets/                  Images, fonts, static files
│   │   └── logo.svg
│   │
│   ├── auth/
│   │   ├── AuthContext.tsx      Authentication state
│   │   └── ProtectedRoute.tsx   Route protection wrapper
│   │
│   ├── components/              Reusable React components
│   │   ├── Navbar.tsx           Top navigation bar
│   │   ├── Sidebar.tsx          Left sidebar menu
│   │   ├── Layout.tsx           Main layout wrapper
│   │   ├── PageContainer.tsx    Page content container
│   │   ├── ChartCard.tsx        Chart component wrapper
│   │   ├── MetricCard.tsx       Metric display card
│   │   ├── StatWidget.tsx       Statistics widget
│   │   ├── TableCard.tsx        Table wrapper component
│   │   ├── SectionHeader.tsx    Section title component
│   │   └── ContentGrid.tsx      Grid layout component
│   │
│   ├── pages/                   Page components (routes)
│   │   ├── Login.tsx            Login page
│   │   ├── Dashboard.tsx        Dashboard/home page
│   │   ├── PortfolioOverview.tsx Portfolio page
│   │   ├── PortfolioHistory.tsx Portfolio history
│   │   ├── AssetAllocation.tsx  Asset allocation page
│   │   ├── Admin.tsx            Admin panel
│   │   └── Profile.tsx          User profile page
│   │
│   └── types/
│       └── index.ts             TypeScript interfaces & types
│
├── public/                      Static assets served at /
│   └── vite.svg
│
├── Dockerfile                   Container image definition
├── index.html                   HTML entry point
├── tsconfig.json                TypeScript configuration
├── vite.config.ts               Vite build configuration
├── package.json                 NPM dependencies
├── nginx.dev.conf               Nginx reverse proxy (local dev)
├── nginx.conf                   Nginx config (production)
└── .env                         Environment variables (local)
```

### Key Files

**`src/api/client.ts`**: Centralized API client
- Base URL configuration
- JWT token injection
- Error handling
- Request/response interceptors

**`src/auth/AuthContext.tsx`**: Authentication state
- Login/logout management
- Token persistence
- User state storage
- Protected route access

**`src/App.tsx`**: Root component
- Route definitions
- Layout structure
- Global app state

**`nginx.dev.conf`** (Local Development):
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://nginx:80;  # Routes to backend
    }
}
```

**`nginx.conf`** (Production):
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    # In production, ALB handles /api routing
}
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI Framework** | React 18+ | Component-based UI |
| **Language** | TypeScript | Type-safe development |
| **Build Tool** | Vite | Fast builds & HMR |
| **HTTP Client** | Fetch API | API communication |
| **Styling** | CSS Modules | Component styling |
| **State** | React Context | State management |
| **Routing** | React Router | Client-side routing |
| **Web Server** | Nginx | Production serving |
| **Container** | Docker | Containerization |
| **Node** | Node.js 18+ | Build environment |

---

## Environment Variables

### Local Development (`.env`)

```bash
# API Configuration
VITE_API_BASE_URL=/api/v1

# Optional: Override API base for specific development
VITE_PORTFOLIO_API=http://localhost:8000/api/v1
VITE_MARKET_API=http://localhost:8001/api/v1
```

### Production (`.env.prod`)

```bash
# API Configuration (resolved via ALB)
VITE_API_BASE_URL=/api/v1

# Optional: API endpoint overrides (if needed)
# Leave unset to use ALB routing
```

### Environment File Precedence

1. `.env.local` (local overrides, not committed)
2. `.env.production.local` (production local, not committed)
3. `.env` (development defaults)
4. `.env.prod` (production defaults)

---

## Docker Setup

### Build Docker Image

**Local Development**:
```bash
docker build -f frontend/Dockerfile -t intelliwealth-frontend:dev .
```

**Production**:
```bash
docker build \
  --build-arg VITE_API_BASE_URL=/api/v1 \
  -f frontend/Dockerfile \
  -t intelliwealth-frontend:latest .
```

### Dockerfile Overview

The `frontend/Dockerfile` uses a **multi-stage build** pattern:

**Stage 1: Builder**
- Node.js 18+ image
- Install dependencies
- Build React app with Vite
- Output: Optimized bundle in `dist/`

**Stage 2: Runtime**
- Nginx Alpine image
- Copy built files from builder
- Configure Nginx
- Serve static files

### Image Configuration

- **Base**: nginx:alpine (small, secure)
- **Build**: node:18-alpine (fast builds)
- **Size**: ~100 MB final image
- **Ports**: 80 (HTTP)

---

## Local Development

### Prerequisites

- **Docker Desktop** 4.10+ (includes Docker & Docker Compose)
- **Git**
- **Text Editor/IDE** (VS Code recommended)

**No local Node.js installation required** - everything runs in containers.

### Quick Start

1. **Start the full stack**:
   ```bash
   cd cloud-infra
   docker compose up --build -d
   ```

2. **Access frontend**:
   ```
   http://localhost:3000
   ```

3. **View logs**:
   ```bash
   docker compose logs -f frontend
   ```

4. **Stop services**:
   ```bash
   docker compose down
   ```

### Development Workflow

**Hot Module Replacement (HMR)**: Vite enables fast refresh during development. Edit React files and see changes immediately in the browser.

**File Watching**: Docker volume mounts the `frontend/src/` directory, so changes are reflected in the container.

### Debugging

**Browser DevTools**:
- React DevTools extension
- Network tab for API calls
- Console for JavaScript errors

**Docker Logs**:
```bash
docker compose logs frontend       # View frontend logs
docker compose logs frontend -f    # Follow logs in real-time
```

**Shell Access**:
```bash
docker compose exec frontend sh
# Inside container: npm list, npm test, etc.
```

---

## Build & Deployment

### Development Build

```bash
docker compose up --build -d frontend
```

### Production Build

**Step 1**: Build optimized bundle
```bash
npm run build
# Output: dist/ folder with optimized assets
```

**Step 2**: Create Docker image
```bash
docker build -f frontend/Dockerfile -t intelliwealth-frontend:v1.0.0 .
```

**Step 3**: Push to registry
```bash
docker tag intelliwealth-frontend:v1.0.0 your_registry/intelliwealth-frontend:v1.0.0
docker push your_registry/intelliwealth-frontend:v1.0.0
```

**Step 4**: Deploy on EC2
```bash
docker compose -f docker-compose.frontend.prod.yml up -d
```

### Build Optimization

- **Code Splitting**: Automatic route-based code splitting
- **Tree Shaking**: Removes unused code
- **Minification**: JavaScript and CSS minified
- **Asset Optimization**: Images and fonts optimized
- **Cache Busting**: Hash-based filenames for CDN caching

**Build Output**:
- `dist/index.html` - Main HTML
- `dist/assets/` - JavaScript, CSS, images
- `dist/assets/[hash].js` - Main bundle (cached)

---

## Service Communication

### Frontend ↔ Portfolio Service

**HTTP Method**: POST/GET/PUT/DELETE  
**Protocol**: HTTPS (via ALB in production)  
**Base URL**: `/api/v1` (resolves to portfolio-service:8000)  
**Authentication**: Bearer Token (JWT)

**Endpoints**:
```
POST   /api/v1/auth/login          Login
POST   /api/v1/auth/logout         Logout
GET    /api/v1/customers/{id}      Get customer
POST   /api/v1/customers           Create customer
GET    /api/v1/portfolio/{id}      Get portfolio
POST   /api/v1/portfolio           Create portfolio
PUT    /api/v1/portfolio/{id}      Update portfolio
DELETE /api/v1/portfolio/{id}      Delete portfolio
```

**Request Example**:
```typescript
const portfolios = await fetch('/api/v1/portfolio/123', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Frontend ↔ Market Service

**HTTP Method**: GET  
**Protocol**: HTTPS (via ALB in production)  
**Base URL**: `/api/v1` (resolves to market-service:8001)  
**Authentication**: Bearer Token (JWT)

**Endpoints**:
```
GET    /api/v1/market/data/{symbol}    Market data
GET    /api/v1/market/risk/{id}        Risk metrics
GET    /api/v1/market/sectors          Sector data
```

### Error Handling

**Response Handling**:
```typescript
try {
  const response = await api.get('/auth/login', data);
  // Handle success (200, 201, etc.)
} catch (error) {
  if (error.status === 401) {
    // Unauthorized - refresh token or logout
  } else if (error.status === 403) {
    // Forbidden - access denied
  } else if (error.status >= 500) {
    // Server error - retry or show error message
  }
}
```

---

## Scalability Notes

### Current Architecture

**Single Instance** (suitable for development):
- One frontend EC2 instance
- Nginx handles static file serving
- ALB distributes traffic

### Scaling for Production

**Horizontal Scaling** (recommended approach):

1. **Auto Scaling Group**
   - Minimum: 2 instances
   - Desired: 2-3 instances
   - Maximum: 5-10 instances
   - Metric: CPU utilization > 70%

2. **Load Balancing**
   - ALB distributes traffic
   - Health checks every 30 seconds
   - Automatic instance replacement

3. **Content Delivery**
   - CloudFront CDN (optional)
   - Cache static assets at edge locations
   - Reduces origin load

4. **Performance Optimization**
   - Gzip compression enabled
   - Browser cache headers set
   - Asset fingerprinting

### Future Improvements

- [ ] CDN integration (CloudFront)
- [ ] Static asset caching strategy
- [ ] Performance monitoring (Sentry, DataDog)
- [ ] A/B testing framework
- [ ] Feature flags (LaunchDarkly)
- [ ] Advanced analytics
- [ ] PWA capabilities (offline support)
- [ ] GraphQL API layer (optional)

---

**Last Updated**: May 2026  
**Maintainer**: Frontend Team
