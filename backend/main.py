"""ASGI 应用入口；业务路由位于 app/controllers。"""

from app.application import create_app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
