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
| Screenshot inspection | README images come from the supplied genuine v4 capture set; revision differences are explicitly disclosed |

The Node tests exercise citation-ID rejection, document-release fact retrieval, provider-key header handling, foreign-origin rejection, insufficient-evidence behavior and journey dependencies. Provider behavior in these tests is simulated; this does not establish live Gemini success.

## Unverified integrations

No real provider credential was used. PostgreSQL/pgvector, Docker Compose, backend migration execution, persistent feedback/admin writes, actual speech recognition/playback and complete deployment were not verified. Earlier reports under `docs/validation/` describe previous work and are not counted as newly executed checks.

## Final execution notes

The preview development server started successfully at port 3000. A fresh Playwright screenshot attempt failed before navigation because its browser executable was not installed. The eight README captures were therefore visually inspected and reused from the supplied v4 files, with revision caveats and exact refresh instructions. No new v15 screenshot or rendered GitHub README preview is claimed.

The owner explicitly confirmed `deepmitra2002/janun` as the destination. On resuming, GitHub reported it as public; the owner’s requested private visibility was applied and verified before continuing the upload. The update uses a normal commit based on the existing main branch, preserving history and repository-only files. The live application deployment and competition portal are unchanged. Fresh screenshot capture and live backend/provider validation remain outstanding as documented above.
