# Janun UI implementation — nine-board handover

Date: 25 October 2026 (Asia/Dhaka). This report supersedes earlier UI milestone descriptions; earlier data and integration limitations remain applicable unless explicitly resolved here.

## Scope and evidence

Read `MASTER-PROMPT.txt` completely and inspected each of the nine numbered boards separately. Opened the current hosted Site source (commit `86a775fddce67ba2898bffe68cfb36e3133b544d`) before editing. Implemented real React components over the retained Next.js/FastAPI architecture. Boards were never installed as page backgrounds. No fabricated government notices, dates, administrative records or sample verdicts were imported.

## Board-by-board checklist

| Board | UI status | Implementation and evidence | Runtime/data limits |
|---|---|---|---|
| 01 Home | Complete | Broad memorial/flag/sun hero with separate citizens, dominant search and voice control, six live category cards, three feature actions, source strip and footer. Light/Dark/mobile screenshots `01-home-*`. | Decorative composition reuses the selected memorial and existing citizens rather than copying a flattened board. |
| 02 Services | Complete | Directory and category routes, responsive sidebar/chips, search, compact horizontal service cards, real review badges, A–Z/Z–A sorting across the full result before pagination, URL filters and working pagination. Screenshots `02-services-*`. | All 254 existing records retain provenance and review states. Sparse summaries are not replaced with invented prose. |
| 03 Guide | Complete | Shared three-tab template, document tiles, eligibility, application steps, source provenance, real notices/captures, fee tables and contextual readiness. Keyboard arrow navigation tested. Screenshots `03-guide-*`. | Direct PDFs appear only if recorded; absent attachments are explained. NID/BRC abbreviations are expanded in requirement tiles. Applicable source conditions remain scoped. |
| 04 Information check | Complete within supported comparison rules | Text/file controls, service search, locally processed PDF/image uploads, progress, editable text, removal and consent; citation-backed supported, contradicted, partial and insufficient-evidence results; unreadable fallback retained. Screenshots `04-check-*` use explicitly entered public test statements. | This is information comparison, not authentication of documents, seals, signatures or identity. Broad semantic analysis is not connected. Single-file limit remains the implemented 8 MB / 10 PDF pages / 16 megapixels / 20,000 extracted characters, rather than copying the board’s sample limit. |
| 05 Readiness | Complete | All-service search, collapsible editable selection/context, question stepper, Yes/No/Not sure, back/next, restart, answer editing and live preparation summary. Child/adult branching and answer reset tested. Screenshots `05-readiness-*`. | Only evidence-supported passport context is conditional. Other service questions retain their recorded requirements. No eligibility or approval guarantee. |
| 06 Assistant | Complete UI and retained retrieval | Memorial masthead, topic sidebar, real answer blocks, sources, next actions, editable composer, output language, copy, user-initiated voice controls and provider-state labels. Screenshots `06-assistant-*` show an actual bounded research response. | Live provider AI and server speech are Blocked: backend/provider configuration is absent. Browser speech depends on permissions and installed/browser-supported voices. |
| 07 Sources | Complete | Search, government/secondary/attachment filters, pagination, readable source cards, agency/collector distinctions, original URLs and real captured-page previews. Screenshots `07-sources-*`. | Government domain classification is not verification of every claim. Some retained records identify a research collector rather than a responsible authority; no authority was invented. |
| 08 Journey | Complete UI; Partial personalized planning | Four working goal cards preserve the existing identity-correction option in addition to the board’s three goals; real research-linked starting points, checkboxes, download, summary and explicit gaps. Screenshots `08-journey-*`. | Cards use consistent vector icons rather than recreating the flattened board’s character illustrations. Research plans are not completed official procedures; provider-backed personalized planning remains unavailable. |
| 09 Support/admin | Complete public support; Partial protected review parity | About values/process cards, Contact topic chips, editable draft/download, FAQ/help links, coordinated policies, protected admin entry and styled existing authenticated review controls. Screenshots `09-about-*`, `09-contact-*`, `09-admin-*`. | Feedback delivery and authenticated hosted review are Blocked until a backend is connected. Existing session, CSRF, authorization, audit, review and publication safeguards are retained. Authenticated visual comparison cannot be certified from the public preview; no fake records or public approve/reject buttons were substituted. |

## Shared requirements

| Requirement | Status | Evidence |
|---|---|---|
| Forest/ivory/sage/terracotta system and Bengali typography | Complete | Shared tokens and component rules in `src/app/redesign.css`, Noto Sans Bengali; all mapped routes use real selectable text. |
| Responsive Light/Dark on all mapped and policy routes | Complete | 192 URL- and viewport-checked browser cases: 16 routes × 6 requested widths × 2 themes; zero horizontal page overflow and zero broken images detected. See `validation/v4/responsive-audit.json`. |
| Light / Dark / System | Complete | Persistent existing preferences, initial pre-hydration theme script, explicit dark surfaces. Browser reload/persistence and System selection tested. |
| Desktop / Tablet / Mobile preview | Complete | Actual interactive same-origin iframe; corrected inner widths 390 and 768 px; exit control, route navigation and absence of recursive frames tested. Natural devices use responsive layout. |
| Preserve data/assets/security | Complete | Byte comparisons of snapshot, full catalogue, evidence files and five original research archives; 254 services and 5,037 team rows unchanged. Backend security regression tests passed. |
| OCR and file privacy | Complete | Browser PDF extraction and image OCR passed using synthetic fixtures. Removal clears extracted text. No original document is sent to an analysis server in research mode. |
| Keyboard/focus | Complete for checked paths | Service tabs accept arrow keys; menu Escape and focus styles retained; forms and major actions are native controls. OS mobile keyboard behavior has not been physically tested. |
| Exact visual identity with all generated pixels | Partial | All boards were compared with actual browser screenshots. Corrected stacked desktop cards, excessive readiness setup height, duplicate monument art, clipped About artwork, assistant autoscroll and preview-width discrepancy. Retained artwork, truthful content length, goal icons, research warnings and a gated admin view cause intentional practical differences. No pixel-perfect claim is made. |

## Checks actually run

- `npm run typecheck`: passed.
- `npm test`: 49 Vitest/React tests and 4 Node tests passed (53 frontend tests).
- `/tmp/janun-test-env/bin/python -m pytest -q` in `backend`: 37 passed. Tests use isolated test data; this is not proof of a deployed database/provider integration.
- `npm run build`: passed; all existing static service/category routes generated.
- `git diff --check`: passed.
- Browser: 15 recorded workflow checks passed, including claim states, conditional reset, editing, file removal, local PDF extraction, image OCR, filtering/sorting, empty state, persistent theme, mobile and tablet preview, source attachments and keyboard tabs.
- Browser layout audit: 192 cases passed, with actual route URL, theme and viewport recorded per measurement.
- Screenshot evidence: desktop Light/Dark and mobile Light/Dark for the 11 mapped views (44 captures). Captures include the temporary review toolbar and device frame outside the app. They are viewport captures, not full-page exports; representative long guides, comparison results and plans were also inspected beyond their initial viewport. The temporary review harness is excluded from publication and source delivery.

Raw logs and audits are in `docs/validation/v4/`. Screenshots are in `docs/screenshots/v4/` and the separate screenshot ZIP.

## Exact remaining blockers

1. **Hosted backend/database:** the existing public Site is a static research export. No API origin or database runtime variables are configured in Sites. It does not host FastAPI/PostgreSQL. Configure and deploy those services before enabling full server behavior.
2. **Live AI / server speech:** no backend provider credentials, model or successful provider-backed request. Research retrieval and scoped source explanations remain operational and clearly labeled.
3. **Protected admin and feedback delivery:** require the configured backend, an initialized administrator, session/origin settings and a monitored operator contact. Contact currently downloads a local draft; it never claims to send it.
4. **Five replacement Word documents:** not supplied. No migration or duplicate replacement was performed. Existing original research archives remain intact.
5. **Human source review:** original review states are preserved. Source visits and narrow rule comparisons do not turn the full dataset into current reviewed official guidance.
6. **External/device verification limits:** original source links were preserved, not revalidated exhaustively in this visual update. Microphone permission/physical mobile keyboard behavior and authenticated production admin interactions were not tested with a live provider/server.

The development preview temporarily stalled on its data file. The optimized production export loaded the same snapshot correctly and was used for the recorded browser QA; application data was not altered to mask that preview issue.
