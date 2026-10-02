#!/usr/bin/env bash
#
# daemon.sh — копировать .md из ~/Downloads в obsidian/inbox/
#
# Режим работы (по решению F):
#   - cron: раз в 5 минут (активен) →  ~/.local/state/edu-daemon.log
#   - вручную: bash pipeline/daemon.sh   (для проверки)
#
# Файл уходит из Downloads (mv -n), дублей нет. Только .md (F2).

set -euo pipefail

DOWNLOADS="${DOWNLOADS:-$HOME/Downloads}"
INBOX="${INBOX:-$HOME/Documents/git/obsidian/inbox}"

mkdir -p "$INBOX"

moved=0
shopt -s nullglob
for f in "$DOWNLOADS"/*.md; do
  base=$(basename "$f")
  # mv -n: не перезаписывать существующий файл
  if mv -n "$f" "$INBOX/$base"; then
    echo "moved: $base"
    moved=$((moved+1))
  fi
done
shopt -u nullglob

echo "done. moved=$moved → $INBOX"

# ---------------------------------------------------------------------------
# cron (УСТАНОВЛЕН, раз в 5 минут) — проверить:  crontab -l
# ---------------------------------------------------------------------------
#   */5 * * * *  /usr/bin/bash /home/kirillkonovalov/Documents/git/obsidian/pipeline/daemon.sh >> /home/kirillkonovalov/.local/state/edu-daemon.log 2>&1
#
# Установка/снятие:
#   Установка : (crontab -l 2>/dev/null; echo '*/5 * * * * /usr/bin/bash /home/kirillkonovalov/Documents/git/obsidian/pipeline/daemon.sh >> /home/kirillkonovalov/.local/state/edu-daemon.log 2>&1') | crontab -
#   Снятие    : crontab -l | grep -v 'pipeline/daemon.sh' | crontab -
# Лог         : tail -f ~/.local/state/edu-daemon.log
# Проверка    : crontab -l
# ---------------------------------------------------------------------------
