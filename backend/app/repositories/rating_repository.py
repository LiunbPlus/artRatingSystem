import json
from datetime import datetime
from typing import Optional

from app.core.database import get_conn


def upsert(work_id: int, user_id: int, scores: dict) -> None:
    scores_json = json.dumps(scores, ensure_ascii=False)
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM ratings WHERE work_id=? AND user_id=?", (work_id, user_id)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE ratings SET scores_json=?, created_at=? WHERE id=?",
            (scores_json, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO ratings (work_id,user_id,scores_json) VALUES (?,?,?)",
            (work_id, user_id, scores_json),
        )
    conn.commit()
    conn.close()


def get_for_user(work_id: int, user_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM ratings WHERE work_id=? AND user_id=?", (work_id, user_id)
    ).fetchone()
    conn.close()
    if not row:
        return None
    rating = dict(row)
    rating["scores"] = json.loads(rating["scores_json"])
    return rating


def has_rated(work_id: int, user_id: int) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM ratings WHERE work_id=? AND user_id=?", (work_id, user_id)
    ).fetchone()
    conn.close()
    return row is not None


def get_for_work(work_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM ratings WHERE work_id=?", (work_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]
