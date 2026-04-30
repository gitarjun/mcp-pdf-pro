import base64
import binascii
import pathlib
import shutil
import httpx
import uuid
from typing import Annotated

import markdown
from fastmcp import FastMCP

from . import config, db, renderer

mcp = FastMCP("Pro-Doc-Agent")


# --- MISSING RESOURCE RE-INTEGRATED ---
@mcp.resource("draft://{doc_id}")
async def get_draft(doc_id: str) -> str:
    """Allows the agent to read the current state of the document (HTML)."""
    html = db.get_latest_html(doc_id)
    return html if html else "Document is currently empty."


# --- TOOLS ---
@mcp.tool()
async def add_text(
    doc_id: Annotated[str, "The unique identifier for the document session"],
    md_text: Annotated[
        str, "The Markdown content to append (supports tables, lists, and headers)"
    ],
) -> str:
    """Appends Markdown content to a document."""
    current_html = db.get_latest_html(doc_id)
    new_content = markdown.markdown(md_text, extensions=["tables"])
    db.save_document(doc_id, f"{current_html}\n<section>{new_content}</section>")
    return f"Content added to {doc_id}."


@mcp.tool()
async def add_image(
    doc_id: Annotated[str, "The unique identifier for the document session"],
    image_data: Annotated[
        str,
        "The FULL ABSOLUTE PATH, a Base64 string, or a URL (http/https) of the image",
    ],
) -> str:
    """Embeds an image into the document from a local path, Base64 string, or remote URL."""

    session_dir = config.STORAGE_DIR / doc_id
    session_dir.mkdir(exist_ok=True)
    file_name = f"img_{uuid.uuid4().hex[:8]}"

    # 1. Handle Remote URL (http/https)
    if image_data.startswith(("http://", "https://")):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_data, follow_redirects=True)
                response.raise_for_status()

                # Guess extension from content-type or URL
                ext = response.headers.get("Content-Type", "").split("/")[-1] or "png"
                ext = ext.split(";")[0]  # clean up potential charset info

                dest_path = session_dir / f"{file_name}.{ext}"
                with open(dest_path, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            return f"Error downloading image from URL: {str(e)}"

    # 2. Handle Base64 String
    elif image_data.startswith("data:image/") and "base64," in image_data:
        try:
            header, encoded = image_data.split("base64,")
            ext = header.split("/")[-1].split(";")[0]
            dest_path = session_dir / f"{file_name}.{ext}"
            with open(dest_path, "wb") as f:
                f.write(base64.b64decode(encoded))
        except (ValueError, binascii.Error) as e:
            return f"Error: Invalid Base64 data. {str(e)}"

    # 3. Handle Local File Path
    else:
        src_path = pathlib.Path(image_data)
        if not src_path.is_absolute():
            return "Error: Please provide a full absolute path for local files."
        if not src_path.exists():
            return f"Error: Local file {image_data} not found."

        dest_path = session_dir / src_path.name
        shutil.copy(src_path, dest_path)

    # Common Embedding Logic
    img_uri = dest_path.absolute().as_uri()
    img_tag = f'<div style="text-align:center;"><img src="{img_uri}" style="max-width:100%; margin:20px 0; border-radius:4px;"/></div>'

    current_html = db.get_latest_html(doc_id)
    db.save_document(doc_id, f"{current_html}\n{img_tag}")

    return f"Image successfully processed and embedded in {doc_id}."


@mcp.tool()
async def undo(
    doc_id: Annotated[str, "The unique identifier for the document session"],
) -> str:
    """Reverts to the previous version of the document."""
    if db.delete_latest_version(doc_id):
        return "Last action undone."
    return "Nothing to undo."


@mcp.tool()
async def finalize_pdf(
    doc_id: Annotated[str, "The unique identifier for the document session"],
    filename: Annotated[str, "Full path to location where pdf has to be saved"],
) -> str:
    """Renders the final PDF."""
    html = db.get_latest_html(doc_id)
    if not html:
        return "Error: Document empty."
    path = await renderer.render_pdf(html, filename)
    return f"PDF saved to {path}"


def main():
    db.init_db()
    mcp.run()
