# TOEIC Reading 能力图谱 v1 · 摘要

生成：2026-10-21（`work/graph_v1/build.py`）。数据文件：`data/graph_v1.json`。适用：现行线性版（P5 30 / P6 16 / P7 54，75 分钟 100 题）。

## 1. 校验结果

- 节点总数：**305**（分组节点 49，叶节点 256）
- ID 唯一：通过；prereqs 全部存在：通过；无环（prereq 拓扑排序 305/305）：通过；parent 链无环：通过
- 分数段倒挂（前置节点段位高于后继）：0 处
- v0 的 20 个节点全部映射：通过
- 错误总数：0

## 2. 各层节点数

| 层 | 总数 | 其中分组 | 叶节点 | 说明 |
|---|---:|---:|---:|---|
| 基础层 (foundation) | 18 | 4 | 14 | 长句主干、阅读速度、指代与篇章逻辑、核心词与构词 |
| 语法层 (grammar) | 63 | 9 | 54 | 9 个语法大类、54 个叶考点（P5/P6） |
| 词汇层 (vocab) | 84 | 7 | 77 | 30 个场景词包 + 12 搭配 + 14 易混 + 12 同义替换 + 4 同词性词汇题 + 4 分段储备 + 职位部门 |
| 题型层 (qtype) | 85 | 18 | 67 | P5 11 型、P6 10 型、P7 15 型 + P7 设问×文本 45 个高发组合 |
| 文本类型层 (texttype) | 20 | 3 | 17 | 邮件、信件、备忘、通知、广告、招聘、文章、表格(发票/日程/申请表)、短信、群聊、网页、评价、说明书、多篇(双/三篇) |
| 应试技巧层 (strategy) | 35 | 8 | 27 | 时间、顺序、定位、排除、放弃、涂卡、复盘 7 组 |
| 合计 | 305 | 49 | 256 | |

## 3. exam_weight 说明与最高 30 个节点（考频类）

`exam_weight = min(1, 每份线性版试卷中该节点为决定性考点的估计题数 / 25)`。25 题≈满分权重，便于区分 P7 大题型与 P5 细考点。来源类型：
- `stat_composite`：多来源合并考频（exam_pattern_stats.json composite 区间中值）
- `stat_single`：单一来源考频
- `derived`：由上级考频按子类/文本份额拆分的估计
- `wordlist_freq`：TSL/BSL/NGSL 词频规模换算（非真题计数）
- `impact_estimate`：影响面估计（无直接题数的能力/技巧节点）
- `aggregate`：子节点汇总

注意：P7 设问×文本组合是设问类型的子集，与父节点题数重叠；技巧/基础节点的权重是影响面估计，不能与考频权重直接相加。

| # | ID | 名称 | 层 | 权重 | 估计题数/卷 | 来源类型 | 目标段 |
|---:|---|---|---|---:|---:|---|---:|
| 1 | `TX.TRIPLE` | 三篇组合 | 文本类型层 | 0.60 | 15 | derived | 700 |
| 2 | `QT.P7.DETAIL` | 细节题（5W1H） | 题型层 | 0.56 | 14 | stat_composite | 400 |
| 3 | `TX.EMAIL` | 电子邮件 | 文本类型层 | 0.56 | 14 | derived | 400 |
| 4 | `QT.P5.VOCAB` | 词汇题（同词性异义） | 题型层 | 0.42 | 10.5 | stat_composite | 400 |
| 5 | `TX.DOUBLE` | 双篇组合 | 文本类型层 | 0.40 | 10 | derived | 600 |
| 6 | `TX.ARTICLE` | 文章/新闻报道/新闻稿 | 文本类型层 | 0.36 | 9 | derived | 600 |
| 7 | `QT.P7.CROSS_REF` | 跨篇连锁题（多篇对照） | 题型层 | 0.32 | 8 | stat_composite | 700 |
| 8 | `QT.P7.INFERENCE` | 推断题（suggested/implied/most likely） | 题型层 | 0.32 | 8 | stat_composite | 600 |
| 9 | `QT.P5.WORD_FORM` | 词性题 | 题型层 | 0.28 | 7 | stat_composite | 400 |
| 10 | `QT.P7.MAIN_PURPOSE` | 主旨/目的题 | 题型层 | 0.24 | 6 | stat_composite | 400 |
| 11 | `QT.P7.TRUE_INDICATED` | 选项照合题（What is indicated/stated/true about…?） | 题型层 | 0.24 | 6 | stat_composite | 600 |
| 12 | `QT.P7X.CROSS_REF.TRIPLE` | 跨篇连锁题 × 三篇组合 | 题型层 | 0.24 | 6.0 | derived | 800 |
| 13 | `TX.NOTICE` | 通知/公告/政策 | 文本类型层 | 0.24 | 6 | derived | 400 |
| 14 | `QT.P6.CTX_VOCAB` | 语境词汇题 | 题型层 | 0.20 | 5 | stat_composite | 600 |
| 15 | `TX.LETTER` | 商务信件 | 文本类型层 | 0.20 | 5 | derived | 400 |
| 16 | `TX.WEB` | 网页 | 文本类型层 | 0.20 | 5 | derived | 600 |
| 17 | `QT.P6.INDEPENDENT` | 独立型语法/词性题 | 题型层 | 0.16 | 4 | stat_composite | 400 |
| 18 | `QT.P6.INSERTION` | 句子插入（文选择）题 | 题型层 | 0.16 | 4 | stat_single | 700 |
| 19 | `QT.P7.DETAIL_NUMBER` | 数字/日期/金额细节题 | 题型层 | 0.16 | 4 | derived | 400 |
| 20 | `TX.AD` | 广告（产品/服务/促销） | 文本类型层 | 0.16 | 4 | derived | 400 |
| 21 | `TX.CHAT` | 在线群聊（多人） | 文本类型层 | 0.16 | 4 | derived | 600 |
| 22 | `TX.MEMO` | 备忘录（内部通知） | 文本类型层 | 0.16 | 4 | derived | 400 |
| 23 | `VO.PARA.WORD_SYNONYM` | 单词同义替换（purchase→buy, complimentary→free） | 词汇层 | 0.16 | 4.0 | derived | 400 |
| 24 | `QT.P5.PREP` | 介词题 | 题型层 | 0.14 | 3.5 | stat_composite | 400 |
| 25 | `VO.LEX.ADJ` | 形容词词汇题 | 词汇层 | 0.14 | 3.5 | stat_single | 600 |
| 26 | `VO.LEX.ADV` | 副词词汇题 | 词汇层 | 0.14 | 3.5 | stat_single | 600 |
| 27 | `VO.LEX.NOUN` | 名词词汇题 | 词汇层 | 0.14 | 3.5 | stat_single | 400 |
| 28 | `VO.LEX.VERB` | 动词词汇题 | 词汇层 | 0.14 | 3.5 | stat_single | 400 |
| 29 | `QT.P5.VERB_FORM` | 动词形态题 | 题型层 | 0.12 | 3 | stat_composite | 400 |
| 30 | `QT.P7.SYNONYM` | 同义词题（closest in meaning） | 题型层 | 0.12 | 3 | stat_composite | 700 |

影响面估计类（基础/技巧，无直接题数，单独排序，不与上表混排）前 10：

| # | ID | 名称 | 权重 | 目标段 |
|---:|---|---|---:|---:|
| 1 | `FD.VOC.NGSL_CORE` | NGSL 核心通用词（约 2,800 词） | 0.70 | 400 |
| 2 | `FD.READ.SPEED_150` | 阅读速度 ≥150 词/分 | 0.60 | 600 |
| 3 | `ST.LOCATE.QUESTION_FIRST` | 先读题干再回文定位 | 0.60 | 400 |
| 4 | `ST.TIME.TOTAL_PLAN` | 整卷配速（P5 10–12 / P6 8–10 / P7 ≥53–55 分钟） | 0.60 | 600 |
| 5 | `FD.SENT.CORE` | 主谓宾/五种基本句型识别 | 0.55 | 400 |
| 6 | `FD.READ.SCAN` | 扫读（带关键词找信息） | 0.50 | 400 |
| 7 | `FD.READ.SPEED_200` | 阅读速度 ≥200 词/分 | 0.50 | 800 |
| 8 | `FD.SENT.LONG` | 长难句拆分（多层从句/后置修饰） | 0.50 | 700 |
| 9 | `QT.P5.IDENTIFY` | 看选项判题型（结构先行 vs 语境先行） | 0.50 | 400 |
| 10 | `ST.GIVEUP.CUTOFF_RULE` | 设定放弃线（卡住即猜，先跳后回） | 0.50 | 600 |


场景词包（wordlist_freq，词表常用度而非真题计数，单独排序）前 10：销售·合同·谈判(0.16)、出差·航班·行程(0.15)、住宿与酒店(0.14)、采购与报价(0.13)、客服·投诉·退换(0.12)、研发与产品(0.12)、财务·会计·预算(0.12)、企业经营：并购·扩张·业绩(0.12)、通信往来与商务套语(0.12)、餐饮·宴会·外烩(0.11)

## 4. 按目标分数段的推荐攻克顺序

算法：只取 target_band ≤ 目标段的非汇总节点（叶节点 + 自带题数的题型节点），按 prereqs 拓扑排序，同层可选时 exam_weight 高者优先。目标 500 取 400 段节点；每个更高目标列出“在上一档基础上新增”的节点（上一档内容默认已完成）。

### 目标 500（新增 79 个节点，累计 79）

重点：P5 词性/介词/代词/基础时态语态 + 高频场景词 + P7 单篇细节与先题后文、不留空。三篇连锁题可先放弃。

| 序 | ID | 名称 | 权重 | 段 |
|---:|---|---|---:|---:|
| 1 | `FD.VOC.NGSL_CORE` | NGSL 核心通用词（约 2,800 词） | 0.70 | 400 |
| 2 | `TX.EMAIL` | 电子邮件 | 0.56 | 400 |
| 3 | `FD.SENT.CORE` | 主谓宾/五种基本句型识别 | 0.55 | 400 |
| 4 | `QT.P5.IDENTIFY` | 看选项判题型（结构先行 vs 语境先行） | 0.50 | 400 |
| 5 | `FD.READ.CHUNK` | 意群切分顺读（斜线读法） | 0.45 | 400 |
| 6 | `FD.READ.SCAN` | 扫读（带关键词找信息） | 0.50 | 400 |
| 7 | `ST.LOCATE.QUESTION_FIRST` | 先读题干再回文定位 | 0.60 | 400 |
| 8 | `FD.READ.SKIM` | 略读（抓段落大意与篇章结构） | 0.40 | 400 |
| 9 | `FD.SENT.CLAUSE_COUNT` | 谓语与连接词计数 | 0.40 | 400 |
| 10 | `FD.SENT.MODIFIER_STRIP` | 剥离修饰语找主干 | 0.40 | 400 |
| 11 | `ST.GIVEUP.NO_BLANK` | 不留空（答错不扣分） | 0.40 | 400 |
| 12 | `ST.LOCATE.KEYWORD_SCAN` | 关键词选择（专名/数字/独特名词） | 0.40 | 400 |
| 13 | `FD.VOC.AFFIX` | 构词：后缀定词性、前缀定词义 | 0.35 | 400 |
| 14 | `QT.P6.CLASSIFY` | 独立型 vs 上下文型判别 | 0.35 | 400 |
| 15 | `ST.REVIEW.DIAGNOSE_BY_TYPE` | 按题型统计正确率诊断弱项 | 0.35 | 400 |
| 16 | `VO.BAND.B600` | 词汇储备 600 段 | 0.35 | 400 |
| 17 | `ST.REVIEW.VOCAB_FROM_ITEMS` | 从真题/错题中摘词（生词本） | 0.30 | 400 |
| 18 | `QT.P5.WORD_FORM` | 词性题 | 0.28 | 400 |
| 19 | `QT.P7.MAIN_PURPOSE` | 主旨/目的题 | 0.24 | 400 |
| 20 | `TX.NOTICE` | 通知/公告/政策 | 0.24 | 400 |
| 21 | `ST.BUBBLE.BATCH` | 分段涂卡（每页/每组集中涂） | 0.20 | 400 |
| 22 | `ST.BUBBLE.FINAL_MINUTES` | 最后几分钟统一猜涂 | 0.25 | 400 |
| 23 | `TX.LETTER` | 商务信件 | 0.20 | 400 |
| 24 | `QT.P6.INDEPENDENT` | 独立型语法/词性题 | 0.16 | 400 |
| 25 | `TX.AD` | 广告（产品/服务/促销） | 0.16 | 400 |
| 26 | `TX.MEMO` | 备忘录（内部通知） | 0.16 | 400 |
| 27 | `QT.P5.VOCAB` | 词汇题（同词性异义） | 0.42 | 400 |
| 28 | `VO.PARA.WORD_SYNONYM` | 单词同义替换（purchase→buy, complimentary→free） | 0.16 | 400 |
| 29 | `QT.P7.DETAIL` | 细节题（5W1H） | 0.56 | 400 |
| 30 | `VO.SCENE.TRAVEL_FLIGHT` | 出差·航班·行程 | 0.15 | 400 |
| 31 | `QT.P5.PREP` | 介词题 | 0.14 | 400 |
| 32 | `VO.LEX.NOUN` | 名词词汇题 | 0.14 | 400 |
| 33 | `VO.LEX.VERB` | 动词词汇题 | 0.14 | 400 |
| 34 | `VO.SCENE.HOTEL_LODGING` | 住宿与酒店 | 0.14 | 400 |
| 35 | `VO.SCENE.PURCHASE_QUOTE` | 采购与报价 | 0.13 | 400 |
| 36 | `VO.SCENE.CUSTOMER_SERVICE` | 客服·投诉·退换 | 0.12 | 400 |
| 37 | `QT.P5.VERB_FORM` | 动词形态题 | 0.12 | 400 |
| 38 | `QT.P7X.DETAIL.EMAIL` | 细节题 × 电子邮件 | 0.12 | 400 |
| 39 | `TX.SCHEDULE` | 日程/行程/议程表 | 0.12 | 400 |
| 40 | `VO.SCENE.CORRESPONDENCE` | 通信往来与商务套语 | 0.12 | 400 |
| 41 | `VO.SCENE.DINING_CATERING` | 餐饮·宴会·外烩 | 0.11 | 400 |
| 42 | `VO.SCENE.OFFICE_ADMIN` | 办公行政与文书 | 0.11 | 400 |
| 43 | `VO.SCENE.RETAIL_SHOPPING` | 零售·购物·会员 | 0.11 | 400 |
| 44 | `VO.SCENE.RECRUIT` | 招聘与求职 | 0.11 | 400 |
| 45 | `VO.SCENE.BANK_PAYMENT` | 银行·支付·账单 | 0.10 | 400 |
| 46 | `VO.SCENE.ORDER_SHIP` | 订单·配送·物流 | 0.10 | 400 |
| 47 | `QT.P5.PRONOUN` | 代词/限定词题 | 0.10 | 400 |
| 48 | `QT.P7X.MAIN_PURPOSE.EMAIL` | 主旨/目的题 × 电子邮件 | 0.10 | 400 |
| 49 | `TX.INVOICE` | 发票/收据/订单确认 | 0.10 | 400 |
| 50 | `TX.TEXT_MSG` | 短信链（2 人） | 0.10 | 400 |
| 51 | `VO.SCENE.TRANSPORT_COMMUTE` | 城市交通·通勤·停车 | 0.10 | 400 |
| 52 | `VO.SCENE.MEETING_SCHEDULE` | 会议与日程安排 | 0.09 | 400 |
| 53 | `QT.P7.REQUEST_ACTION` | 要求/建议行动题（What is X asked to do?） | 0.08 | 400 |
| 54 | `GR.POS.NOUN_AFTER_DET` | 限定词/冠词/所有格后填名词 | 0.06 | 400 |
| 55 | `QT.P7X.DETAIL.NOTICE` | 细节题 × 通知/公告/政策 | 0.06 | 400 |
| 56 | `VO.PARA.NUMBER_TIME` | 数字/时间换算（two weeks→14 days, every Monday→weekly） | 0.06 | 400 |
| 57 | `QT.P7.DETAIL_NUMBER` | 数字/日期/金额细节题 | 0.16 | 400 |
| 58 | `QT.P7X.DETAIL_NUMBER.FORM` | 数字/日期/金额细节题 × 表格类 | 0.08 | 400 |
| 59 | `QT.P7X.REQUEST_ACTION.EMAIL` | 要求/建议行动题 × 电子邮件 | 0.05 | 400 |
| 60 | `GR.CONN.PREP_VS_CONJ` | 介词 vs 连词（despite/although, during/while, because of/because） | 0.04 | 400 |
| 61 | `GR.POS.ADV_VERB` | 修饰动词的副词 | 0.04 | 400 |
| 62 | `GR.POS.ADJ_BEFORE_NOUN` | 名词前填形容词 | 0.04 | 400 |
| 63 | `QT.P7X.DETAIL.TEXT_MSG` | 细节题 × 短信链 | 0.04 | 400 |
| 64 | `QT.P7X.DETAIL_NUMBER.SCHEDULE` | 数字/日期/金额细节题 × 日程/行程/议程表 | 0.04 | 400 |
| 65 | `GR.CONN.PREP_TIME` | 时间介词（at/on/in/by/until/within/during/for） | 0.04 | 400 |
| 66 | `GR.PRON.CASE` | 人称代词格（主格/宾格/所有格） | 0.04 | 400 |
| 67 | `GR.POS.NOUN_AFTER_PREP` | 介词后填名词（或动名词） | 0.03 | 400 |
| 68 | `GR.VERB.TENSE_SIMPLE` | 一般时态与时间状语 | 0.03 | 400 |
| 69 | `GR.VERB.VOICE_PASSIVE` | 主动 vs 被动语态 | 0.04 | 400 |
| 70 | `QT.P7X.MAIN_PURPOSE.LETTER` | 主旨/目的题 × 商务信件 | 0.03 | 400 |
| 71 | `QT.P7X.MAIN_PURPOSE.NOTICE` | 主旨/目的题 × 通知/公告/政策 | 0.03 | 400 |
| 72 | `GR.POS.NOUN_SUBJ_OBJ` | 主语/宾语位置填名词 | 0.03 | 400 |
| 73 | `GR.VERB.AGREE_SV` | 主谓一致 | 0.03 | 400 |
| 74 | `QT.P7X.MAIN_PURPOSE.MEMO` | 主旨/目的题 × 备忘录 | 0.02 | 400 |
| 75 | `QT.P7X.REQUEST_ACTION.MEMO` | 要求/建议行动题 × 备忘录 | 0.02 | 400 |
| 76 | `GR.CONN.PREP_PLACE` | 地点/方位介词（at/in/on/across/throughout/along） | 0.02 | 400 |
| 77 | `QT.P7X.MAIN_PURPOSE.AD` | 主旨/目的题 × 广告 | 0.01 | 400 |
| 78 | `GR.CONN.CONJ_COORD` | 并列连词（and/but/or/yet/so） | 0.01 | 400 |
| 79 | `GR.VERB.MODAL_BASE` | 情态动词/助动词 + 动词原形 | 0.01 | 400 |

### 目标 600（新增 114 个节点，累计 193）

重点：P5 连词/非谓语/搭配、P6 语境题、P7 照合/NOT/原因题、整卷配速与放弃线。

| 序 | ID | 名称 | 权重 | 段 |
|---:|---|---|---:|---:|
| 1 | `FD.READ.SPEED_150` | 阅读速度 ≥150 词/分 | 0.60 | 600 |
| 2 | `ST.TIME.TOTAL_PLAN` | 整卷配速（P5 10–12 / P6 8–10 / P7 ≥53–55 分钟） | 0.60 | 600 |
| 3 | `ST.REVIEW.TIMED_MOCK` | 限时整卷模考（含涂卡） | 0.50 | 600 |
| 4 | `ST.TIME.PER_ITEM_P5` | P5 单题限时（词性 5–15 秒 / 词汇 ≤30 秒） | 0.45 | 600 |
| 5 | `ST.GIVEUP.CUTOFF_RULE` | 设定放弃线（卡住即猜，先跳后回） | 0.50 | 600 |
| 6 | `TX.ARTICLE` | 文章/新闻报道/新闻稿 | 0.36 | 600 |
| 7 | `ST.LOCATE.QUESTION_ORDER` | 题序≈文序、两题一组读 | 0.35 | 600 |
| 8 | `ST.REVIEW.ERROR_CAUSE_LOG` | 错题按原因分类（词汇/语法/定位/时间） | 0.40 | 600 |
| 9 | `TX.DOUBLE` | 双篇组合 | 0.40 | 600 |
| 10 | `FD.READ.UNKNOWN_WORD` | 生词不停（语境猜义/跳读） | 0.30 | 600 |
| 11 | `ST.GIVEUP.TARGET_BASED` | 按目标分数决定放弃哪些题 | 0.30 | 600 |
| 12 | `VO.BAND.B730` | 词汇储备 730 段 | 0.30 | 600 |
| 13 | `ST.REVIEW.AUDIO_SHADOW` | 用题目音频复习阅读（听写/跟读） | 0.25 | 600 |
| 14 | `ST.REVIEW.SPEED_REPEAT` | 测时→复读同一篇提速 | 0.25 | 600 |
| 15 | `TX.WEB` | 网页 | 0.20 | 600 |
| 16 | `ST.LOCATE.PARAPHRASE_MATCH` | 按改写而非原词匹配 | 0.50 | 600 |
| 17 | `ST.ELIM.OPTIONS` | 逐项排除法 | 0.40 | 600 |
| 18 | `ST.ELIM.TRAP_TYPES` | 错误选项套路（未提及/部分正确/张冠李戴/过度推断/照搬原词） | 0.45 | 600 |
| 19 | `ST.REVIEW.EXPLAIN_DISTRACTORS` | 逐项说明错误选项为何错 | 0.35 | 600 |
| 20 | `QT.P6.CTX_VOCAB` | 语境词汇题 | 0.20 | 600 |
| 21 | `VO.SCENE.SALES_DEAL` | 销售·合同·谈判 | 0.16 | 600 |
| 22 | `VO.LEX.ADJ` | 形容词词汇题 | 0.14 | 600 |
| 23 | `VO.LEX.ADV` | 副词词汇题 | 0.14 | 600 |
| 24 | `VO.PARA.GENERALIZE` | 具体→概括（laptops, printers → office equipment） | 0.12 | 600 |
| 25 | `QT.P7.TRUE_INDICATED` | 选项照合题（What is indicated/stated/true about…?） | 0.24 | 600 |
| 26 | `VO.SCENE.FINANCE_ACCOUNT` | 财务·会计·预算 | 0.12 | 600 |
| 27 | `VO.TITLES_DEPTS` | 部门与职位名称（accounting, HR, CFO, receptionist） | 0.20 | 600 |
| 28 | `VO.SCENE.INVENTORY_PRODUCTION` | 库存·生产·供应链 | 0.11 | 600 |
| 29 | `VO.SCENE.EVENT_CONFERENCE` | 活动·会展·研讨会 | 0.11 | 600 |
| 30 | `VO.SCENE.TECH_IT` | IT 与技术支持 | 0.10 | 600 |
| 31 | `TX.APP_FORM` | 申请表/问卷/评价表 | 0.10 | 600 |
| 32 | `TX.CHAT` | 在线群聊（多人） | 0.16 | 600 |
| 33 | `VO.SCENE.CONSTRUCTION_MAINT` | 施工·维修·设施管理 | 0.09 | 600 |
| 34 | `VO.SCENE.HR_TRAINING` | 人事：培训·晋升·福利·考核 | 0.09 | 600 |
| 35 | `VO.SCENE.COMMUNITY_CULTURE` | 社区·文化·公共活动 | 0.08 | 600 |
| 36 | `QT.P7.NOT_TRUE` | NOT/TRUE 题 | 0.08 | 600 |
| 37 | `QT.P7X.DETAIL.ARTICLE` | 细节题 × 文章/新闻报道/新闻稿 | 0.08 | 600 |
| 38 | `QT.P7X.DETAIL.DOUBLE` | 细节题 × 双篇组合 | 0.08 | 600 |
| 39 | `QT.P7X.MAIN_PURPOSE.MULTI` | 主旨/目的题 × 多篇文本 | 0.08 | 600 |
| 40 | `TX.JOB_POSTING` | 招聘广告 | 0.08 | 600 |
| 41 | `TX.REVIEW` | 评价/顾客反馈 | 0.08 | 600 |
| 42 | `VO.PARA.SUMMARY_NOMINAL` | 句子→抽象名词概括（a ceremony to honor… → an awards event） | 0.08 | 600 |
| 43 | `QT.P7.INFERENCE` | 推断题（suggested/implied/most likely） | 0.32 | 600 |
| 44 | `QT.P7.INFER_WHO` | 推断身份/读者对象题 | 0.08 | 600 |
| 45 | `VO.PARA.WORD_TO_PHRASE` | 单词↔短语（postpone→put off, inspect→look over） | 0.08 | 600 |
| 46 | `VO.SCENE.HEALTH_MEDICAL` | 医疗·保健·预约 | 0.08 | 600 |
| 47 | `VO.SCENE.SAFETY` | 安全规定与检查 | 0.07 | 600 |
| 48 | `VO.SCENE.MARKETING_AD` | 市场推广与广告 | 0.07 | 600 |
| 49 | `QT.P7X.DETAIL.WEB` | 细节题 × 网页 | 0.06 | 600 |
| 50 | `QT.P7X.TRUE_INDICATED.ARTICLE` | 选项照合题 × 文章/新闻报道/新闻稿 | 0.06 | 600 |
| 51 | `QT.P7.CALC_LOOKUP` | 计算/表格对照题 | 0.06 | 600 |
| 52 | `VO.PARA.POS_SHIFT` | 词性转换（decide→decision, expand→expansion） | 0.06 | 600 |
| 53 | `VO.COLLO.VERB_NOUN` | 动词+名词搭配 | 0.05 | 600 |
| 54 | `QT.P5.CONNECTOR_MIX` | 介词/连词/副词混排题 | 0.06 | 600 |
| 55 | `GR.CONN.CONJ_ADVERBIAL` | 从属连词（although/unless/once/as soon as/provided that/so that） | 0.04 | 600 |
| 56 | `QT.P5.CONJ` | 连词题 | 0.06 | 600 |
| 57 | `QT.P7X.MAIN_PURPOSE.ARTICLE` | 主旨/目的题 × 文章/新闻报道/新闻稿 | 0.04 | 600 |
| 58 | `QT.P7X.TRUE_INDICATED.WEB` | 选项照合题 × 网页 | 0.04 | 600 |
| 59 | `VO.COLLO.ADJ_NOUN` | 形容词+名词搭配 | 0.04 | 600 |
| 60 | `VO.PARA.CAUSE_EFFECT` | 因果改写（due to→because, result in→cause） | 0.04 | 600 |
| 61 | `QT.P7.REASON` | 原因题（Why…?） | 0.08 | 600 |
| 62 | `GR.CONN.PREP_MEANING` | 按语义选介词（despite/due to/regarding/except/prior to） | 0.06 | 600 |
| 63 | `FD.READ.REFERENCE` | 指代追踪（代词/this/such/the former） | 0.45 | 600 |
| 64 | `FD.READ.DISCOURSE` | 篇章逻辑信号（转折/因果/追加/举例/顺序） | 0.40 | 600 |
| 65 | `GR.CONN.CONJ_ADVERB` | 接续副词（however/therefore/in addition/otherwise） | 0.05 | 600 |
| 66 | `QT.P6.CTX_CONJ_ADV` | 接续副词题 | 0.04 | 600 |
| 67 | `QT.P7X.CALC_LOOKUP.INVOICE` | 计算/表格对照题 × 发票/收据/订单确认 | 0.03 | 600 |
| 68 | `QT.P7X.NOT_TRUE.AD` | NOT/TRUE 题 × 广告 | 0.03 | 600 |
| 69 | `QT.P7X.TRUE_INDICATED.REVIEW` | 选项照合题 × 评价/顾客反馈 | 0.03 | 600 |
| 70 | `VO.COLLO.VERB_PREP` | 动词+介词（comply with/adhere to/account for/depend on） | 0.03 | 600 |
| 71 | `GR.POS.ADV_ADJ` | 修饰形容词/分词/副词的副词 | 0.03 | 600 |
| 72 | `QT.P6.CTX_PRONOUN` | 语境代词题 | 0.03 | 600 |
| 73 | `QT.P7X.TRUE_INDICATED.JOB_POSTING` | 选项照合题 × 招聘广告 | 0.03 | 600 |
| 74 | `VO.COLLO.FIXED_PHRASE` | 固定短语（in charge of/on short notice/at no extra cost） | 0.03 | 600 |
| 75 | `GR.POS.ADJ_COMPLEMENT` | be/系动词/宾补位置填形容词 | 0.02 | 600 |
| 76 | `GR.POS.NOUN_PERSON_THING` | 人名词 vs 事物名词 | 0.02 | 600 |
| 77 | `GR.POS.VERB_SLOT` | 缺谓语时填限定动词 | 0.02 | 600 |
| 78 | `QT.P7X.INFER_WHO.JOB_POSTING` | 推断身份/读者对象题 × 招聘广告 | 0.02 | 600 |
| 79 | `QT.P7X.INFER_WHO.NOTICE` | 推断身份/读者对象题 × 通知/公告/政策 | 0.02 | 600 |
| 80 | `VO.COLLO.ADJ_PREP` | 形容词+介词（eligible for/responsible for/aware of/familiar with） | 0.02 | 600 |
| 81 | `GR.POS.ADV_AUX_SLOT` | 助动词与动词之间的副词 | 0.02 | 600 |
| 82 | `GR.VERB.TENSE_PERFECT` | 完成时（since/for/by the time/already） | 0.02 | 600 |
| 83 | `QT.P6.CTX_TENSE` | 语境时态题 | 0.08 | 600 |
| 84 | `QT.P5.COMPARATIVE` | 比较题 | 0.02 | 600 |
| 85 | `QT.P5.RELATIVE` | 关系词题 | 0.02 | 600 |
| 86 | `QT.P7X.CALC_LOOKUP.SCHEDULE` | 计算/表格对照题 × 日程/行程/议程表 | 0.02 | 600 |
| 87 | `VO.COLLO.NOUN_PREP` | 名词+介词（demand for/access to/increase in/solution to） | 0.02 | 600 |
| 88 | `VO.COLLO.PHRASAL_VERB` | 短语动词（carry out/set up/fill out/turn in） | 0.02 | 600 |
| 89 | `VO.COLLO.TIME_EXPR` | 时间表达（in advance/ahead of schedule/until further notice） | 0.02 | 600 |
| 90 | `VO.CONF.ADV_TIME` | 时间副词（already/yet/still/soon/recently/once） | 0.02 | 600 |
| 91 | `VO.CONF.FORM_NOUN` | 同根名词（attendance/attendee/attendant, product/production/productivity） | 0.02 | 600 |
| 92 | `GR.NONFIN.GERUND` | 动名词（介词后/只接 -ing 的词） | 0.02 | 600 |
| 93 | `GR.NONFIN.TO_INF` | to 不定式（目的/只接 to do 的词） | 0.02 | 600 |
| 94 | `GR.POS.NOUN_COUNT` | 可数/不可数与单复数 | 0.02 | 600 |
| 95 | `GR.PRON.DETERMINER_QUANT` | 数量限定词（each/every/all/most/few/little） | 0.02 | 600 |
| 96 | `GR.PRON.REFLEXIVE` | 反身代词（by oneself / 强调） | 0.02 | 600 |
| 97 | `GR.REL.REL_PRONOUN` | 关系代词（who/which/that/whose） | 0.02 | 600 |
| 98 | `QT.P7X.NOT_TRUE.JOB_POSTING` | NOT/TRUE 题 × 招聘广告 | 0.02 | 600 |
| 99 | `VO.COLLO.BE_PP_PREP` | be + 过去分词 + 介词（be equipped with/be located in/be committed to） | 0.02 | 600 |
| 100 | `VO.COLLO.NUM_EXPR` | 数量与范围表达（up to/as many as/no later than/at least） | 0.02 | 600 |
| 101 | `VO.CONF.PREP_LOOKALIKE` | 形近/义近介词（beside/besides, among/between, by/until, within/during） | 0.02 | 600 |
| 102 | `GR.COMP.COMPARATIVE` | 比较级与强调（much/even/far + -er） | 0.01 | 600 |
| 103 | `GR.NONFIN.PARTICIPLE_ADJ` | 情感/状态分词形容词（-ing vs -ed） | 0.01 | 600 |
| 104 | `GR.VERB.AGREE_QUANT` | 数量表达与一致（each/a number of/the number of） | 0.01 | 600 |
| 105 | `GR.VERB.TENSE_FUTURE_CLAUSE` | 时间/条件从句以现在代将来 | 0.01 | 600 |
| 106 | `VO.COLLO.REQUEST_EXPR` | 请求/提醒/告知句式（be advised that/kindly/feel free to） | 0.01 | 600 |
| 107 | `VO.CONF.FORM_VERB` | 形近动词（affect/effect, rise/raise, lie/lay, ensure/insure） | 0.01 | 600 |
| 108 | `VO.CONF.QUANT_WORDS` | 数量名词与修饰（amount/number, few/little, a variety of） | 0.01 | 600 |
| 109 | `GR.COMP.SUPERLATIVE` | 最高级（the most…of/in/ever） | 0.01 | 600 |
| 110 | `GR.CONN.CONJ_CORRELATIVE` | 成对连词（both–and/either–or/neither–nor/not only–but also/whether–or） | 0.02 | 600 |
| 111 | `QT.P5.PAIR_GRAMMAR` | 成对表达/语法搭配/数量一致题 | 0.02 | 600 |
| 112 | `GR.PRON.POSSESSIVE_PRONOUN` | 名词性物主代词（mine/theirs/ours） | 0.01 | 600 |
| 113 | `VO.CONF.PREFIX_NEG` | 否定/反义前缀（un-/in-/dis-/non-/mis-） | 0.01 | 600 |
| 114 | `VO.CONF.SO_SUCH_TOO` | so/such/too/enough | 0.01 | 600 |

### 目标 700（新增 62 个节点，累计 255）

重点：P6/P7 句子插入、推断、意图、同义词、双篇连锁；阅读速度 150 wpm 以上；错误选项套路。

| 序 | ID | 名称 | 权重 | 段 |
|---:|---|---|---:|---:|
| 1 | `ST.TIME.PER_SET_P7` | P7 每题/每组用时目标 | 0.45 | 700 |
| 2 | `ST.TIME.CHECKPOINTS` | 看表检查点（如 147 题时剩 X 分钟） | 0.35 | 700 |
| 3 | `TX.TRIPLE` | 三篇组合 | 0.60 | 700 |
| 4 | `ST.ORDER.PART_SEQUENCE` | Part 间顺序（按序 vs 先做 P7） | 0.20 | 700 |
| 5 | `VO.BAND.B860` | 词汇储备 860 段 | 0.20 | 700 |
| 6 | `ST.ELIM.SCOPE` | 范围陷阱（过宽/过窄/绝对化） | 0.30 | 700 |
| 7 | `QT.P7X.DETAIL.TRIPLE` | 细节题 × 三篇组合 | 0.12 | 700 |
| 8 | `VO.SCENE.RND_PRODUCT` | 研发与产品 | 0.12 | 700 |
| 9 | `VO.SCENE.CORP_STRATEGY` | 企业经营：并购·扩张·业绩 | 0.12 | 700 |
| 10 | `VO.SCENE.REAL_ESTATE` | 物业·租赁·办公空间 | 0.11 | 700 |
| 11 | `VO.SCENE.MEDIA_PUBLISH` | 媒体·出版·报道 | 0.11 | 700 |
| 12 | `QT.P7.CROSS_REF` | 跨篇连锁题（多篇对照） | 0.32 | 700 |
| 13 | `ST.ORDER.WITHIN_P7` | P7 内部顺序（先易后难，多篇不整块留后） | 0.35 | 700 |
| 14 | `ST.LOCATE.DEPTH_BY_QTYPE` | 按题型决定读多少 | 0.30 | 700 |
| 15 | `ST.ORDER.HARD_ITEMS_LAST` | 难题后做（插入句/NOT 题延后） | 0.30 | 700 |
| 16 | `QT.P7X.CROSS_REF.DOUBLE` | 跨篇连锁题 × 双篇组合 | 0.12 | 700 |
| 17 | `QT.P7.INTENT` | 意图题（引号中的话） | 0.08 | 700 |
| 18 | `QT.P7X.INFERENCE.ARTICLE` | 推断题 × 文章/新闻报道/新闻稿 | 0.08 | 700 |
| 19 | `QT.P7X.INFERENCE.EMAIL` | 推断题 × 电子邮件 | 0.08 | 700 |
| 20 | `VO.SCENE.ENVIRONMENT_ENERGY` | 环境·能源·可持续 | 0.07 | 700 |
| 21 | `QT.P7.INFER_NEXT` | 推断下一步/将来行为题 | 0.06 | 700 |
| 22 | `TX.INSTRUCTIONS` | 说明书/保修条款/操作指南 | 0.06 | 700 |
| 23 | `QT.P7X.INTENT.CHAT` | 意图题 × 在线群聊 | 0.04 | 700 |
| 24 | `QT.P7X.INTENT.TEXT_MSG` | 意图题 × 短信链 | 0.04 | 700 |
| 25 | `VO.PARA.ROLE_REFERENCE` | 人物/机构代称（the accountant→a finance employee, Brix Co.→the firm） | 0.04 | 700 |
| 26 | `VO.PARA.SPECIFY` | 概括→具体（按条件推回具体实例） | 0.04 | 700 |
| 27 | `VO.PARA.VOICE_SHIFT` | 主被动/视角转换 | 0.04 | 700 |
| 28 | `QT.P6.INSERTION` | 句子插入（文选择）题 | 0.16 | 700 |
| 29 | `QT.P7.INSERTION` | 句子位置题（[1]–[4]） | 0.08 | 700 |
| 30 | `QT.P6.INS_TRANSITION` | 插入句：段中衔接句 | 0.07 | 700 |
| 31 | `QT.P6.INS_CLOSING` | 插入句：结尾/行动号召句 | 0.05 | 700 |
| 32 | `QT.P7X.INSERTION.ARTICLE` | 句子位置题 × 文章/新闻报道/新闻稿 | 0.05 | 700 |
| 33 | `QT.P6.INS_OPENING` | 插入句：段首/引入句 | 0.04 | 700 |
| 34 | `VO.COLLO.ADV_VERB_ADJ` | 副词+动词/形容词搭配 | 0.04 | 700 |
| 35 | `QT.P7X.DETAIL.INSTRUCTIONS` | 细节题 × 说明书/保修条款/操作指南 | 0.03 | 700 |
| 36 | `VO.CONF.BUSINESS_SENSE` | 常用词的商务义（address/issue/term/figure/branch/party/run） | 0.03 | 700 |
| 37 | `GR.CONN.PREP_PHRASE_MULTI` | 复合介词（in addition to/on behalf of/in accordance with） | 0.02 | 700 |
| 38 | `QT.P7X.INFERENCE.REVIEW` | 推断题 × 评价/顾客反馈 | 0.02 | 700 |
| 39 | `QT.P7X.INFER_NEXT.CHAT` | 推断下一步/将来行为题 × 在线群聊 | 0.02 | 700 |
| 40 | `VO.CONF.ADV_FOCUS` | 焦点/程度副词（only/just/even/also/too/either/nearly/almost） | 0.02 | 700 |
| 41 | `VO.CONF.POLYSEMY_CONTEXT` | 多义词按语境取义 | 0.02 | 700 |
| 42 | `QT.P7.SYNONYM` | 同义词题（closest in meaning） | 0.12 | 700 |
| 43 | `QT.P7X.SYNONYM.MULTI` | 同义词题 × 多篇文本 | 0.05 | 700 |
| 44 | `QT.P7X.SYNONYM.ARTICLE` | 同义词题 × 文章/新闻报道/新闻稿 | 0.04 | 700 |
| 45 | `QT.P7X.SYNONYM.EMAIL` | 同义词题 × 电子邮件 | 0.03 | 700 |
| 46 | `GR.NONFIN.PARTICIPLE_MODIFIER` | 分词作后置/前置修饰（主动 -ing / 被动 -ed） | 0.02 | 700 |
| 47 | `QT.P7X.INFER_WHO.CHAT` | 推断身份/读者对象题 × 在线群聊 | 0.02 | 700 |
| 48 | `QT.P7X.INSERTION.EMAIL` | 句子位置题 × 电子邮件 | 0.02 | 700 |
| 49 | `QT.P7X.NOT_TRUE.ARTICLE` | NOT/TRUE 题 × 文章/新闻报道/新闻稿 | 0.02 | 700 |
| 50 | `VO.CONF.FORM_ADJ` | 同根形容词（considerable/considerate, economic/economical, reliable/reliant） | 0.02 | 700 |
| 51 | `VO.CONF.SYN_ADJ` | 近义形容词（available/accessible, complimentary/free, possible/potential） | 0.02 | 700 |
| 52 | `VO.CONF.SYN_NOUN` | 近义名词（fee/fare/charge/rate, client/patron/customer） | 0.02 | 700 |
| 53 | `VO.CONF.SYN_VERB_PATTERN` | 近义动词的句型差异（inform sb of / explain sth to sb / discuss sth） | 0.02 | 700 |
| 54 | `GR.POS.NOUN_COMPOUND` | 复合名词（名词+名词） | 0.02 | 700 |
| 55 | `FD.SENT.LONG` | 长难句拆分（多层从句/后置修饰） | 0.50 | 700 |
| 56 | `GR.VERB.VERB_PATTERN` | 动词句型（及物/不及物/双宾/宾补） | 0.02 | 700 |
| 57 | `GR.POS.ADV_SENTENCE` | 修饰全句的副词/句首副词 | 0.01 | 700 |
| 58 | `GR.PRON.INDEFINITE` | 不定代词（another/the other/others/one） | 0.01 | 700 |
| 59 | `GR.REL.NOUN_CLAUSE` | 名词从句连接词（whether/if/that/wh-） | 0.01 | 700 |
| 60 | `QT.P7X.INSERTION.LETTER` | 句子位置题 × 商务信件 | 0.01 | 700 |
| 61 | `GR.SPECIAL.PARALLEL` | 并列结构一致 | 0.01 | 700 |
| 62 | `GR.COMP.EQUATIVE` | 原级比较（as…as / as many as） | 0.00 | 700 |

### 目标 800（新增 13 个节点，累计 268）

重点：三篇连锁、200 wpm、假设倒装/虚拟、低频易混与改写（否定改写、概括改写）。

| 序 | ID | 名称 | 权重 | 段 |
|---:|---|---|---:|---:|
| 1 | `FD.READ.SPEED_200` | 阅读速度 ≥200 词/分 | 0.50 | 800 |
| 2 | `VO.BAND.B990` | 词汇储备 990 段 | 0.10 | 800 |
| 3 | `VO.SCENE.LEGAL_COMPLIANCE` | 法务与合规 | 0.09 | 800 |
| 4 | `QT.P7X.CROSS_REF.TRIPLE` | 跨篇连锁题 × 三篇组合 | 0.24 | 800 |
| 5 | `VO.PARA.NEGATION_SHIFT` | 否定/反义改写（not until→only after, unable→cannot） | 0.04 | 800 |
| 6 | `VO.PARA.IDIOM_EXPR` | 习语/惯用说法改写（hit the shelves→go on sale） | 0.02 | 800 |
| 7 | `GR.NONFIN.PARTICIPLE_CLAUSE` | 分词构句与连词+分词 | 0.01 | 800 |
| 8 | `GR.VERB.CONDITIONAL_INVERSION` | 假设语气与省略 if 倒装 | 0.01 | 800 |
| 9 | `GR.PRON.DEMONSTRATIVE` | 指示代词（those who / that of） | 0.01 | 800 |
| 10 | `GR.SPECIAL.ELLIPSIS` | 省略结构（as requested/if necessary/when needed） | 0.01 | 800 |
| 11 | `GR.VERB.SUBJUNCTIVE_DEMAND` | 要求/建议类 that 从句用原形 | 0.01 | 800 |
| 12 | `GR.REL.REL_ADVERB` | 关系副词（where/when）与 介词+which | 0.00 | 800 |
| 13 | `GR.REL.REL_WHAT` | what vs that（先行词有无） | 0.00 | 800 |

### 目标 900（新增 2 个节点，累计 270）

重点：低频语法收尾（复合关系词、倒装），P5 全对与 P7 留检查时间。

| 序 | ID | 名称 | 权重 | 段 |
|---:|---|---|---:|---:|
| 1 | `GR.REL.COMPOUND_REL` | 复合关系词（whoever/whatever/however） | 0.00 | 900 |
| 2 | `GR.SPECIAL.INVERSION_NEG` | 否定/only 前置倒装 | 0.00 | 900 |

## 5. 新旧制差异与对节点的影响

本图谱只以**现行线性版**为准：日本/韩国 2016-05-29 起、中国等其他公开考试 2018-04 起（exam_pattern_stats.json：toeic.xdf.cn/201803/10761795.html），至 2026 年未变。

| 项目 | 旧制（2006–2016/2018） | 现行线性版 | 对图谱节点的影响 |
|---|---|---|---|
| Part 5 | 40 题 | 30 题 | 题型不变，各考点题数按 30 题折算；旧书 P5 比例可参考，但绝对题数要乘 0.75 |
| Part 6 | 12 题（3 篇×4，只填词/短语） | 16 题（4 篇×4，每篇 1 道句子插入） | 新增 `QT.P6.INSERTION` 及 3 个位置子类；`QT.P6.CLASSIFY` 上下文型比重上升；旧书无句子插入训练 |
| Part 7 | 48 题（单篇 28 + 双篇 4 组 20） | 54 题（单篇 29 + 双篇 2 组 10 + 三篇 3 组 15） | 新增 `TX.TRIPLE`、`QT.P7X.CROSS_REF.TRIPLE`；新增文本 `TX.TEXT_MSG`、`TX.CHAT`；新增题型 `QT.P7.INTENT`、`QT.P7.INSERTION` |
| 时长 | 75 分钟 100 题 | 75 分钟 100 题 | 每题可用时间不变，但 P7 文本量增加 → `ST.TIME.TOTAL_PLAN` 中 P7 需 ≥53–55 分钟，`FD.READ.SPEED_*` 权重上调 |
| 改错题 | 2006 年前旧版 Part 6 为改错（Error Recognition） | 无 | 不收录任何改错节点 |

书目层面：`books_taxonomy.md` 标注了旧制书目（新东方/群言 2010–2011 年引进书、北语 2010 官方指南、外研社 2009 Tactics for TOEIC）。这些书的语法单元仍可用于 GR 层，但其 Part 6/7 章节缺少句子插入、三篇、短信/群聊、意图题，相关节点只采用新制来源。

**多阶段自适应版（MSA）**：ETS 另有 TOEIC L&R Multistage Adaptive 版本，阅读部分约 37 分钟 45 题（Unit 1 25 题 + Unit 2 20 题，Unit 2 难度由 Unit 1 表现决定），题型与线性版相同，主要用于机构/在线考试（ETS 4-skills Examinee Handbook 2025-08：https://www.ets.org/content/dam/ets-org/de/pdfs/toeic/toeic-4-skills-tests-examinee-handbook.pdf ；ETS Global：https://www.etsglobal.org/us/en/blog/news/adaptative-toeic-test）。对图谱的影响：节点与 prereqs 通用；`est_items`/`exam_weight` 按线性版 100 题计，MSA 题数约为其 45%，时间策略节点（`ST.TIME.*`、`ST.BUBBLE.*`）不适用于在线 MSA（无答题卡）。

## 6. v0 → v1 映射

| v0 | v0 名称 | v1 节点 |
|---|---|---|
| G1 | 词性判断 | `FD.VOC.AFFIX`, `GR.POS`, `GR.POS.NOUN_AFTER_DET`, `GR.POS.NOUN_AFTER_PREP`, `GR.POS.NOUN_SUBJ_OBJ`, `GR.POS.NOUN_COUNT`, `GR.POS.NOUN_PERSON_THING`, `GR.POS.NOUN_COMPOUND` 等 18 个 |
| G2 | 形容词/副词位置 | `GR.POS.ADJ_BEFORE_NOUN`, `GR.POS.ADJ_COMPLEMENT`, `GR.POS.ADV_VERB`, `GR.POS.ADV_ADJ`, `GR.POS.ADV_AUX_SLOT`, `GR.POS.ADV_SENTENCE` |
| G3 | 主谓一致 | `GR.VERB.AGREE_SV`, `GR.VERB.AGREE_QUANT`, `QT.P5.VERB_FORM` |
| G4 | 时态与时间状语 | `GR.VERB.TENSE_SIMPLE`, `GR.VERB.TENSE_PERFECT`, `GR.VERB.TENSE_FUTURE_CLAUSE`, `GR.VERB.MODAL_BASE`, `GR.VERB.SUBJUNCTIVE_DEMAND`, `GR.VERB.CONDITIONAL_INVERSION`, `QT.P5.VERB_FORM`, `QT.P6.CTX_TENSE` |
| G5 | 被动语态 | `GR.VERB.VOICE_PASSIVE`, `GR.VERB.VERB_PATTERN`, `GR.NONFIN.PARTICIPLE_MODIFIER`, `GR.NONFIN.PARTICIPLE_CLAUSE`, `GR.NONFIN.PARTICIPLE_ADJ`, `QT.P5.VERB_FORM` |
| G6 | 关系代词 | `GR.REL`, `GR.REL.REL_PRONOUN`, `GR.REL.REL_ADVERB`, `GR.REL.REL_WHAT`, `GR.REL.NOUN_CLAUSE`, `GR.REL.COMPOUND_REL`, `QT.P5.RELATIVE` |
| G7 | 连词/介词辨析 | `GR.CONN`, `GR.CONN.PREP_TIME`, `GR.CONN.PREP_PLACE`, `GR.CONN.PREP_MEANING`, `GR.CONN.PREP_PHRASE_MULTI`, `GR.CONN.PREP_VS_CONJ`, `GR.CONN.CONJ_ADVERBIAL`, `GR.CONN.CONJ_COORD` 等 14 个 |
| G8 | 代词格 | `GR.PRON`, `GR.PRON.CASE`, `GR.PRON.POSSESSIVE_PRONOUN`, `GR.PRON.REFLEXIVE`, `GR.PRON.DETERMINER_QUANT`, `GR.PRON.INDEFINITE`, `GR.PRON.DEMONSTRATIVE`, `QT.P5.PRONOUN` 等 9 个 |
| V1 | 会议与日程词汇 | `VO.SCENE.MEETING_SCHEDULE`, `VO.LEX`, `QT.P5.VOCAB` |
| V2 | 人事与招聘词汇 | `VO.SCENE.RECRUIT`, `VO.SCENE.HR_TRAINING`, `VO.LEX`, `QT.P5.VOCAB` |
| V3 | 采购与报价词汇 | `VO.SCENE.PURCHASE_QUOTE`, `VO.SCENE.ORDER_SHIP`, `VO.LEX`, `QT.P5.VOCAB` |
| V4 | 易混词 | `VO.CONF`, `VO.CONF.FORM_ADJ`, `VO.CONF.FORM_NOUN`, `VO.CONF.FORM_VERB`, `VO.CONF.SYN_VERB_PATTERN`, `VO.CONF.SYN_NOUN`, `VO.CONF.SYN_ADJ`, `VO.CONF.ADV_TIME` 等 20 个 |
| R1 | 细节定位 | `QT.P7.DETAIL`, `QT.P7.DETAIL_NUMBER`, `QT.P7.REASON`, `QT.P7.REQUEST_ACTION`, `QT.P7.TRUE_INDICATED`, `QT.P7.CALC_LOOKUP`, `QT.P7X.DETAIL.EMAIL`, `QT.P7X.DETAIL.ARTICLE` 等 24 个 |
| R2 | 同义替换识别 | `VO.PARA`, `VO.PARA.WORD_SYNONYM`, `VO.PARA.WORD_TO_PHRASE`, `VO.PARA.GENERALIZE`, `VO.PARA.SPECIFY`, `VO.PARA.POS_SHIFT`, `VO.PARA.VOICE_SHIFT`, `VO.PARA.NEGATION_SHIFT` 等 18 个 |
| R3 | 推断题 | `QT.P7.INFERENCE`, `QT.P7.INFER_WHO`, `QT.P7.INFER_NEXT`, `QT.P7.INTENT`, `QT.P7X.INFERENCE.ARTICLE`, `QT.P7X.INFERENCE.EMAIL`, `QT.P7X.INTENT.TEXT_MSG`, `QT.P7X.INTENT.CHAT` 等 12 个 |
| R4 | NOT/TRUE 题 | `QT.P7.TRUE_INDICATED`, `QT.P7.NOT_TRUE`, `QT.P7X.NOT_TRUE.AD`, `QT.P7X.NOT_TRUE.ARTICLE`, `QT.P7X.NOT_TRUE.JOB_POSTING`, `ST.ELIM.OPTIONS`, `ST.ELIM.TRAP_TYPES` |
| R5 | 多篇跨文定位 | `TX.MULTI`, `TX.DOUBLE`, `TX.TRIPLE`, `QT.P7.CROSS_REF`, `QT.P7X.CROSS_REF.DOUBLE`, `QT.P7X.CROSS_REF.TRIPLE` |
| R6 | 句子插入 | `QT.P6`, `QT.P6.CLASSIFY`, `QT.P6.INSERTION`, `QT.P6.INS_OPENING`, `QT.P6.INS_TRANSITION`, `QT.P6.INS_CLOSING`, `QT.P7.INSERTION`, `QT.P7X.INSERTION.ARTICLE` 等 10 个 |
| S1 | 限时阅读速度 | `FD.READ.SPEED_150`, `FD.READ.SPEED_200`, `QT.P5.IDENTIFY`, `ST`, `ST.TIME`, `ST.TIME.TOTAL_PLAN`, `ST.TIME.PER_ITEM_P5`, `ST.TIME.PER_SET_P7` 等 12 个 |
| S2 | 放弃与时间分配 | `ST`, `ST.GIVEUP`, `ST.TIME.TOTAL_PLAN`, `ST.ORDER.WITHIN_P7`, `ST.ORDER.HARD_ITEMS_LAST`, `ST.GIVEUP.NO_BLANK`, `ST.GIVEUP.CUTOFF_RULE`, `ST.GIVEUP.TARGET_BASED` 等 9 个 |

## 7. 已知局限

- 考频来自公开博客/题库统计与书目目录，样本小且口径不一；`derived` 类题数是按比例拆分的估计，应用 App 实测作答数据（如 EdNet 匿名标签）回校。
- 场景词包按主题人工聚类，种子词在 TSL/BSL 命中有限（两表是 NGSL 的补充，基础场景词多在 NGSL）；词包权重反映语料常用度，不是真题计数。
- target_band 为经验判断（参考 haradaeigo、IIBC methods07、金のフレーズ分段），非官方标准。
