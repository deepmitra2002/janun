# Janun Phase 2 - reviewed execution prompt

## Role and outcome
Act as a senior UI/UX, frontend, full-stack, accessibility and quality engineer. Improve the existing Janun Bangladesh citizen-services project in place. Execute the work, tests and documentation; do not stop with recommendations. Preserve the Next.js/React frontend, FastAPI backend, PostgreSQL/pgvector, source review, RAG and preparation planner unless inspection proves a minimal integration change is needed.

The user has authorized reviewing this prompt and then executing it. Make routine reversible decisions without another approval round. Keep current environment files, user data and working functionality. Deliver the updated source package and this revised prompt. Continue the existing local source-package delivery workflow; do not replace the app with a hosted mockup or migrate it to a different runtime.

## 1. Inspect and baseline
Read repository instructions, README, configuration, manifests, routes, components, API contracts, schema, source publication rules and tests. Inspect Git status; preserve unrelated edits. Record baseline results and exact gaps in docs/phase-2-audit.md. Do not assume intended features exist. Keep an ordered implementation plan and progress record.

## 2. Truthful service information
Janun is independent, not a government website. Never fabricate requirements, fees, authorities, dates, counts, testimonials, verification or successful API responses. Published service metadata is not proof that its sources are still reviewed and current. Derive current-review indicators from published current source versions whose review deadline has not expired. Display source-specific dates. Hide unsupported factual claims; distinguish unknown fees from free services and conflicting data from missing data. Label original service content separately from interface translations; do not machine-translate administrative instructions as verified content.

## 3. Design and accessibility
Preserve the established restrained green/cream civic identity and Janun wordmark. Define reusable color, spacing, radius, focus and type tokens. Use readable line lengths and Bangla-friendly line height with a suitable Bengali font and fallbacks. Avoid third-party font requests if a local font can be bundled. Reuse shared service cards, status, sources, breadcrumb, loading, empty and error components. Keep touch controls at least 44px where practical, keyboard focus visible, reduced-motion support, semantic landmarks and properly labelled forms. Avoid overflow at 360, 390, 768, 1024 and 1440px; do not claim viewport checks without browser evidence.

## 4. Shared navigation and language
Use a Bangla-first public interface with persistent Bangla/English selection. Handle blocked browser storage without crashing. Synchronize document language on initial restoration and later changes. Provide Home, Services, Categories, Ask Janun, journey and About access without crowding the header. The mobile menu needs aria-expanded, aria-controls, active-page state, Escape closure and appropriate focus return. Navigation and footer links must work. Localize the public Phase 2 surfaces; clearly state any remaining English-only administrative or source content.

## 5. Homepage
Make the prominent search search the service directory. Keep an explicit AI entry point and useful suggested questions. Use real database categories, not an invented static ten-category taxonomy inconsistent with existing IDs. Existing categories are authoritative for this release; extra categories require a reviewed taxonomy and migration in a later phase. Show real service cards when available, an honest empty state otherwise, and retry actions on API failures. Do not call an alphabetical sample popular or recently reviewed. Explain find service, understand requirements, consult official source in three steps. Include independence, freshness, FAQs, feedback and policy links. Use an original lightweight CSS/SVG visual without fabricated service facts.

## 6. Directory and categories
Use existing APIs, typed responses, trimmed bounded queries, Bangla/English search and the backend's limited alias support. Do not advertise comprehensive Banglish search. Preserve query/category/page in URL state so reload and browser navigation do not lose filters. Include clear filters, accessible category controls, results feedback, pagination based on returned page size, loading/empty/error/retry states and real links. Differentiate no published records from no matches. Validate category slugs; known empty categories are not errors, unknown categories are not empty successful categories. Category pages need a localized title, description and breadcrumbs.

## 7. Service details
Render overview, source-record authorities, eligibility, documents, steps, official portal, fees, timing, deadline, source links, review status and source dates. Show missing fields honestly. Render FAQ or related-service data only if actually available. Provide contextual feedback and a working copy-link action with visible failure feedback. Clear old details on slug change and ignore stale requests. Distinguish a 404 from a retryable network/server error. Do not imply that the official portal URL is evidence for every claim.

## 8. Minimal backend work
Keep existing endpoint compatibility. Add only metadata and search fixes necessary for truthful public presentation. Search names and descriptive keywords safely, normalize whitespace, handle wildcard-only queries predictably, and reject unknown category filters. Any added summary fields must be derived from real current reviewed versions, not service status alone. Preserve admin and AI behavior. Do not add accounts, payment, voice, a new RAG pipeline, or new government submission flows.

## 9. Verification
Write regression tests for URL state, search trimming, retries, category validation, unknown versus empty results, stale request handling, source freshness, localization/storage failures, mobile keyboard interactions and truthful metadata. Reuse isolated fixtures; never expose test data as verified production data. Run backend suite, frontend suite, typecheck, configured lint and production build. If lint is not configured, state that; do not label another check lint. Browser, PostgreSQL and live-AI checks require actual capability and credentials. Never install or improvise browser tooling contrary to the environment's supported workflow. Distinguish implemented, automatically tested and unverified results.

## 10. Documentation and delivery
Update docs/phase-2-audit.md, docs/phase-2-completion.md and README. Include prompt review decisions, changes, exact test results, dependencies, run commands, known limitations and Phase 3 prerequisites. Package the source without credentials, dependencies, caches or runtime data. Do not claim production certification, full accessibility compliance or deployment without evidence.

## Ordered execution
1. Audit and baseline. 2. Shared design/language/navigation. 3. Truthful API metadata and search behavior. 4. Homepage/directory/categories/details. 5. Regression checks and review. 6. Documentation and source package.
