# 📄 MCP PDF Agent

An **Model Context Protocol (MCP)** server designed for AI agents to incrementally build, manage, and render high-fidelity PDF documents. 

Unlike basic PDF generators, this agent handles **session persistence**, **remote asset caching**, and **Base64 injection** to ensure that complex documents with images and tables render correctly every time.

## ✨ Key Features

*   **Stateful Document Sessions:** Initialize a document ID and append content over multiple turns.
*   **Smart Asset Management:** Automatically fetches remote (HTTP/S) images and stores them locally to prevent broken links during rendering.
*   **Self-Contained Rendering:** Injects images as Base64 data URIs into the HTML before generation, bypassing Chromium's strict local file security policies.
*   **Enterprise Styling:** Built-in CSS optimized for professional reports, including clean typography, styled tables, and centered figures.
*   **Headless Precision:** Powered by Playwright (Chromium) for pixel-perfect PDF output that respects CSS layouts.

## 🛠️ Requirements

*   **Python:** 3.12+
*   **Package Manager:** [uv](https://github.com/astral-sh/uv)
*   **Browser Engine:** Playwright Chromium

## 🚀 Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Install Playwright Browsers
```bash
uv run playwright install chromium
```

## ⚙️ MCP Configuration

Add this to your `cline_mcp_settings.json` (or your preferred MCP host config).
```json
{
  "mcpServers": {
    "pdf-generator": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/your-org/mcp-pdf-agent.git",
        "pdf-server"
      ]
    }
  }
}
```

Set `PLAYWRIGHT_BROWSERS_PATH` only if your environment needs it.

## 📖 Available Tools

Documents are created implicitly the first time content or an image is added for a given `doc_id`.

*   `add_text(doc_id, md_text)`: Appends Markdown content to a document session.
*   `add_image(doc_id, image_data)`: Processes and embeds an image (supports absolute local paths, Base64, and URLs).
*   `finalize_pdf(doc_id, filename)`: Renders the accumulated content into a PDF.
*   `undo(doc_id)`: Reverts the last addition to the document.

## 🩺 Troubleshooting

### "Executable doesn't exist" (Playwright)
Ensure the `PLAYWRIGHT_BROWSERS_PATH` in your config matches the output of:
```bash
uv run playwright install --show-install-dir
```

### Missing Images in PDF
This server uses **Base64 injection**. If images are missing, check the MCP logs and `~/.mcp-pdf-agent/server.log` to ensure the files exist in `~/.mcp-pdf-agent/document_assets/`. The server will fall back to standard links if the local file cannot be read.

### Code Changes Not Reflecting
If using `uvx`, your code might be cached. Use the `uv run --directory` method shown in the configuration section to force the server to use your local source files.

## 📜 License
MIT
