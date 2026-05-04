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

- `index.html` - public library index for Building Blocks and Anker patterns.
- `antler.html` - public Antler Toque index.
- `Library/Blocks/Block */` - published Building Blocks HTML and generated PDFs.
- `Library/Anker/` - published Anker HTML and generated PDFs.
- `Ravelry/Antler Toque/` - Antler Toque HTML and generated PDFs by size.
- `Source/` - original/reference materials and extracted/intermediate HTML.
- `Fonts/` - bundled fonts embedded into generated PDFs.
- `.github/workflows/` - upload workflows for Google Cloud Storage publishing.

## Working Rules

- Check `git status --short` before editing.
- Do not revert user changes or overwrite generated PDFs unless the task explicitly requires regeneration.
- Generate PDFs with the Playwright scripts instead of hand-editing PDF files.
- Keep generated PDF names paired with their HTML stems using ` - A4.pdf` and ` - Letter.pdf`.
- Update `index.html` or `antler.html` when adding, removing, or renaming published files.
- Preserve bundled font paths unless updating the scripts at the same time.
- Keep edits scoped to the requested pattern, script, or docs.

## Publishing Notes

- `index.html` and `Library/**` publish to `gs://knitting-building-blocks`.
- `antler.html` and `Ravelry/**` publish to `gs://ravelry-for-adhd-ppl`.
- GitHub Actions run on pushes to `master` and require the `GCP_SA_KEY` secret.
