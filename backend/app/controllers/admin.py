from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse

from app.core.session import require_admin
from app.repositories import invite_repository, user_repository

router = APIRouter(prefix="/api/admin")


@router.post("/invite-codes")
async def generate_invite_codes(request: Request, count: int = Form(1)):
    require_admin(request)
    if not 1 <= count <= 100:
        return JSONResponse({"success": False, "message": "生成数量应在1-100之间"}, 400)
    return {"success": True, "codes": invite_repository.generate(count)}


@router.get("/invite-codes")
async def list_invite_codes(request: Request):
    require_admin(request)
    return {"success": True, "invite_codes": invite_repository.get_all()}


@router.get("/users")
async def list_users(request: Request):
    require_admin(request)
    return {"success": True, "users": user_repository.get_all()}
