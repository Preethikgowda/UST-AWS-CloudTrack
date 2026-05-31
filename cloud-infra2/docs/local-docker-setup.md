# Local Docker Setup

Run the full local application with Docker Compose.

## Start

```bash
cp .env.example .env
docker compose up --build -d
```

## Services

```text
Frontend:       http://localhost:3000
Portfolio API:  http://localhost:8000/docs
Market API:     http://localhost:8001/docs
PostgreSQL:     localhost:5432
Redis:          localhost:6379
```

## Health Checks

```bash
curl http://localhost:3000/health
curl http://localhost:8000/health
curl http://localhost:8000/readiness
curl http://localhost:8001/health
curl http://localhost:8001/readiness
```

Expected backend responses:

```json
{"status":"ok"}
```

```json
{"status":"ready","db":"ok"}
```

## Logs

```bash
docker compose logs -f frontend
docker compose logs -f portfolio-service
docker compose logs -f market-service
docker compose logs -f postgres
docker compose logs -f redis
```

## Stop

```bash
docker compose down
```

## Reset Data

```bash
docker compose down -v
docker compose up --build -d
```
