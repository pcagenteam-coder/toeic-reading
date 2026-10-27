# 难度重评 v2 进度（UX_SPEC_v2 §6）

## 脚本
- `work/diff/rate.py --set open|private [--workers 10（上限 10，用户要求）]`：LLM 评分，断点续跑（按 uid 去重）。
  - 公开结果 `work/diff/out_open.jsonl`；私有结果 `private_data/work_private/diff/out_private.jsonl`（私有题文本不进公开仓库）。
  - 单位：P5 每 5 题一次，P6/P7 每题组一次。字段：cefr, hard_words, distractor, locate, reasoning, paraphrase, syntax, sent_len, time_sec, score, band, handbook_chapter, technique_zh。
  - 长跑：`setsid nohup python3 work/diff/rate.py --set private --workers 10（上限 10，用户要求） > work/diff/run_private.log 2>&1 &`（shell 120s 超时，必须后台）。
- `work/diff/merge.py`：合并 → data/difficulty/difficulty_v2_open.json、private_data/difficulty/difficulty_v2_private.json、docs/review/difficulty_v2_report.md。
- build.py 读上述文件：写 band / difficulty_est(diff1_5) / chapter / technique_zh，缺失回退旧值。

## 状态
- [ ] 试点 20 题
- [ ] 公开全量
- [ ] 私有全量
- [ ] merge + 报告
- [ ] build 接入 + 测试
- [ ] grep 私有文本 + 提交推送
