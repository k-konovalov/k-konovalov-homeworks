# Лог сессии — Educational Pipeline

> Дата: 01.10.2026
> Тема: проектирование и реализация образовательного пайплайна (сохранение теории в Obsidian + повторение через quiz/SM-2)
> Локация: `~/Documents/git/{itmo,obsidian}`

---

## Ход обсуждения

### 1. Пользователь
> Изучи `PROMPT.md` и `educational-pipeline-plan.md`. Какие шаги можно выполнить?

### 2. Ассистент
Разобрал обе спецификации и фактическую структуру репозиториев (`itmo/`, `obsidian/`).
Свернул состояние:
- `obsidian/inbox/`, `obsidian/pipeline/` — **ещё не существовали**
- `~/Downloads` — **3 файла** (`index.md` Proxmox, `Игнорирование отслеживания файлов проектов.md`, `README.md`)
- SKILL `educational-pipeline` — **не существовал**
- Python 3.14.4, `jq` 1.8.1 — ок

Предложил разбить на 3 фазы:
- **A** — фундамент: каталоги, `quiz.py`, `daemon.sh`, шаблоны, `index.md`
- **B** — `SKILL.md` + бэкап в vault
- **C** — живой прогон: katalogизация inbox + quiz + heavy method + report + commit

### 3. Пользователь
> 1. это ITMO статья для одной из тем в **itmo_OS**
> 2. не понял, пусть лежит там где лежит
> 3. попробуем с двух файлов
> 4. сначала ручной запуск, cron в самом конце
> 5. один коммит в конце сессии
>
> Давай сделаем **Фазу A**

### 4. Ассистент — Фаза A (выполнена)
Создано:
- `obsidian/pipeline/quiz.py` — 4 команды: `pool`, `log`, `report`, `import`
  - SM-2 шкала `1 → 2 → 4 → 7 → 15 → 30 → 60`
  - Порог слабой темы: avg5 `< 0.7`
  - Пул: `next_review_iso <= сегодня`, лимит 10/день
- `obsidian/pipeline/daemon.sh` — `mv -n` из `~/Downloads/*.md` → `obsidian/inbox/`
- `obsidian/pipeline/templates/` — `theory.md`, `questions.json`, `zettelkasten.md`
- `obsidian/pipeline/README.md`
- `obsidian/Навыки/Обучение/itmo_OS/{index.md, theory/, zettelkasten/}`

Тест: полный цикл `import → pool → log (0.0/1.0/brain_dump) → report` — SM-2 корректен.

---

### 5. Пользователь
> 3. каталогизировать (README про opencode+ollama)
> Давай продолжим над **Фазой B**

### 6. Ассистент — Фаза B (выполнена)
Создано:
- `~/.agents/skills/educational-pipeline/SKILL.md` (199 строк)
  - Секции: 0.Константы, 1.Триггеры, 2.Порядок сессии (H2), 3.Сбор теории, 4.Inbox, 5.Quiz (+5.1 Формат), 6.Тяжёлый метод, 7.Сводка, 8.Git, 9.Бэкап, 10.Чек-лист, 11.Правила
- Бэкап: `obsidian/edu-pipeline.SKILL.md.bak` (md5 совпадает)

---

### 7. Пользователь
> Давай начнем **Фазу C**

### 8. Ассистент — Фаза C (выполнена)

**Inbox развёрнут:**
| Файл | Решение | Куда ушёл |
|---|---|---|
| `index.md` (Proxmox, 36KB) | каталогизировать | `itmo_OS/proxmox-ve` |
| `Игнорирование отслеживания файлов проектов.md` | оставить как есть (решение #2) | inbox → на месте |
| `README.md` (opencode+ollama) | каталогизировать | `Навыки/Программирование/LLM/opencode-ollama.md` |

**Созданный материал (Proxmox VE):**
- `theory/proxmox-ve.md` (Type-1, KVM, LXC, 3 метода auth, `ssh{}`, ENV, security)
- `theory/proxmox-ve.questions.json` (7 вопросов)
- `theory/proxmox-ve.progress.json` (SM-2)
- `zettelkasten/{Type1Hypervisor, ApiToken, LXC, LeastPrivilege}.md`
- `index.md` (MOC) — новая строка `[[proxmox-ve]]`

**Сессия (прогон):**
- **Quiz** 7 вопросов: 6/7 (86%). Промах — «когда SSH обязателен» (ответ: user выбрал «Storage» вместо `source_file.path`/snippets/`idmap`).
- **Тяжёлый метод** (четверг → Brain dump): PVE/KVM/LXC — ✅, аргументы — ⚠️ (нет `ssh{}`, `random_vm_ids`, ENV, format token), «ssh в остальных случаях» — ❌ (это не метод auth, а блок `ssh{}` для 4 операций). Score `0.5`.
- **Сводка (`report`):** avg 81%, avg5 70%, слабое место `proxmox-ve-005` (SSH), due сегодня = 1.
- **Commit:** `1fc9b22 vault: itmo_OS/proxmox-ve — save|quiz|method|report` (20 files, +1942)

**Вопрос пользователя:** «Можешь формировать вопросы не через обычный список вариантов, а через вопросы с выбором (формат opencode)» → Перешёл на интерактивный инструмент `question`.

---

### 9. Пользователь
> Добавь пункт про формат вопроса в скилл

### 10. Ассистент
Добавил секцию **5.1 Формат вопроса (вопрос с выбором)** в SKILL.md:
- использовать `question` tool opencode (не текстовый список)
- параметры: `question`, `options[4]{label, description}`, `header ≤ 30`, `multiple: false`
- фолбэк — текстовый список 1/2/3/4
- бэкап обновлён (md5 `b4fb85b5…`)

---

### 11. Пользователь
> Добавь cron демона

### 12. Ассистент
- cron-демон **установлен** (раз в 5 минут)
- Лог: `~/.local/state/edu-daemon.log` (тест: `moved: _edu_daemon_test.md`)
- `daemon.sh` + `README.md` — обновлены (команды установки/снятия)
- **Commit:** `ae19a3c vault: infra — cron daemon (*/5 min) включён`

---

### 13. Пользователь
> Необходимо проверить скилл

### 14. Ассистент
(Прочитал SKILL.md полностью. Начал проверку.)

### 15. Пользователь
> я имею в виду его работу

### 16. Ассистент
(Понял: пользователь просит проверить **рабочие сценарии** скилла, а не его текст. Запланировал прогон: триггеры → полный цикл сессии → дедупликация → тяжёлый метод → пустое состояние → `question`-инструмент.)

### 17. Пользователь
> создай в корне `/git` лог с сообщениями из нашего чата

### 18. Ассистент
Это файл.

---

## Состояние системы на момент лога

### Git история (obsidian)
```
ae19a3c  vault: infra — cron daemon (*/5 min) включён
1fc9b22  vault: itmo_OS/proxmox-ve — save|quiz|method|report
2168d97  Update kotlin_coroutines.md          (до сессии)
3cc3147  Update android_internals.md          (до сессии)
…
```

### Пул SM-2 (itmo_OS/proxmox-ve, 7 вопросов)
| id | interval | next | attempts |
|---|---|---|---|
| `proxmox-ve-001` | 2d | 03.10 | 1 (1.0) |
| `proxmox-ve-002` | 2d | 03.10 | 1 (1.0) |
| `proxmox-ve-003` | 2d | 03.10 | 1 (1.0) |
| `proxmox-ve-004` | 2d | 03.10 | 1 (1.0) |
| `proxmox-ve-005` | 1d | **01.10** | 2 (0.0, 0.5) |
| `proxmox-ve-006` | 2d | 03.10 | 1 (1.0) |
| `proxmox-ve-007` | 2d | 03.10 | 1 (1.0) |

### Cron
```
*/5 * * * *  /usr/bin/bash ~/Documents/git/obsidian/pipeline/daemon.sh \
             >> ~/.local/state/edu-daemon.log 2>&1
```

### Inbox
Осталось 1 файл: `Игнорирование отслеживания файлов проектов.md` (намеренно оставлен по решению #2).

---

## Открытые действия
- [ ] Проверить **работу** скилла (сценарные прогоны)
- [ ] По решению #2: решить, что делать с `.gitignore`-файлом в inbox (каталогизировать → `itmo_base_python`? Убрать?)
- [ ] При появлении новых `.md` в Downloads — они сами уйдут в `inbox/` (cron активен)
