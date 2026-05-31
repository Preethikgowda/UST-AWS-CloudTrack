# Application Overview

IntelliWealth is a portfolio intelligence platform built as Dockerized microservices.

## Active Services

```text
frontend
portfolio-service
market-service
postgres
redis
```

## User Workflows

```text
Sign up
Frontend -> Portfolio Service -> PostgreSQL

Login
Frontend -> Portfolio Service -> PostgreSQL -> JWT

Portfolio management
Frontend -> Portfolio Service -> PostgreSQL

Market/risk views
Frontend -> Market Service -> PostgreSQL + Redis
```

## Responsibilities

Frontend:

```text
React user interface, authentication flow, dashboard, portfolio views.
```

Portfolio service:

```text
Authentication, customers, portfolios, assets, transactions, history.
```

Market service:

```text
Market data, sector data, risk metrics, Redis-backed caching.
```

PostgreSQL:

```text
Primary relational storage.
```

Redis:

```text
Ephemeral market-service cache.
```
