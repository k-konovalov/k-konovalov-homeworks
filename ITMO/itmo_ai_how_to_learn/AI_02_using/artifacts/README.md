# pipeline/

Скрипты и шаблоны образовательного пайплайна.

## quiz.py

CLI для quiz + SM-2 + аналитика.

### Команды

```
quiz.py pool    [--limit N]                        # JSON-массив на stdout
quiz.py log    <topic> <id> <score> [--type X]     # лог ответа + SM-2
quiz.py report [--course <slug>] [--json]          # аналитика
quiz.py import <topic> <file.json> [--course <slug>]
```

### Типы ответов (`--type`)

`quiz` (по умолчанию), `brain_dump`, `feynman`, `elaboration`

### SM-2

- Шкала: `1 → 2 → 4 → 7 → 15 → 30 → 60` дней
- `score >= 0.7` → +1 шаг; `score < 0.7` → сброс на 1 день
- Pool = все, чей `next_review_iso <= сегодня`; лимит 10/день

### Выход `pool`

JSON-массив: `id, topic, question, options, correct_index`. ИИ читает stdout,
ведёт quiz, затем вызывает `log`.

### Хранилище

- `vault/Навыки/Обучение/<course>/theory/<slug>.questions.json`
- `vault/Навыки/Обучение/<course>/theory/<slug>.progress.json`

### Vault

- `--vault <path>` (override) → `OBSIDIAN_VAULT` env → `~/Documents/git/obsidian`

## templates/

- `theory.md.template` — структура theme-файла
- `questions.json.template` — структура массива вопросов
- `zettelkasten.md.template` — атомарная карточка идеи

## daemon.sh

Копирует `.md` из `~/Downloads` в `~/Documents/git/obsidian/inbox/`.

- **Cron (активен):** раз в 5 минут → `~/.local/state/edu-daemon.log`
- **Вручную (проверка):** `bash pipeline/daemon.sh`
- **Управление:** `crontab -l` (показать), снять: `crontab -l | grep -v 'pipeline/daemon.sh' | crontab -`
