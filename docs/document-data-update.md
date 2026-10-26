# Five-document data update — 25 October 2026

The five uploaded DOCX files are integrated into Janun's existing application. The homepage design is retained. The current build uses the supplied source-confirmed facts, retaining each record's authority, scope, dates, official URLs, original PDF links, limitations and embedded evidence.

| Input | Public input records | Internal operations |
| --- | ---: | ---: |
| 1.docx — passport, transport, tax/business, national directories | 33 | 4 |
| 2.docx — health and social support | 13 | 0 |
| 3.docx — education, scholarships and jobs | 11 | 0 |
| 4.docx — identity, civil registration, police and legal | 23 | 0 |
| 5.docx — land, agriculture and Dhaka WASA | 6 | 0 |
| Total | 86 | 4 |

Two overlapping input intents (birth correction and GRS) are consolidated into 84 canonical updated entries. 53 entries replace earlier fields; 31 are new. 14 existing duplicate routes resolve to their canonical updated entries. The resulting directory contains 271 entries. All 254 former service routes resolve, and 187 unrelated entries are byte-for-byte unchanged. The original 5,037-row research catalogue is unchanged. Prior values are retained in the replacement ledger and alias archive; original DOCX files and their complete extracted content are under research/documents-2026-10-25.

## What changed

- Service guides show source-confirmed facts and document/record provenance. Search, source links, static routes, and source-backed assistant answers use the updated data.
- 41 embedded images are extracted without alteration. PDF page captures and supplied source screenshots are distinguishable from illustrative charts/source cards. The service PDF tab provides image previews/downloads and original PDF URLs. Page references are retained where supplied.
- Selected explicit requirements populate preparation checks. Unspecified requirements remain unknown rather than inheriting older assumptions. Independent review is not fabricated: 2.docx keeps its 24 October check date, documents 3–5 keep 25 October, and the month-only 1.docx retains its October date with a separate import date.
- Local hospital charters, Dhaka WASA zones, institution-specific policies, seasonal agriculture orders and future job notices retain their scope. BPSC's November application dates are not presented as already open on 25 October.
- Backend source includes an explicit idempotent importer. Existing IDs and source-version history are preserved, obsolete evidence on replaced services is archived, and independent verified_at dates are not invented.

## Conflict decisions and remaining limits

1. Police clearance: 1.docx says Tk 500; 4.docx says Tk 1,500 plus applicable service charge. The app records both claims as a conflict and leaves the current fee unset until the payment instruction can be confirmed. No silent choice was made.
2. Passport identity: 1.docx's blanket age-18 NID requirement is corrected to the official age bands: under 18 birth registration; ages 18–20 NID or birth registration; over 20 domestic application NID, with the mission exception retained. The source used is https://www.bdcgny.org/e-password and the existing official passport instructions.
3. The broad 2026–27 tax-free threshold, minimum-tax and universal filing claims in 1.docx require the applicable enacted tax-year provision. An indexed official NBR budget document conflicts with the supplied threshold; these claims and the supplied VAT turnover thresholds are not used as definitive current rates. Other supported process and source information is included. Relevant source: https://nbr.gov.bd/uploads/budget/Budget_Speech_English.pdf .
4. The supplied reports themselves distinguish source confirmation from independent human review. That distinction is retained. Bangla-only records are not passed off as reviewed English translations; English-only original facts in 4.docx remain in their supplied language.
5. Original PDF URLs and embedded page images are included. Separate evidence ZIPs mentioned inside the DOCX files were not attached in this request; their original PDFs are not claimed to have been recovered or downloaded. Live availability of every external government URL was not verified.
6. The existing public app runs a static source-backed dataset. A separate live backend database and AI provider are not configured. The full backend importer is supplied and tested, but no nonexistent production database migration is claimed.

## Validation

- 58 frontend tests passed (54 Vitest plus 4 Node).
- 39 backend tests passed, including idempotent document import, preservation of the existing service ID, archival of old fields and alias resolution.
- Production build and TypeScript compilation passed; 314 static pages generated.
- Browser checks covered a service from each uploaded document, the original-PDF/evidence tab and loaded image, a source-backed UGC answer, and mobile preview/dark mode. The 390px preview's body width and scroll width were both 375px, excluding the scrollbar.
- The import manifest contains source document SHA256 hashes, image hashes and exact semantic mappings. The change ledger retains prior field values.

## Reproduce the release

From the project root:

```sh
python3 -m pip install -r scripts/requirements-documents.txt
python3 scripts/import_document_release.py
python3 scripts/build_demo_data.py
npm ci
npm test
npm run build
```

For a separately configured backend, run migrations, then execute from backend/:

```sh
python -m app.cli import-verified-documents
```

This explicit owner-authorized import publishes source-confirmed document records while retaining independent review as pending. It does not scrape, infer claim-level verification, or fabricate missing facts.
