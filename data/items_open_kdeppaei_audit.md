# items_open_kdeppaei 清洗报告（工作包 A1）

- 生成：2026-10-22；转换脚本：`python3 data/items_open_kdeppaei_convert.py`（需 node；本机已装 `opencc-python-reimplemented` 做繁→简）
- 产物：`data/items_open_kdeppaei.json`（公开池）、`data/items_open_kdeppaei_log.json`（剔除/丢弃明细、节点分布）
- 来源：github.com/kdeppaei/toeic-question-ocean 本地副本 `private_data/sources/github/kdeppaei_toeic-question-ocean/`（`banks/` 33 个题库文件 + `modules/` 2 个导入模块）

## 1. 许可结论
- 仓库 `LICENSE`：**MIT License, Copyright (c) 2026 Chun-Hsiung Luo**。允许复制、修改、再分发，条件只有保留版权与许可声明 → **作者原创题可以公开再分发**，留在 `data/`（公开池），不放 `private_data/items/`。
- 署名：meta.license 已写明；公开版署名页需列出 “kdeppaei/toeic-question-ocean — MIT © 2026 Chun-Hsiung Luo”（另附 MIT 全文）。
- MIT 只覆盖作者有权授权的内容。`modules/` 里的 ESL Lounge 题不是作者的，作者自己也标注 “由使用者提供的整理檔匯入”，MIT 管不到 → 全部剔除（见下）。

## 2. 剔除：ESL Lounge 336 题（依据与方法）
| 文件 | 内容 | 题数 |
|---|---|---|
| `modules/part5-exercise-guides.js` | `sourceName: "ESL Lounge Student"`，`sourceUrl` 指向 esl-lounge.com/student/toeic/toeic-045…054（Exercise 1–10） | P5 120 |
| `modules/reading-exercise-guides.js` → `"6"` | 同上，toeic-055…064 | P6 120（30 篇） |
| `modules/reading-exercise-guides.js` → `"7"` | 同上，toeic-065… | P7 96 |
| **合计** | | **336**（与维护者审计数一致） |

- 依据：两个模块在文件头自报来源 ESL Lounge Student 并逐练习给出原站 URL；ESL Lounge 条款禁止转载（背景见 `docs/research/external_sources_2026-10-22.md` §1）。
- 做法：**两个模块整体不读入**（不是逐题挑）。转换脚本仍会读一遍这两个模块，只为统计题数和建立 ESL 文本指纹。
- 残留检查：用 ESL 336 题的题干/篇章/完整句建 8-gram 指纹，比对 `banks/` 全部 805 道阅读题的题干和篇章 → **命中 0**（阈值：8-gram 覆盖 ≥30%）。即 `banks/` 里没有 ESL Lounge 文本的副本。
- `banks/` 按版本顺序执行（question-bank.js → v15…v29 → v2.10 → v3.0 → v3.1 标注 → v31…v50）得到 1,107 题，与维护者“剔除后 1,107 题”一致；其中 P1–P4 听力 302 题不在本包范围，未取。

## 3. 来源可疑题检查
- **跨库比对**：把 `private_data/` 下其他 25 个来源（ETS 1000 Vol.4、xdf1000、GrittingLeo、tasty_toeic、24,632 条外部 P5 参考库等）建 8-gram 索引，比对 805 道阅读题的题干和篇章：没有一篇篇章、没有一道 P5 题干达到 30% 覆盖；唯一命中的是 “What is the purpose of the e-mail?” 这类 P7 通用问法（各库都有，不算抄袭）。
- `work/item_audit.py`（导入题模式）对 24,632 条外部参考题 + items_v0/pilot 做近似重复检查：**无近似重复**。
- 来源标注：416 题有作者逐题声明（`sourceNote`/`sourceType:"original"`，如 “No third-party question text… was copied”）；**389 题（question-bank.js 236 + v15–v23 153）没有逐题来源字段**，但属于作者主库、无 `sourceUrl`/`user` 标记、跨库比对无命中 → 按 MIT 原创保留（判断依据写在这里，A2 抽查时可重点看这一批）。
- 结论：因来源可疑而剔除 **0 题**（ESL 336 题之外）。

## 4. 转换与丢弃
- 进入转换的阅读题：P5 328 / P6 120 / P7 357 = 805。
- **答案缺失/格式坏丢弃 1 题**：`P6-072`（选项 October/selected/unsafe/freshness 都是篇章原词、篇章里也没有对应空位，题目设计坏）。其余 804 题均为 4 个不重复选项 + 0–3 整数答案；151 题带 `answerAudit` 的全部与答案一致。
- P6 有 5 种原始结构，全部还原成单篇 + `[n]` 空位：①每题一段（同信头片段）→ 拼接；②同一篇 + 裸 `_____` → 按题干句定位；③篇章缺空（G17）→ 按题干把答案词换成空；④`(n) _____` / `_____ (n)`；⑤v2.8 逐题揭示（各题篇章只露本空）→ 取最完整一版并按上下文定位四个空。
- P7 多篇按标题行拆文档（DOCUMENT n / 全大写标题 / 独立短标题行），篇数与原类别（雙篇/三篇）全部吻合：单篇 55 / 双篇 32 / 三篇 18。
- **选项洗牌**：原库正确项高度集中在 A（P5 193/328、P6 104/120、P7 326/357），本 app 不在运行时洗牌 → 按题 id 定种子做确定性洗牌（`[1]–[4]` 位置题不洗），`choiceNotes` 随选项移动并转成 `distractor_reasons`（159 题）。洗牌后答案分布：P5 A90/B81/C74/D83，P6 A38/B25/C29/D27，P7 A90/B86/C93/D88。
- 解析：原繁体 `explanation` → 简体 `explain_zh`（804 题全有）；原中文翻译 → `translation_zh`（579 题）；v3.1 英文证据句 → `evidence_en`；原难度 400/600/800 → `difficulty_est` 2/3/4。
- form：不是整套题，切成 26 个迷你卷（KDP5-01…11 每卷 ≤30、KDP6-01…08 每卷 4 篇、KDP7-01…07 每卷 ≤54），每卷 <90 题，engine 不会当成模考卷；模考仍只有 MXT01–06。

## 5. 去重（pilot 107 + maximcuynat 600 + 自身）
- 规则：题干（P5）/ 篇章（P6、P7）文本归一化（小写、去空位标记和标点）后完全相同，或 3-gram Jaccard ≥ 0.8 → 剔除。
- 结果：**去重剔除 0 题**。最接近的一对 `KDP-P5-164` vs `MXC-T01-102`（J=0.60，同为 “By the time the auditors arrive next Monday, the finance team -------…” 句型，宾语和选项不同）→ 低于阈值，保留，记为已知相似。

## 6. 保留数
| | P5 | P6 | P7 | 合计 |
|---|---|---|---|---|
| 保留 | 328 | 119（30 篇） | 357（105 组） | **804** |

## 7. 节点分布（规则粗打，未人工校对）
- 方法：P5 按原中文类别 → 题型，再复用 `work/convert_maximcuynat.py` 的题干/选项规则细分 GR/VO 节点；P6 按选项形态判题型 + 句子插入位置；P7 按题干判题型（原 tag 若是整组标的，以题干为准）+ 文本类型 + 场景关键词。所有节点均存在于 graph_v1（脚本校验）。
- 用到 159 个节点，覆盖叶子 146/256（FD 7/14、GR 38/54、VO 40/77、TX 17/17、QT 43/67、ST 1/27）；比 pilot+maximcuynat 新增 10 个叶子（GR.SPECIAL.INVERSION_NEG / PARALLEL / ELLIPSIS、GR.NONFIN.PARTICIPLE_CLAUSE / PARTICIPLE_MODIFIER、GR.REL.NOUN_CLAUSE、GR.VERB.VERB_PATTERN、TX.INSTRUCTIONS、QT.P7X.DETAIL.INSTRUCTIONS、QT.P7X.NOT_TRUE.ARTICLE），三库合计覆盖叶子 198/256。
- 主节点：QT.P7.DETAIL 175，QT.P5.VERB_FORM 89，QT.P6.INDEPENDENT 86，QT.P5.WORD_FORM 54，QT.P7.REASON 54，QT.P5.PAIR_GRAMMAR 46，QT.P5.PREP 34，QT.P7.DETAIL_NUMBER 29，QT.P5.RELATIVE 27，QT.P5.VOCAB 27，QT.P5.CONNECTOR_MIX 25，QT.P7.INFERENCE 19，QT.P7X.CROSS_REF.TRIPLE 19，QT.P7X.CROSS_REF.DOUBLE 17，QT.P6.INSERTION 15，QT.P7.MAIN_PURPOSE 15，QT.P5.CONJ 11，QT.P6.CTX_VOCAB 9，QT.P7.NOT_TRUE 9，QT.P5.COMPARATIVE 8，QT.P5.PRONOUN 7，QT.P7.INFER_WHO 6，QT.P7.REQUEST_ACTION 6，QT.P6.CTX_TENSE 5，QT.P6.CTX_CONJ_ADV 4，QT.P7.TRUE_INDICATED 3，QT.P7.INFER_NEXT 2，QT.P7.INTENT 1，QT.P7.INSERTION 1，QT.P7.SYNONYM 1
- 语法节点前几名：GR.CONN.PREP_VS_CONJ 33，GR.POS.ADV_VERB 27，GR.VERB.CONDITIONAL_INVERSION 25，GR.NONFIN.PARTICIPLE_CLAUSE 23，GR.SPECIAL.INVERSION_NEG 22（这个库倒装/分词构句/假设语气题特别多，偏 800 分难度：原难度 800 档 452 题、600 档 300、400 档 52）。
- 文本类型（文档数）：NOTICE 55，EMAIL 46，INSTRUCTIONS 20，TEXT_MSG 18，ARTICLE 17，MEMO 10，WEB 7，INVOICE 6，SCHEDULE 6，AD 5，LETTER 4，JOB_POSTING 3，APP_FORM 3，REVIEW 2，CHAT 1。

## 8. 构建与测试
- `app/build.py`：`OPEN_SETS` 加一行 `('data/items_open_kdeppaei.json', 'open')`，与 maximcuynat 相同方式。
- `python3 app/build.py --public`：items 1511（pilot 107 + open 1404），skipped 0，bundles 262；模考卷仍为 MXT01–06。
- `node app/test/smoke.js`：SMOKE OK。

## 9. 遗留问题
- 导入题模式审题（`work/item_audit.py`）结构项“不通过” 336 题，全是现行考试版式规范，不是数据错误：多篇组 2–5 题而非 5 题、多篇组缺跨篇题（34 组）、题号不在 176–200 规定段、P6 早期 21 篇没有句子插入题、P6-G18 只剩 3 题。app 不依赖这些规范；如要拼成标准迷你卷，需另行挑组。
- 节点是规则粗打：P7 DETAIL/REASON 占比偏高，个别 P5 搭配题介词类型（如 familiar with 打成 VERB_PREP）不准 → A2 抽查。
- `explain_zh` 是作者原解析繁转简（台湾用语，例如 “介系詞→介系词”），不是 A3 要求的大白话版；`explain_en` 为空。
- 389 题没有逐题来源声明（见 §3），已比对无命中，A2 抽查时优先看。
