# Requested interface and Gemini update

Changes are limited to the user's first-visit tour, mobile home/service search composition, System theme behavior and Gemini integration. The 271-service snapshot, original research catalogue and five-document replacement release are unchanged.

- An 11-step first-visit tour uses a spotlight, guide card, smooth scrolling, automatic page navigation, Back/Next/Skip/Finish, keyboard controls and reduced-motion support. Completion is stored locally. The footer can replay the tour.
- The mobile home and service-directory masthead use compact spacing and a small memorial/sun landscape based on the supplied reference. The desktop composition remains intact. Mobile search, voice input and device preview remain interactive.
- System always resolves to Light, including the pre-render theme script. Explicit Dark remains available.
- Gemini is called only from the server. Its key is a hosted secret and is absent from source and client assets. Responses are grounded in server-selected Janun records, with citation validation, same-origin checks, request limits and per-instance rate limiting. Provider errors fall back to explicitly labelled source search. No database/data rewrite is involved.

## Hosting and source

The existing Next static pages and assets are retained. A server Worker wraps those pages and supplies /api/ai/chat and /api/ai/status. Build the hosted artifact with npm run build:hosted. Configure GEMINI_API_KEY as a secret and GEMINI_MODEL as a server runtime value. Never set a NEXT_PUBLIC_ API key.

## Checks

- Existing tests plus the new tour/theme and Gemini tests: 57 Vitest and 9 Node tests pass.
- Production Next build and TypeScript compilation pass.
- Worker checks cover home, services with/without trailing slash, service details, assistant and AI status routes.
- The supplied credential authenticated with Google's model-list endpoint. Generation on gemini-2.5-flash returned NOT_FOUND because Google no longer allows that model for new users; the integration uses Google's recommended gemini-3.8-flash instead. Production generation is verified separately after deployment.
- Browser inspection covers the spotlight tour, mobile home and service search, dark appearance, 390px frame and no horizontal overflow. Tour completion remains dismissed after reload.

Gemini's instructions preserve location, document date, missing facts and unresolved conflicts. A model answer does not turn an independently unreviewed record into verified advice. Rate limiting is per server instance, not a global quota guarantee.
