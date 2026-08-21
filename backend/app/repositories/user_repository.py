import hashlib
import secrets
from typing import Optional

from app.core.database import get_conn


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest(), salt


def verify(username: str, password: str) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not row:
        return None
    password_hash, _ = hash_password(password, row["salt"])
    return dict(row) if password_hash == row["password_hash"] else None


def get_by_id(user_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all() -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT u.id, u.username, u.role, u.created_at, "
        "(SELECT COUNT(*) FROM ratings r WHERE r.user_id=u.id) AS rating_count "
        "FROM users u ORDER BY u.created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def change_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return False, "用户不存在"
    old_hash, _ = hash_password(old_password, row["salt"])
    if old_hash != row["password_hash"]:
        conn.close()
        return False, "原密码错误"
    new_hash, new_salt = hash_password(new_password)
    conn.execute("UPDATE users SET password_hash=?, salt=? WHERE id=?", (new_hash, new_salt, user_id))
    conn.commit()
    conn.close()
    return True, "密码修改成功"


def create(username: str, password: str, invite_code: str, role: str = "judge") -> tuple:
    conn = get_conn()
    code = conn.execute("SELECT * FROM invite_codes WHERE code=? AND is_used=0", (invite_code,)).fetchone()
    if not code:
        conn.close()
        return False, "邀请码无效或已使用", None
    if conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
        conn.close()
        return False, "用户名已存在", None
    password_hash, salt = hash_password(password)
    cursor = conn.execute(
        "INSERT INTO users (username,password_hash,salt,role) VALUES (?,?,?,?)",
        (username, password_hash, salt, role),
    )
    user_id = cursor.lastrowid
    conn.execute("UPDATE invite_codes SET is_used=1, used_by=? WHERE id=?", (user_id, code["id"]))
    conn.commit()
    user = dict(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())
    conn.close()
    return True, "注册成功", user
