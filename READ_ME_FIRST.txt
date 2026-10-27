JANUN existing-data + AI fix
Based on GitHub commit c2ee85a (latest fetched main, after sources-list fix).

INSTALL ONCE
1. Extract this ZIP.
2. Upload the included backend, src and tests folders to the ROOT of deepmitra2002/janun, preserving their paths. GitHub should show seven modified runtime files and two new test files. Do not upload an enclosing ZIP folder. If teammates have changed these files after c2ee85a, compare/merge their edits first.
3. Commit the code update.
4. In Render, deploy the new commit on BOTH janun-api (FastAPI backend) and janun-sqxq (frontend). Wait until both are Live.
5. Refresh /admin with Ctrl+Shift+R. In the AI configuration card, click Test AI connection.
6. If connected, open /ask, clear the old conversation, and ask: জন্ম নিবন্ধন করতে কী কী লাগে?

YOUR EXISTING RECORDS ARE ALREADY IN SUPABASE
No per-record uploads, manual JSON entry, review/publish clicks, SQL updates, migration or new start command are needed for chat to search the existing imported team research.
The existing two-query admin source-list fix is retained.

AI SETTINGS
Keep your existing Render backend LLM_PROVIDER=gemini, GEMINI_API_KEY and LLM_MODEL. All keys stay on the backend.
No new environment variables are required. CHAT_USE_TEAM_RESEARCH defaults to true. Setting it false intentionally restores published-only chat retrieval.
Embeddings are optional; keyword retrieval works without OpenAI embedding credentials.

CONNECTION TEST RESULTS
Connected: confirms a real provider answer with the configured key/model.
Authentication error: check GEMINI_API_KEY and selected provider access.
Configuration error: check exact LLM_MODEL and enabled model access.
Quota exceeded: check provider quota, rate limits or billing.
Timeout/unavailable: retry; check provider availability.
The test does not send your records or questions to the provider: it sends one fixed synthetic test message. It may consume a small provider request.

WHAT CHANGED
Chat can retrieve current pending/review team-imported records without marking them verified or published. This applies only to records already tagged by the team importer. Arbitrary private admin drafts are excluded.
Reviewed results remain preferred. Archived, rejected, stale and superseded material, old versions, and expired previously reviewed records cannot fall back into team research.
Responses using supplied records have an explicit review-pending notice, citations and source badges. Original conflicts, publication restrictions, cycle and date metadata accompany every retrieved chunk. Missing/unknown fields must not be invented.
Provider errors return fixed categories and actionable messages, without provider exception text or secrets.
The admin Test AI connection button checks generation separately from content availability. Provider configured only means credentials/model were detected.

SCOPE
This fix enables chat explanations from the existing imported research; it does not bulk-publish the public reviewed-service directory or remove the strict rules from document comparison. It does not independently verify all imported claims.
No database records or review dates are modified by deploying this update. Keep the same Supabase DATABASE_URL.

VALIDATION
69 backend tests passed.
70 frontend tests passed (9 Node +61 Vitest).
TypeScript and Next.js production build passed.
Actual bundled catalogue:242 records imported into an isolated temporary SQLite database; Bangla birth registration, passport documents and NID correction all retrieved relevant chunks.
Reviewer provenance finding fixed and covered by a real-catalogue regression test.
Live Supabase/PostgreSQL performance and live Gemini quota/model access were not available in this environment. The connection-test button verifies provider access after deployment.

ROLLBACK
Restore the seven runtime files from commit c2ee85a and redeploy both services. No database rollback is needed. To disable only research fallback, set CHAT_USE_TEAM_RESEARCH=false on janun-api and redeploy it.
