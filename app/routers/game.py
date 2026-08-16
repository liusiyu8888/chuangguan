"""闯关业务路由。"""
import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import Progress, Question
from app.service import QUESTIONS_PER_LEVEL, get_progress, max_level, question_for, questions_in_level, questions_in_level_all, reset_progress, total_levels
from app.templating import templates

logger = logging.getLogger(__name__)

router = APIRouter()


def _context_extra(progress: Progress, session: Session) -> dict:
    """统一的模板上下文公共字段。"""
    total = total_levels(session)
    return {
        "progress": progress,
        "current_level": progress.current_level,
        "total_levels": total,
        "max_unlocked_display": min(progress.max_unlocked, total),
        "questions_per_level": questions_in_level(session, progress.current_level),
    }


@router.get("/")
def index(request: Request, session: Session = Depends(get_session)):
    """首页：展示进度与入口。"""
    progress = get_progress(session)
    ctx = _context_extra(progress, session)
    ctx.update(
        {
            "questions_count": len(session.exec(select(Question)).all()),
            "questions_per_level": QUESTIONS_PER_LEVEL,
        }
    )
    return templates.TemplateResponse(request, "index.html", ctx)


@router.get("/play")
def play(request: Request, session: Session = Depends(get_session)):
    """进入闯关：加载当前关卡的第一题。"""
    progress = get_progress(session)
    question = question_for(session, progress.current_level, 1)
    if question is None:
        # 该关没有题（例如题库为空），回到首页
        return HTMLResponse(
            '<div class="bg-white rounded-2xl shadow p-8 text-center">'
            '<p class="text-gray-600 mb-4">当前关卡还没有题目。</p>'
            '<a href="/" class="inline-block px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">返回首页</a>'
            "</div>"
        )
    ctx = _context_extra(progress, session)
    ctx.update({"question": question, "question_index": 1})
    return templates.TemplateResponse(request, "play.html", ctx)


@router.get("/question")
def question(request: Request, session: Session = Depends(get_session)):
    """返回当前进度对应的当前题片段（答对后取下一题 / 重试时返回本关第 1 题）。"""
    progress = get_progress(session)
    question = question_for(session, progress.current_level, progress.current_question)
    if question is None:
        # 本关题目不足（正常情况下不会发生），返回空片段
        return HTMLResponse('<div class="text-gray-500 text-center py-8">本关暂无题目。</div>')
    ctx = _context_extra(progress, session)
    ctx.update({"question": question, "question_index": progress.current_question})
    return templates.TemplateResponse(request, "fragments/question.html", ctx)


@router.post("/answer")
def answer(
    request: Request,
    question_id: int = Form(...),
    selected: str = Form(...),
    session: Session = Depends(get_session),
):
    """提交答案并判定，返回反馈片段。"""
    progress = get_progress(session)
    q = session.get(Question, question_id)
    if q is None:
        return HTMLResponse('<div class="text-red-500 text-center py-8">题目不存在，请刷新后重试。</div>')
    ctx = _context_extra(progress, session)

    if selected == q.answer:
        # ---------- 答对 ----------
        progress.current_correct += 1
        per_level = questions_in_level(session, progress.current_level)
        if progress.current_correct >= per_level:
            # 本关全部答对，过关！
            cleared_level = progress.current_level
            progress.current_question = 1
            progress.current_correct = 0
            progress.current_level += 1
            progress.max_unlocked = max(progress.max_unlocked, progress.current_level)
            session.add(progress)
            session.commit()
            if progress.current_level > total_levels(session):
                ctx.update({"cleared_level": cleared_level, "question": q, "questions_per_level": per_level})
                return templates.TemplateResponse(request, "fragments/game_over.html", ctx)
            ctx.update({"cleared_level": cleared_level, "question": q, "questions_per_level": per_level, "current_level": progress.current_level})
            return templates.TemplateResponse(request, "fragments/level_clear.html", ctx)
        # 还没答满 5 题，下一题
        progress.current_question += 1
        session.add(progress)
        session.commit()
        ctx.update({"question": q, "question_index": progress.current_question})
        return templates.TemplateResponse(request, "fragments/answer_correct.html", ctx)
    # ---------- 答错：本关重来 ----------
    progress.current_question = 1
    progress.current_correct = 0
    session.add(progress)
    session.commit()
    correct_text = {
        "A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d
    }.get(q.answer, "")
    ctx.update({"question": q, "selected": selected, "correct_text": correct_text})
    return templates.TemplateResponse(request, "fragments/answer_wrong.html", ctx)


@router.post("/restart")
def restart(request: Request, session: Session = Depends(get_session)):
    """答错后重试：重置本关并返回第 1 题片段。"""
    progress = get_progress(session)
    progress.current_question = 1
    progress.current_correct = 0
    session.add(progress)
    session.commit()
    question = question_for(session, progress.current_level, 1)
    if question is None:
        return HTMLResponse('<div class="text-gray-500 text-center py-8">本关暂无题目。</div>')
    ctx = _context_extra(progress, session)
    ctx.update({"question": question, "question_index": 1})
    return templates.TemplateResponse(request, "fragments/question.html", ctx)


@router.post("/reset-all")
def reset_all(session: Session = Depends(get_session)):
    """重置全部进度到第 1 关。"""
    reset_progress(session)
    return HTMLResponse(
        '<div class="bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl px-4 py-3">'
        "进度已重置，欢迎重新开始！</div>"
    )


def _correct_text(q: Question) -> str:
    """取某题的正确答案文本。"""
    return {
        "A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d
    }.get(q.answer, "")


@router.get("/learn")
def learn(request: Request, session: Session = Depends(get_session)):
    """学习模式：浏览全部题目，答案默认隐藏，点击显示。默认展示第 1 关。"""
    progress = get_progress(session)
    ctx = _context_extra(progress, session)
    questions = questions_in_level_all(session, 1)
    ctx.update({"level": 1, "questions": questions, "correct_map": {q.id: _correct_text(q) for q in questions}})
    return templates.TemplateResponse(request, "learn.html", ctx)


@router.get("/learn/level/{level}")
def learn_level(request: Request, level: int, session: Session = Depends(get_session)):
    """学习模式：切换指定关卡，返回该关题目列表片段（HTMX 就地替换）。"""
    total = total_levels(session)
    if level < 1:
        level = 1
    if level > total:
        level = total
    questions = questions_in_level_all(session, level)
    ctx = {"level": level, "questions": questions, "total_levels": total, "correct_map": {q.id: _correct_text(q) for q in questions}}
    return templates.TemplateResponse(request, "fragments/learn_list.html", ctx)
