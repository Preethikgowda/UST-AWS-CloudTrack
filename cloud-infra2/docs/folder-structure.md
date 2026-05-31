# Folder Structure

```text
.
├── docker/
│   └── init.sql
├── docs/
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── nginx.dev.conf
│   ├── package.json
│   └── src/
├── market-service/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
├── portfolio-service/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
├── scripts/
│   └── build-and-push.sh
├── docker-compose.yml
├── docker-compose.prod.yml
├── docker-compose.frontend.prod.yml
├── .env.example
├── .env.prod.example
└── README.md
```

Removed from active application setup:

```text
ai-insight-service/
k8s/
monitoring/
```
