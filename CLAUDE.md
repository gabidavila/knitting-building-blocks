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
- Antler Toque published files live in `Ravelry/Antler Toque/<size>/`.
- Original/reference material lives under `Source/`.
- The bundled fonts in `Fonts/` are intentionally embedded into PDFs so output is stable without external font loading.

## Deployment

- `index.html` and `Library/**` publish to `gs://knitting-building-blocks`.
- `antler.html` and `Ravelry/**` publish to `gs://ravelry-for-adhd-ppl`.
- Deployment runs from GitHub Actions on pushes to `master`; workflows use the `GCP_SA_KEY` secret.

## Agent Guidance

- Check `git status --short` before editing; this repo may contain user changes and generated outputs.
- Do not revert or overwrite existing generated PDFs unless the task requires regenerating them.
- When adding or renaming published patterns, update the matching public index page URLs.
- Keep edits scoped. Avoid unrelated cleanup in generated HTML, source files, or font assets.
- Prefer ASCII in new documentation and code unless existing content requires otherwise.
