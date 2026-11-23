#!/usr/bin/env python3
"""Build GitHub Pages data from the repository's dated question Markdown.

No third-party libraries are required. The deployed Pages artifact contains
static assets and JSON; the repo's source Markdown remains the source of truth.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "site" / "data"
QUESTIONS = ROOT / "questions"

SUBJECT_ALIASES = [
    ("linear algebra", "Mathematical Physics"),
    ("vector calculus", "Mathematical Physics"),
    ("differential equations", "Mathematical Physics"),
    ("effective potential", "Classical Mechanics"),
    ("electromagnetic waves", "Electromagnetic Theory"),
    ("quantum step", "Quantum Mechanics"),
    ("quantum harmonic", "Quantum Mechanics"),
    ("two-level canonical", "Statistical Physics"),
    ("double-slit", "Optics"),
    ("density of states", "Solid State"),
]

TITLE = re.compile(r"(?m)^##\s+Q(\d+)(?:\.|\s*[\u2014\u2013-])\s*(.+?)\s*$")
DETAILS = re.compile(
    r"<details>\s*<summary[^>]*>.*?</summary>\s*(.*?)\s*</details>",
    re.S | re.I,
)

def parse_sheet(file: Path) -> dict:
    raw = file.read_text(encoding="utf-8")
    matches = list(TITLE.finditer(raw))
    questions = []
    for index, match in enumerate(matches):
        chunk = raw[match.end(): matches[index+1].start() if index+1 < len(matches) else len(raw)]
        found = DETAILS.search(chunk)
        if not found:
            raise ValueError(f"Missing collapsible solution: {file.name} Q{match.group(1)}")
        prompt = chunk[:found.start()].strip()
        prompt = re.sub(r"(?m)^\*\*Practice style:\*\*.*\n?", "", prompt).strip()
        prompt = re.sub(r"^\*\*Question\.\*\*\s*", "", prompt)
        solution = found.group(1).strip()
        label = match.group(2).strip()
        if " \u2014 " in label:
            subject, topic = label.split(" \u2014 ", 1)
        else:
            subject, topic = "Other", label
            for prefix, resolved in SUBJECT_ALIASES:
                if label.lower().startswith(prefix):
                    subject = resolved
                    break
        questions.append({
            "id": f"{file.stem}-q{int(match.group(1))}",
            "number": int(match.group(1)),
            "subject": subject,
            "topic": topic,
            "question": prompt,
            "solution": solution,
        })
    if len(questions) != 10 or sorted(q["number"] for q in questions) != list(range(1, 11)):
        raise ValueError(f"{file.name}: expected exactly Q1..Q10, got {len(questions)}")
    day = dt.date.fromisoformat(file.stem)
    return {
        "date": day.isoformat(),
        "dayLabel": day.strftime("%d %b %Y"),
        "questions": questions,
        "source": f"https://github.com/KrAzad0/QUESTIONS/blob/main/questions/{file.name}",
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    daily = [parse_sheet(f) for f in sorted(QUESTIONS.glob("????-??-??.md"), reverse=True)]
    if not daily:
        raise RuntimeError("No question sets found in questions/")
    result = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "totalQuestions": sum(len(s["questions"]) for s in daily),
        "days": daily,
    }
    (OUTPUT / "questions.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for src, dest in [
        ("2027-ROADMAP.md", "roadmap.md"),
        ("RESOURCES.md", "resources.md"),
        ("TRACKER.md", "tracker.md"),
    ]:
        shutil.copyfile(ROOT / "docs" / src, OUTPUT / dest)

    # GitHub Pages should serve files directly (no Jekyll transformation).
    (ROOT / "site" / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Site data ready: {len(daily)} dates / {result['totalQuestions']} worked questions")


if __name__ == "__main__":
    main()
