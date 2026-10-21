# জানুন · Janun

An independent Bangladesh citizen-service guide built with **Next.js + FastAPI + PostgreSQL/pgvector**.

This package includes the Phase 2 public-interface improvements. It is not a production certification. It includes real API-backed screens, a human source-review workflow, hybrid retrieval, configurable OpenAI integration and a life-event preparation planner. This edition bundles the five team datasets: **254 service research records and 5,037 total catalogue entries**. Docker startup imports eligible service records as drafts. Open **Admin → team data** to search all collected services and reference lists. See [team-data integration](docs/team-data-integration.md).

The initial seed contains **draft research targets only**. It does not publish invented government requirements.

## Start locally with Docker Desktop

Requirements: Docker Desktop with Compose. This works from PowerShell, Terminal or a Linux shell.

1. Extract this folder and open a terminal in it.
2. Copy `.env.example` to `.env` (PowerShell: `Copy-Item .env.example .env`; macOS/Linux: `cp .env.example .env`).
3. Set `POSTGRES_PASSWORD` to a long random **alphanumeric** password. The Compose database URL requires special characters to be URL-encoded.
4. Optionally set `OPENAI_API_KEY`, `LLM_MODEL`, `EMBEDDING_MODEL` and `EMBEDDING_DIMENSIONS`. Use supported models in your own account. Match embedding dimensions before the first migration. Model identifiers are intentionally not guessed.
5. Start the app:

```sh
docker compose up --build -d
docker compose logs -f api
```

6. Create the administrator (interactive, password hidden):

```sh
docker compose exec api python -m app.cli create-admin
```

7. Open **http://localhost:3000** and sign in at **http://localhost:3000/admin**.

No default admin password exists. The database has a persistent Docker volume. `docker compose down` preserves it; **do not use `down -v` unless intentionally deleting the database**.

## Publish the first reviewed service

1. Admin → Services shows the seeded draft research targets.
2. Admin → Sources → select a service and register the exact official page, document title and agency.
3. Fetch the source, or upload an authorized text/HTML/PDF copy. Source hosts must be in `SOURCE_HOSTS`. Redirects, private addresses and oversized files are refused. Scanned PDFs need OCR outside this first release.
4. Open **Inspect & review**. Compare the extracted text with the official original. Review previous versions where available.
5. Mark `review`, then enter evidence-supported claims and mark `verified`. Use `null` for unknown fees or dates. Record an actual review note. Do not treat a portal homepage as proof of service requirements.
6. Mark the source `published`.
7. Select **Index embeddings** if the embedding provider is configured. Without it, PostgreSQL keyword retrieval remains available; semantic retrieval requires indexed vectors.
8. Admin → Services → **Publish** the service. A current published source is required.
9. Open the service directory, ask a question and inspect its real source cards.

Publication is a human responsibility. The developer does not pre-approve official information on your behalf. Draft services and unreviewed source chunks are not used for public answers.

## What you can use

- Responsive homepage, service directory, category views and service detail pages.
- Bangla-first public navigation, directory, support pages and controls with a bundled Bengali font. Administrative screens, API error strings and original reviewed source content may remain English. Interface switching does not translate official claims.
- Actual source-based chat with citations, uncertainty, provider errors and bounded follow-up context.
- Life-event planner for studying abroad, a new baby, starting a business and identity updates.
- Checklist progress and downloadable text checklist. Progress is held only during the current visit.
- Protected source administration, PDF/HTML/text import, version comparison, review decisions, publication, archive actions, audit history and feedback.
- PostgreSQL schema, versioned migration, draft seed, admin setup, Docker configurations and tests.

The planner uses curated intent mappings and reviewed service steps. It is **not yet an autonomous multi-agent planner**. It does not assert cross-service legal dependencies. Coverage gaps are shown explicitly.

## Without an AI key

The directory, review workflow, feedback and journey planning still work. Chat can retrieve reviewed excerpts but clearly reports that generation is not configured. It never supplies canned factual answers as a substitute for an LLM.

## Development without Docker

You still need a PostgreSQL server with the `vector` extension available.

Backend (Python 3.12):

```sh
cd backend
python -m venv .venv
# Activate .venv using the command for your shell.
pip install -r requirements.txt
# Copy backend/.env.example to backend/.env and set DATABASE_URL.
alembic upgrade head
python -m app.cli seed
python -m app.cli create-admin
uvicorn app.main:app --reload --port 8000
```

Frontend (Node 24):

```sh
cd frontend
npm ci
# Optional: copy .env.example to .env.local; BACKEND_URL defaults to http://127.0.0.1:8000.
npm run dev
```

Run the backend and frontend in separate terminals. `BACKEND_URL` is server-only and is baked into rewrites at frontend build time. Use the same origin for browser API requests.

## Tests and build

```sh
cd backend
python -m pytest -q
```

```sh
cd frontend
npm test
npm run typecheck
npm run build
```

Backend tests use an isolated in-memory SQLite database **only for tests**. They exercise API behavior and policy logic; they do not prove PostgreSQL/vector execution.

After real sources and models are configured:

```sh
python scripts/evaluate.py --url http://localhost:3000
```

The evaluator records answers, source coverage and latency. Human review must still score factual support and correctness. There are no claimed accuracy or performance numbers.

## Validation performed in the build environment

See `docs/validation.md` for actual executed checks and remaining limitations.

## Before a public launch

- Run Compose, migrations and PostgreSQL hybrid retrieval on your machine or host.
- Configure HTTPS, the exact `ALLOWED_ORIGINS`, `ENVIRONMENT=production` and your AI credentials.
- Review and publish a small set of real service documents.
- Perform live AI evaluation, browser/mobile/accessibility QA and a security review.
- Finish the operator’s privacy contact and retention policy.
- Review `docs/deployment.md` and `docs/security.md`.

No production deployment has been performed. This package keeps the requested Python/PostgreSQL architecture rather than replacing it with a static mockup.

## Phase 2 update

See `docs/phase-2-prompt-improved.md` for the reviewed prompt, `docs/phase-2-audit.md` for the baseline, and `docs/phase-2-completion.md` for changes and verification limits. Public search now opens the directory; filters persist in URLs; categories and homepage cards load from the API; review indicators derive from current unexpired source versions. No additional database migration is required. Run `npm ci` after updating to install the bundled Bengali font.
