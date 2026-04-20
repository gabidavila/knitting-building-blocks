#!/usr/bin/env python3
"""Convert waiting processing HTML files to A4 and Letter PDFs with zero margins.

Fonts are injected as base64 @font-face rules so no network access is needed.
"""

import asyncio
import base64
from pathlib import Path

from playwright.async_api import async_playwright

SIZES = {
    "A4": {"width": "210mm", "height": "297mm"},
    "Letter": {"width": "8.5in", "height": "11in"},
}

FONTS_DIR = Path(__file__).parent / "Fonts"

FONT_FACES = [
    {
        "family": "Playfair Display",
        "style": "normal",
        "weight": "100 900",
        "file": FONTS_DIR / "Playfair_Display/PlayfairDisplay-VariableFont_wght.ttf",
    },
    {
        "family": "Playfair Display",
        "style": "italic",
        "weight": "100 900",
        "file": FONTS_DIR / "Playfair_Display/PlayfairDisplay-Italic-VariableFont_wght.ttf",
    },
    {
        "family": "Source Sans 3",
        "style": "normal",
        "weight": "100 900",
        "file": FONTS_DIR / "Source_Sans_3/SourceSans3-VariableFont_wght.ttf",
    },
    {
        "family": "Source Sans 3",
        "style": "italic",
        "weight": "100 900",
        "file": FONTS_DIR / "Source_Sans_3/SourceSans3-Italic-VariableFont_wght.ttf",
    },
    {
        "family": "Calling Code",
        "style": "normal",
        "weight": "400",
        "file": FONTS_DIR / "Desktop-Calling Code/Fonts/callingcode-regular.otf",
        "format": "opentype",
    },
    {
        "family": "Calling Code",
        "style": "normal",
        "weight": "700",
        "file": FONTS_DIR / "Desktop-Calling Code/Fonts/callingcode-bold.otf",
        "format": "opentype",
    },
    {
        "family": "Calling Code",
        "style": "italic",
        "weight": "400",
        "file": FONTS_DIR / "Desktop-Calling Code/Fonts/callingcode-italic.otf",
        "format": "opentype",
    },
    {
        "family": "Calling Code",
        "style": "italic",
        "weight": "700",
        "file": FONTS_DIR / "Desktop-Calling Code/Fonts/callingcode-bolditalic.otf",
        "format": "opentype",
    },
]


def build_font_css() -> str:
    rules = []
    for font_face in FONT_FACES:
        fmt = font_face.get("format", "truetype")
        mime = "font/otf" if fmt == "opentype" else "font/truetype"
        data = base64.b64encode(font_face["file"].read_bytes()).decode()
        rules.append(
            f"@font-face {{\n"
            f"  font-family: '{font_face['family']}';\n"
            f"  font-style: {font_face['style']};\n"
            f"  font-weight: {font_face['weight']};\n"
            f"  src: url('data:{mime};base64,{data}') format('{fmt}');\n"
            f"}}"
        )
    rules.append(":root { --mono: 'Calling Code', monospace; }")
    rules.append(".row-label, .instr { font-family: 'Calling Code', monospace !important; }")
    return "\n".join(rules)


async def html_to_pdf(page, html_path: Path, out_path: Path, width: str, height: str, font_css: str):
    await page.goto(html_path.as_uri(), wait_until="networkidle")
    await page.evaluate(
        f"""() => {{
        document.querySelectorAll('link[href*="fonts.googleapis.com"]').forEach(el => el.remove());
        const style = document.createElement('style');
        style.textContent = `{font_css}`;
        document.head.prepend(style);
    }}"""
    )
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
    html_files = sorted(base.glob("waiting processing/*.html"))

    if not html_files:
        print("No HTML files found.")
        return

    print("Encoding fonts...")
    font_css = build_font_css()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        for html_file in html_files:
            print(f"\nProcessing: {html_file.name}")
            for size_name, dims in SIZES.items():
                out_path = html_file.parent / f"{html_file.stem} - {size_name}.pdf"
                await html_to_pdf(page, html_file, out_path, dims["width"], dims["height"], font_css)

        await browser.close()

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
