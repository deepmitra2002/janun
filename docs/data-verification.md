# Source review rules

1. Register the exact official source and the service it supports. Confirm the authority, not only the domain suffix.
2. Fetch only permitted public sources; do not bypass CAPTCHA, logins or robots restrictions. An authorized upload is for material the reviewer is allowed to use.
3. Compare extracted text against the official page/PDF, including dates, applicant categories and exceptions. HTML extraction and PDF parsing can lose structure.
4. Move pending → review → verified → published, recording a review note and review due date.
5. Enter only supported structured claims. Unknown fees/dates are null, not zero. The current JSON claim fields preserve official descriptions; normalized numeric fee modeling is a future migration.
6. Publish the service after its current source is published. Index embeddings if configured.
7. Changed content creates a new pending version and marks the older published version stale. A source reverting to historical content still gets a new review event.
8. Freshness filtering checks the current version and review due date on every public retrieval/detail request. Old versions cannot become authoritative simply by remaining in the database.

The previous and current text are available side by side in the review dialog. This is content comparison, not an automated semantic diff. Source dates record import and review times separately.

Conflicting fee, deadline or processing-time values are hidden and flagged. Cross-source list conflicts still require human review. The LLM must abstain or ask for clarification when applicability or evidence is unclear.
