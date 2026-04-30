import sqlite3
from . import config

def init_db():
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute(config.SQL_INIT_TABLE)

def save_document(doc_id: str, html: str):
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute(config.SQL_INSERT_DOC, (doc_id, html))

def get_latest_html(doc_id: str) -> str:
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.execute(config.SQL_SELECT_LATEST, (doc_id,))
        row = cursor.fetchone()
        return row[0] if row else ""

def delete_latest_version(doc_id: str) -> bool:
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.execute(config.SQL_SELECT_HISTORY_IDS, (doc_id,))
        rows = cursor.fetchall()
        if len(rows) > 1:
            conn.execute(config.SQL_DELETE_BY_ID, (rows[0][0],))
            return True
    return False