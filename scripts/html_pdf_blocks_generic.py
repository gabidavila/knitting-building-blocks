#!/usr/bin/env python3
"""Convert all Block HTML files to A4 and Letter PDFs with zero margins.

Fonts are injected as base64 @font-face rules so no network access is needed.
"""

import asyncio
import base64
from pathlib import Path
from playwright.async_api import async_playwright

SIZES = {
    "A4":     {"width": "210mm", "height": "297mm"},
    "Letter": {"width": "8.5in", "height": "11in"},
}

REPO_ROOT = Path(__file__).resolve().parents[1]
FONTS_DIR = REPO_ROOT / "assets/fonts"
LIBRARY_DIR = REPO_ROOT / "site/library"

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
    for f in FONT_FACES:
        fmt = f.get("format", "truetype")
        mime = "font/otf" if fmt == "opentype" else "font/truetype"
        data = base64.b64encode(f["file"].read_bytes()).decode()
        rules.append(
            f"@font-face {{\n"
            f"  font-family: '{f['family']}';\n"
            f"  font-style: {f['style']};\n"
            f"  font-weight: {f['weight']};\n"
            f"  src: url('data:{mime};base64,{data}') format('{fmt}');\n"
            f"}}"
        )
    # Override the monospace generic to use Calling Code
    rules.append(":root { --mono: 'Calling Code', monospace; }")
    rules.append(".row-label, .instr, .abbrev-box code { font-family: 'Calling Code', monospace !important; }")
    return "\n".join(rules)

async def html_to_pdf(page, html_path: Path, out_path: Path, width: str, height: str, font_css: str):
    await page.goto(html_path.as_uri(), wait_until="networkidle")
    # Replace Google Fonts link with local embedded fonts
    await page.evaluate(f"""() => {{
        document.querySelectorAll('link[href*="fonts.googleapis.com"]').forEach(el => el.remove());
        const style = document.createElement('style');
        style.textContent = `{font_css}`;
        document.head.prepend(style);
    }}""")
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
    html_files = sorted(LIBRARY_DIR.glob("blocks/block-*/block-*.html"))

    if not html_files:
        print("No HTML files found.")
        return

    print("Encoding fonts...")
    font_css = build_font_css()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for html_file in html_files:
            print(f"\nProcessing: {html_file.name}")
            for size_name, dims in SIZES.items():
                out_path = html_file.parent / f"{html_file.stem}-{size_name.lower()}.pdf"
                await html_to_pdf(page, html_file, out_path, dims["width"], dims["height"], font_css)

        await browser.close()

    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(main())
