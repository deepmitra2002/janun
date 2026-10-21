# Public JANUN demo

The user authorized public display of team research on 2026-10-12 (UTC), pending later human verification.

- Run `python scripts/build_demo_data.py` to regenerate the 254-service snapshot from the five-team catalogue.
- Set `NEXT_PUBLIC_DEMO_MODE=true` before building the frontend to enable the browser-local demo adapter.
- Directory search, category filters, service pages and the question interface use the same snapshot.
- Chat is extractive keyword retrieval with source links; it does not call an LLM, translate source facts, or perform fresh government verification.
- Records retain needs_review, a null human review date, supplied geographic scope, original fields and limitations. Collected links can include secondary sources.
- The original 5,037-row catalogue and all source ZIPs remain available. The public directory contains 254 service records, not all reference rows or a complete office directory.
- Full backend admin review, persistent feedback and personalized journey generation are not hosted in this static demo. Unsupported actions explicitly say so.
- Backend publication gates are unchanged; demo mode is an explicit frontend override.

Hosted source is a static export of the retained JANUN frontend with generated detail routes. Sites project: appgprj_6acd21ce07cc81919a97632397ff8882.
