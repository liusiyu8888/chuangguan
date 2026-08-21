"""百科知识大闯关 - 纯静态版预览入口

docs/ 是纯静态项目（零后端、零依赖），可直接发布到
GitHub Pages（部署目录选 /docs）/ AtomGit Pages 等任意静态托管。

本文件仅作为 AtomCode 沙箱的预览服务：把 docs/ 目录整体
以静态文件方式挂载（html=True 自动处理 index.html），让沙箱
iframe 能直接预览，且页面间的相对链接（index.html / game.html /
study.html / css/ / js/）全部可用。
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_SITE_DIR = os.path.join(BASE_DIR, "..", "docs")

app = FastAPI(title="百科知识大闯关（纯静态版）")

# 整体挂载 docs 目录：/ → index.html，/game.html、/study.html、
# /css/、/js/ 等全部按文件自动路由，页面内相对链接均可正常访问。
app.mount(
    "/",
    StaticFiles(directory=STATIC_SITE_DIR, html=True),
    name="static-site",
)
