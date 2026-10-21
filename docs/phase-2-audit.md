# Phase 2 audit

Baseline: commit 112f4ed. Working tree was clean. Existing stack: Next.js 16.4 / React 19 / TypeScript / Tailwind 4; FastAPI/SQLAlchemy; PostgreSQL/pgvector; source review and RAG. No replacement architecture needed.

Baseline checks: backend 19 passed; frontend 4 Node checklist tests + 4 Vitest public-flow tests passed. Typecheck/build recorded separately on completion. No lint script exists. Duplicate vitest.config.ts and .mts are identical and produce a configuration warning.

Findings:
- Homepage search routes to chat, categories are static, no live service discovery cards.
- Directory ignores URL search, has no clear/retry, swallows category failures, advertises broad Banglish support without corresponding coverage.
- Category route passes any slug into a filter and displays a generic directory title.
- Detail conflates 404 and outage; lacks request cleanup, review status, agency summary and retry.
- Published directory records have no source-freshness metadata; publication is not equivalent to a current review.
- Language selection defaults to English, storage can throw, restored language does not update html lang; footer and most public labels are untranslated.
- Mobile nav lacks expanded/control attributes and Escape behavior; focus and Bengali line height need improvement.
- Existing app already has backend-connected chat, planner, feedback and protected administration. Preserve them.

Environment: managed Sites container; no supported control-browser skill available. Do not launch a preview or improvise a browser. Browser viewport/accessibility visual QA will remain unverified. PostgreSQL/Docker and live provider/source credentials are not configured in this task; isolated SQLite API tests are not evidence of PostgreSQL operation.

Prompt review improvements: specify directory-vs-chat search, real taxonomy instead of invented categories, current source status rather than publication badges, URL filter persistence, retry/404 semantics, safe language persistence, original-source language distinction, bounded backend changes and explicit delivery/test limits.
