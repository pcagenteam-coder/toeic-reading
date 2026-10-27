# 难度重评 v2 进度（UX_SPEC_v2 §6）

## 脚本
- `work/diff/rate.py --set open|private [--workers 10（上限 10，用户要求）]`：LLM 评分，断点续跑（按 uid 去重）。
  - 公开结果 `work/diff/out_open.jsonl`；私有结果 `private_data/work_private/diff/out_private.jsonl`（私有题文本不进公开仓库）。
  - 单位：P5 每 5 题一次，P6/P7 每题组一次。字段：cefr, hard_words, distractor, locate, reasoning, paraphrase, syntax, sent_len, time_sec, score, band, handbook_chapter, technique_zh。
  - 长跑：`setsid nohup python3 work/diff/rate.py --set private --workers 10（上限 10，用户要求） > work/diff/run_private.log 2>&1 &`（shell 120s 超时，必须后台）。
- `work/diff/merge.py`：合并 → data/difficulty/difficulty_v2_open.json、private_data/difficulty/difficulty_v2_private.json、docs/review/difficulty_v2_report.md。
- build.py 读上述文件：写 band / difficulty_est(diff1_5) / chapter / technique_zh，缺失回退旧值。

## 注意（续跑者必读）
- Kunyou 网关会丢弃长 system 消息 → rubric 并入 user 消息。
- 推理模型思考占 max_tokens，曾大量 finish=length → 现 7000+900×题数（≤16000）。
- igrok 端点从本沙箱返回 "Invalid token"（2026-10-27 23:30），脚本自动暂停该端点 10 分钟再探，实际只跑 Kunyou 10 路。
- 停止：`bash work/diff/stop.sh`（单独一条命令执行，勿与其它命令串联，pkill -f 会误杀同行 shell）。启动：`(setsid nohup bash work/diff/run_all.sh >/dev/null 2>&1 &)`。
- 私有 P5 每 10 题一次（960 单位），公开 P5 每 5 题（376 单位）。速度约 9 单位/分钟。
- work/diff/err.log 仅诊断用，不提交（可能含私有题模型输出片段）。

## 状态
- [x] 试点 20 题（质量可用：特征合理、章节/技巧贴题；分数偏中段）
- [ ] 公开全量
- [ ] 私有全量
- [ ] merge + 报告
- [ ] build 接入 + 测试
- [ ] grep 私有文本 + 提交推送
