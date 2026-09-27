#!/usr/bin/env python3
"""Build per-size HTML pages for the multi-size patterns.

The private GCS bucket is served from storage.cloud.google.com, which redirects
through an auth flow to a signed URL and drops the original query string. A
`?size=` deep link therefore arrives with no size and the page falls back to its
default, so the index links to one standalone file per size instead.

Each page is the pattern's source HTML with PAGE_SIZE locked to a single size;
the size bar on those pages links to its siblings.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PATTERNS = [
    {
        "source": REPO_ROOT / "site/library/rafas-hat/rafas-hat.html",
        "title": "Rafa's Hat — Joji Locatelli",
        "sizes": {
            "small": {"file": "rafas-hat-small.html", "label": 'Small (14¾")'},
            "medium": {"file": "rafas-hat-medium.html", "label": 'Medium (16")'},
            "large": {"file": "rafas-hat-large.html", "label": 'Large (17½")'},
        },
    },
    {
        "source": REPO_ROOT / "site/library/antler-toque/antler-toque.html",
        "title": "Antler Toque — Tin Can Knits",
        "sizes": {
            "baby": {"file": "antler-toque-baby.html", "label": 'Baby (16")'},
            "child": {"file": "antler-toque-child.html", "label": 'Child (18")'},
            "adultsm": {"file": "antler-toque-adult-sm.html", "label": 'Adult SM (21")'},
            "adultl": {"file": "antler-toque-adult-l.html", "label": 'Adult L (23")'},
        },
    },
]

PAGE_SIZE_DECL = "const PAGE_SIZE = null;"


def build(pattern) -> None:
    source_html = pattern["source"].read_text(encoding="utf-8")
    title = pattern["title"]
    title_tag = f"<title>{title}</title>"

    if PAGE_SIZE_DECL not in source_html:
        raise SystemExit(f"{pattern['source']}: missing `{PAGE_SIZE_DECL}`")
    if title_tag not in source_html:
        raise SystemExit(f"{pattern['source']}: missing `{title_tag}`")

    name, _, designer = title.partition(" — ")

    for key, size in pattern["sizes"].items():
        html = source_html.replace(PAGE_SIZE_DECL, f"const PAGE_SIZE = '{key}';", 1)
        sized_title = f"{name} — {size['label']} — {designer}" if designer else f"{name} — {size['label']}"
        html = html.replace(title_tag, f"<title>{sized_title}</title>", 1)

        out_path = pattern["source"].with_name(size["file"])
        out_path.write_text(html, encoding="utf-8")
        print(f"Saved: {out_path.relative_to(REPO_ROOT)}")


def main() -> None:
    for pattern in PATTERNS:
        build(pattern)


if __name__ == "__main__":
    main()
