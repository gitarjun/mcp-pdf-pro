import os
import pathlib
import base64
import re
import sys
from playwright.async_api import async_playwright
from . import config


def inject_base64_images(html_body: str) -> str:
    """Finds file:// paths and replaces them with Base64 data."""

    def substitute_base64(match):
        raw_path = match.group(1)
        clean_path = raw_path.replace("file://", "")
        path = pathlib.Path(clean_path)

        if path.exists():
            ext = path.suffix.lower().replace(".", "")
            mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
            try:
                with open(path, "rb") as img_file:
                    encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
                    return f'src="data:{mime_type};base64,{encoded_string}"'
            except Exception as e:
                print(f"DEBUG: Read error for {path.name}: {e}", file=sys.stderr)
        else:
            print(f"DEBUG: File not found: {clean_path}", file=sys.stderr)
        return match.group(0)

    return re.sub(r'src=["\'](file://[^"\']+)["\']', substitute_base64, html_body)


async def render_pdf(html_body: str, output_filename: str, doc_id: str = "debug"):
    """Saves a debug HTML file, then renders the PDF."""

    processed_html = inject_base64_images(html_body)

    full_html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <style>{config.DEFAULT_CSS}</style>
        </head>
        <body>{processed_html}</body>
    </html>
    """

    # --- DEBUG STEP ---
    # Save the HTML to the document's specific folder for manual inspection
    debug_dir = config.STORAGE_DIR / doc_id
    debug_dir.mkdir(exist_ok=True)
    debug_file_path = debug_dir / "last_render_debug.html"

    with open(debug_file_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"DEBUG: HTML artifact saved to {debug_file_path}", file=sys.stderr)
    # ------------------

    output_path = os.path.abspath(output_filename)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Load the physical file we just created to ensure the "Origin" is local
        await page.goto(f"file://{debug_file_path.absolute()}", wait_until="networkidle")

        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
        )
        await browser.close()

    return output_path