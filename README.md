# 🧠 百科知识大闯关（纯静态版）

小学 AI + 百科知识答题闯关游戏：内置 **200 道题 × 40 关**，每关 5 道，**全部答对才能进入下一关**，答错本关重来。纯静态、零后端、零依赖，可直接发布到任意静态托管。

## 核心功能

- **闯关玩法**：40 关 × 5 题，全对过关；答错显示正确答案与解析并本关重来
- **内置题库**：200 题（AI 知识 100 + 百科知识 100；单选 120 + 判断 80，判断题以「正确/错误」呈现）
- **学习模式**：浏览全部题目，可搜索 / 按关卡筛选，答案默认隐藏，点击显示
- **进度持久化**：闯关进度 / 已解锁关卡自动保存到浏览器 localStorage，支持一键重置
- **音效反馈**：Web Audio 实时合成，答对 / 答错 / 过关 / 通关各有专属提示音
- **科技感 UI**：深空星空、霓虹渐变、发光按钮与进度条，答对答错各有动效

## 目录结构

```
docs/                   # 纯静态项目（发布内容，GitHub Pages 部署目录选 /docs）
├── index.html          # 首页：开始闯关 / 学习模式 / 关卡地图 / 进度统计 / 重置
├── game.html           # 闯关页：40 关 × 5 题
├── study.html          # 学习模式
├── css/style.css       # 科技感暗色主题
└── js/
    ├── data.js         # 200 题数据
    ├── common.js       # 进度存储（localStorage）+ 音效（Web Audio）
    ├── game.js         # 闯关逻辑
    ├── index.js        # 首页逻辑
    └── study.js        # 学习模式逻辑
app/main.py             # 仅沙箱预览用（静态文件服务），非发布内容
```

## 运行方式

**纯静态（发布 / 本地双击）**：直接打开 `docs/index.html` 即可，无需任何服务器。

**沙箱预览（FastAPI 静态服务）**：

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000`。

## 发布到静态托管

| 平台 | 方式 |
|---|---|
| GitHub Pages | 推送 `docs/` → 仓库 Settings → Pages → Source 选分支 + 目录选 `/docs` → Save |
| AtomGit Pages | 推送后仓库「服务 / Pages」选择部署目录 `docs/` 并启用 |
| 其它（Vercel / Netlify / Gitee Pages） | 上传或关联 `docs/` 目录即可 |

发布后即可获得外网链接（如 `https://<用户名>.atomgit.com/<仓库名>/`）。

> 说明：纯静态版进度存浏览器 localStorage，换设备不共享（纯静态特性）。

## 变更日志

- 2026-08-20：重构为**纯静态多文件版**，删除全部旧版（FastAPI 后端版 / 单文件离线版 / 工具脚本），仓库仅保留 `static-site/` 与沙箱预览入口。
