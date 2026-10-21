# Container packaging

Two application images and a PostgreSQL service make local execution repeatable. The root [Compose definition](../docker-compose.yml) also orchestrates the one-off migration.

```mermaid
flowchart LR
  DB[PostgreSQL healthy] --> Migrate[Alembic completed]
  Migrate --> API[FastAPI ready]
  API --> UI[Nginx serving]
```

| Image | Build approach | Runtime |
|---|---|---|
| Backend | Python 3.13 Alpine with pinned application dependencies. | Uvicorn, UID 10001, port 8000. |
| Frontend | Node 24 compiles React; only compiled assets enter the final image. | Unprivileged Nginx, UID 101, port 8080. |

Run from the repository root:

```bash
docker compose up --build -d --wait
python3 scripts/smoke.py http://localhost:3000
docker compose down
```

The named PostgreSQL volume survives a normal stop. Database ports are private to the Compose network; published application ports bind to loopback.

```bash
docker build -f docker/backend.Dockerfile -t taskboard-backend:local application/backend
docker build -f docker/frontend.Dockerfile -t taskboard-frontend:local application/frontend
```

CI publishes both images to GHCR under full commit-SHA tags after tests, source security gates and image scanning. [Delivery workflow](../.github/workflows/ci-cd.yml) · [security model](../security/README.md).
