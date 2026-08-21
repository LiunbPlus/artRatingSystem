import json
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.config import BASE_DIR, THUMB_DIR, UPLOAD_DIR
from app.repositories import rating_repository, work_repository
from app.services import rating_service


VALID_CATEGORIES = {"photo", "text", "video", "object"}
ALLOWED_EXTENSIONS = {
    "photo": {".jpg", ".jpeg", ".png"},
    "video": {".mp4"},
    "object": {".jpg", ".jpeg", ".png"},
}


def list_with_stats(category: Optional[str] = None, include_hidden: bool = False,
                    sort_by: str = "created_at", sort_order: str = "DESC") -> list[dict]:
    works = work_repository.get_all(category, include_hidden, sort_by, sort_order)
    for work in works:
        work["stats"] = rating_service.summary(work["id"])
    return works


def list_for_user(user: dict, category: Optional[str], sort_by: str,
                  sort_order: str) -> list[dict]:
    works = list_with_stats(category, user["role"] == "admin", sort_by, sort_order)
    for work in works:
        rating = rating_repository.get_for_user(work["id"], user["id"])
        work["rated"] = rating is not None
        work["my_rating"] = rating["scores"] if rating else None
        work["my_avg"] = (
            round(sum(rating["scores"].values()) / len(rating["scores"]), 2)
            if rating and rating["scores"] else None
        )
    return works


def list_unrated(user: dict, category: Optional[str]) -> list[dict]:
    works = list_with_stats(category, user["role"] == "admin")
    return [work for work in works if not rating_repository.has_rated(work["id"], user["id"])]


def get_with_stats(work_id: int) -> Optional[dict]:
    work = work_repository.get_by_id(work_id)
    if work:
        work["stats"] = rating_service.summary(work_id)
    return work


async def upload(title: str, author_name: str, contact: str, description: str,
                 category: str, text_content: str,
                 files: Optional[list[UploadFile]]) -> tuple[bool, str, Optional[int]]:
    if category not in VALID_CATEGORIES:
        return False, "无效的分类", None
    if category == "text":
        if not text_content.strip():
            return False, "请输入文字内容", None
        saved = []
    else:
        if not files or not files[0].filename:
            return False, "请上传文件", None
        saved = []
        for upload_file in files:
            if not upload_file.filename:
                continue
            extension = Path(upload_file.filename).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS[category]:
                return False, f"不支持的文件格式：{extension}。摄影/手工支持 jpg/png，视频支持 mp4", None
            unique_name = f"{uuid.uuid4().hex}{extension}"
            directory = {"photo": "images", "video": "videos", "object": "objects"}[category]
            save_path = UPLOAD_DIR / directory / unique_name
            save_path.write_bytes(await upload_file.read())
            saved.append((save_path, f"/static/uploads/{directory}/{unique_name}", unique_name))
        if not saved:
            return False, "请上传文件", None

    file_path = saved[0][1] if saved else ""
    images_json = json.dumps([item[1] for item in saved], ensure_ascii=False) if saved else ""
    thumbnail_path = ""
    if category in ("photo", "object"):
        thumbnail_path = await run_in_threadpool(_generate_thumbnail, saved[0][0], saved[0][2])
    work_id = work_repository.add(
        title, author_name, contact, description, category, file_path,
        thumbnail_path, text_content, images_json,
    )
    return True, "作品上传成功", work_id


def update(work_id: int, **fields) -> bool:
    return work_repository.update(work_id, **{key: value for key, value in fields.items() if value})


def delete(work_id: int) -> Optional[dict]:
    work = work_repository.delete(work_id)
    if not work:
        return None
    for path in [*(work.get("images") or []), work.get("thumbnail_path")]:
        if path:
            try:
                (BASE_DIR / path.lstrip("/")).unlink(missing_ok=True)
            except OSError:
                pass
    return work


def _generate_thumbnail(file_path: Path, unique_name: str) -> str:
    try:
        from PIL import Image
        thumbnail_name = f"thumb_{unique_name}"
        with Image.open(file_path) as image:
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(THUMB_DIR / thumbnail_name, "JPEG", quality=85)
        return f"/static/uploads/thumbnails/{thumbnail_name}"
    except Exception:
        return ""
