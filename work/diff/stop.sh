#!/bin/bash
# 停止难度评分后台任务（只杀本任务的 run_all.sh / rate.py 进程）
for p in $(pgrep -f "work/diff/run_all.sh") $(pgrep -f "python3 work/diff/rate.py"); do
  [ "$p" != "$$" ] && kill "$p" 2>/dev/null
done
echo stopped
