import secrets

from app.core.database import get_conn


def generate(count: int = 1) -> list[str]:
    conn = get_conn()
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()
        conn.execute("INSERT INTO invite_codes (code) VALUES (?)", (code,))
        codes.append(code)
    conn.commit()
    conn.close()
    return codes


def get_all() -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT ic.*, u.username AS used_by_name FROM invite_codes ic "
        "LEFT JOIN users u ON ic.used_by=u.id ORDER BY ic.created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
