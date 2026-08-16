"""数据模型定义。"""
from sqlmodel import Field, SQLModel


class Question(SQLModel, table=True):
    """一道选择题。"""

    id: int | None = Field(default=None, primary_key=True)
    level: int = Field(index=True, description="所属关卡（1 起）")
    text: str = Field(description="题目内容")
    option_a: str = Field(description="选项 A")
    option_b: str = Field(description="选项 B")
    option_c: str = Field(description="选项 C")
    option_d: str = Field(description="选项 D")
    answer: str = Field(description="正确答案字母 A/B/C/D")
    explanation: str = Field(default="", description="答案解析")


class Progress(SQLModel, table=True):
    """闯关进度（单用户本地游戏，只保留一条记录 id=1）。"""

    id: int | None = Field(default=None, primary_key=True)
    current_level: int = Field(default=1, description="正在挑战的关卡")
    current_question: int = Field(default=1, description="本关当前答题序号（1-5）")
    current_correct: int = Field(default=0, description="本关已连续答对题数")
    max_unlocked: int = Field(default=1, description="已解锁的最高关卡")
