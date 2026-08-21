from typing import Optional

from fastapi import HTTPException, Request
from itsdangerous import URLSafeSerializer

from app.core.config import SECRET_KEY
from app.repositories import user_repository


serializer = URLSafeSerializer(SECRET_KEY)


def get_session(request: Request) -> dict:
    token = request.cookies.get("session")
    if not token:
        return {}
    try:
        return serializer.loads(token)
    except Exception:
        return {}


def set_session(response, data: dict) -> None:
    response.set_cookie(
        key="session", value=serializer.dumps(data), httponly=True,
        max_age=86400 * 7, samesite="lax"
    )


def clear_session(response) -> None:
    response.delete_cookie("session")


def get_current_user(request: Request) -> Optional[dict]:
    user_id = get_session(request).get("user_id")
    return user_repository.get_by_id(user_id) if user_id else None


def require_login(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401)
    return user


def require_admin(request: Request) -> dict:
    user = require_login(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403)
    return user
