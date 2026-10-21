# Free Vercel + Render deployment

The Next.js frontend runs on Vercel and forwards `/api/*` to a single FastAPI
service on Render. PostgreSQL must support pgvector. Nothing in these files
creates paid resources. Deployment still requires your hosting accounts.

## 1. Database

Create a free PostgreSQL database with pgvector, for example on Neon. Copy its
connection URL directly into Render's secret environment settings, never into
Git or chat. Keep its TLS parameters, including `sslmode=require`. Render's free
PostgreSQL offering is time-limited and is unsuitable for a lasting database.
Check the provider's current quotas, retention, and expiry terms.

Use one writable database endpoint for application traffic and migrations.
The startup migration creates the vector extension; the database role must be
allowed to do so. Keep embedding dimensions at 1536 unless intentionally
configuring a matching model before the first migration.

## 2. Render API

Push these changes to GitHub, then in Render choose **New → Blueprint** and
connect `deepmitra2002/janun`. Review `render.yaml`; the service plan is `free`.
Supply:

- `DATABASE_URL`: the PostgreSQL connection URL.
- `ALLOWED_ORIGINS`: your exact stable Vercel HTTPS origin (no trailing slash).

If the Vercel project URL is not known yet, set the anticipated origin, then
correct it after Vercel deployment before using admin actions. Never use `*`.
Startup runs migrations, seeds categories, imports research as drafts, and
starts one worker on Render's assigned port. The commands are repeatable.
Free Render lacks a separate pre-deploy command; initialization therefore runs
at startup. Do not scale this configuration to multiple workers/instances.

Wait for `/ready` on the Render service URL to return `{"status":"ready"}`.
Do not invent an onrender.com hostname; use the URL Render actually assigns.

## 3. Vercel website

Import the same repository at Vercel and set:

- Framework: Next.js; Root Directory: `frontend`; Node.js: 24.x.
- `BACKEND_URL`: the actual Render HTTPS service origin, without a trailing slash.
- Keep `NEXT_PUBLIC_DEMO_MODE` unset for the full backend application.

`frontend/vercel.json` configures the locked installation and build commands.
Deploy and copy the stable production URL into Render's `ALLOWED_ORIGINS`.
Redeploy Vercel whenever `BACKEND_URL` changes because rewrites are built into
the frontend. No database password or AI credential belongs in Vercel's public
variables.

Check the homepage and `/api/categories` through Vercel. Create an administrator
privately with `python -m app.cli create-admin` in a supported authenticated
Render shell. Free Render may not provide an interactive shell; in that case,
run the CLI from a trusted local machine with temporary database connectivity.
Do not expose a public admin-creation endpoint. Restrict database networking
again after setup. Review sources before publishing any service.

The public directory starts empty because research records remain drafts. If
you intentionally want the existing research demo instead, set
`NEXT_PUBLIC_DEMO_MODE=true` in Vercel and redeploy; that uses browser-local
research data and does not provide backend admin or real AI features.

## 4. Scheduled checks

The deployed research demo is at
https://janun-dncorleone1211-9558.vercel.app. The scheduled workflow defaults to
checking this homepage and its bundled demo catalogue. Render is not connected
yet. The Vercel deployment uses `NEXT_PUBLIC_DEMO_MODE=true`; turn it off and
set `BACKEND_URL` when the backend is healthy. It was deployed by source upload
because the Vercel account has no GitHub login connection. Connect GitHub in
Vercel before expecting pushes to trigger automatic website deployments.

In GitHub repository **Settings → Secrets and variables → Actions → Variables**,
add `JANUN_SITE_URL` (stable Vercel production origin) and `JANUN_API_URL`
(Render origin) after the full backend is deployed. With `JANUN_API_URL` unset,
only the demo homepage and catalogue are checked. Enable Actions and run
**Website uptime** manually once.
The workflow checks database readiness, rendered homepage content, and the
frontend API proxy every ten minutes. Configure GitHub Actions failure email
notifications in your account. No monitoring credential is required.

This is a health monitor, not a continuous-availability guarantee. GitHub
scheduled jobs can be delayed, skipped, or disabled after repository inactivity.
They only run from the default branch and consume any applicable Actions quota.
Requests may reduce idle time but cannot prevent Render sleep, monthly limits,
provider suspension, database suspension, or cold starts. Do not use synthetic
traffic to bypass provider limits. For continuous availability, use an
always-on Render instance and a durable database, plus an external monitor.

## Limits before a broader launch

Vercel requires a reachable Render HTTPS endpoint, so this deployment exposes
the API to the internet. CORS does not make the API private. Authentication
still protects admin routes, but the current per-process limiter groups proxy
traffic together. Keep one worker; configure a trusted ingress/client identity
policy and distributed rate limiting before scaling. Review `docs/security.md`.
AI generation requires separately supplied credentials and explicit model names.
No deployment URL or live availability is verified until the hosting services
have actually deployed and the HTTPS checks pass.
