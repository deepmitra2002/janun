# Janun v4 setup and deployment

The frontend remains at the repository root, FastAPI at `backend/`. The existing `.openai/hosting.json` Site identity is retained. `docs/design-implementation-v4.md` is the current implementation/status report.

## Static research preview

Requires Node compatible with the locked Next.js version (the checked environment used Node 24).

```bash
npm ci
cp .env.example .env.local
# Keep NEXT_PUBLIC_DEMO_MODE=true for the local research preview.
npm run prepare:assets
npm run dev
```

The committed `.env.production` enables research mode. To produce static output:

```bash
npm run typecheck
npm test
npm run build
```

Serve `out/` over HTTP(S) with directory `index.html` routing. Do not open it with `file://`. Keep `public/demo-data.json`, PDF workers, WebAssembly, OCR workers and language models available. The OCR models are retained for browser-local Bangla/English extraction. A runtime-only environment change cannot retrofit server behavior into an already built static export.

## Full backend deployment

1. Configure PostgreSQL/pgvector and set a strong `POSTGRES_PASSWORD` using the supplied environment examples. Keep credentials outside Git and outside browser bundles.
2. Configure server `ALLOWED_ORIGINS`, session/cookie and administrator settings as documented in `backend/.env.example` and the existing architecture/deployment documents.
3. Set provider values on the backend: `OPENAI_API_KEY`, `LLM_MODEL`, and optional embedding settings with matching dimensions. Configure server speech only if needed.
4. For the Next.js server build, set `NEXT_PUBLIC_DEMO_MODE=false` in the build process environment and set server-only `BACKEND_URL`. To use a separately hosted HTTPS backend from a static client, set `NEXT_PUBLIC_API_BASE_URL` at build time, configure origins deliberately, and verify credential/cookie behavior before enabling administrator access. Never place provider secrets in a `NEXT_PUBLIC_*` variable.
5. The retained Docker Compose path builds the server frontend and FastAPI/database services. Review `.env.example`, run migrations/imports using the existing workflow, then initialize an administrator with the documented CLI. There is no default admin password.
6. Review and publish evidence through the retained workflow; do not promote research records directly for cosmetic purposes.

```bash
cp .env.example .env
# Fill the environment file with your real server settings.
docker compose up --build
```

Docker/PostgreSQL/provider production operation was not executed in this UI task. The isolated backend tests passed; that does not certify hosting or live integrations.

## Current hosting

The public Sites publication uses the retained static `out/` configuration and audience. The hosting source repository is synchronized before saving and deploying a new version. This task does not change GitHub repository visibility or include credentials in the source ZIP. See the handover report for the final publication result.
