# Repository Structure

The repository separates publishable website files from generation tools, source references, and scratch output.

```text
.
├── site/
│   ├── index.html
│   ├── favicon.svg
│   └── library/
├── scripts/
├── assets/
│   └── fonts/
├── source/
├── work/
│   ├── waiting-processing/
│   ├── tmp/
│   └── tests/
└── docs/
```

- `site/` is the publish root. Its contents sync to `gs://ravelry-for-adhd-ppl`.
- `scripts/` contains Playwright PDF generators.
- `assets/fonts/` contains bundled fonts embedded into generated PDFs.
- `source/` contains original/reference inputs.
- `work/` contains scratch files and generated comparison outputs that are not part of the public site.
