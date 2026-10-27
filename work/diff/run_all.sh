#!/bin/bash
# 后台长跑：先公开后私有（断点续跑）。启动: (setsid nohup bash work/diff/run_all.sh >/dev/null 2>&1 &)
cd "$(dirname "$0")/../.."
python3 work/diff/rate.py --set open --workers 20 >> work/diff/run_open.log 2>&1
python3 work/diff/rate.py --set open --workers 20 >> work/diff/run_open.log 2>&1   # 补跑失败单位
python3 work/diff/rate.py --set private --workers 20 >> work/diff/run_private.log 2>&1
python3 work/diff/rate.py --set private --workers 20 >> work/diff/run_private.log 2>&1
echo ALLDONE >> work/diff/run_private.log
