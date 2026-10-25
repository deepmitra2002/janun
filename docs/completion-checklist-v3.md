# Janun v3 — completion and evidence checklist

25 October 2026, Asia/Dhaka. This is a public UI and bounded source-evidence update. It is **not** a completed live-AI/backend deployment.

| Requirement | Status | Evidence and remaining boundary |
|---|---|---|
| Selected visual direction | Complete | Rebalanced header, smaller hero, native Bangla text, supplied logos/icons/citizens, coordinated decorative vector scenery, service tabs and readiness sidebar; Light/Dark desktop screenshots in `screenshots/v3/`. The flattened references are not represented as a pixel-identical reconstruction. |
| Real responsive layouts | Complete | All 15 navigation/footer/admin routes checked at 360, 390, 430, 768, 1280 and 1536px in both themes: 180 checks, no horizontal document overflow. See responsive audit JSON files. |
| Mobile/tablet preview | Complete | Display options render the real app in a same-origin 390/768px iframe. Navigation and forms work; frames do not recursively nest. Natural phones use responsive layout. Return-to-normal control and saved preference provided. |
| Light/Dark/System | Complete | Explicit palettes, local preference, light initial default, system listener, pre-paint theme bootstrap, no inversion filter. All 15 routes audited in both themes; reload persistence checked. |
| Existing directory/categories | Complete | Original 254 records and 10 categories retained. Filtering/navigation regressions pass. |
| Readiness discovery | Complete | Full paginated catalogue is loaded, with name search; no first-50 limit. |
| Conditional readiness | Partial | New passport flow branches by age/location using specific official conditions; answer changes clear hidden/stale branches. Other services use available structured data, with gaps visible. Additional passport circumstances are explicitly unassessed. Human review remains required. |
| Fees and imported codes | Complete for scoped passport schedule | Twelve domestic fee rows, conditions and direct official source replace internal fee-code presentation in service details. All twelve amounts matched the official browser page. Other services retain known/unknown state; no invented fees. |
| Supporting materials | Partial | Genuine official checklist and instruction-page captures, original notice links, issuer and source dates attached to the passport page. Original direct PDF links remain available for 15 records. No new original PDF was downloaded: direct HTTP attempts returned 403; this is recorded, not replaced by a fabricated PDF. |
| Source provenance/review | Complete for preservation | Original snapshot is byte-for-byte unchanged; all 254 research review states remain `needs_review`. The separately versioned overlay identifies specific official pages checked on this date, with publication review still pending. |
| Live AI assistant | Blocked | FastAPI/OpenAI grounded integration is retained and configurable. No provider-backed request succeeded. Current Sites publication has no configured API/database/AI runtime variables. Existing Vercel Janun project cannot be inspected because the connector's team grant returned 403. |
| English answers | Partial | Passport scope has a faithful, identified English explanation and source links; no untranslated-field wrapper for that scope. General grounded translation depends on a configured provider and reviewed content. Banglish defaults to Bangla. |
| Claim comparison | Partial | Supported, contradicted, partial and insufficient results work for the two deliberately scoped passport instruction concepts, with rule summaries and source links. Shared English/Bangla fixtures pass in frontend/backend; all four states exercised in the browser. Uncovered facts are not forced into a verdict. Broader semantic comparison needs reviewed rules/provider configuration. |
| Browser PDF/image extraction | Partial validation | Existing local PDF/OCR implementation retained, with file/type/signature/size/page bounds and explicit review. Text-PDF extraction was browser-tested in the preceding update. New image/scanned-PDF upload tests were not performed after the earlier upload approval denial; current validation includes invalid/oversized inputs and parser/type regressions. No fresh end-to-end OCR-quality claim is made. |
| Voice interaction | Partial / provider blocked | Native user-initiated recognition and device playback retained; unavailable/permission/error text fallbacks. Explicit server recognition/playback integrations added with capability checks, 60-second recording bound, 5 MB audio limit, rate limits and no-store output. Provider credentials/models/voices and actual microphone/audio-device tests are still required. |
| Journey planning | Partial | All four supported research goals produce source-linked preparation starting points, progress and downloadable checklists. Academic-certificate route corrected after browser inspection. No legal dependencies or completeness invented. Full reviewed planning requires backend, published evidence and team access. |
| About/Privacy/Contact/policies | Partial | Public wording now describes actual local preferences, temporary text/files, external speech/AI processing and absent feedback delivery. Feedback drafts can be downloaded. A monitored operator contact and hosting-log retention policy have not been supplied; this absence is explicitly disclosed. No invented contact/retention promise. |
| Five-document migration | Blocked | The five new Word documents are absent. Existing intake tool and original team ZIPs preserved; no replacement migration claimed. |
| Security/privacy | Complete for implemented guards | Existing source publication/authentication protections retained. Uploaded files stay local; server audio requires explicit submission. Original claims are untrusted data; no automatic document authenticity or fraud verdict. Final npm audit: zero reported vulnerabilities. |
| Tests/build | Complete | 4 Node + 45 Vitest + 36 pytest tests passed (85 total), TypeScript and Next.js production export passed. Backend tests use isolated SQLite fixtures, not live PostgreSQL/provider integration. |
| Delivery | Complete after confirmed deployment | Updated source, original datasets, organized assets, screenshots, coverage report, environment examples and this checklist supplied. Existing public Site audience preserved. |

## Specific blockers

1. **Vercel team access:** an existing `janun` project was found, but details, environment and deployment reads returned HTTP 403 because this connection lacks its team authorization. No CLI/browser bypass or changes to that project were attempted. Reauthorize the existing Vercel team connection before inspecting or deploying the backend.
2. **Runtime configuration:** the current Sites publication has zero environment entries; no reachable backend URL, database URL or AI key is configured there. Local task environment also has none of these configured. The inaccessible Vercel project's environment is unknown, not assumed empty.
3. **Human-published evidence:** the base catalogue's research records remain pending. The separately checked source overlay is not a blanket verification of 254 services. Broader provider answers require the existing review/publication workflow.
4. **Operator inputs:** five replacement Word documents, monitored operator contact and hosting-log retention policy remain missing.
5. **Live validation:** provider-backed questions/audio, a production PostgreSQL/pgvector connection, real microphone playback and fresh image/scanned-PDF quality tests have not succeeded in this session.

## Source/attachment access record

Official browser pages read: passport instructions (updated 3 August 2026), fees (updated 12 July 2026), and enrollment checklist notice (updated 21 October 2024). Their literal URLs and capture provenance are stored in `src/lib/evidence-overlay.json`, mirrored in `backend/data/evidence-overlay.json`. The earlier notice at `/landing/notices/34` is a primary-source indexed reference; it was not independently read in full in the browser.

Direct HTTP retrieval of the official instruction, fee and notice pages, and the known land-fee PDF returned 403. The public browser could read the passport pages; genuine page screenshots were captured with their original URLs. A screenshot is labeled as a captured page, never as an original official PDF. Fee data already existed in the supplied team's fee table and was checked against the official page; no unpublished rates were added.

## Coverage

`service-coverage-v3.json` covers all 254 records structurally: 95 have no document list, 135 no eligibility list, 157 no fee, and 178 no processing time in the snapshot. These gaps remain visible. Service-specific factual checking was limited to the stated passport pages, not all catalogue facts or all external links.

## Browser evidence

- `janun-v3-route-audit-light.json` / `janun-v3-route-audit-dark.json`: 15 routes per theme.
- `janun-v3-responsive-audit-light.json` / `janun-v3-responsive-audit-dark.json`: 90 viewport/route checks per theme.
- `screenshots/v3/`: desktop homepage, service, information-check and phone-preview views in Light and Dark. The phone screenshots include the working preview frame, not native-device emulation.

Changes after the audit were limited to compacting explanatory sidebar copy, making the preview toolbar sticky, and improving decorative-icon contrast; the final production build/type check passed afterward. No full mobile keyboard or physical-device test is claimed.
