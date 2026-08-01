#!/usr/bin/env python3
"""Convert Coventry HTML files to A4 and Letter PDFs with zero margins."""

import asyncio
import base64
from pathlib import Path

from playwright.async_api import async_playwright

SIZES = {
    "A4": {"width": "210mm", "height": "297mm"},
    "Letter": {"width": "8.5in", "height": "11in"},
}

REPO_ROOT = Path(__file__).resolve().parents[1]
FONTS_DIR = REPO_ROOT / "assets/fonts"
HTML_DIR = REPO_ROOT / "site/library/coventry"
CHROME_PATH = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

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

    rules.append(
        """
        @page { margin: 0; }
        html, body { margin: 0 !important; padding: 0 !important; }
        .plain, .repeat-compact, .repeat-item {
          font-family: 'Calling Code', monospace !important;
        }
        """
    )
    return "\n".join(rules)


async def prepare_page(page, html_path: Path, font_css: str):
    await page.goto(html_path.as_uri(), wait_until="networkidle")
    await page.evaluate("localStorage.removeItem('coventry-expanded-cowl-v1-repeats')")
    await page.evaluate("localStorage.removeItem('coventry-expanded-cowl-v1')")
    await page.reload(wait_until="networkidle")
    await page.evaluate(
        f"""() => {{
            document.querySelectorAll('link[href*="fonts.googleapis.com"]').forEach(el => el.remove());
            const style = document.createElement('style');
            style.textContent = `{font_css}`;
            document.head.prepend(style);
        }}"""
    )
    await page.emulate_media(media="print")
    await page.evaluate("document.fonts.ready")


async def html_to_pdf(page, out_path: Path, width: str, height: str):
    await page.pdf(
        path=str(out_path),
        width=width,
        height=height,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        print_background=True,
        prefer_css_page_size=False,
    )
    print(f"Saved: {out_path}")


async def main():
    html_files = sorted(HTML_DIR.glob("*.html"))
    if not html_files:
        raise SystemExit(f"No HTML files found in {HTML_DIR}")

    font_css = build_font_css()

    async with async_playwright() as playwright:
        launch_kwargs = {}
        if CHROME_PATH.exists():
            launch_kwargs["executable_path"] = str(CHROME_PATH)

        browser = await playwright.chromium.launch(**launch_kwargs)
        page = await browser.new_page()

        for html_file in html_files:
            await prepare_page(page, html_file, font_css)
            for size_name, dims in SIZES.items():
                out_path = html_file.with_name(f"{html_file.stem}-{size_name.lower()}.pdf")
                await html_to_pdf(page, out_path, dims["width"], dims["height"])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
