"""百科知识大闯关 - FastAPI 入口。

本项目同时提供两套产物：
1. 网页版（FastAPI + HTMX + 数据库）：路由在 app/routers/game.py
2. 纯静态版（static-site/，可发布到 GitHub Pages / AtomGit Pages）：
   通过 /static-site 挂载，GET / 默认返回静态首页
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.routers.game import router as game_router

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_SITE_DIR = Path(__file__).resolve().parent.parent / "static-site"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="百科知识大闯关", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(game_router)

# 纯静态版挂载（可发布到任意静态托管）
if STATIC_SITE_DIR.exists():
    app.mount("/static-site", StaticFiles(directory=str(STATIC_SITE_DIR)), name="static-site")

    @app.get("/", include_in_schema=False)
    async def static_home():
        """默认首页：返回纯静态版首页。"""
        return FileResponse(str(STATIC_SITE_DIR / "index.html"))
