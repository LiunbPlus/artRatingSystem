from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.session import require_login
from app.repositories import work_repository
from app.services import rating_service

router = APIRouter(prefix="/api/works")


@router.get("/{work_id}/my-rating")
async def get_my_rating(request: Request, work_id: int):
    user = require_login(request)
    return {"success": True, "rating": rating_service.get_user_rating(work_id, user["id"])}


@router.get("/{work_id}/dimensions")
async def get_dimensions(request: Request, work_id: int):
    require_login(request)
    work = work_repository.get_by_id(work_id)
    if not work:
        raise HTTPException(404, "作品不存在")
    return {"success": True, "dimensions": rating_service.get_dimensions(work["category"]), "category": work["category"]}


@router.post("/{work_id}/rate")
async def rate_work(request: Request, work_id: int):
    user = require_login(request)
    if not work_repository.get_by_id(work_id):
        raise HTTPException(404, "作品不存在")
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"success": False, "message": "请求体不是有效的JSON"}, 400)
    if not isinstance(body, dict):
        return JSONResponse({"success": False, "message": "请求体格式错误"}, 400)
    success, message = rating_service.validate_and_rate(work_id, user["id"], body.get("scores", {}))
    return JSONResponse({"success": success, "message": message}, 200 if success else 400)
