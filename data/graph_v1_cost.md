# graph_v1 排程字段（C2）：learn_cost_min / must_for_band

生成：`python3 data/graph_v1_cost_build.py` → `data/graph_v1_cost.json`（幂等，纯规则）。不改 `graph_v1.json` 本体，`app/build.py` 构建时合并。

## 1. 遗留节点（strategies_v2 changelog 记的 suggested_new_node）
| id | 名称 | 层/父 | 前置 | 段 | 权重 |
|---|---|---|---|---|---|
| `ST.ORDER.TEXT_TYPE_TRIAGE` | 按文体决定做不做（跳篇不跳序） | strategy / ST.ORDER | ST.GIVEUP.NO_BLANK, FD.READ.SKIM | 400 | 0.30（影响面估计） |
| `ST.REVIEW.PARAPHRASE_LOG` | 记“改写对” | strategy / ST.REVIEW（delivery=engine） | ST.REVIEW.VOCAB_FROM_ITEMS, VO.PARA.WORD_SYNONYM | 400 | 0.30（影响面估计） |

build.py 把 S2-P7-05 / S2-P7-12（`suggested_new_node`）的绑定节点补上这两个 id。节点总数 305 → 307（叶 258）。

## 2. learn_cost_min（分钟，从 0 练到本档目标掌握度，含练习与复习）
| 类型 | 规则 |
|---|---|
| 语法叶节点 | 25 × 段位系数（400:1.0 / 600:1.3 / 700:1.6 / 800:2.0 / 900:2.4） |
| P5 题型 | 15 × 题型段位系数（400:1.0 / 600:1.15 / 700:1.3 / 800:1.5）；IDENTIFY 10；VOCAB 40 |
| P6 题型 | 20 × 系数；插入句子类 15 × 系数；INSERTION 45；CLASSIFY 10 |
| P7 设问类型 | 30 × 系数；CROSS_REF 45 |
| P7 设问×文本组合 | 单篇 12、双篇 20、三篇/多篇 30 × 系数（父题型已学，只算增量）；跨篇对照双 40 / 三 60 |
| 文本类型 | 15 × 系数（表格类 12）；双篇 40、三篇 60 |
| 场景词包 / 搭配易混 / 改写类型 / 同词性词汇 | 45 / 25 / 15 × 系数；VO.LEX.* 30 |
| 分段词表 | B600 900、B730 1200、B860 1500、B990 1800 |
| 技巧节点 | 10（规则卡读懂 + 2–3 次练习中用上）；整卷配速 30、限时模考 90、复读/跟读 60、错因分类 20 |
| 基础能力 | 句型 30–40、长难句 90、意群 60、扫读/略读 30、阅读提速 600/900、NGSL 核心 1500、词缀 60 |

分组节点的值是“作为练习目标时自身的成本”（如题目直接挂在 `QT.P7.DETAIL` 上），不含子节点。
计划器用 剩余成本 = learn_cost_min × max(0.1, 缺口比例)，学不动再 ×3。各档 must 叶节点总成本：≤500 约 72 小时、600 约 140、730 约 201、860+ 约 256（含词表/阅读提速等长期项；计划器“约 X 小时”只算有题可练的考点）。

## 3. must_for_band
基础：节点 `target_band` 起累积（400→≤500、600→600、700→730、800→860+；900 段任何档都不必须）。再按 strategies_v2 冲突裁决覆盖（覆盖优先于一切）：

| 规则 | 移出 |
|---|---|
| C8 / S2-P5-03（600 档语法只练两样） | ≤500/600：语法只留 `GR.POS.*` 与介词/连词（PREP_TIME/PLACE/MEANING、PREP_VS_CONJ、CONJ_ADVERBIAL/COORD/ADVERB）；QT.P5.VERB_FORM/PRONOUN/RELATIVE/COMPARATIVE/PAIR_GRAMMAR、QT.P6.CTX_TENSE/CTX_PRONOUN 移到 730 |
| C3 / S2-P6-02 | ≤500/600：P6 插入句（及 P7 句子位置题）直接涂 |
| C2 / S2-ALL-02（终点线） | ≤500/600：多篇（TX.MULTI/DOUBLE/TRIPLE、`QT.P7X.*.{DOUBLE,TRIPLE,MULTI}`、QT.P7.CROSS_REF）；730：三篇相关 |
| S2-P7-05（跳篇不跳序） | ≤500/600：TX.ARTICLE 与 `QT.P7X.*.ARTICLE` |

提入：某档最小技巧集（`min_sets`，delivery=user）条目绑定的 qtype/strategy/skill 节点，若基础段位只高一档、且前置未被移出，提入该档（例：S2-P7-09 把 QT.P7.SYNONYM 提入 600）。
前置闭包：must 节点的叶前置也列为 must；被移出的前置或 ≥300 分钟的长期能力（如阅读提速）记为豁免，写在 `must_note`。
分组节点：任一子节点必须 → 该档必须。

结果（叶节点）：≤500 84、600 166、730 242、860+ 256。每个节点的覆盖原因见 json 的 `must_note`。
