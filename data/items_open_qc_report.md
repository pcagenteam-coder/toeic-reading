# A2 公开题库全量质检报告（items_open_maximcuynat / items_open_kdeppaei）

日期：2026-10-23　范围：maximcuynat 全部 600 题（P5 180 / P6 96 / P7 324），kdeppaei 全部 804 题（P5 328 / P6 119 / P7 357）

## 1. 方法

- **逐题复核**：用 `work/qc/dump.py` 按题打印（P6/P7 连同整篇篇章），人工逐题判断四项：
  1. 答案唯一性：其余三个选项放进句子或篇章里是否也说得通；
  2. 选项/文本错误：题干、选项、篇章有无错字、重复句、语义不通；
  3. 主节点：必须是 `data/graph_v1.json` 的叶节点，并与题目实际考点一致。P7 还要逐组判断是否真的需要跨篇（CROSS_REF）；
  4. 难度：`difficulty_est` 是否与题型、篇章形态大致相符。
  - 范围：maximcuynat P6/P7 全部和 kdeppaei 全部 804 题逐题看过。maximcuynat P5 的答案此前已逐题核过，本轮补看了主节点。
- **修正分两层**：
  - 规则层：系统性错误改两个转换脚本 `work/convert_maximcuynat.py` 和 `data/items_open_kdeppaei_convert.py`，详见 §3.1；
  - 逐题层：只能逐题判断的写进 `data/items_open_qc_fixes.json`（共 166 条），每条带 `reason` 和 `cat`（answer / text / node）。
- **应用脚本 `work/qc/apply_qc_fixes.py`**：
  - 支持的修正：题目级字段（stem / q / options / answer / explain_zh / translation_zh / difficulty_est / node / node_ids），以及 bundle 级的 `text_type` / `doc_types`；
  - 节点处理：自动保留 TX / 场景 / P6 分类节点；单篇 P7 改文本类型时，“题型 × 文本”叶节点按新类型重算；跨篇状态变了就重算 P7 难度；
  - 校验：节点存在且为叶节点、`node == node_ids[0]`、单篇不能挂 CROSS_REF、改选项时正确项文本不能错位、P5 空位恰好 1 个；
  - 幂等：重复跑结果完全相同（已用 cmp 验证）。被修正的题带 `qc_fix` 字段，meta 记 `qc_applied`。
- **统计**：`work/qc/qc_stats.py` 对比 QC 前基线（`work/qc/_baseline/`，不入库）和最终产物。

### 复跑顺序（每次重新生成公开题库）
```
python3 work/convert_maximcuynat.py
python3 data/items_open_kdeppaei_convert.py
python3 work/qc/apply_qc_fixes.py
python3 app/build.py --public
# 可选：python3 work/qc/qc_stats.py （需本地有 _baseline）
```

## 2. 各源各 Part 错误率（QC 前基线中被判错的题）

一道题命中下列任一项即计为 1 道错题：答案不唯一、文本错误、主节点题型错、P5/P6 考点节点错、P7 跨篇状态错。场景标签和难度单列，不计入错题率。

| 来源 | Part | 题数 | 错题 | 错误率 | 答案 | 文本 | 节点 | 其中跨篇判定 | 场景标签改动 | 难度改动 |
|---|---|---|---|---|---|---|---|---|---|---|
| maximcuynat | P5 | 180 | 19 | 10.6% | 0 | 0 | 19 | – | 5 | 180（新增） |
| maximcuynat | P6 | 96 | 14 | 14.6% | 0 | 0 | 14 | – | 44 | 96（新增） |
| maximcuynat | P7 | 324 | 9 | 2.8% | 0 | 0 | 9 | 2 | 123 | 324（新增） |
| **maximcuynat** | 合计 | 600 | 42 | **7.0%** | 0 | 0 | 42 | 2 | 172 | 600 |
| kdeppaei | P5 | 328 | 64 | 19.5% | 3 | 1 | 62 | – | 23 | 0 |
| kdeppaei | P6 | 119 | 43 | 36.1% | 1 | 12 | 34 | – | 68 | 0 |
| kdeppaei | P7 | 357 | 62 | 17.4% | 2 | 0 | 61 | 51 | 145 | 53 |
| **kdeppaei** | 合计 | 804 | 169 | **21.0%** | 6 | 13 | 157 | 51 | 236 | 53 |

- maximcuynat：答案和文本零错误，错误全在节点（P5/P6 缺考点或考点错、语境题与句内题混标、P7 少量设问误判）。
- kdeppaei：P6 错误率最高（36%），主要是 G05–G07 篇章首句重复（12 题）、语境时态与句内时态混标、插入句子类型标错。P7 的跨篇问题集中：基线把一批单篇题误标为 CROSS_REF，又漏标了一批真正需要跨篇的题，最终全源只剩 33 道题主节点是 CROSS_REF。
- 文本类型（TX）误判共 18 个 kdeppaei bundle（例如 NOTICE 被判成 INSTRUCTIONS、E-MAIL 被判成 LETTER），按 bundle 修正，不计入题目错误率。

**最终残余错误率（估计）**：全部题目都已逐题过一遍。修正后在两源各随机抽 30 题复查（共 60 题），没有发现新错误，估计残余错误率两源都低于 3%，主要来自 §4 列出的主观判定。

## 3. 修正清单摘要

### 3.1 规则层（转换脚本）
`work/convert_maximcuynat.py`（kdeppaei 转换脚本也复用其中的场景词包、P7 题型规则和 p7_rule_diff）：
- **场景词包去假阳性**：
  - IT 区分大小写；
  - TECH_IT 和 ENVIRONMENT_ENERGY 词表收紧；
  - RETAIL 去掉单独的 shop、membership 和 customer；
  - MEDIA 去掉 publish* 和 subscri*（避免 “publish the rota”、软件订阅被误判）；
  - COMMUNITY 的 park 排除 car park、business park、industrial park；
  - SALES 的 deal 改为 business deal；
  - “in order to” 不再触发 ORDER_SHIP。
- **P5 规则**：
  - 纯连词表加入 if / once 等，介词/连词混合题归 CONNECTOR_MIX；
  - adj + prep 搭配（familiar / similar / satisfied / due / different / inclusive / accessible …）归 ADJ_PREP，be composed of 归 BE_PP_PREP；
  - that 从句中的动词原形归 SUBJUNCTIVE_DEMAND；
  - 分词后置修饰 / 分词状语区分开；
  - “more / highly + 空”归表语或名词前形容词；
  - to / 情态动词后的词汇题归 VO.LEX.VERB。
- **P7 题型规则**：
  - INFER_WHO 不再命中 “listed in the job posting”；
  - INTENT 加入 “imply / suggest when he writes ‘…’”；
  - INFER_NEXT 加入 “What will most likely happen …” 和 “What will X do next?”；
  - DETAIL_NUMBER 的时间词支持复数（months / days …）；
  - 计算题归 CALC_LOOKUP。
- **补 `difficulty_est`**（沿用 kdeppaei 的 p7_diff 思路）：
  - P5/P6 按考点节点的 target_band；
  - P7 用 p7_rule_diff：按篇章形态定基准，高阶设问 +1，跨篇 +1，篇幅 +1（单篇超过 250 词、多篇超过 550 词才加），三篇跨篇推断题可到 5。

`data/items_open_kdeppaei_convert.py`：
- p7_diff 接收跨篇参数；
- 修复 P6 篇章首句重复（G05 / G06 / G07 每个空前都重复了首句）：断句正则改为对 `cp + 'X'` 匹配，并排除 A.M. / Mr / Ms / Dr 等缩写；
- P6_TAG：短语动词题和名词词汇题归 CTX_VOCAB；分词后置修饰归 VERB_FORM + PARTICIPLE_MODIFIER。

### 3.2 逐题层（data/items_open_qc_fixes.json，166 条）
| 来源 | Part | 答案/选项 | 文本/TX | 节点 |
|---|---|---|---|---|
| kdeppaei | P5 | 3 | 1 | 24 |
| kdeppaei | P6 | 2 | 2（TX） | 32 |
| kdeppaei | P7 | 1 | 15（TX，bundle 级） | 57 |
| maximcuynat | P5 | – | – | 12 |
| maximcuynat | P6 | – | – | 14 |
| maximcuynat | P7 | – | – | 3 |

按 `reason` 字段可以找到每条的理由。代表性条目：
- **KDP-P5-095**：verified 和 verifies 都能成立，答案不唯一。题干加 “next week”，只剩 will verify 成立。
- **KDP-P5-156 / 220、KDP-P6-055、KDP-P6-G24-Q3、KDP-P7-R69-Q4**：单复数或 NOT 题存在第二个可选答案。改题干或替换干扰项，使答案唯一。
- **KDP-P5-131**：原句不构成让步，语义不通，改写了让步前提。
- **KD 跨篇逐组判定**：26 个多篇组逐组读完。误标 CROSS_REF 的题改回单篇题型（如 R40-Q3、R44-Q3、R59、R66 全组、R73-Q2）；真正需要跨篇的题补标 CROSS_REF.DOUBLE / TRIPLE（如 R92-Q4/Q5、R98-Q1/Q2/Q4、R99-Q1、R101-Q3、R102-Q3、R103-Q1/Q4、R104-Q1/Q3、R105-Q1–Q3、R108-Q3、R109-Q1/Q3/Q4）；需要计算的题补 CALC_LOOKUP。
- **maximcuynat**：
  - P6：语境时态与句内时态的区分（T01-139/142、T02-137、T04-143），并列动词误标成形容词（T04-131/136），接续副词题（T05-141）；
  - P7：漏标跨篇（T01-178、T01-200），局部原因题被误标为主旨题（T03-155）；
  - P5：12 道题缺考点或考点错（如 T03-112 approval 应为名词作宾语）。

## 4. 残余风险
1. **主观判定**：P6 “语境题 / 句内题”的划分，和 P7 “跨篇 / 单篇 + 常识”的边界（如 maximcuynat T02-T1-189、KD R106-Q1、R108-Q4），都是按“不读另一篇能不能唯一作答”这一口径判的，换个审核人可能有出入。
2. **场景标签仍是关键词规则**：已修掉明显的假阳性，但多义词仍有零星误标。例如 audit 被归到 FINANCE（质量审计）、register 被归到 EVENT（课程注册）、跨行业文本里的 delivery 被归到 ORDER_SHIP。场景标签只用于练习筛选，不影响判分。
3. **难度是规则估计**：maximcuynat 没有原始难度档，`difficulty_est` 完全来自规则；kdeppaei P7 跨篇状态改了的题重算了难度。两者都没有用真实作答数据校准，上线后应按正确率回调。
4. **基线依赖**：`work/qc/_baseline/` 不入库，只有本地复算错误率时才需要。`apply_qc_fixes.py` 遇到不存在的 id 会直接报错退出，所以以后上游题目一旦改 id，必须同步修改 fixes。
5. **qc_fixes 依赖转换输出的结构**：改选项时脚本会校验正确项文本没变。但如果上游改动了题干原文，题干修正会覆盖上游的新文本，需要人工留意。

## 5. 验收
- `python3 app/build.py --public`：通过（1511 题 / 262 bundles；6 套模考，每套 100 题）
- `node app/test/smoke.js`：输出 SMOKE OK
- `node app/test/fsrs.test.js`：16 passed, 0 failed
