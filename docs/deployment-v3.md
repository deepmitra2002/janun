# Janun v3 deployment and configuration

## Current public publication

The existing Sites project is a static export of Next.js, serving the shared catalogue and separate evidence overlay. It hosts local PDF/OCR workers and the device preview; it does not execute Python or run PostgreSQL. Public access is retained. The precise confirmed deployment URL is returned in the delivery message.

## Connect a separately deployed FastAPI backend

The retained backend exports `backend/app/main.py:app`. Deploy it on a Python/ASGI-capable target with `backend/requirements.txt`, PostgreSQL with pgvector, and the existing migrations. Team authorization is currently required to inspect the already discovered Vercel `janun` project. No changes were made to that project after its 403 response.

A same-origin full Next.js server is supported with:

```text
NEXT_PUBLIC_DEMO_MODE=false
BACKEND_URL=http://api:8000
```

Alternatively, the static frontend can call a separately deployed public HTTPS API. Set at frontend **build time**:

```text
NEXT_PUBLIC_DEMO_MODE=true
NEXT_PUBLIC_API_BASE_URL=https://YOUR-API-HOST/api
```

Replace `YOUR-API-HOST` with the actual tested endpoint. `NEXT_PUBLIC_API_BASE_URL` is a public URL, never a secret. Its presence turns off the research adapter; API failures are surfaced and do not silently return snapshot results. Rebuild and redeploy the frontend after setting it. Configure the backend's `ALLOWED_ORIGINS` to the actual Janun origin. Backend administrator sessions retain their same-origin protections; use the full Next.js proxy for supported administrator operations.

Required backend configuration:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB
ENVIRONMENT=production
ALLOWED_ORIGINS=https://janun-citizen-guide.dncorleone1211.chatgpt.site
OPENAI_API_KEY=SET_ON_BACKEND_ONLY
LLM_MODEL=CHOOSE_A_PROVIDER_SUPPORTED_MODEL
EMBEDDING_MODEL=OPTIONAL_SUPPORTED_EMBEDDING_MODEL
EMBEDDING_DIMENSIONS=1536
```

Choose an embedding model/dimension combination that agrees with the existing database/index configuration. No model identifier or credential has been assumed configured.

For explicit server speech:

```text
SPEECH_TRANSCRIPTION_MODEL=CHOOSE_A_SUPPORTED_TRANSCRIPTION_MODEL
SPEECH_SYNTHESIS_MODEL=CHOOSE_A_SUPPORTED_SPEECH_MODEL
SPEECH_VOICE_EN=CHOOSE_A_SUPPORTED_VOICE
SPEECH_VOICE_BN=CHOOSE_A_SUPPORTED_VOICE
```

These are configuration placeholders, not secrets in the browser. `/api/capabilities` exposes configured feature booleans without keys. `/api/speech/transcribe` accepts bounded explicit audio submissions; `/api/speech/speak` sends only the explicitly selected displayed answer. Actual provider language quality must be tested after configuration.

## Existing local Docker path

Use the root `.env.example` and `docker-compose.yml`; set a real database password in `.env`, then run `docker compose up --build`. It runs existing migrations and seeds/imports team research. Speech model/voice variables are forwarded to the API container. Source imports remain drafts until reviewed; deploying containers alone does not publish those records or make grounded AI answers possible.

No new SQL migration was introduced in this update. Optional structured readiness questions continue to use the existing source-claims JSON. The checked overlay is separately versioned; base research data and source-publication rules are preserved.

## Verification before claiming a full integration

1. Confirm `/ready` reaches the production database and pgvector schema.
2. Review and publish applicable official evidence; index approved current versions.
3. Confirm `/api/capabilities` reflects configured AI/speech.
4. Execute Bangla, English and Banglish provider-backed questions with valid evidence citations.
5. Exercise configured claim comparison, published-source journeys, explicit audio recognition/playback and failure states.
6. Recheck CORS, administrator session protections and logs/retention with the operator.

The delivered UI's research explanations and checklists must not be presented as evidence that these live integrations have passed.
