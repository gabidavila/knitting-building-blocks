# Agent Memory

## Project Purpose

This repository converts knitting pattern HTML into polished, borderless A4 and Letter PDFs and publishes the resulting HTML/PDF library to Google Cloud Storage.

## Key Commands

```bash
python3 html_pdf_blocks_generic.py
python3 html_to_pdf_anker.py
python3 html_to_pdf_antler_toque.py
python3 html_to_pdf_blocks_9_12.py
```

Runtime setup:

```bash
pip3 install playwright
python3 -m playwright install chromium
```

## Repository Map

- `index.html` - public library index for Building Blocks, Anker, and Antler Toque patterns.
- `Library/Blocks/Block */` - published Building Blocks HTML and generated PDFs.
- `Library/Anker/` - published Anker HTML and generated PDFs.
- `Library/Antler Toque/` - Antler Toque HTML and generated PDFs by size.
- `Source/` - original/reference materials and extracted/intermediate HTML.
- `Fonts/` - bundled fonts embedded into generated PDFs.
- `.github/workflows/` - upload workflows for Google Cloud Storage publishing.

## Working Rules

- Check `git status --short` before editing.
- Do not revert user changes or overwrite generated PDFs unless the task explicitly requires regeneration.
- Generate PDFs with the Playwright scripts instead of hand-editing PDF files.
- Keep generated PDF names paired with their HTML stems using ` - A4.pdf` and ` - Letter.pdf`.
- Update `index.html` when adding, removing, or renaming published files.
- Preserve bundled font paths unless updating the scripts at the same time.
- Keep edits scoped to the requested pattern, script, or docs.

## Building Blocks Checklist Context

- Gabi is building interactive HTML knitting pattern checklists for Michelle Hunter's Knit Purl Hunter "Building Blocks" series.
- The 12 blocks cover Seed Stitch, Diagonal Rib, Yarn Over & Bobbles, Simple Decreases, Cables, Right Twist, Leaf Lace, Slip Stitch, Left Twist, SSK Lace, Make One Increase, and Advanced Decreases.
- All 12 Building Blocks checklists use the standardized Wide format and file naming `Block N - Wide.html`.
- Blocks 9-12 source files may exist in `/mnt/project/` as `block9.html` through `block12.html`; run `ls /mnt/project/` before assuming those files are unavailable.
- A parallel Donna Brooks / D&M DesignWorks project includes Waverly Weekend Cowl, Philippa Cabled Cowl, and Coventry Cables & Lace Cowl checklists and PDFs.

## Building Blocks Wide Design Rules

- Use column order: Done checkbox, Row label, 48px badge column with no header, Instructions.
- Body rows show only RS/WS badges in the badge column: green for RS and red for WS.
- Non-body rows show only type tags, stacked if needed; never show a `Body` tag.
- WS rows use `.row-ws` with background `#f7f7f7`.
- Token rendering order is `[WS]`/`[RS]`, `[SeedO]`/`[SeedE]` via `§SEED§` placeholders, strip `[Setup]`, repeat-core regex, `[MB]`, then `[YO]`.
- Repeat-core regex must stop on `§`: `/(\*[^*]+; repeat from \*[^§<\n]*)/g`.
- Seed placeholders use `§SEED§text§/SEED§`; first occurrence renders as `seed |`, second as `| seed`.
- Monospace text uses `Calling Code` for `.instr`, `.abbrev-box code`, and all monospace elements. Embed it with `@font-face` if external loading is unavailable.
- Layout stays fluid: `width: 100%`, no `max-width`; `.header-inner` uses `margin: 0 20px`, `.progress-bar` uses `padding: 0 20px`, and `main` uses `padding: 1.5rem 20px 4rem`.
- `.yarn-icon` is always generated as `float: left; margin-top: 8px;`.
- localStorage keys are block-specific: `blockN-pattern-v1`.

## Pattern Logic Notes

- When a Set Up Row is present and the pattern says "work N times," render N+1 reps total. Rep 1 starts at Row 2 because the Set Up Row substitutes for Row 1; the final rep ends at the specified row.
- `k2tog tbl` and `SSK` are functionally equivalent left-leaning decreases and may be treated as interchangeable in these patterns.
- Long-tail cast-on estimate: about 80 inches for 48 stitches in chunky yarn on US size 10 needles.
- Verify rendered output after string replacements; identical old and new strings can appear to succeed without changing anything.

## Publishing Notes

- `index.html` and `Library/**` publish to `gs://ravelry-for-adhd-ppl`.
- The old `gs://knitting-building-blocks` bucket is no longer used.
- Antler Toque now publishes from `Library/Antler Toque/` through `index.html`; do not use a separate root Antler index.
- GitHub Actions run on pushes to `master` and require the `GCP_SA_KEY` secret.
