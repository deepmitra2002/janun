# Janun Phase 2 implementation plan
Spec: docs/phase-2-prompt-improved.md
Goal: improve the public interface and connected navigation while preserving Phase 1.
Architecture: existing Next.js client components and same-origin FastAPI requests; small additive backend metadata, no DB migration.

Global constraints: real sources only; no invented verification; preserve original claims and existing auth/RAG; local source package delivery.

Review focus: expired evidence on published services; unknown category versus empty category; failed network responses and retries; URL filter restoration; storage-restricted and keyboard-only users.

## Task 1: truthful directory API
- Add API regression tests for source summary freshness, unknown categories, whitespace/wildcard searches and description keywords. Watch failures.
- Extend backend/app/main.py with batched source summary metadata and safe query terms; preserve old fields and pagination. Keep category endpoint invocation explicit.
- Run backend pytest.

## Task 2: shared public interface
- Add tests for language persistence, blocked storage, document lang and Escape menu behavior; source cards must not crash on malformed URLs.
- Update shell/common/api types, navigation, reusable states and Bengali typography/design overrides.
- Run frontend tests and typecheck.

## Task 3: discovery and details
- Add tests for query restoration/trimming/clear, category validation, network retry, no-match state, service 404, homepage directory search and data-only cards.
- Update home/directory/details, add categories index, wire URL query through existing browser history and truthful API states.
- Run frontend tests; extend only for observed regressions.

## Task 4: verify and deliver
- Localize public supporting pages and preserve backend errors/source content as original text.
- Run backend/frontend suites, typecheck and production build. Record absent lint/browser/PostgreSQL/live-AI checks honestly.
- Fresh final code review; fix important regressions, update docs and README; create source ZIP with reviewed prompt and exact results.
