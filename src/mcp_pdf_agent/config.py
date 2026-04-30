import pathlib

# File System Paths
APP_DIR = pathlib.Path.home() / ".mcp-pdf-agent"
APP_DIR.mkdir(exist_ok=True)

DB_PATH = str(APP_DIR / "mcp_docs.db")
STORAGE_DIR = APP_DIR / "document_assets"
STORAGE_DIR.mkdir(exist_ok=True)

# SQL Queries
SQL_INIT_TABLE = """
CREATE TABLE IF NOT EXISTS doc_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT,
    html_content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

SQL_INSERT_DOC = "INSERT INTO doc_history (doc_id, html_content) VALUES (?, ?)"

SQL_SELECT_LATEST = "SELECT html_content FROM doc_history WHERE doc_id = ? ORDER BY id DESC LIMIT 1"

SQL_SELECT_HISTORY_IDS = "SELECT id FROM doc_history WHERE doc_id = ? ORDER BY id DESC"

SQL_DELETE_BY_ID = "DELETE FROM doc_history WHERE id = ?"

# Rendering Constants
DEFAULT_CSS = """
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 50px; color: #333; line-height: 1.6; }
h1 { color: #2c3e50; border-bottom: 2px solid #eee; margin-top: 30px; }
h2 { color: #34495e; margin-top: 25px; }

/* Table Styling */
table { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 20px 0; 
    font-size: 0.9em; 
}
th { 
    background-color: #f8f9fa; 
    color: #333; 
    text-align: left; 
    padding: 12px; 
    border-bottom: 2px solid #dee2e6; 
}
td { 
    padding: 12px; 
    border-bottom: 1px solid #eee; 
}
tr:nth-child(even) { background-color: #fafafa; }

/* Image Styling */
img { 
    display: block; 
    margin: 30px auto; 
    max-width: 100%; 
    height: auto; 
    border-radius: 6px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Subtle shadow for depth */
}

/* Page Break Utility */
.page-break { page-break-before: always; }
"""