# -*- coding: utf-8 -*-
"""从 app.builtin_questions 导出 200 题到 static-site/js/data.js。"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from app.builtin_questions import _RAW, QUESTIONS_PER_LEVEL  # noqa: E402

questions = []
for i, (text, a, b, c, d, ans, expl) in enumerate(_RAW, 1):
    level = (i - 1) // QUESTIONS_PER_LEVEL + 1
    questions.append({
        "id": i,
        "level": level,
        "text": text,
        "option_a": a,
        "option_b": b,
        "option_c": c,
        "option_d": d,
        "answer": ans,
        "explanation": expl,
    })

payload = {
    "per_level": QUESTIONS_PER_LEVEL,
    "total_levels": len(_RAW) // QUESTIONS_PER_LEVEL,
    "questions": questions,
}

out = "window.QUIZ_DATA = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n"
out_path = pathlib.Path("static-site/js/data.js")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(out, encoding="utf-8")

log = pathlib.Path("_verify_data.txt")
log.write_text(
    "SIZE=%d QUESTIONS=%d LEVELS=%d\n" % (out_path.stat().st_size, len(questions), payload["total_levels"]),
    encoding="utf-8",
)
