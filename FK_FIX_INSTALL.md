JANUN catalogue sync database save-order correction

Prerequisite: the previous JANUN_Catalogue_Parity_Fix.zip is already uploaded.

Upload backend/app/catalogue_sync.py from this ZIP to the same path in GitHub, replacing the previous file. Commit it. The included backend/tests/test_catalogue_sync.py adds regression coverage and may also be uploaded.

In Render janun-api, use Manual Deploy > Deploy latest commit. Keep Start Command:

alembic upgrade head && python -m app.cli sync-public-catalogue && uvicorn app.main:app --host 0.0.0.0 --port $PORT

The correction saves services, sources, source versions and chunks in parent-first batches within one transaction. No database reset or manual Supabase changes are required. The failed sync transaction is rolled back by the command.

Validation: reproduced the reported knowledge_chunks foreign-key failure with SQLite foreign-key enforcement enabled, then confirmed the correction passes that regression and all 76 backend tests. PostgreSQL production execution still requires deployment verification.
