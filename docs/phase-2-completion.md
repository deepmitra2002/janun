# Phase 2 implementation report

## Prompt review
The improved executable prompt is in `phase-2-prompt-improved.md`. It tightens data truthfulness, separates directory search from AI questions, keeps the existing category taxonomy, defines current-source review status, clarifies URL/history behavior and errors, limits backend changes, and requires honest verification claims. User authorization was to review first and then execute; both were performed in that order.

## Implemented
- Kept Next.js/React/TypeScript, FastAPI/SQLAlchemy and PostgreSQL/pgvector. Existing admin review, AI, planner, Docker and authentication architecture remains intact.
- Bangla-first public shell with persistent language choice, guarded browser storage, document language synchronization, active navigation, categories index, mobile menu controls, Escape/focus behavior and translated footer.
- Bundled Noto Sans Bengali font; no runtime Google Fonts request. Added one dependency: `@fontsource/noto-sans-bengali` (5.3.0 in lockfile), with regular/semibold CSS imports.
- Homepage directory search, explicit AI entry, API-backed categories and alphabetical service sample, truthful empty/error/retry states, localized FAQs, journey links, independence and feedback messaging.
- Directory query/category/page URL state, trimmed searches, clear/reset, category validation, labelled controls, pagination using response page size and distinct no-match versus unpublished-data states.
- Service details with breadcrumbs, current-source state, source-record authorities, individual review dates, safe external links, 404/error/retry states, race protection, contextual feedback and copy-link feedback. Original reviewed factual text is not machine-translated.
- Small additive API fields: `verification_status`, `source_count`, `last_verified_at`, `authorities`. Computed from current published source versions with unexpired review dates using a batched query. Existing fields retained; no database migration.
- Directory search includes descriptions, tolerates blank queries and returns no results for wildcard-only input. Invalid category filters return 404.
- Public support/policy copy, chat/planner controls and error/not-found pages have Bangla/English presentation. Admin UI, server error strings and original source content can remain English.
- Focus/spacing/type/radius tokens and responsive overrides, readable Bengali line heights, larger controls, reduced-motion support, accessible loading/error/status patterns. Removed duplicate Vitest config warning.

## Validation
Final totals and independent-review outcomes are recorded below after the final run. Tests use isolated fixtures; no invented service records were published.

## Explicit limits
- Browser visual/responsive checks at 360, 390, 768, 1024 and 1440px were not run. This managed environment has no supported control-browser skill, and the Sites workflow forbids improvising another browser. CSS changes and DOM/keyboard tests do not certify visual layout or WCAG compliance.
- PostgreSQL/pgvector/Compose and real AI-provider tests were not run. Backend tests use SQLite in memory; this does not validate PostgreSQL retrieval.
- No production deployment or official source review/publication was performed. Real collected documents still require the existing administrator workflow.
- No lint command/configuration is present in this repository. Typecheck and production build are reported separately, not relabelled as lint.
- No new accounts, payments, government submission, voice, persistent saved journeys or RAG rewrite. New government categories, service-specific FAQs and related-service content require actual reviewed records rather than fixtures.
- Client-rendered category/service missing states display suitable not-found guidance; they do not establish a server-side 404 HTTP response for the Next.js HTML route. API endpoints return 404.
- Some old CSS rules are retained underneath targeted overrides to preserve admin/chat layouts. A future CSS cleanup and browser accessibility audit remain appropriate.

## Run locally
Use the existing README Docker workflow; create an admin, collect/review/publish sources, then publish services. For manual frontend development run `npm ci`, `npm run dev`; start the configured PostgreSQL-backed FastAPI service separately. API requests remain same-origin through Next rewrites. `BACKEND_URL` is server-only and must be configured before build.

## Changed areas
`backend/app/main.py`, API tests; frontend layout, globals, navigation, common states, home, directory/details/categories, information/contact, chat/planner, not-found/error, API types, localization; package manifests; Phase 2 documentation and frontend regression tests. Existing environment files and source data were not overwritten.

## Final verification results
- Backend: `.venv/bin/python -m pytest -q` - **21 passed**.
- Frontend: `npm test` - **4 Node tests + 18 Vitest tests passed** (22 total).
- `npm run typecheck` - passed.
- `npm run build` - passed; includes the new `/categories` route.
- `git diff --check` - passed.
- Total automated tests: **43 passed**. Browser-level rendering, live PostgreSQL, real provider and production checks remain unverified as described above.

Independent static review found no Critical issues. It found a history regression and mobile-menu focus issue; both were reproduced by failing regression tests and fixed, followed by passing full suites, typecheck and build. User filter changes now create history entries; opening navigation focuses its first link and Escape returns focus to the toggle.

Deferred minor: conflicting fee/timing fields are withheld and accompanied by a generic conflict warning; individual affected fields still use the same unknown-value label as missing data. More specific per-field conflict labels can be added later.

Decisions retained: continue in the existing checkout on an improvement branch (avoids a duplicate project); deliver the source package rather than migrating to an incompatible hosting runtime; keep the real database taxonomy rather than inventing categories. These preserve the supplied architecture and records, at the cost of deferring deployment and taxonomy expansion. No merge to the baseline branch or remote push was performed.
