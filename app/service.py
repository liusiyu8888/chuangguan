"""闯关业务核心逻辑（进度读取、取题、关卡判定）。"""
from sqlmodel import Session, select

from app.models import Progress, Question

QUESTIONS_PER_LEVEL = 5


def get_progress(session: Session) -> Progress:
    """获取（必要时创建）唯一的进度记录。"""
    progress = session.get(Progress, 1)
    if progress is None:
        progress = Progress(id=1)
        session.add(progress)
        session.commit()
        session.refresh(progress)
    return progress


def reset_progress(session: Session) -> Progress:
    """把进度重置回第 1 关。"""
    progress = get_progress(session)
    progress.current_level = 1
    progress.current_question = 1
    progress.current_correct = 0
    progress.max_unlocked = 1
    session.commit()
    return progress


def total_levels(session: Session) -> int:
    """题库总关卡数（没有题目返回 0）。"""
    rows = session.exec(select(Question.level).distinct()).all()
    return max(rows) if rows else 0


def questions_in_level(session: Session, level: int) -> int:
    """某关实际题目数量（最后一关可能不足 QUESTIONS_PER_LEVEL）。"""
    return len(
        session.exec(select(Question).where(Question.level == level)).all()
    )


def questions_in_level_all(session: Session, level: int) -> list[Question]:
    """某关全部题目（按入库顺序），供学习模式浏览。"""
    return session.exec(
        select(Question).where(Question.level == level).order_by(Question.id)
    ).all()


def max_level(session: Session) -> int:
    """题库当前最大关卡号（没有题目返回 0）。"""
    return total_levels(session)


def question_for(session: Session, level: int, ordinal: int) -> Question | None:
    """按题目入库顺序取某关第 ordinal 题（1 起）。"""
    qs = session.exec(
        select(Question).where(Question.level == level).order_by(Question.id)
    ).all()
    idx = ordinal - 1
    if 0 <= idx < len(qs):
        return qs[idx]
    return None
