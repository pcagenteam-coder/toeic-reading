#!/bin/bash
# 进度 + 存活检查：沙箱重启会杀后台进程，若 run_all 不在且未 ALLDONE 则重启。用法: bash work/diff/poll.sh [sleep秒]
cd "$(dirname "$0")/../.."
sleep "${1:-0}"
o=$(wc -l < work/diff/out_open.jsonl 2>/dev/null); p=$(wc -l < private_data/work_private/diff/out_private.jsonl 2>/dev/null)
echo "open $o/376 private ${p:-0}/960"
if ! grep -q ALLDONE work/diff/run_private.log 2>/dev/null; then
  if ! pgrep -f "bash work/diff/run_all.sh" >/dev/null; then
    (setsid nohup bash work/diff/run_all.sh >/dev/null 2>&1 &); echo restarted
  fi
else
  echo ALLDONE
fi
