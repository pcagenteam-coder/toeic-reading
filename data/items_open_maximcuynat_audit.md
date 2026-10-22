# items_open_maximcuynat 审题报告（work/item_audit.py，导入题模式）

- 生成：2026-10-22；脚本：`python3 work/item_audit.py data/items_open_maximcuynat.json`（template_id 全空 → 自动进入导入题模式）
- 来源：maximcuynat/toeic-practice reading-test-1..6（MIT），转换脚本 work/convert_maximcuynat.py
- 题数 600（P5 180 / P6 96 / P7 324），bundle 114，6 套 MXT01–MXT06 各 100 题，跳过 0
- **不通过 0 题，全局问题 0**；警告 1286 条（导入题模式下编写规范类问题只记警告）
- 查重：本地参考题库（不入库，仅用于比对） 24632 条 + items_v0 + pilot 91 条，无近似重复（J≥0.5）也无部分相似（J≥0.3）

## 警告分类
- 超纲词（文章）：900
- 超纲词（选项）：229
- 超纲词（题干）：134
- 选项集合与：14
- 正确项明显最长：5
- P：2
- 连续相同答案：2

超纲词（NGSL+TSL 外）共 698 个不同词，涉及 336 个题/篇；高频：xample×84、bay×19、portal(派生自 port)×11、timber×11、narrator×10、calibration×9、crate×9、corridor×9、bays×8、exempt×7、crates×7、enquiries×7、levy×7、allowance(派生自 allow)×6、photographic×6、refurbishment×6、resurfacing×6、fortnight×6、overflow×6、coolant(派生自 cool)×6、shippers×6、curator×6、pallets×5、depot×5、motorway×5
说明：`xample` 是 `xxx@xxx.example` 邮箱/网址被切词的假阳性；原题为英式拼写/用词（enquiries、licence、fortnight、motorway、rota、centre），NGSL/TSL 未收，属正常第三方语料特征。

## 答案分布（按 form+题号顺序）
- P5: {'A': 49, 'B': 47, 'C': 49, 'D': 35, 'max_run': 2}
- P6: {'A': 31, 'B': 24, 'C': 21, 'D': 20, 'max_run': 5}
- P7: {'A': 70, 'B': 79, 'C': 80, 'D': 95, 'max_run': 6}
P6 最长连续同答案 5 题、P7 6 题（原题如此，未改动选项顺序）。

## 节点覆盖
- 用到 153 个不同节点（全部存在于 graph_v1，转换脚本已校验），覆盖叶子节点 140/256；比 pilot 新增 41 个节点；pilot+open 合计覆盖叶子 188/256
  - FD: 6/14
  - GR: 35/54
  - VO: 31/77
  - TX: 16/17
  - QT: 51/67
  - ST: 1/27
- 主节点分布：QT.P7.DETAIL 108，QT.P5.VERB_FORM 59，QT.P6.INDEPENDENT 55，QT.P5.WORD_FORM 52，QT.P7.MAIN_PURPOSE 42，QT.P7X.CROSS_REF.TRIPLE 40，QT.P7.INFERENCE 30，QT.P6.INSERTION 24，QT.P7.TRUE_INDICATED 23，QT.P7X.CROSS_REF.DOUBLE 23，QT.P5.VOCAB 18，QT.P5.PREP 17，QT.P7.REQUEST_ACTION 17，QT.P5.RELATIVE 8，QT.P6.CTX_TENSE 8，QT.P7.INTENT 8，QT.P6.CTX_VOCAB 7，QT.P5.PAIR_GRAMMAR 6，QT.P5.CONNECTOR_MIX 6，QT.P7.INFER_WHO 6，QT.P7.INSERTION 6，QT.P7.NOT_TRUE 6，QT.P7.DETAIL_NUMBER 6，QT.P5.CONJ 5，QT.P5.COMPARATIVE 5，QT.P7.SYNONYM 5，QT.P5.PRONOUN 4，QT.P7.REASON 4，QT.P6.CTX_CONJ_ADV 2
- 打标方式：原题 tags（word-form/verb-tense/detail/cross-reference…）定题型，再按题干/选项规则细分到 GR/VO/QT.P7X 节点，按关键词打 VO.SCENE；规则粗打，未人工校对。P7 主节点沿用 xdf 约定用 QT.P7.<题型> 分组节点，跨篇题主节点为 QT.P7X.CROSS_REF.DOUBLE/TRIPLE。

## 正确项明显最长 / 篇幅超范围（逐条）
- MXC-T01-149: 正确项明显最长 [5, 10, 4, 5]
- MXC-T01-182: 正确项明显最长 [4, 6, 4, 9]
- MXC-T04-161: 正确项明显最长 [10, 4, 5, 6]
- MXC-T04-173: 正确项明显最长 [4, 5, 10, 6]
- MXC-T05-198: 正确项明显最长 [4, 4, 4, 8]
- MXC-T05-P7-S2: P7 篇幅 159 词，超出 35–150（TX.TEXT_MSG）
- MXC-T06-P7-S6: P7 篇幅 167 词，超出 35–150（TX.TEXT_MSG）
- P6: 连续相同答案 5 题（>3）
- P7: 连续相同答案 6 题（>3）
