#!/usr/bin/env python3
"""
quiz.py — образовательный пайплайн (Phase 1-4)

Команды (D1):
  pool    [--limit N]                       дневной пул, JSON-массив на stdout
  log     <topic> <id> <score> [--type X]   лог ответа + SM-2
  report  [--course <slug>] [--json]        аналитика по темам/курсу
  import  <topic> <file.json>               инициализация progress.json

Пути (D3): --vault <path> → env OBSIDIAN_VAULT → ~/Documents/git/obsidian
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------

# C1 — шкала интервалов. score >= 0.7 → +1 шаг; score < 0.7 → сброс на 1 день.
SCALE_DAYS = [1, 2, 4, 7, 15, 30, 60]
SCORE_THRESHOLD = 0.7
DEFAULT_LIMIT = 10  # C2

# B5 — допустимые type
VALID_TYPES = ("quiz", "brain_dump", "feynman", "elaboration")

LEARN_ROOT = Path("Навыки") / "Обучение"


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def default_vault() -> Path:
    env = os.environ.get("OBSIDIAN_VAULT")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / "Documents" / "git" / "obsidian").resolve()


def to_iso(d: date) -> str:
    return d.isoformat()  # YYYY-MM-DD


def to_ru(d: date) -> str:
    return d.strftime("%d.%m.%Y")  # ДД.ММ.ГГГГ


def parse_score(raw: str) -> float:
    s = float(raw)
    if not (0.0 <= s <= 1.0):
        raise SystemExit(f"score должен быть в диапазоне 0.0–1.0 (получено {raw})")
    return s


def parse_iso(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def course_slug_of(rel: Path) -> str | None:
    """Из относительного пути vault → slug курса (первая часть после LEARN_ROOT)."""
    parts = rel.parts
    if len(parts) <= len(LEARN_ROOT.parts):
        return None
    # vault/Навыки/Обучение/<course>/...
    prefix = tuple(LEARN_ROOT.parts)
    if tuple(parts[: len(prefix)]) == prefix:
        return parts[len(prefix)]
    return None


def next_interval_days(score: float, current_interval_days: int) -> int:
    """C1: score>=0.7 → следующий шаг; score<0.7 → 1 день."""
    if score < SCORE_THRESHOLD:
        return SCALE_DAYS[0]
    # следующий шаг в шкале
    try:
        idx = SCALE_DAYS.index(current_interval_days)
    except ValueError:
        idx = 0
    nxt = min(idx + 1, len(SCALE_DAYS) - 1)
    return SCALE_DAYS[nxt]


# ---------------------------------------------------------------------------
# Хранилище
# ---------------------------------------------------------------------------

class Storage:
    def __init__(self, vault: Path):
        self.vault = vault
        self.learn_root = vault / LEARN_ROOT
        self._inferred_course: str | None = None

    # --- поиск файлов ------------------------------------------------------

    def iter_progress_files(self) -> list[Path]:
        if not self.learn_root.exists():
            return []
        return sorted(self.learn_root.rglob("*.progress.json"))

    def iter_questions_files(self) -> list[Path]:
        if not self.learn_root.exists():
            return []
        return sorted(self.learn_root.rglob("*.questions.json"))

    def find_progress_by_id(self, question_id: str) -> Path | None:
        for p in self.iter_progress_files():
            data = self.read(p)
            for q in data.get("questions", []):
                if q.get("id") == question_id:
                    return p
        return None

    def read(self, path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def question_path(self, topic_file: Path) -> Path:
        """progress.json ↔ questions.json."""
        return topic_file.with_name(topic_file.name.replace(".progress.json", ".questions.json"))

    def topic_dir(self, course: str, topic_slug: str) -> Path:
        return self.learn_root / course / "theory"

    def topic_file(self, course: str, topic_slug: str) -> Path:
        return self.topic_dir(course, topic_slug) / f"{topic_slug}.progress.json"

    def question_file(self, course: str, topic_slug: str) -> Path:
        return self.topic_dir(course, topic_slug) / f"{topic_slug}.questions.json"


# ---------------------------------------------------------------------------
# Команды
# ---------------------------------------------------------------------------

def cmd_pool(args: argparse.Namespace, st: Storage) -> int:
    """D2: JSON-массив id/topic/question/options/correct_index."""
    today_iso = to_iso(date.today())

    # Собираем все вопросы из progress.json + текст/варианты из questions.json
    questions_by_id: dict[str, dict[str, Any]] = {}
    for qf in st.iter_questions_files():
        try:
            arr = st.read(qf)
        except Exception:
            continue
        if not isinstance(arr, list):
            continue
        for q in arr:
            if not isinstance(q, dict) or "id" not in q:
                continue
            questions_by_id[q["id"]] = q

    candidates: list[dict[str, Any]] = []
    for pf in st.iter_progress_files():
        data = st.read(pf)
        for q in data.get("questions", []):
            qid = q.get("id")
            if qid not in questions_by_id:
                continue
            nri = q.get("next_review_iso")
            if not nri or nri > today_iso:
                continue  # не день
            # last score: последний attempt, либо 1.5 (новые — в конце)
            attempts = q.get("attempts", [])
            last_score = attempts[-1].get("score", 1.5) if attempts else 1.5
            nri_iso = nri or "0000-01-01"
            candidates.append(
                {
                    "id": qid,
                    "topic": data.get("topic", ""),
                    "next_review_iso": nri_iso,
                    "last_score": last_score,
                    "body": questions_by_id[qid],
                }
            )

    # C3: min next_review_iso; внутри группы — min score (слабее — раньше)
    candidates.sort(key=lambda x: (x["next_review_iso"], x["last_score"]))

    limit = args.limit if args.limit and args.limit > 0 else DEFAULT_LIMIT
    pool = candidates[:limit]

    out = []
    for c in pool:
        b = c["body"]
        out.append(
            {
                "id": c["id"],
                "topic": c["topic"],
                "question": b.get("question", ""),
                "options": b.get("options", []),
                "correct_index": b.get("correct_index", 0),
            }
        )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_log(args: argparse.Namespace, st: Storage) -> int:
    score = parse_score(args.score)
    qtype = args.type or "quiz"
    qtype = qtype.lower()
    if qtype not in VALID_TYPES:
        raise SystemExit(f"type должен быть один из {', '.join(VALID_TYPES)}")

    today = date.today()
    today_iso = to_iso(today)
    today_ru = to_ru(today)

    pf = st.find_progress_by_id(args.id)
    if pf is None:
        raise SystemExit(f"Вопрос {args.id} не найден в progress.json (topic={args.topic})")

    data = st.read(pf)
    target = None
    for q in data.get("questions", []):
        if q.get("id") == args.id:
            target = q
            break
    if target is None:
        raise SystemExit(f"Вопрос {args.id} не найден внутри {pf.name}")

    # B3: append attempt
    attempt = {
        "date_iso": today_iso,
        "date_ru": today_ru,
        "score": score,
    }
    if qtype != "quiz":
        attempt["type"] = qtype
    target.setdefault("attempts", []).append(attempt)

    # C1: SM-2
    old_interval = int(target.get("interval_days", SCALE_DAYS[0]))
    new_interval = next_interval_days(score, old_interval)
    target["interval_days"] = new_interval

    # next_review: при ошибке — сегодня; при успехе — сегодня + interval
    if score < SCORE_THRESHOLD:
        nrd = today
    else:
        nrd = today + timedelta(days=new_interval)
    target["next_review_iso"] = to_iso(nrd)
    target["next_review_ru"] = to_ru(nrd)

    st.write(pf, data)

    # Человек-читаемый вывод
    print(
        f"OK  {args.id}  score={score:.2f}  type={qtype}  "
        f"interval={new_interval}d  next={target['next_review_ru']}"
    )
    return 0


def cmd_report(args: argparse.Namespace, st: Storage) -> int:
    if not st.learn_root.exists():
        msg = "Нет папок с теорией — пока пусто."
        print(msg)
        return 0

    topics: list[dict[str, Any]] = []
    for pf in st.iter_progress_files():
        data = st.read(pf)
        q_list = data.get("questions", [])
        attempts_all = [a for q in q_list for a in q.get("attempts", [])]
        n_att = len(attempts_all)
        last5 = sorted(attempts_all, key=lambda a: a.get("date_iso", ""))[-5:]
        avg_last5 = (sum(a.get("score", 0.0) for a in last5) / len(last5)) if last5 else None
        avg_all = (
            sum(a.get("score", 0.0) for a in attempts_all) / n_att
            if n_att
            else None
        )
        today_iso = to_iso(date.today())
        due = sum(
            1
            for q in q_list
            if (q.get("next_review_iso") or "9999-12-31") <= today_iso
        )
        weak_q = [
            q
            for q in q_list
            if (
                q.get("attempts")
                and (
                    sum(
                        a.get("score", 0.0)
                        for a in sorted(q["attempts"], key=lambda a: a.get("date_iso", ""))[-5:]
                    )
                    / min(5, len(q["attempts"]))
                )
                < SCORE_THRESHOLD
            )
        ]
        topics.append(
            {
                "topic": data.get("topic", ""),
                "file": str(pf),
                "course": course_slug_of(pf.relative_to(st.vault)) or "",
                "n_questions": len(q_list),
                "n_attempts": n_att,
                "avg_all": avg_all,
                "avg_last5": avg_last5,
                "due_today": due,
                "weak_question_ids": [q["id"] for q in weak_q],
            }
        )

    if args.course:
        topics = [t for t in topics if t["course"] == args.course]

    if args.json:
        print(json.dumps(topics, ensure_ascii=False, indent=2))
        return 0

    if not topics:
        print(f"Курс {args.course if args.course else '(все)'}: нет вопросов.")
        return 0

    print(f"{'TOPIК':<32} {'вопр.':>6} {'попыт':>6} {'avg':>6} {'avg5':>6} {'due':>5}  слабые")
    print("-" * 86)
    for t in topics:
        s_all = f"{t['avg_all'] * 100:.0f}%" if t["avg_all"] is not None else "-"
        s_l5 = f"{t['avg_last5'] * 100:.0f}%" if t["avg_last5"] is not None else "-"
        weak = ", ".join(t["weak_question_ids"]) if t["weak_question_ids"] else "-"
        print(
            f"{t['topic']:<32} {t['n_questions']:>6} {t['n_attempts']:>6} "
            f"{s_all:>6} {s_l5:>6} {t['due_today']:>5}  {weak}"
        )
    print("-" * 86)
    print("avg = средняя score за всё, avg5 = за последние 5, due = в пуле сегодня")
    return 0


def cmd_import(args: argparse.Namespace, st: Storage) -> int:
    src = Path(args.file).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"Файл не найден: {src}")
    arr = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(arr, list):
        raise SystemExit("Файл вопросов должен быть JSON-массивом объектов")

    # Проверка структуры
    for i, q in enumerate(arr):
        if not isinstance(q, dict):
            raise SystemExit(f"Элемент {i} не объект")
        for k in ("id", "question", "options", "correct_index"):
            if k not in q:
                raise SystemExit(f"Элемент {i} без поля '{k}'")

    # Копируем questions.json рядом с будущим progress.json
    topic_slug = args.topic
    qfile = st.question_file(st._inferred_course, topic_slug)
    qfile.parent.mkdir(parents=True, exist_ok=True)
    st.write(qfile, arr)

    # Инициализируем progress.json
    pfile = qfile.with_name(f"{topic_slug}.progress.json")
    today = date.today()
    init_questions = []
    existing: list[dict] = []
    if pfile.exists():
        existing = st.read(pfile).get("questions", [])
    seen = {q["id"] for q in existing}
    for qd in arr:
        if qd["id"] in seen:
            continue
        init_questions.append(
            {
                "id": qd["id"],
                "interval_days": SCALE_DAYS[0],
                "next_review_iso": to_iso(today),
                "next_review_ru": to_ru(today),
                "attempts": [],
            }
        )
    merged = existing + init_questions
    # Сохраняем поле topic (topic = курс/тема, если известно)
    topic_field = f"{st._inferred_course}/{topic_slug}"
    st.write(
        pfile,
        {
            "topic": topic_field,
            "questions": merged,
        },
    )
    print(
        f"OK  импорт {len(arr)} вопросов → {qfile.relative_to(st.vault)}\n"
        f"    новых в progress.json: {len(init_questions)}"
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(prog="quiz.py", description="Образовательный пайплайн (quiz + SM-2 + аналитика)")
    p.add_argument("--vault", type=Path, default=None, help="Путь к vault (переопределяет env и default)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("pool", help="Дневной пул (JSON-массив на stdout)")
    pl.add_argument("--limit", type=int, default=0, help=f"Лимит (0 = default {DEFAULT_LIMIT})")

    lg = sub.add_parser("log", help="Залогировать ответ")
    lg.add_argument("topic", help="Slug темы (например, proxmox-terraform)")
    lg.add_argument("id", help="question_id (например, proxmox-terraform-001)")
    lg.add_argument("score", help="0.0–1.0")
    lg.add_argument("--type", default="quiz", choices=VALID_TYPES, help="Тип ответа")

    rp = sub.add_parser("report", help="Аналитика")
    rp.add_argument("--course", default=None, help="Только этот курс (slug)")
    rp.add_argument("--json", action="store_true", help="JSON-вывод")

    im = sub.add_parser("import", help="Импорт вопросов + инициализация progress.json")
    im.add_argument("topic", help="Slug темы")
    im.add_argument("file", help="Путь к JSON-файлу с вопросом/вопросами")
    im.add_argument("--course", default=None, help="Курс (slug). Если не задан — единственная папка, либо первая по алфавиту.")

    args = p.parse_args()
    vault = args.vault or default_vault()
    st = Storage(vault)

    # Определяем курс для import: --course (если задан), иначе — единственная
    # папка под LEARN_ROOT с каталогом theory/, иначе — ошибка.
    if args.cmd == "import":
        explicit = getattr(args, "course", None)
        if explicit:
            st._inferred_course = explicit
        else:
            courses = []
            if st.learn_root.exists():
                for child in st.learn_root.iterdir():
                    if child.is_dir() and (child / "theory").exists():
                        courses.append(child.name)
            if len(courses) == 1:
                st._inferred_course = courses[0]
            elif len(courses) == 0:
                raise SystemExit("Нет ни одной папки курса (Навыки/Обучение/<course>/theory/). Создайте.")
            else:
                st._inferred_course = sorted(courses)[0]

    if args.cmd == "pool":
        return cmd_pool(args, st)
    if args.cmd == "log":
        return cmd_log(args, st)
    if args.cmd == "report":
        return cmd_report(args, st)
    if args.cmd == "import":
        return cmd_import(args, st)
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
