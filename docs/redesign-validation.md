# Janun redesign — validation and handover

Date: 25 October 2026 (Asia/Dhaka).

## Delivered behavior

Implemented the supplied green/ivory visual direction with live text and semantic controls, supplied SVG logos/icons, citizen cutout, decorative passport art and skyline. Existing Next.js routes and FastAPI architecture are retained. No new official facts, testimonials or success metrics were added. Six homepage service groups link to real data; other categories remain available. Health/land grouping changes navigation only and retains raw provenance.

Search → shared 254-record research snapshot → focused answer → collected source links was checked in the browser. Banglish defaults to Bangla, English queries to English. Research mode explicitly identifies its search as retrieval without live AI. English research answers avoid silently returning untranslated Bangla factual fields; they direct the user to the original record when a reviewed English translation is unavailable.

Service → preparation questionnaire → result → edit/restart retains current-session answers. Research-mode results never confirm official readiness. Conditional question support consumes explicitly supplied structured conditions; existing prose is not converted into invented eligibility rules.

Information checking → selected service → reviewed text → claim-by-claim result and related links works. Unreviewed records correctly produce insufficient evidence, including for a false-looking synthetic test claim. No document-authentication or fraud verdict is claimed. Full backend comparison uses only published fresh structured claims, rejects unpublished services, and omits stale evidence.

## Dependency security

The final build surfaced advisories in the inherited Next.js version and the initial PDF parser dependency. Updated to Next.js 16.4.3, PDF.js 6.2.108 or later in the lockfile, and a patched undici override. The final npm audit reported zero vulnerabilities. A patched-framework upgrade was recommended and completed before publication.

## Executed checks

- Next.js production export: passed, including all 254 service detail routes, category routes and new readiness/verification/source pages.
- TypeScript type check: passed after test typing correction.
- Frontend: 4 Node tests plus 30 Vitest tests passed. Covers existing routes/data states, query history, language/storage failures, unknown services, search, chat context, source safety, checklist decisions and conditional branches, unreviewed evidence, invalid/oversized uploads, voice fallback and Banglish/English output.
- Backend: 26 pytest tests passed against SQLite fixtures. Covers publication/review gates, freshness, API validation, original flows and new claim-check endpoint with supported/insufficient/stale/unpublished cases and no-store response headers.
- Browser: production export tested through the managed preview. Language toggle, home question submission, automatic question retrieval, passport tabs, readiness answers/results, claim-check results and mobile navigation passed.
- Browser-local text PDF extraction passed with a synthetic, non-personal fixture. The extracted text was editable and removing the file cleared it.
- Homepage responsive frame widths: 360, 390, 768, 1280, 1536 pixels. Measured content widths equalled scroll widths (native scrollbar width excluded); no horizontal overflow. Screenshots reviewed for heading fit, layout, colors and illustration proportions. Responsive frames were used rather than native device emulation.
- Retained screenshots: desktop homepage, desktop service guide, mobile homepage. The mobile capture includes the surrounding QA canvas and represents a real narrow iframe layout.

## Limits and unfinished integrations

- The five new Word documents are absent. The staged import tool is supplied, but no replacement or independent verification of service facts has been performed.
- Hosted version remains a static research preview. FastAPI/PostgreSQL/pgvector, live LLM, persistent feedback, admin writes and generated personal journeys are retained in source and require full server deployment/configuration. Existing audience is preserved.
- The image-upload browser test was denied by the browser's upload approval gate. It was not retried or bypassed. Image/scanned-PDF OCR is integrated with local models, but was not verified end to end in this session. Text-PDF extraction was browser-verified before the PDF parser patch; the patched build was typechecked and built, but upload-based extraction was not re-exercised after the denied upload gate. OCR quality, especially Bengali scans, needs validation with suitable permitted documents.
- Browser microphone recording and actual Bangla/English voice playback were not exercised. The unsupported-recognition text fallback was tested. Recognition may use the browser vendor's service and requires user permission. Local speech voices vary by device.
- Claims use conservative exact matching. Semantic paraphrases, partial support and contradiction need further reviewed claim-level rules or an appropriately grounded provider; no synthetic verdicts are substituted.
- Existing records often combine age-conditional requirements into one prose field. Readiness preserves that text and asks the user to confirm applicability; it does not claim automated age-specific eligibility decisions.
- Live official links were preserved, not re-validated for current service policy. Original research may include secondary links. Genuine attachments are offered only where an actual PDF/image URL was recorded.
- Docker and production PostgreSQL/pgvector execution were not tested. API tests used isolated SQLite fixtures; no live AI credentials or official-record integration were used.
- Next.js development preview did not hydrate reliably in this environment; browser validation used the successful production export. The standard development entry point remains available for local work.

## Deployment

Existing Site identity and audience remain unchanged. Source and output are published together using the Sites workflow. No new schema migration is required; optional reviewed conditional questions use the existing source-claims JSON field. See root README for static preview, manual backend setup, Docker Compose and environment examples. Never expose real environment secrets or pending personal uploads in public assets.
