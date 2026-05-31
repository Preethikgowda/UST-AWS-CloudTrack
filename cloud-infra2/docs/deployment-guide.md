# Docker Deployment Guide

This project is prepared to run as Docker containers locally and later on EC2.

No Kubernetes, monitoring stack, or cloud infrastructure files are included in the active application setup.

## Local Development

```bash
cp .env.example .env
docker compose up --build -d
```

Services:

```text
frontend             http://localhost:3000
portfolio-service    http://localhost:8000/docs
market-service       http://localhost:8001/docs
postgres             localhost:5432
redis                localhost:6379
```

Useful commands:

```bash
docker compose ps
docker compose logs -f
docker compose down
docker compose down -v
```

## Production Images

Build and push DockerHub images:

```bash
export DOCKERHUB_USERNAME=<your-dockerhub-username>
export IMAGE_TAG=latest
./scripts/build-and-push.sh
```

Images:

```text
${DOCKERHUB_USERNAME}/intelliwealth-frontend:${IMAGE_TAG}
${DOCKERHUB_USERNAME}/intelliwealth-portfolio-service:${IMAGE_TAG}
${DOCKERHUB_USERNAME}/intelliwealth-market-service:${IMAGE_TAG}
```

## Backend Runtime

Copy `.env.prod.example` to `.env.prod` and fill real values:

```bash
cp .env.prod.example .env.prod
```

Start backend services:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

Run migrations:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec portfolio-service alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env.prod exec market-service alembic upgrade head
```

## Frontend Runtime

Start frontend:

```bash
docker compose -f docker-compose.frontend.prod.yml --env-file .env.prod up -d
```

## Health Checks

```text
frontend             GET /health
portfolio-service    GET /health, /readiness, /liveness
market-service       GET /health, /readiness, /liveness
```
