from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse

from app.core.session import clear_session, require_login, set_session
from app.services import auth_service


router = APIRouter(prefix="/api")


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = auth_service.login(username, password)
    if not user:
        return JSONResponse({"success": False, "message": "用户名或密码错误"}, 401)
    response = JSONResponse({"success": True, "user": {
        "id": user["id"], "username": user["username"], "role": user["role"]
    }})
    set_session(response, {"user_id": user["id"], "username": user["username"]})
    return response


@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...), invite_code: str = Form(...)):
    success, message, user = auth_service.register(username, password, invite_code)
    if not success:
        return JSONResponse({"success": False, "message": message}, 400)
    response = JSONResponse({"success": True, "message": message, "user": {
        "id": user["id"], "username": user["username"], "role": user["role"]
    }})
    set_session(response, {"user_id": user["id"], "username": user["username"]})
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse({"success": True})
    clear_session(response)
    return response


@router.post("/change-password")
async def change_password(request: Request, old_password: str = Form(...), new_password: str = Form(...)):
    success, message = auth_service.change_password(require_login(request), old_password, new_password)
    return JSONResponse({"success": success, "message": message}, 200 if success else 400)
