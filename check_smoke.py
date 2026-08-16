# -*- coding: utf-8 -*-
"""非长驻健康检查：首页 200、题库规模（200 题 40 关）、答题全流程。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import engine, init_db
from app.main import app
from app.service import reset_progress

# 显式初始化数据库（TestClient 非上下文模式不触发 lifespan），确保旧库自动升级
init_db()

# 脚本非幂等：先把进度重置到第 1 关，避免上次运行残留的进度影响断言
with Session(engine) as _s:
    reset_progress(_s)

client = TestClient(app)

# 1. 首页
r = client.get("/")
assert r.status_code == 200, f"首页状态码 {r.status_code}"
html = r.text
assert "百科知识大闯关" in html
assert "200 题" in html or "200" in html
print("[1] 首页 200，含题库规模 ✓")

# 2. play 页
r = client.get("/play")
assert r.status_code == 200, f"play 状态码 {r.status_code}"
assert "人工智能的英文缩写是" in r.text
print("[2] play 第一关第一题正确 ✓")

# 3. 题库规模：200 题、40 关、每关 5 题
from sqlmodel import select
from app.models import Question, Progress

with Session(engine) as s:
    total = len(s.exec(select(Question)).all())
    assert total == 200, f"题库总数 {total}，应为 200"
    levels = {q.level for q in s.exec(select(Question)).all()}
    assert levels == set(range(1, 41)), "关卡应覆盖 1-40"
    for lv in range(1, 41):
        n = len(s.exec(select(Question).where(Question.level == lv)).all())
        assert n == 5, f"第 {lv} 关题数 {n}，应为 5"
    print("[3] 题库 200 题 × 40 关，每关 5 题 ✓")

# 4. 答题：第 1 关 5 题全对 → 过关
with Session(engine) as s:
    qs = s.exec(select(Question).where(Question.level == 1).order_by(Question.id)).all()
    assert len(qs) == 5
    p = s.get(Progress, 1)
    assert p is not None and p.current_level == 1
    for i, q in enumerate(qs):
        resp = client.post("/answer", data={"question_id": q.id, "selected": q.answer})
        assert resp.status_code == 200
        if i < 4:
            assert "回答正确" in resp.text
        else:
            assert "恭喜过关" in resp.text
    s.expire_all()
    p = s.get(Progress, 1)
    assert p.current_level == 2, f"过关后应在第 2 关，实际 {p.current_level}"
    print("[4] 第 1 关 5 题全对 → 进入第 2 关 ✓")

# 5. 答错流程
with Session(engine) as s:
    qs2 = s.exec(select(Question).where(Question.level == 2).order_by(Question.id)).all()
    q = qs2[0]
    wrong = "A" if q.answer != "A" else "B"
    resp = client.post("/answer", data={"question_id": q.id, "selected": wrong})
    assert resp.status_code == 200
    assert "重新挑战" in resp.text
    p = s.get(Progress, 1)
    assert p.current_question == 1 and p.current_correct == 0
    print("[5] 答错 → 本关重置重试 ✓")

# 6. 最后一关（第 40 关）通关 → 大满贯 + win 音效
with Session(engine) as s:
    reset_progress(s)
    p = s.get(Progress, 1)
    p.current_level = 40
    p.max_unlocked = 40
    s.add(p)
    s.commit()
    qs40 = s.exec(select(Question).where(Question.level == 40).order_by(Question.id)).all()
    assert len(qs40) == 5
    for i, q in enumerate(qs40):
        resp = client.post("/answer", data={"question_id": q.id, "selected": q.answer})
        assert resp.status_code == 200
    assert "全关大满贯" in resp.text
    assert 'playSfx("win")' in resp.text
    print("[6] 第 40 关 5 题通关 → 大满贯 + 大满贯音效 ✓")

# 7. 导入路由已移除
r = client.get("/import")
assert r.status_code == 404, f"导入路由应已移除，实际 {r.status_code}"
print("[7] /import 路由已移除 ✓")

# 8. 判断题渲染：只有 A/B 两个选项按钮
with Session(engine) as s:
    q = s.exec(select(Question).where(Question.option_c == "")).first()
    p = s.get(Progress, 1)
    p.current_level = q.level
    p.current_question = 1
    p.current_correct = 0
    s.add(p)
    s.commit()
    r = client.get("/question")
    assert r.status_code == 200
    assert "正确" in r.text and "错误" in r.text
    assert r.text.count("option-btn") == 2
    print("[8] 判断题渲染 2 个选项（正确/错误）✓")

# 9. 音效引擎存在
r = client.get("/")
assert "playSfx" in r.text and "AudioContext" in r.text
print("[9] 音效引擎（Web Audio）已加载 ✓")

# 10. 学习模式：默认第 1 关，答案隐藏 + 显示按钮
r = client.get("/learn")
assert r.status_code == 200, f"学习模式状态码 {r.status_code}"
assert "学习模式" in r.text
assert "显示答案" in r.text and "隐藏答案" in r.text
assert "x-data=\"{ show: false }\"" in r.text, "答案应默认隐藏（Alpine 初始状态）"
print("[10] 学习模式默认第 1 关、答案隐藏、可点击显示 ✓")

# 11. 学习模式：切换第 40 关（HTMX 片段）
r = client.get("/learn/level/40")
assert r.status_code == 200
assert "正确答案" in r.text
assert "显示答案" in r.text
print("[11] 学习模式切换第 40 关片段 ✓")

# 12. 首页不含「内置题库」卡片
r = client.get("/")
assert "内置题库" not in r.text, "首页不应再有「内置题库」卡片"
assert "学习模式" in r.text
print("[12] 首页「内置题库」卡片已移除，改为学习模式入口 ✓")

print("\n全部检查通过 ✔")
