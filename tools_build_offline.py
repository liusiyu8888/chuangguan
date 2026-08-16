"""构建「百科知识大闯关 · 离线版」单文件 HTML。

从 app.builtin_questions 读取 200 道题，嵌入 offline_template.html 模板，
输出为不依赖任何后端 / CDN / Node 的单文件离线版，双击即可在浏览器中游玩。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.builtin_questions import builtin_questions  # noqa: E402

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "offline_template.html"
OUTPUT = ROOT / "百科知识大闯关-离线版.html"


def main() -> None:
    questions = builtin_questions()
    if len(questions) != 200:
        raise SystemExit(f"题库数量异常：期望 200 题，实际 {len(questions)} 题")

    # 序列化题目；转义 "</" 防止提前闭合 <script>
    payload = json.dumps(
        [
            {
                "level": q.level,
                "text": q.text,
                "option_a": q.option_a or "",
                "option_b": q.option_b or "",
                "option_c": q.option_c or "",
                "option_d": q.option_d or "",
                "answer": q.answer,
                "explanation": q.explanation or "",
            }
            for q in questions
        ],
        ensure_ascii=False,
    ).replace("</", "<\\/")

    html = TEMPLATE.read_text(encoding="utf-8")
    if "__QUESTIONS_JSON__" not in html:
        raise SystemExit("模板中缺少占位符 __QUESTIONS_JSON__")
    html = html.replace("__QUESTIONS_JSON__", payload)

    OUTPUT.write_text(html, encoding="utf-8")
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"✅ 已生成：{OUTPUT.name}（{size_kb:.0f} KB，{len(questions)} 题）")


if __name__ == "__main__":
    main()
