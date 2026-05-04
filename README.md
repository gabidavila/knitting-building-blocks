# Knitting Pattern Library Automation

This project stores HTML versions of knitting patterns and generates borderless A4 and Letter PDFs from them. It also includes static index pages for browsing the published pattern library.

## Project Structure

- `index.html` - public library index for Building Blocks and Anker patterns.
- `antler.html` - public index for Antler Toque variants.
- `Library/Blocks/Block */` - polished Building Blocks HTML files plus generated A4 and Letter PDFs.
- `Library/Anker/` - Anker pattern HTML files plus generated A4 and Letter PDFs.
- `Ravelry/Antler Toque/` - Antler Toque source HTML and generated PDFs by size.
- `Source/` - original source PDFs or extracted/intermediate HTML.
- `Fonts/` - bundled font files used during PDF generation.
- `tests/` and `tmp/` - working output and comparison areas.
- `.github/workflows/` - GitHub Actions that upload published HTML/PDF files to Google Cloud Storage.

## Local Setup

The conversion scripts require Python 3 and Playwright with Chromium.

```bash
pip3 install playwright
python3 -m playwright install chromium
```

The scripts embed local fonts directly into generated PDFs, so PDF generation does not depend on Google Fonts or other network font requests.

## Generate PDFs

Regenerate all Building Blocks PDFs:

```bash
python3 html_pdf_blocks_generic.py
```

Regenerate Anker PDFs:

```bash
python3 html_to_pdf_anker.py
```

Regenerate Antler Toque PDFs for Baby, Child, Adult SM, and Adult L:

```bash
python3 html_to_pdf_antler_toque.py
```

Render any staged HTML files placed in `waiting processing/`:

```bash
python3 html_to_pdf_blocks_9_12.py
```

Each script writes both A4 and Letter PDFs next to its matching HTML file.

## Publishing

Publishing is handled by GitHub Actions on pushes to `master`.

- Library uploads go to `gs://knitting-building-blocks` when `index.html`, `Library/**/*.html`, or `Library/**/*.pdf` changes.
- Ravelry uploads go to `gs://ravelry-for-adhd-ppl` when `antler.html`, `Ravelry/**/*.html`, or `Ravelry/**/*.pdf` changes.

Both workflows require the `GCP_SA_KEY` repository secret.

## Working Notes

- Keep the generated PDF names aligned with their HTML stems, for example `Block 5 - Wide.html`, `Block 5 - Wide - A4.pdf`, and `Block 5 - Wide - Letter.pdf`.
- The public index files contain hard-coded Google Cloud Storage URLs. Update those entries when adding or renaming published files.
- Preserve bundled font paths unless the conversion scripts are updated at the same time.
- Source files under `Source/` are inputs or references, not the polished published output.
