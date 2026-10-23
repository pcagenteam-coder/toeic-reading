# 语法 60 秒微讲解 grammar_v1

- 文件：`grammar_v1.json`（75 条，全部自编）；源文本 `work/explain/lessons_src.txt`，构建 `python3 work/explain/build_lessons.py`（会校验覆盖与字段）。
- 覆盖：`data/graph_v1.json` 中 **GR.\* 全部 54 个叶节点** + **QT.P5.\* 11 个、QT.P6.\* 10 个题型叶节点**。
- 每条字段：`rule` 一句话规则｜`examples` 2 个托业式例句（英文 + 中文）｜`trap` 常见陷阱｜`signal` 识别信号（看到什么就用这招）｜`strategy_ids` 关联 strategies_v2 条目｜`in_min_set` 进入哪些档的最小技巧集。
- 优先级（`priority` 1→75，600 档视角）：
  1. tier 0（29 条）：600 档核心——看选项判题型、词性（GR.POS.*、P5 词性题、P6 独立型）、介词/连词（GR.CONN.*、P5 介词/连词/混排题）；组内按节点 target_band、再按 600 档最小集顺序；
  2. tier 1（4 条）：在 600 档最小集但非核心（P5 词汇、动词形态题、P6 语境词汇、插入句——后者 600 档策略是“直接涂”）；
  3. tier 2（42 条）：其余（动词时态语态、非谓语、代词、关系词、比较、特殊句式），按 target_band 由低到高。
- `meta.order_by_band`：各档（≤500 / 600 / 730 / 860+）最小技巧集覆盖到的节点及顺序，App 可按用户目标档取用。
- 解析与微讲解的关联：`data/explanations/zh_open_v1.json` 每题的 `node` 与 `tip_strategy_id` 可回链到本文件的 `node` / `strategy_ids`。
