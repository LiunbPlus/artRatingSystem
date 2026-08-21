import json
from datetime import datetime
from typing import Optional

from app.core.database import get_conn


def _parse_images(row: dict) -> dict:
    try:
        images = json.loads(row.get("images_json") or "")
        if isinstance(images, list) and images:
            row["images"] = images
            return row
    except (TypeError, ValueError):
        pass
    row["images"] = [row["file_path"]] if row.get("file_path") else []
    return row


def add(title: str, author_name: str, contact: str, description: str,
        category: str, file_path: str, thumbnail_path: str = "",
        text_content: str = "", images_json: str = "") -> int:
    conn = get_conn()
    cursor = conn.execute(
        """INSERT INTO works (title,author_name,contact,description,category,
        file_path,thumbnail_path,text_content,images_json) VALUES (?,?,?,?,?,?,?,?,?)""",
        (title, author_name, contact, description, category, file_path,
         thumbnail_path, text_content, images_json),
    )
    work_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return work_id


def get_all(category: Optional[str] = None, include_hidden: bool = False,
            sort_by: str = "created_at", sort_order: str = "DESC") -> list[dict]:
    conn = get_conn()
    query = "SELECT * FROM works WHERE 1=1"
    params = []
    if not include_hidden:
        query += " AND is_hidden=0"
    if category and category != "all":
        query += " AND category=?"
        params.append(category)
    allowed_sort = {"created_at", "title", "author_name", "category", "id"}
    sort_by = sort_by if sort_by in allowed_sort else "created_at"
    sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"
    rows = conn.execute(f"{query} ORDER BY {sort_by} {sort_order}", params).fetchall()
    conn.close()
    return [_parse_images(dict(row)) for row in rows]


def get_by_id(work_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM works WHERE id=?", (work_id,)).fetchone()
    conn.close()
    return _parse_images(dict(row)) if row else None


def update(work_id: int, **kwargs) -> bool:
    allowed = {"title", "author_name", "contact", "description", "category",
               "file_path", "thumbnail_path", "text_content", "is_hidden"}
    fields = {key: value for key, value in kwargs.items() if key in allowed}
    if not fields:
        return False
    fields["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = list(fields.values()) + [work_id]
    conn = get_conn()
    conn.execute(f"UPDATE works SET {', '.join(f'{key}=?' for key in fields)} WHERE id=?", values)
    conn.commit()
    conn.close()
    return True


def delete(work_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM works WHERE id=?", (work_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM works WHERE id=?", (work_id,))
        conn.commit()
    conn.close()
    return _parse_images(dict(row)) if row else None


def toggle_hidden(work_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM works WHERE id=?", (work_id,)).fetchone()
    if row:
        new_state = 0 if row["is_hidden"] else 1
        conn.execute(
            "UPDATE works SET is_hidden=?, updated_at=? WHERE id=?",
            (new_state, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), work_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM works WHERE id=?", (work_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
