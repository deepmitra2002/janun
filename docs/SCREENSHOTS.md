# Application screenshot provenance

The source upload contains 56 application capture files. The README currently reuses eight genuine captures from `docs/screenshots/v4/`, covering Home, Services, the service guide, Information Verification, Readiness Check, Ask Janun and mobile Light/Dark views. No generated mockup is presented as an application screenshot.

These captures were supplied with the application source. They show a design-review frame and an earlier revision. They have been inspected for rendering/readability; they are not evidence of a successful live provider call. The latest v15 mobile homepage artwork differs. Historical captures remain under their original paths rather than being renamed as new evidence.

## README asset mapping

| Screen | File relative to repository root | Revision |
| --- | --- | --- |
| Home, desktop Light | `docs/screenshots/v4/01-home-desktop-light.jpg` | Earlier v4 |
| Services | `docs/screenshots/v4/02-services-desktop-light.jpg` | Earlier v4 |
| Service guide | `docs/screenshots/v4/03-guide-desktop-light.jpg` | Earlier v4 |
| Information Verification | `docs/screenshots/v4/04-check-desktop-light.jpg` | Earlier v4 |
| Readiness Check | `docs/screenshots/v4/05-readiness-desktop-light.jpg` | Earlier v4 |
| Ask Janun | `docs/screenshots/v4/06-assistant-desktop-light.jpg` | Earlier v4 |
| Home, mobile Light | `docs/screenshots/v4/01-home-mobile-light.jpg` | Earlier v4; artwork superseded |
| Home, mobile Dark | `docs/screenshots/v4/01-home-mobile-dark.jpg` | Earlier v4; artwork superseded |

## Capture the current revision

1. Follow the root README's research-preview setup. Disable the hosted Gemini flag for local-only capture. Use the bundled data; do not introduce real personal documents or credentials.
2. Start `npm run dev` and open `http://localhost:3000`. Close the guided tour if present. Use a consistent 1440 × 1000 desktop viewport and Light appearance.
3. Capture `/`, `/services/`, one relevant `/services/<slug>/` guide, `/verify/`, `/readiness/` and `/ask/`. Wait until catalogue content and fonts render; avoid loading/error placeholders.
4. Use a 390 × 844 viewport for Home in Light and Dark. Check the actual responsive page and the built-in mobile-preview frame. Confirm the latest flag, memorial, sun and citizen artwork is visible.
5. Save fresh captures under `docs/screenshots/current/` as `home-desktop.png`, `services.png`, `service-guide.png`, `information-verification.png`, `readiness.png`, `assistant.png`, `home-mobile-light.png` and `home-mobile-dark.png`.
6. Inspect text readability, navigation, clipping and any personal information. Link only files that exist. Update the README gallery, captions and this manifest together.

Fresh v15 captures remain outstanding until a running local instance and screenshot export complete successfully. The hosted application was visibly accessible during this task, but inspection alone is not a saved screenshot deliverable.
