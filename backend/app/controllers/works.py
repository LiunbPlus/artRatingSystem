from typing import List

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from app.core.session import require_admin, require_login
from app.repositories import work_repository
from app.services import work_service


router = APIRouter(prefix="/api/works")


@router.get("")
async def get_works(request: Request, category: str = Query("all"),
                    sort_by: str = Query("created_at"), sort_order: str = Query("DESC")):
    user = require_login(request)
    works = work_service.list_for_user(
        user, None if category == "all" else category, sort_by, sort_order
    )
    return {"success": True, "works": works, "count": len(works)}


@router.get("/unrated")
async def get_unrated_works(request: Request, category: str = Query("all")):
    works = work_service.list_unrated(
        require_login(request), None if category == "all" else category
    )
    return {"success": True, "works": works, "count": len(works)}


@router.get("/{work_id}")
async def get_work(request: Request, work_id: int):
    require_login(request)
    work = work_service.get_with_stats(work_id)
    if not work:
        raise HTTPException(404, "作品不存在")
    return {"success": True, "work": work}


@router.post("/upload")
async def upload_work(request: Request, title: str = Form(...), author_name: str = Form(...),
                      contact: str = Form(""), description: str = Form(""),
                      category: str = Form(...), text_content: str = Form(""),
                      files: List[UploadFile] = File(default=None)):
    require_admin(request)
    success, message, work_id = await work_service.upload(
        title, author_name, contact, description, category, text_content, files
    )
    payload = {"success": success, "message": message}
    if work_id is not None:
        payload["work_id"] = work_id
    return JSONResponse(payload, 200 if success else 400)


@router.put("/{work_id}")
async def update_work(request: Request, work_id: int, title: str = Form(""),
                      author_name: str = Form(""), contact: str = Form(""),
                      description: str = Form(""), text_content: str = Form("")):
    require_admin(request)
    if not work_repository.get_by_id(work_id):
        raise HTTPException(404, "作品不存在")
    work_service.update(work_id, title=title, author_name=author_name, contact=contact,
                        description=description, text_content=text_content)
    return {"success": True, "message": "作品信息已更新"}


@router.delete("/{work_id}")
async def delete_work(request: Request, work_id: int):
    require_admin(request)
    if not work_service.delete(work_id):
        raise HTTPException(404, "作品不存在")
    return {"success": True, "message": "作品已删除"}


@router.post("/{work_id}/toggle-hidden")
async def toggle_hidden(request: Request, work_id: int):
    require_admin(request)
    work = work_repository.toggle_hidden(work_id)
    if not work:
        raise HTTPException(404, "作品不存在")
    state = "已隐藏" if work["is_hidden"] else "已公开"
    return {"success": True, "message": f"作品{state}", "is_hidden": work["is_hidden"]}
