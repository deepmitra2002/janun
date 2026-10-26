# Documentation validation — 26 October 2026

## Scope

Documentation and supporting assets for the uploaded `Janun-v15-Source.zip`, with the complete supplied source synchronized into the existing GitHub repository. Application behavior was not intentionally changed. Existing repository-only files and commit history are retained.

## Evidence baseline

- Inspected package/lockfile, scripts, Next configuration, routes, API adapter, snapshot, environment examples, Dockerfiles, Compose, FastAPI configuration and AI logic, hosted Gemini worker, document extraction and historical documentation.
- Confirmed the snapshot has **271 services**, **13 categories** and `needs_review` on **all 271** service entries.
- Confirmed the GitHub account owns `deepmitra2002/janun`, with write permission; repository was private at inspection.
- The competition URL opens an administrator authentication route. No unseen rubric, award, event-specific eligibility or submission acceptance is claimed.
- The hosted Janun homepage rendered in its interactive 390px device-preview frame, with search, service links, readiness, comparison and language controls visible. This observation is not a full live API/deployment verification.

## Executed checks

| Check | Result |
| --- | --- |
| Dependency installation | `npm ci --offline --no-audit --no-fund` completed; 154 packages added |
| Worker/journey tests | `node --test tests/*.test.mjs`: **9 passed, 0 failed** |
| TypeScript | `npm run typecheck` passed |
| Frontend tests | `npm test` passed: 9 Node tests plus 57 Vitest tests (66 total) |
| Production packaging | `npm run build:hosted` completed with exit code 0; Next.js generated 314 static pages and the hosted worker bundle |
| README/new documentation links | 53 local link/anchor targets passed; archived README file targets also passed |
| Uploaded source completeness | All 359 uploaded files other than the intentionally replaced root README matched byte-for-byte in the Git checkout |
| Credential-pattern scan | No matches for the scanned provider/GitHub credential patterns in source/config files; this is a bounded check, not a security audit |
| Documentation whitespace | The newly authored README/guides pass the scoped Git whitespace check. Imported CSV and historical logs retain their original CRLF/trailing whitespace for source fidelity. |
| Screenshot inspection | Superseded by the live-app refresh below: eight fresh screenshots inspected and linked from the README |

The Node tests exercise citation-ID rejection, document-release fact retrieval, provider-key header handling, foreign-origin rejection, insufficient-evidence behavior and journey dependencies. Provider behavior in these tests is simulated; this does not establish live Gemini success.

## Unverified integrations

No real provider credential was used. PostgreSQL/pgvector, Docker Compose, backend migration execution, persistent feedback/admin writes, actual speech recognition/playback and complete deployment were not verified. Earlier reports under `docs/validation/` describe previous work and are not counted as newly executed checks.

## Final execution notes

The initial handover used v4 captures after local Playwright could not start. That gallery has now been replaced by the live-app refresh below.

The owner explicitly confirmed `deepmitra2002/janun` as the destination. On resuming, GitHub reported it as public; the owner’s requested private visibility was applied and verified before continuing the upload. The update uses a normal commit based on the existing main branch, preserving history and repository-only files. The live application deployment and competition portal are unchanged. Fresh screenshot capture is now completed as described below. Live backend/provider validation remains outside this visual update.


## Live screenshot and vector-logo refresh

On 26 October 2026 the deployed application was inspected directly. Eight fresh screenshots now replace every old image in the active README: desktop Home, Services, the updated passport guide, Information Verification, Readiness Check, Ask Janun, and mobile Home in Light and Dark. Desktop screenshots use one consistent viewport. Mobile images show the real 390px preview and are tightly framed without regenerated content.

The current green and white SVG logos were downloaded from the live application and added under `docs/branding/`. They replace the README raster logo and support light/dark color schemes. The updated capture manifest records SHA-256 hashes and file sizes.

Readiness used a fictional age/location profile. A public service-information comparison was observed without entering personal information. Screenshots show the clean verification form and assistant welcome state; they do not claim full-backend or live-provider verification. Application source and runtime behavior were unchanged.

README asset paths, heading anchors, SVG XML, screenshot dimensions and file hashes were checked. The published GitHub README is checked for image loading after the documentation commit. Earlier test/build results above apply to the unchanged application source; tests were not rerun for this visual-only documentation change.
