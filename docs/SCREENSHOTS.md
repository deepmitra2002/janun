# Current live-application screenshots

The active README gallery was refreshed from the live Janun application on **26 October 2026**. The images in `docs/screenshots/current/` are genuine browser captures of the deployed application, not mockups or screenshots of an earlier design board.

Source: https://janun-citizen-guide.dncorleone1211.chatgpt.site/

## Capture details

- Desktop: the same 1363 × 936 CSS-pixel browser viewport, Bangla interface, Light appearance. Browser JPEG exports are 1348 × 926 pixels.
- Mobile: the application's functioning **390 CSS-pixel mobile preview**, in Light and Dark. Screenshots are tightly framed around the app. The Dark image is an exact crop of the browser screenshot; no interface text, artwork or colors were generated, repainted or sharpened.
- Onboarding was closed for capture. Menus and transient display controls are excluded from the final images.
- Readiness uses a fictional applicant profile: over 20, applying inside Bangladesh; no identity number or personal document was entered.
- Information Verification shows the clean input screen. A public attestation example was also exercised during inspection; that does not constitute document authentication.
- Ask Janun shows the welcome screen. No live model response is claimed by that image.
- No private account information, credentials, OTPs or submitted applications are included.

## Active gallery

| Image | Live route / state | Repository path |
| --- | --- | --- |
| Home | `/`, Light | `docs/screenshots/current/home-desktop-light.jpg` |
| Services | `/services/`, 271-entry directory | `docs/screenshots/current/services.jpg` |
| Service guide | `/services/team-nafiew-janun-pass-001/`, requirements tab | `docs/screenshots/current/service-guide.jpg` |
| Information Verification | `/verify/`, clean input screen | `docs/screenshots/current/information-verification.jpg` |
| Readiness Check | `/readiness/`, passport preparation flow | `docs/screenshots/current/readiness.jpg` |
| Ask Janun | `/ask/`, welcome screen | `docs/screenshots/current/assistant.jpg` |
| Mobile Home, Light | `/?frame=1`, functioning mobile preview | `docs/screenshots/current/home-mobile-light.jpg` |
| Mobile Home, Dark | `/?frame=1`, functioning mobile preview | `docs/screenshots/current/home-mobile-dark.jpg` |

File sizes and SHA-256 hashes are recorded in [the capture manifest](screenshots/current/manifest.json).

## Vector branding

The README uses the current live app's actual SVG logos, downloaded from its header and footer. These replace the earlier small raster logo in documentation; application assets and behavior were not changed.

- [Green vector logo](branding/janun-logo.svg): `/ui/logos/janun-logo-bn.svg` on the live site.
- [White vector logo](branding/janun-logo-white.svg): `/ui/logos/janun-logo-bn-white.svg` on the live site.

The README's picture element selects the white SVG for a dark color scheme and the green SVG otherwise. The files contain scalable vector paths, preserving the current branding at larger display sizes.

## Historical captures

Older files under `docs/screenshots/v4/`, `v3/` and the earlier handovers remain available as implementation history. They are no longer used by the active README gallery. Historical README material is explicitly labeled and links back to the current root README.

## Refresh procedure

1. Open the deployed application and close onboarding. Use the same desktop viewport, language and appearance for all desktop pages.
2. Capture the routes and states in the table, waiting for service content and fonts to render. Use only public information or fictional preparation answers.
3. Select the built-in Mobile view and capture Home in Light and Dark, preserving the actual 390px app layout. Frame the app itself so text stays readable.
4. Download the actual live SVG branding when it changes. Do not substitute a generated approximation.
5. Inspect every final image for clipping, readable text, loading placeholders and personal information. Update the README, capture manifest and this page together.

Additional route coverage, live microphone behavior and a live provider-backed answer are separate validation tasks; these eight visual captures do not claim those checks.
