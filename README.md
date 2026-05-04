# Knitting Pattern Library Automation

This project stores HTML versions of knitting patterns and generates borderless A4 and Letter PDFs from them. It also includes a static index page for browsing the published pattern library.

## Project Structure

- `site/index.html` - public library index for Building Blocks, Anker, and Antler Toque patterns.
- `site/Library/Blocks/Block */` - polished Building Blocks HTML files plus generated A4 and Letter PDFs.
- `site/Library/Anker/` - Anker pattern HTML files plus generated A4 and Letter PDFs.
- `site/Library/Antler Toque/` - Antler Toque HTML and generated PDFs by size.
- `source/` - original source PDFs or extracted/intermediate HTML.
- `assets/fonts/` - bundled font files used during PDF generation.
- `work/tests/` and `work/tmp/` - working output and comparison areas.
- `scripts/` - Playwright PDF generation scripts.
- `.github/workflows/` - GitHub Actions that upload all published HTML/PDF files to Google Cloud Storage.

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
python3 scripts/html_pdf_blocks_generic.py
```

Regenerate Anker PDFs:

```bash
python3 scripts/html_to_pdf_anker.py
```

Regenerate Antler Toque PDFs for Baby, Child, Adult SM, and Adult L:

```bash
python3 scripts/html_to_pdf_antler_toque.py
```

Render any staged HTML files placed in `work/waiting-processing/`:

```bash
python3 scripts/html_to_pdf_blocks_9_12.py
```

Each script writes both A4 and Letter PDFs next to its matching HTML file.

## Publishing

Publishing is handled by GitHub Actions on pushes to `master`.

- The single publish workflow uploads `site/index.html`, `site/favicon.svg`, and `site/Library/**` to `gs://ravelry-for-adhd-ppl` with `site/` as the bucket root.
- Public library URL: [https://storage.googleapis.com/ravelry-for-adhd-ppl/index.html](https://storage.googleapis.com/ravelry-for-adhd-ppl/index.html).
- The old `gs://knitting-building-blocks` target is no longer used.

The workflow requires the `GCP_SA_KEY` repository secret.

## Working Notes

- Keep the generated PDF names aligned with their HTML stems, for example `Block 5 - Wide.html`, `Block 5 - Wide - A4.pdf`, and `Block 5 - Wide - Letter.pdf`.
- The public index targets the `ravelry-for-adhd-ppl` Google Cloud Storage bucket. Update those entries when adding or renaming published files.
- Preserve bundled font paths unless the conversion scripts are updated at the same time.
- Source files under `source/` are inputs or references, not the polished published output.
