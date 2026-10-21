# Janun architecture

The supplied master prompt is the specification. Janun is an independent Bangladesh citizen-services platform, with a life-event planner added to the requested multilingual service directory and RAG assistant.

## Design
Next.js App Router and TypeScript render responsive cream/forest-green interfaces. FastAPI provides validated JSON APIs. PostgreSQL is the production database; pgvector stores embeddings. SQLAlchemy supports SQLite only for isolated automated API tests. Production uses versioned Alembic migrations.

Source versions pass pending → review → verified → published. A human administrator records each decision. New versions suspend old knowledge until review. Retrieval requires current published sources, chunks, and services; expired review dates are excluded. Citation IDs are constrained to retrieved records. An LLM can still misinterpret evidence, so evaluation measures support separately from citation validity.

The journey planner identifies relevant published service records from curated intent mappings; it exposes coverage gaps and builds checklists from reviewed service steps. It does not assert undocumented inter-service dependencies or government approval. Checkbox progress is local and contains no identity documents.

Admin sessions use random opaque tokens (only hashes stored), Argon2 password hashing, HttpOnly cookies, explicit origin checks and request headers. Anonymous questions are not persisted. Ingestion accepts exact allowlisted HTTPS hosts, blocks non-public addresses, disables redirects, limits bytes/time and accepts text HTML/PDF only. Production must also enforce outbound network policy against DNS rebinding.

## Deployment decision
Keep the requested Python/PostgreSQL stack. The built-in Workers hosting cannot directly host this FastAPI service; deliver a Docker Compose application for an appropriate host rather than a disconnected hosted mockup. No API keys or deployment credentials were supplied. Live provider evaluation and public deployment therefore remain conditional.

## Non-goals
No real government submission, payments, NID integration or sensitive document storage. Voice-assisted form filling remains an extension. Do not publish fabricated requirements to populate the UI.
