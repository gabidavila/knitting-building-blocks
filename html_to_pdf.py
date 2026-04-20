#!/usr/bin/env python3
"""Convert all Block HTML files to A4 and Letter PDFs with zero margins."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SIZES = {
    "A4":     {"width": "210mm", "height": "297mm"},
    "Letter": {"width": "8.5in", "height": "11in"},
}

async def html_to_pdf(page, html_path: Path, out_path: Path, width: str, height: str):
    await page.goto(html_path.as_uri(), wait_until="networkidle")
    await page.evaluate("document.fonts.ready")
    await page.pdf(
        path=str(out_path),
        width=width,
        height=height,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        print_background=True,
    )
    print(f"  Saved: {out_path.name}")

async def main():
    base = Path(__file__).parent
    html_files = sorted(base.glob("Block */Block *.html"))

    if not html_files:
        print("No HTML files found.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for html_file in html_files:
            print(f"\nProcessing: {html_file.name}")
            for size_name, dims in SIZES.items():
                out_name = html_file.stem + f" - {size_name}.pdf"
                out_path = html_file.parent / (html_file.stem + f" - {size_name}.pdf")
                await html_to_pdf(page, html_file, out_path, dims["width"], dims["height"])

        await browser.close()

    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(main())
