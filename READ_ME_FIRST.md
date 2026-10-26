# JANUN Gemini setup — 26 October 2026

This update is based on `janun-main_2.zip`, GitHub archive commit
`8aa25e8112872a808aea8c4591f2e8912fa858db` (the v15 deployment).
It changes backend provider configuration and generation only. Existing UI,
catalogue, publication workflows and the friend's other files are retained.

## Upload the changes to GitHub

The connected GitHub tool returned 404 for deepmitra2002/janun. Nothing was
pushed, merged or deployed by this update. The supplied ZIP was the source.

Use the small patch ZIP to update your repository. Inside `changes/`, the paths
match the repository root. Upload the contents with the folder structure intact:

- backend/app/config.py
- backend/app/ai.py
- backend/app/main.py
- backend/app/admin.py
- backend/tests/test_gemini.py
- backend/.env.example
- .env.example
- docker-compose.yml
- docs/GEMINI_RENDER_SETUP.md

The four `backend/app/` files are the runtime changes. The full ZIP is also
provided as a complete source snapshot. Do not upload an enclosing
`janun-main/` or `changes/` directory as a new nested repository folder.
If teammates have committed since the baseline above, merge the supplied
`gemini.patch` instead of overwriting newer files. With a local checkout,
run `git apply --check /path/to/gemini.patch` before `git apply`.

## Configure the existing Render BACKEND: janun-api

Keep the database URL, production environment, CORS origin, Python runtime,
backend root directory, build command and migration/import start command.
Add these variables in **janun-api → Environment**:

| Key | Value |
| --- | --- |
| LLM_PROVIDER | gemini |
| GEMINI_API_KEY | Your Google AI Studio API key, entered only in Render |
| LLM_MODEL | A Gemini text model ID enabled for your project |

Google's OpenAI-compatibility documentation currently demonstrates
`gemini-3.8-flash`. Use that if available to your project; otherwise choose an
enabled model and copy its exact API ID from Google AI Studio. A model name
does not establish quota, free-tier eligibility or billing access.

References checked during this update:

- https://ai.google.dev/gemini-api/docs/openai/
- https://ai.google.dev/gemini-api/docs/models

Leave `OPENAI_API_KEY` and `EMBEDDING_MODEL` empty if you have no separate OpenAI
configuration. Gemini chat does not enable OpenAI embeddings or server audio.
Without embeddings the existing PostgreSQL text retrieval is still used.
Browser OCR and browser-supported speech features are unchanged.

The Gemini endpoint is fixed server-side to Google's documented
`https://generativelanguage.googleapis.com/v1beta/openai/` and uses Chat
Completions with JSON output. The Gemini key is never placed in NEXT_PUBLIC
variables or frontend files. Do not set OPENAI_BASE_URL to Google: OpenAI
embeddings and audio retain their separate existing client.

Save the backend environment changes and deploy the updated commit. Keys
must never be pasted in chat, committed or shown in screenshots.

## Check configuration, then content

1. `/health` should return status `ok`.
2. `/ready` should return status `ready`.
3. `/api/capabilities` should show `ai: true` after the three variables are set.
   This proves configuration detection only, NOT a successful Gemini request.
4. The existing API only retrieves sources eligible under its publication
   query. The most recent observed backend directory contained zero published
   services. Draft imports alone do not provide answerable evidence.
5. Review applicable sources and publish intended content through the existing
   workflow. Do not use bulk publication merely to make the model answer.
   The existing `import-verified-documents` command in this v15 source explicitly
   publishes supplied-document records with `verified_at=None`; it is unchanged
   and was NOT invoked here. It is not independent verification.
6. After suitable evidence is available, submit a non-personal test question
   through `/api/chat`; require `status: answered`, valid sources and the desired
   language. Missing evidence gives `insufficient_evidence`; provider errors,
   refusals or truncated JSON give an unavailable/abstaining response.

## Do not switch the static frontend yet

`NEXT_PUBLIC_API_BASE_URL` changes ALL frontend API traffic, including directory
requests, to the backend. It does not connect chat alone. Setting it while the
backend directory is empty will replace the visible static directory with an
empty live directory. Keep the current static frontend configuration until
publication and live provider checks are complete.

When ready, set the static site's build-time variable to
`NEXT_PUBLIC_API_BASE_URL=https://janun-api.onrender.com/api` and rebuild the
frontend. Keep `NEXT_PUBLIC_DEMO_MODE=true` for static export; the explicit API
URL overrides the demo adapter. Backend `ALLOWED_ORIGINS` must include
`https://janun.onrender.com`. Cross-origin administrator sessions require the
existing same-origin Next.js proxy deployment; merely connecting the static
API URL does not provide that admin setup.

## Validation and limits

The full backend suite passed: **49 tests**. Ten new tests use the real OpenAI
SDK with a local HTTP transport, validating Google URL/auth/request shape,
selected-provider credentials, JSON/citation checks, rate limits, truncated
answers, and abstention without evidence. Existing OpenAI regression tests
remain passing. No new runtime dependency or database migration is needed.

No actual Gemini key was supplied. Live Google quota/model access, answer
quality, production provider generation and the updated Render deployment
remain untested. No frontend files were changed or frontend build claimed.

Rollback: restore the four backend app files from the baseline ZIP and redeploy,
or set `LLM_PROVIDER=openai` with valid separate OpenAI credentials/model.
Changing to OpenAI without those credentials honestly leaves AI unconfigured.
