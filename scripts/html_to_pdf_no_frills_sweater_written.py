#!/usr/bin/env python3
"""Render the No Frills Sweater written pattern (S and M) to A4 and Letter PDFs with page margins."""

import asyncio
import base64
from pathlib import Path

from playwright.async_api import async_playwright

from html_to_pdf_no_frills_sweater import FONT_FACES

SIZES = {
    "A4": {"width": "210mm", "height": "297mm"},
    "Letter": {"width": "8.5in", "height": "11in"},
}

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "source/No Frills Sweater"
OUTPUT_DIR = REPO_ROOT / "site/library/no-frills-sweater"
HTML_PATH = SOURCE_DIR / "no-frills-sweater-written-pattern-s-m.html"
STEM = "no-frills-sweater-written-pattern-s-m"


FOOTER = (
    '<div style="width:100%;font-size:9px;color:#6B6478;padding:0 16mm;text-align:right;'
    'font-family:Helvetica,Arial,sans-serif">'
    '<span class="pageNumber"></span> of <span class="totalPages"></span></div>'
)


def build_font_css() -> str:
    rules = []
    for ff in FONT_FACES:
        fmt = ff.get("format", "truetype")
        mime = "font/otf" if fmt == "opentype" else "font/truetype"
        data = base64.b64encode(ff["file"].read_bytes()).decode()
        rules.append(
            f"@font-face {{ font-family: '{ff['family']}'; font-style: {ff['style']}; "
            f"font-weight: {ff['weight']}; src: url('data:{mime};base64,{data}') format('{fmt}'); }}"
        )
    rules.append(
        "body { font-family: 'Source Sans 3', sans-serif !important; } "
        "h1, h2 { font-family: 'Playfair Display', serif !important; } "
        "code, .step { font-family: 'Calling Code', monospace !important; }"
    )
    return "\n".join(rules)


async def main():
    font_css = build_font_css()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(HTML_PATH.as_uri(), wait_until="networkidle")
        await page.evaluate(
            f"""() => {{
                const style = document.createElement('style');
                style.textContent = `{font_css}`;
                document.head.prepend(style);
            }}"""
        )
        await page.emulate_media(media="print")
        await page.evaluate("document.fonts.ready")
        for name, dims in SIZES.items():
            out = OUTPUT_DIR / f"{STEM}-{name.lower()}.pdf"
            await page.pdf(
                path=str(out), width=dims["width"], height=dims["height"],
                margin={"top": "13mm", "right": "16mm", "bottom": "14mm", "left": "16mm"},
                print_background=True,
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=FOOTER,
            )
            print(f"Saved: {out}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
