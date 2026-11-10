# JANUN catalogue parity update

This patch is for the current deepmitra2002/janun main branch, including the earlier live catalogue visibility fix.

1. Extract JANUN_Catalogue_Parity_Fix.zip. Upload its backend folder into the GitHub repository root, merging with the existing backend folder. Commit the files. Do not create an extra nested folder.
2. In Render, open janun-api, then Settings. Replace Start Command with:

```sh
alembic upgrade head && python -m app.cli sync-public-catalogue && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

3. Save and deploy the latest commit. Wait for the API service to become Live. The frontend does not require changes for this patch.
4. Reload https://janun-sqxq.onrender.com/services?category=education with Ctrl+Shift+R. A clean, original import database should now have 13 sidebar categories, 46 Education records and 271 service records overall. Check Agriculture, Land, Local government, Utilities and Social assistance too.
5. Open an updated education card and a passport card. Their titles, descriptions and supplied document details should match the newer catalogue. Pending review labels remain intentional.

The sync runs safely on every startup: it skips records with human metadata/source/content edits, reviews, rejection, withdrawal or renamed import identities. Custom category labels are preserved. Protected records are listed in the startup JSON report, so counts can differ if you have edited records. No Supabase manual upload or SQL is required. Old source versions are retained. This does not independently verify the supplied information or automatically publish reviewed government evidence.

If deployment fails, copy the first exception from janun-api logs. Do not delete database records or rerun the older import-verified-documents command to force matching counts.

Validation: 75 backend tests, 64 browser-component tests and 9 Node tests passed; TypeScript and production build passed. Catalogue test checks every one of the 271 detail routes and tests repeat sync, review/edit protection, source URL changes and renamed withdrawn records.
