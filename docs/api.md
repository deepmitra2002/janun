# API reference

Development OpenAPI is available at backend `/docs`; it is disabled in production.

Public:
- `GET /health`, `GET /ready`
- `GET /api/categories`
- `GET /api/services?q=&category=&page=1&page_size=12`
- `GET /api/services/{slug}`
- `GET /api/categories/{slug}/services`
- `POST /api/chat`: `{question, language: auto|bn|en|banglish, history?: [{role,content}]}`. Up to 6 bounded turns; no persistence. Returns answer, language, sources, status, needs_clarification, request_id.
- `POST /api/journeys`: `{goal, language: en|bn}`. Returns reviewed steps, sources, coverage gaps and notice.
- `POST /api/feedback`: `{message, service_slug?}`.

Admin (same-origin session required, mutating requests also need `X-Janun-Request: 1` and an allowed Origin):
- `POST /api/admin/login`, `POST /api/admin/logout`
- `GET /api/admin/overview`
- `GET|POST /api/admin/services`, `PUT /api/admin/services/{id}`
- `POST /api/admin/services/{id}/publish|archive`
- `GET|POST /api/admin/sources`
- `POST /api/admin/sources/{id}/fetch|upload`
- `POST /api/admin/versions/{id}/review|index`
- `GET /api/admin/feedback|audit`

Review input: `{status, note, review_days, claims?}`. Structured claims can be changed only during verification. Every review decision is audited. Backend authorization protects every admin endpoint, regardless of what the UI hides.
