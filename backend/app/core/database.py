import sqlite3

from app.core.config import DB_PATH


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """创建表并执行轻量迁移；账号创建由业务流程负责。"""
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'judge',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS invite_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            is_used INTEGER NOT NULL DEFAULT 0,
            used_by INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (used_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS works (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_name TEXT NOT NULL,
            contact TEXT DEFAULT '',
            description TEXT DEFAULT '',
            category TEXT NOT NULL,
            file_path TEXT NOT NULL,
            thumbnail_path TEXT DEFAULT '',
            text_content TEXT DEFAULT '',
            is_hidden INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            scores_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(work_id, user_id),
            FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    columns = [row[1] for row in cur.execute("PRAGMA table_info(works)").fetchall()]
    if "images_json" not in columns:
        cur.execute("ALTER TABLE works ADD COLUMN images_json TEXT DEFAULT ''")
    conn.commit()
    conn.close()
