import base64
import os
import pathlib
import re

from playwright.async_api import async_playwright

from . import config


def inject_base64_images(html_body: str) -> str:
    """
    Finds file:// paths and replaces them with Base64 data URIs.
    This ensures the PDF is self-contained and avoids Chromium security blocks.
    """

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
            except Exception:
                pass  # Fallback to original if file reading fails
        return match.group(0)

    return re.sub(r'src=["\'](file://[^"\']+)["\']', substitute_base64, html_body)


async def render_pdf(html_body: str, output_filename: str):
    """Renders a self-contained PDF from HTML body."""

    # Inject images as Base64 to make the HTML portable
    processed_html = inject_base64_images(html_body)

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <style>{config.DEFAULT_CSS}</style>
        </head>
        <body>{processed_html}</body>
    </html>
    """

    output_path = os.path.abspath(output_filename)

    async with async_playwright() as p:
        # Launch Chromium (Headless)
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Set content directly - Base64 makes the HTML self-contained
        await page.set_content(full_html, wait_until="networkidle")

        # Generate the PDF with standard professional margins
        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"},
        )
        await browser.close()

    return output_path
