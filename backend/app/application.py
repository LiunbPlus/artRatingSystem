from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.controllers import admin, auth, ratings, works
from app.core.config import (
    APP_TITLE, APP_VERSION, CORS_ORIGINS, UPLOAD_DIR, ensure_upload_directories,
)
from app.core.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    ensure_upload_directories()
    yield


def create_app() -> FastAPI:
    application = FastAPI(title=APP_TITLE, version=APP_VERSION, lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 保持数据库中既有 /static/uploads/... 路径继续有效。
    application.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    for router in (auth.router, works.router, ratings.router, admin.router):
        application.include_router(router)
    return application
