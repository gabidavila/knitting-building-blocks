# Project Memory

## Purpose

This repository is a local automation workspace for converting knitting pattern HTML into polished, borderless A4 and Letter PDFs, then publishing the HTML/PDF library to Google Cloud Storage.

## Important Commands

```bash
python3 html_pdf_blocks_generic.py
python3 html_to_pdf_anker.py
python3 html_to_pdf_antler_toque.py
python3 html_to_pdf_blocks_9_12.py
```

Install/runtime prerequisite:

```bash
pip3 install playwright
python3 -m playwright install chromium
```

## Conventions

- Use Playwright PDF scripts for generated PDFs; do not hand-edit PDFs.
- Generated PDFs should sit next to their source HTML and use ` - A4.pdf` and ` - Letter.pdf` suffixes.
- Building Blocks published files live in `Library/Blocks/Block */`.
- Anker published files live in `Library/Anker/`.
- Antler Toque published files live in `Library/Antler Toque/<size>/`.
- Antler Toque is listed through `index.html`; do not use a separate root Antler index.
- Original/reference material lives under `Source/`.
- The bundled fonts in `Fonts/` are intentionally embedded into PDFs so output is stable without external font loading.

## Deployment

- `index.html` and `Library/**` publish to `gs://ravelry-for-adhd-ppl`.
- The old `gs://knitting-building-blocks` bucket is no longer used.
- Deployment runs from GitHub Actions on pushes to `master`; workflows use the `GCP_SA_KEY` secret.

## Agent Guidance

- Check `git status --short` before editing; this repo may contain user changes and generated outputs.
- Do not revert or overwrite existing generated PDFs unless the task requires regenerating them.
- When adding or renaming published patterns, update the matching public index page URLs so they point to `ravelry-for-adhd-ppl`.
- Keep edits scoped. Avoid unrelated cleanup in generated HTML, source files, or font assets.
- Prefer ASCII in new documentation and code unless existing content requires otherwise.

## Building Blocks Context

Gabi is building interactive HTML knitting pattern checklists for Michelle Hunter's Knit Purl Hunter "Building Blocks" series. The 12 blocks cover Seed Stitch, Diagonal Rib, Yarn Over & Bobbles, Simple Decreases, Cables, Right Twist, Leaf Lace, Slip Stitch, Left Twist, SSK Lace, Make One Increase, and Advanced Decreases. All 12 checklists have been rebuilt into the standardized Wide format, named `Block N - Wide.html`.

Blocks 9-12 source files may exist in `/mnt/project/` as `block9.html` through `block12.html`; run `ls /mnt/project/` before deciding they are unavailable. A parallel Donna Brooks / D&M DesignWorks checklist/PDF project includes Waverly Weekend Cowl, Philippa Cabled Cowl, and Coventry Cables & Lace Cowl.

## Building Blocks Wide Format

- Column order is Done checkbox, Row label, 48px badge column with no header, Instructions.
- Body rows show only RS/WS badges in the badge column: green for RS and red for WS.
- Non-body rows show only type tags, stacked if needed; never show a `Body` tag.
- WS rows use `.row-ws` with background `#f7f7f7`.
- Token rendering order is `[WS]`/`[RS]`, `[SeedO]`/`[SeedE]` through `§SEED§` placeholders, strip `[Setup]`, repeat-core regex, `[MB]`, then `[YO]`.
- Repeat-core regex must stop on `§`: `/(\*[^*]+; repeat from \*[^§<\n]*)/g`.
- Seed placeholders use `§SEED§text§/SEED§`; first occurrence renders as `seed |`, second as `| seed`.
- Use `Calling Code` for `.instr`, `.abbrev-box code`, and all monospace elements. Embed it with `@font-face` if external loading is unavailable.
- Keep layout fluid: `width: 100%`, no `max-width`; `.header-inner` uses `margin: 0 20px`, `.progress-bar` uses `padding: 0 20px`, and `main` uses `padding: 1.5rem 20px 4rem`.
- Generate `.yarn-icon` as `float: left; margin-top: 8px;`.
- Use block-specific localStorage keys: `blockN-pattern-v1`.

## Pattern Logic Notes

- If a Set Up Row is present and the pattern says "work N times," render N+1 reps total. Rep 1 starts at Row 2 because the Set Up Row substitutes for Row 1; the final rep ends at the specified row.
- `k2tog tbl` and `SSK` are functionally equivalent left-leaning decreases and may be treated as interchangeable in these patterns.
- Long-tail cast-on estimate: about 80 inches for 48 stitches in chunky yarn on US size 10 needles.
- Verify rendered output after string replacements; identical old and new strings can appear to succeed without changing anything.

## Collaboration Notes

Gabi works iteratively with precise visual feedback and expects root-cause fixes, not superficial changes. Prefer previewing layouts before exporting PDFs, and verify visual/rendered output when changing checklist rendering logic.
