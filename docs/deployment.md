# Deployment and operations

## Topology
Browser → Next.js `/api` rewrite → FastAPI → PostgreSQL/pgvector. FastAPI calls the configured OpenAI provider. Only Next.js should be internet-facing. PostgreSQL and API stay on a private network.

Built-in Workers hosting cannot directly run this Python API. Use a container-capable host or deploy Next.js and FastAPI separately with a managed PostgreSQL database. No third-party hosting account or public domain has been configured here.

## Required configuration
- `DATABASE_URL`: PostgreSQL SQLAlchemy URL using `postgresql+psycopg`.
- `ENVIRONMENT=production`: enables Secure admin cookies.
- `ALLOWED_ORIGINS`: exact external HTTPS origin, no wildcard.
- `BACKEND_URL`: reachable API address, supplied before the Next.js build.
- `OPENAI_API_KEY`, `LLM_MODEL`, `EMBEDDING_MODEL`: provider credentials/model choices.
- `EMBEDDING_DIMENSIONS`: must match both provider output and database vector column. The initial migration uses this value. Changing it later requires a new schema migration and complete re-indexing, not an environment edit alone.
- `SOURCE_HOSTS`: exact source host allowlist; no broad wildcard government domain.

Install pgvector in the database service, then `alembic upgrade head`. Do not use ORM create_all as a production migration system. Review the initial SQL in `backend/migrations/001_initial.sql`. Run migrations once per release before starting the API. Compose includes this sequence for a single local API container.

Build commands: backend `pip install -r requirements.txt`; frontend `npm ci && npm run build`.
Start: backend `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --no-proxy-headers`; frontend `npm start` or the standalone Docker image.

Set up HTTPS at the public reverse proxy; apply HSTS there. Preserve Origin headers. Do not expose FastAPI directly without an ingress policy. Do not enable trust of arbitrary forwarded IP headers. Current in-memory rate limiting is deliberately single-process and will group requests from the same proxy. Before a shared public launch, replace it with distributed rate limiting and configure a trusted ingress/client identity policy.

## Health and monitoring
`/health` is process liveness; `/ready` checks the database. Record status codes, latency and provider cost without raw questions or credentials. Alert on provider errors, failed ingestion and sources beyond their review dates. Date filtering excludes expired source knowledge even without a scheduled job.

## Backups
Create encrypted backups outside the repository. Example within Compose:

```sh
docker compose exec -T db pg_dump -U janun -d janun -Fc > janun-backup.dump
```

Restoration should first be rehearsed into a separate empty database. Never overwrite a live database without an explicit maintenance decision. Use `pg_restore --no-owner --dbname=<new_database>` against the rehearsal instance and confirm source records, audit history and vector counts.

## Costs
Each chat can use one query embedding and one generation request. Source indexing calls embeddings per unindexed chunk. Configure account budgets and model token limits. Rate limits are not a complete billing control.

## Public-release blockers
No live PostgreSQL, Docker build, browser QA, real LLM evaluation or deployed HTTPS flow was executed in the authoring environment. Resolve these before claiming public readiness. Legal/privacy pages describe current behavior but still require an actual operator contact and retention schedule.
