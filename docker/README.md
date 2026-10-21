# Container packaging

One reproducible stack from database startup to a ready browser interface.

## Problem

Starting the right processes is not enough. The database must accept connections, migrations must finish, and the API must be usable before the frontend serves requests.

## Approach

```mermaid
flowchart LR
  DB[PostgreSQL healthy] --> Migration[Alembic completed]
  Migration --> API[FastAPI ready]
  API --> UI[Nginx serving]
```

| Image | Build | Runtime |
|---|---|---|
| [Backend](backend.Dockerfile) | Python 3.13 Alpine with pinned dependencies. | Uvicorn, UID 10001, port 8000. |
| [Frontend](frontend.Dockerfile) | Node compiles React; only static assets enter the final stage. | Unprivileged Nginx, UID 101, port 8080. |

The [Compose definition](../docker-compose.yml) encodes startup dependencies. A named volume persists PostgreSQL records, the database has no published host port, and application ports bind to loopback.

## Run

From the repository root:

```bash
docker compose up --build -d --wait
python3 scripts/smoke.py http://localhost:3000
docker compose down
```

A normal stop retains the database volume. CI builds the same Dockerfiles, scans both images and publishes commit-SHA tags after the gates pass.

[Quick start](../README.md#run-locally) · [Delivery workflow](../.github/workflows/ci-cd.yml) · [Kubernetes](../kubernetes/README.md)
