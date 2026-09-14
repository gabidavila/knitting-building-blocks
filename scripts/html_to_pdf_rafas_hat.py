#!/usr/bin/env python3
"""Render Rafa's Hat size variants to borderless A4 and Letter PDFs."""

import asyncio
import base64
from pathlib import Path

from playwright.async_api import async_playwright

SIZES = {
    "A4": {"width": "210mm", "height": "297mm"},
    "Letter": {"width": "8.5in", "height": "11in"},
}

SIZE_VARIANTS = [
    {"key": "small", "folder": "small", "label": 'Small (14¾")'},
    {"key": "medium", "folder": "medium", "label": 'Medium (16")'},
    {"key": "large", "folder": "large", "label": 'Large (17½")'},
]

REPO_ROOT = Path(__file__).resolve().parents[1]
FONTS_DIR = REPO_ROOT / "assets/fonts"
HTML_PATH = REPO_ROOT / "site/library/rafas-hat/rafas-hat.html"
OUTPUT_DIR = REPO_ROOT / "site/library/rafas-hat"

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

    rules.append(
        """
        @page { margin: 0; }
        html, body { margin: 0 !important; padding: 0 !important; }
        .row-label, .instr, .abbrev-box code { font-family: 'Calling Code', monospace !important; }
        """
    )
    return "\n".join(rules)


async def set_size(page, size_key: str, size_label: str):
    await page.evaluate(
        """([sizeKey, sizeLabel]) => {
            localStorage.removeItem('rafas-hat-v1');
            currentSize = sizeKey;
            state = {};
            renderAll();
            const bar = document.querySelector('.size-bar');
            if (bar) {
              bar.innerHTML = `<label>Size:</label><span class="size-btn active" style="cursor:default">${sizeLabel}</span>`;
            }
            document.title = `Rafa's Hat - ${sizeLabel}`;
        }""",
        [size_key, size_label],
    )


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
    font_css = build_font_css()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(HTML_PATH.as_uri(), wait_until="networkidle")
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

        for variant in SIZE_VARIANTS:
            await set_size(page, variant["key"], variant["label"])
            size_dir = OUTPUT_DIR / variant["folder"]
            size_dir.mkdir(parents=True, exist_ok=True)
            stem = "rafas-hat"

            for size_name, dims in SIZES.items():
                out_path = size_dir / f"{stem}-{size_name.lower()}.pdf"
                await html_to_pdf(page, out_path, dims["width"], dims["height"])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
