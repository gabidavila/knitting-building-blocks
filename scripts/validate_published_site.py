#!/usr/bin/env python3
"""Validate the private Cloud Storage site's published paths and index links."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"
INDEX_PATH = SITE_ROOT / "index.html"
BUCKET_BASE = "https://storage.cloud.google.com/ravelry-for-adhd-ppl"


def published_path(url_path: str) -> Path:
    return SITE_ROOT / unquote(url_path.split("?", 1)[0])


def main() -> int:
    index = INDEX_PATH.read_text()
    errors: list[str] = []

    if "https://storage.googleapis.com/ravelry-for-adhd-ppl" in index:
        errors.append("index.html still links to the anonymous storage.googleapis.com host")

    if f'const DEFAULT_BUCKET_URL = "{BUCKET_BASE}";' not in index:
        errors.append("index.html does not use the authenticated Cloud Storage bucket base")

    # Both icon references must be inlined: Cloud Storage serves this private page from an
    # ephemeral *-apidata.googleusercontent.com origin, so no fetchable icon URL survives.
    if 'rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,' not in index:
        errors.append("index.html favicon link must be an inline data URI")

    if 'class="hero-title-icon" src="data:image/svg+xml;base64,' not in index:
        errors.append("index.html hero icon must be an inline data URI")

    if f"{BUCKET_BASE}/favicon.svg" in index:
        errors.append("index.html must not reference favicon.svg by URL; inline it instead")

    tracked_site_paths = subprocess.run(
        ["git", "ls-files", "site"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if any(" " in path for path in tracked_site_paths):
        errors.append("published site contains paths with spaces")

    index_paths = re.findall(r'\bpath: "([^"]+)"', index)
    for value in index_paths:
        if not published_path(value).is_file():
            errors.append(f"index path does not exist: {value}")

    bucket_urls = re.findall(r'\$\{DEFAULT_BUCKET_URL\}/([^`]+)', index)
    for value in bucket_urls:
        if not published_path(value).is_file():
            errors.append(f"bucket URL does not resolve to a published file: {value}")

    original_links = re.findall(r'\boriginal: `\$\{DEFAULT_BUCKET_URL\}/([^`]+)`', index)
    if len(original_links) != 12:
        errors.append(f"expected 12 Building Blocks original-PDF links, found {len(original_links)}")

    if errors:
        print("Published-site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(index_paths)} pattern paths and {len(bucket_urls)} bucket URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
