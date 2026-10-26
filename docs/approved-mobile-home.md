# Approved mobile homepage artwork

## Cause and change
The previous mobile rules reused a wide landscape with background-size: cover at 57% center, plus a separate citizen cutout. The crop concealed important scenery and the two independent layers made mobile composition fragile.

The mobile homepage now uses the supplied mobile-home-approved.png (1199 × 698) as one width-fitted image in normal document flow. Text, search/voice controls and wrapping chips remain real interactive components above it on a matching quiet sky background. Width is 100%, height is auto, object-fit is contain, and no fixed hero height is used. Previous mobile background and character layers are hidden. The supplied artwork is copied byte-for-byte and is neither recolored nor inverted.

Styles are confined to the homepage at max-width:760px. Tablet and desktop retain their original layers. Search, voice handler, routes, onboarding, theme logic and all source data are unchanged.

## Local browser verification
Actual homepage documents in exact-width QA frames:

| Viewport | Body / scroll width | Artwork dimensions | Gap to category section | Old visible layers |
| --- | --- | --- | --- | --- |
| 360px | 360 / 360px | 360 × 209.56px | 1px border | 0 |
| 390px | 390 / 390px | 390 × 227.03px | 1px border | 0 |
| 430px | 430 / 430px | 430 × 250.31px | 1px border | 0 |

Flag, memorial peak, sun and all three faces remain visible. Search is above the entire illustration. Dark mode has a dark text/control area and unchanged art colors (filter:none). Existing bottom padding is 72px versus 58.64px fixed navigation height. The native 390px app preview is also checked separately.

Desktop and 768px tablet measurements of heading, description, search and citizen image are exactly unchanged from the live v12 baseline. A mobile search submitted passport requirements and navigated to /ask/?q=passport%20requirements.

Automated checks: 57 Vitest tests and 9 Node tests passed (66 total). Production Next/Worker build and TypeScript compilation passed. Browser recordings/screenshots distinguish local QA from the final deployed verification.

Microphone permission and speech-provider transcription are not triggered during visual QA; the existing VoiceInput component and handler are unchanged.
