# Validation report — 10 October 2026

## Executed successfully
- Backend: `python -m pytest -q` — **19 passed**.
- Frontend: `npm test` — **4 checklist tests + 4 UI-flow tests passed**.
- Frontend: `npm run typecheck` — passed.
- Frontend: `npm run build` — passed, including all public and admin routes.
- Backend: `alembic upgrade head --sql` — initial PostgreSQL migration SQL generated successfully (offline, no database connection).
- Backend Python compile check — passed.
- Installed SDK inspection confirmed the OpenAI Responses and embedding API argument names used in the implementation. No live provider calls were made.

## Important regression fixes
An independent read-only code review identified source recurrence, permissive citation filtering, discarded clarification questions and unbounded robots.txt retrieval. These were reproduced and corrected:
- A → B → A official content recurrence creates a new pending version and invalidates obsolete published content.
- Any fabricated citation ID rejects the answer; string-valued booleans fail strict response validation.
- Clarification questions remain visible; bounded follow-up context is sent without database persistence.
- Both robots and source documents have bounded streamed reads; validated source IPs are pinned with TLS SNI.
Additional tests cover malformed Content-Length and oversized streaming request bodies.

## Unverified infrastructure
- Actual PostgreSQL/pgvector migrations and hybrid SQL retrieval. Tests use SQLite only for isolated API behavior. Docker/PostgreSQL were unavailable; system installation was blocked by runtime permissions.
- Docker image builds and full Compose startup.
- Real model answers, embedding quality and multilingual accuracy. No API key or model choices were provided.
- Live official-source import and a human-reviewed content corpus. Initial services remain drafts.
- Browser screenshots, responsive visual inspection, keyboard/screen-reader audit and HTTPS deployment.

The DOM-based UI tests exercise real components with test-only mocked HTTP responses. They are not equivalent to browser end-to-end tests. Vitest emits a non-failing future configuration-loader warning; the TypeScript/build error was corrected.

## Remaining scope beyond this first build
- Full Bangla translation of every help, admin and error string; calibrated automatic Banglish language detection.
- Rich service-edit and category-management UI (service update API exists).
- Numeric/conditional fee modeling beyond reviewed display text; advanced applicant-specific eligibility rules.
- Asynchronous ingestion jobs, retries dashboard, scheduled freshness tasks and OCR worker.
- Voice-assisted form preparation and an autonomous agent planner; the present planner uses curated intent mappings.
- Provider integration tests and an annotated evidence-support benchmark.
- Distributed rate limiting, production contact/retention process, modal focus trapping and deployment security review.

This report documents a tested first implementation, not completion of every production requirement in the master prompt.
