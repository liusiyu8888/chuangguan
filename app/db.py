"""数据库连接与初始化。"""
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.builtin_questions import builtin_questions
from app.models import Question

DB_PATH = Path(__file__).resolve().parent.parent / "app.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """建表并填充内置题库（首次运行时）。"""
    SQLModel.metadata.create_all(engine)
    seed_builtin_questions()


def get_session():
    """提供数据库会话的依赖。"""
    with Session(engine) as session:
        yield session


def seed_builtin_questions() -> None:
    """题库为空时写入内置题库；旧版内置题库（39 题 / 196 题）自动升级为最新版 200 题。"""
    from sqlmodel import select

    with Session(engine) as session:
        existing = session.exec(select(Question)).all()
        if not existing:
            session.add_all(builtin_questions())
            session.commit()
            return
        # 题库是纯内置内容（所有题文本都来自最新内置题库），但与最新版题量不一致
        # （旧版 13 关 × 3 题 = 39 题，或文档版 196 题）→ 重建为最新版 200 题。
        builtin_texts = {q.text for q in builtin_questions()}
        existing_texts = {q.text for q in existing}
        if (
            existing_texts
            and existing_texts.issubset(builtin_texts)
            and len(existing_texts) != len(builtin_texts)
        ):
            for q in existing:
                session.delete(q)
            session.add_all(builtin_questions())
            session.commit()
