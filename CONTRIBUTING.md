# Contributing to Janun

Start with the [README](README.md), [reviewer guide](docs/REVIEWER_GUIDE.md) and [current validation record](docs/VALIDATION_CURRENT.md).

## Propose a change

Open an issue or a focused pull request describing the problem, expected behavior and relevant service or route. For interface changes, include actual screenshots at desktop and mobile widths. Keep application changes separate from unrelated catalogue updates.

## Correct service information

Include the official source URL, issuing authority, geographic/applicant scope, publication/effective date and the precise claim being changed. Explain any conflicting source. Do not infer that missing text means a document is unnecessary. Preserve provenance and prior values; imported material must pass the existing human review workflow before being treated as reviewed current guidance.

Use fictional examples. Never attach identity numbers, credentials, OTPs or private documents. Do not include real `.env` files or provider keys.

## Validate

```bash
npm ci
npm run typecheck
npm test
npm run build
```

For backend changes, install `backend/requirements.txt` in a virtual environment and run `python -m pytest -q` from `backend/`. Describe environment limitations and failing checks in the pull request. See the README for the separate database and AI configuration.

## Licensing

No project license is specified. A contribution does not establish permission to redistribute third-party content. Retain existing attribution and asset-provenance files; ask the maintainer before introducing material with unclear rights.
