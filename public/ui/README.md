# Janun UI Asset Pack

Prepared from the two supplied PNG UI mockups. No application code was changed.

## Contents
- logos/: extracted transparent PNGs, white variants, raster-traced path SVGs.
- icons/png/: transparent cutouts at their original screenshot resolution.
- icons/svg/: clean, editable companion drawings in the same visual style.
- illustrations/: original artwork crops; see individual limitations in asset-manifest.json.
- ASSET-PREVIEW.png: visual index on light/dark preview backgrounds.
- preview.html: local asset browser; open after extracting the ZIP.
- design-tokens.css: suggested colors and spacing.
- asset-manifest.json: provenance, crop coordinates, dimensions, and limitations.

## Important distinctions
The inputs are flattened raster images, with no recoverable layers or original SVGs. Logo SVGs contain traced paths, not embedded PNGs or font-dependent text. Their silhouettes retain pixel-level contours at large magnifications. Companion icon SVGs are reconstructed, not original vectors extracted from the PNGs. Transparent PNGs are direct color-mask cutouts and can retain minor edge artifacts. Their small native dimensions limit enlargement.

Hero illustrations contain background and, for desktop/close-up crops, embedded lettering or UI overlap. These are labeled reference crops rather than falsely advertised as clean transparent hero art. The mobile illustration and skyline crops provide text-free alternatives at native resolution. Parts hidden by interface controls cannot be recovered from these files.

The passport illustration and any lettering inside it are decorative generated artwork, not an authentic government document. No PDF in the mockup has been treated as a real attachment or official evidence.

## Suggested app placement
Use logos/janun-logo-bn.svg in the header, logos/janun-logo-bn-white.svg on dark backgrounds, icons/svg/ for scalable service cards, and illustrations/hero-mobile-text-free.png only at small display sizes. Keep interface labels as live HTML text rather than copying them from screenshots. Use consistent icon style within a given interface.
