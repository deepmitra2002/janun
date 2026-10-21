# Five-team data integration

The supplied Nafiew, Deep, Sachin, Tammam and Sami archives are combined into `backend/data/team-catalogue.json`. It contains 5,037 searchable entries, including 254 service research records. Other entries are facilities, institutions, offices, source metadata, fee tables, mappings and audit reports; they are not counted as unique citizen services.

## Use the app

1. Follow the main README to set up `.env` and start `docker compose up --build -d`.
2. Startup runs migrations, seed, and `python -m app.cli import-team-data` automatically. The importer adds eligible service records and pending source versions, without modifying existing services or publishing them.
3. Create/sign in with your administrator at `/admin`.
4. Open **team data**. Search Bangla/English text, select a member, choose services or reference material, and filter a table. Full original fields are visible in each record.
5. Review imported records in **Sources**. Uploaded research summaries are explicitly labelled editorial; they are not original official documents. Verify the linked official source and enter structured claims using the existing review editor before publishing.
6. After source and service publication, existing public directory and chat retrieval use the approved content. Unreviewed uploads never become public chatbot evidence automatically.

For a non-Docker installation, after migrations and seed:

```sh
python -m app.cli import-team-data
```

Restarting or rerunning import does not duplicate identical records. Changed existing services/sources are reported as conflicts, not overwritten. Records with no resolvable HTTPS source remain searchable in team data and appear in `needs_source` in the import report.

## Preservation and duplicate handling

- Original archives are included under `team-data-originals/`; no uploaded archive was modified.
- CSV field values and source verification labels remain intact in `payload`. Metadata IDs are namespaced by member/table to avoid collisions.
- Redundant exported JSON copies are not imported again as separate CSV services. Sami's `programs.csv`, Tammam's `programs.csv` and summary directories remain reference tables.
- Sachin's disabled/duplicate candidates remain searchable but are not staged for publication.
- Exact-name matches are candidates in the catalogue, not automatic semantic merges. Same URLs can serve different services and different local rules; no URL-only merging occurs.
- Source citations and geography remain in their original records. This change does not implement automatic jurisdiction-aware public retrieval or assert complete national coverage.
- Import requires a trusted local operator, performs no remote fetch and does not expand SOURCE_HOSTS. To fetch a new source in Admin, add its reviewed exact hostname through the existing configuration.

## Rebuilding the catalogue

From the app root, provide a directory containing the original five archives:

```sh
python scripts/combine_team_data.py team-data-originals --output backend/data/team-catalogue.json
```

This is an integration of supplied research, not a new verification of government rules. A completed import is not human approval. Package metadata, record ID, original status and known gaps are visible for review.

## Executed validation

- 24 backend tests passed, including authenticated catalogue access, pagination/search, source isolation and repeat-import behavior.
- 19 frontend component tests and 4 planner tests passed.
- TypeScript check and Next.js production build passed.
- Isolated SQLite import: 242 drafts created; second run skipped the same 242; zero conflicts. Eleven Sachin records remain disabled as supplied. Tammam EDU-015 has no resolved HTTPS source and stays in the catalogue only.
- No live PostgreSQL deployment or user-hosted database was accessed.
