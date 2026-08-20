"""百科知识大闯关 - 纯静态版预览入口

static-site/ 是纯静态项目（零后端、零依赖），可直接发布到
GitHub Pages / AtomGit Pages 等任意静态托管。

本文件仅作为 AtomCode 沙箱的预览服务：把 static-site/ 目录
以静态文件方式挂载，让沙箱 iframe 能直接预览。
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_SITE_DIR = os.path.join(BASE_DIR, "..", "static-site")

app = FastAPI(title="百科知识大闯关（纯静态版）")

# 挂载 static-site 下的 css / js 等静态资源
app.mount(
    "/css",
    StaticFiles(directory=os.path.join(STATIC_SITE_DIR, "css")),
    name="css",
)
app.mount(
    "/js",
    StaticFiles(directory=os.path.join(STATIC_SITE_DIR, "js")),
    name="js",
)


@app.get("/")
async def index() -> FileResponse:
    """首页：直接返回 static-site/index.html"""
    return FileResponse(os.path.join(STATIC_SITE_DIR, "index.html"))


@app.get("/game.html")
async def game() -> FileResponse:
    """闯关页"""
    return FileResponse(os.path.join(STATIC_SITE_DIR, "game.html"))


@app.get("/study.html")
async def study() -> FileResponse:
    """学习模式页"""
    return FileResponse(os.path.join(STATIC_SITE_DIR, "study.html"))
