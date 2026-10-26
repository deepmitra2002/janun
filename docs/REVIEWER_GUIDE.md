# Janun — reviewer guide

Janun is an independent, Bangla-first guide to Bangladesh citizen services. It brings service discovery, document preparation, source inspection and bounded information comparison into one interface. Authorities remain responsible for applications and decisions.

[Open the application](https://janun-citizen-guide.dncorleone1211.chatgpt.site/) · [Competition submission](https://cloudcampbd.com/submissions/4b7d5732-aae6-41d6-8e66-e8519d2c24ce) · [Technical overview](../README.md#technology-and-architecture)

## A five-minute demonstration

1. **Home → Services:** search for passport or birth registration. Show the Bangla/English switch and the recorded review status.
2. **Service guide:** inspect requirements, steps, fees where recorded, original-source links and available document evidence. Point out geographic and date restrictions.
3. **Readiness Check:** choose the service, answer applicable preparation questions, and inspect missing or uncertain items. This is preparation guidance, not eligibility approval.
4. **Information Verification:** paste a short, fictional service-related claim, select its service and compare it with available evidence. Explain an insufficient-evidence result rather than treating it as a false claim. The upload flow also supports browser-local PDF extraction and OCR.
5. **Ask Janun:** ask a specific service question. Identify whether the result is a Gemini response, a research-search fallback or an insufficient-evidence response. Inspect its source links.
6. **Display options:** select mobile view and Dark mode; return to desktop. The preview contains the functioning application.

## What the source demonstrates

| Area | Evidence in this snapshot | Boundary |
| --- | --- | --- |
| Citizen experience | Responsive routes, bilingual navigation, service guides, readiness and source directory | No government application submission |
| Research corpus | 271 service entries, 13 categories; retained 5,037-row original catalogue | All 271 snapshot entries have `verification_status: needs_review` |
| Document integration | Five retained DOCX inputs; provenance, service mappings and replacement ledger | Source confirmation is distinct from independent publication review |
| Hosted AI | `worker/gemini.mjs` retrieves up to three matching services and validates citation IDs | Model prose is not independently fact-checked; availability depends on runtime secrets and provider compatibility |
| Full backend | FastAPI, PostgreSQL/pgvector, source review, retrieval, administration and feedback endpoints | Requires a separately configured backend and database |
| Local document processing | PDF.js and Tesseract with retained worker/language assets | OCR can misread text; user must review extraction |

## Evidence to inspect

- [Current README](../README.md): operating modes, setup, environment and limitations.
- [Document integration report](document-data-update.md): mapping, conflicts and provenance.
- [Service mapping](document-service-map.csv) and [replacement ledger](validation/document-replacement-ledger.json).
- [Source release](../backend/data/document-release.json) and [research snapshot](../public/demo-data.json).
- [Validation record](VALIDATION_CURRENT.md): checks actually performed for this documentation update.
- [Screenshot manifest](SCREENSHOTS.md): reused captures, revision caveats and refresh instructions.

## Submission readiness

The competition URL redirected to an administrator sign-in page during inspection. Competition name, judging rubric, eligibility, deadline and required attachments were therefore not independently established. This guide does not claim compliance with an unseen rubric or imply submission approval.

The GitHub repository was private when inspected. Competition reviewers need repository access or an owner-approved visibility change. No license file was present in the source snapshot. Confirm distribution rights for third-party documents, evidence images, OCR models and artwork before choosing a license or changing visibility.

## Next validation priorities

- Independently review claims, effective dates and source conflicts before publication.
- Exercise Gemini with an operator-configured supported model and record redacted live evidence.
- Run PostgreSQL migrations, review/publish workflow and full-backend integration in a configured environment.
- Refresh screenshots of the latest mobile artwork and test real microphone/speech behavior.
- Evaluate retrieval and abstention using reviewed, representative Bangla and English questions. No accuracy or user-impact metric is claimed here.
