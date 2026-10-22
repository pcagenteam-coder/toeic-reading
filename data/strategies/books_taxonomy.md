# 主流托业阅读备考书 · 考点切分与跨书合并（books_taxonomy）

更新：2026-10-21。个人非商用备考研究。依据：`data/strategies/books.json`（21 本书目录概要 + 54 条技巧）、出版社/书店公开目录与简介（本轮新核对了下列页面），未使用任何盗版内容。下文“考点清单”中的 `ID` 对应 `data/graph_v1.json` 节点。

本轮新核对的公开页面：
- 해커스 토익 Reading 最新改订版（hackersbook.com/book/detail/216）：2020-01-02 出版，800 页，ISBN 9788965423348；结构 = Part5/6 Grammar + Part5/6 Vocabulary + Part6/7 Reading（题型别/文本别）+ 4 回模考。
- ETS 토익 정기시험 기출입문서 RC 免费讲座目录（ybmbooks.com/reader/free_class_toeic_primer_rc.asp）：完整 20 讲标题（见 B07）。
- TOEIC L&R テスト 文法問題 でる1000問（kinokuniya 9784866390833，アスク 2017/06 增補版）：7 章题数（见 B16）。
- 托业阅读专项突破（queshu.com/book/10698313，群言 2010.8）、托业阅读全真模拟1000题（dogwood.com.cn，群言 2011-04）、托业词汇词根+联想记忆法（dushu.com，群言 2013-07）、托业考试官方指南（dushu.com，北语 2010-09）、新托业考试官方指南·听力阅读（books.com.tw CN10236961，外研社 2009-09，含 28 单元目录）。

## 0. 新旧制判定规则

图谱只以**现行线性版**为准（日韩 2016-05-29、中国等 2018-04 起；P5 30 / P6 16 含 4 道句子插入 / P7 54 含三篇、短信/群聊、意图题、插入句；75 分钟 100 题；2026 年未变）。

- **旧制**：按 2006–2016/2018 版（P5 40 / P6 12 / P7 48，无三篇、无短信群聊、无意图题与插入句）编写的书。2006 年前更早版本另有改错题（Error Recognition）。
- 判定依据：出版日期早于该书所在市场的改版日期，或目录缺少新制题型。
- 处理：旧制书的 **P5 语法/词汇单元**仍可作为考点来源（P5 题型未变，只是题数 40→30）；其 **P6/P7 章节**中的旧制特有安排（P6 只填词、P7 只有双篇等）**不进图谱**。本 21 本中没有发现含改错题的书。

| 标记 | 含义 |
|---|---|
| 🟢 新制 | 按现行版编写（已核实或目录含新制题型） |
| 🟡 新制（推断） | 出版年未核实，但目录/简介含新制题型或为改版后系列 |
| ⚪ 不受影响 | 只覆盖 P5 或纯词汇，题型新旧制一致 |
| 🔴 旧制 | 按 2006 版编写，P6/P7 部分不进图谱 |

## 1. 逐本切分摘要

### 韩国（KR）

**B01 해커스 토익 Reading（David Cho，기본서）🟢**（2020-01 最新改订版，2023 再改）
- 切分：文法 20 章 + 词汇 12 章 + Part6 2 章 + Part7 20 章 + 4 回模考 + 进阶诊断测试与分级学习计划。
- Part5/6：“토익 Grammar”按语法范畴分章（句子结构→词性→动词→非谓语→代词→介/连/关系词→特殊句式）；Part6“지문 흐름 예상（预测文章流向）”策略。
- Part7：题型别（主旨、细节、NOT、推断、意图、句子位置、同义词）+ 文本别 + 连锁文本。
- 对应节点：GR 全部大类、VO.COLLO/VO.CONF、QT.P6.*、QT.P7.*、TX.*。

**B02 해커스 토익 Part 7 집중공략 777 🟡**
- 切分：Part7 文本 9 类出题模式 × 设问 7 类策略 + 模考。按“文本类型 × 设问类型”二维组织，是本图谱 QT.P7X.* 组合节点的主要参照。

**B03 시나공 토익 Reading（구원）🟡**（ISBN 9791159242083）
- 切分：Part5/6 按“不翻译就能解（结构题）/需要翻译（语义题）”两大类；Part7 按设问 7 类 + 文本 9 类。
- 特点：把“解题路径”而不是“语法范畴”放在第一层 → 对应 QT.P5.IDENTIFY、FD.SENT.CLAUSE_COUNT。

**B04 시나공 토익 출제순위 파트 5&6（구원）🟡**
- 切分：按出题频率（“每月出”→“两年一次”）排序语法点；词汇按词性；Part6 单独一章。
- 对应：图谱 exam_weight 排序思路（P5-14“按频率学”）。

**B05 시나공 토익 파트 5,6 실전문제집（강진오）🟢**（yes24 2024 上架）
- 切分：20 套 P5/6 实战，导言“파트별 유형 및 전략”；P5&6 15 分钟内完成的时间目标。

**B06 YBM 전략토익 RC 🟡**
- 切分：Part5&6 12 单元；Part7 设问 8 类 + 文本 6 类。

**B07 ETS 토익 정기시험 기출입문서 RC（YBM）🟢**（由官方免费讲座目录还原，已核对）
- Part5 14 单元：01 문장구조 / 02 명사 / 03 대명사 / 04 형용사와 부사 / 05 비교 / 06 동사의 형태와 수 일치 / 07 시제 / 08 능동태와 수동태 / 09 to부정사와 동명사 / 10 분사 / 11 전치사 / 12 등위접속사와 명사절 접속사 / 13 부사절 접속사 / 14 관계사 + 부사 어휘。
- Part6 5 类：01 동사 시제 고르기 / 02 대명사 고르기 / 03 어휘 고르기 / 04 접속부사 고르기 / 05 문장 넣기。
- Part7 3 章：패러프레이징（改写）导入 → Ch01 질문 유형 / Ch02 지문 유형 / Ch03 연계지문。
- 意义：ETS 官方授权入门书的 P6 五分法与本图谱 QT.P6.CTX_TENSE / CTX_PRONOUN / CTX_VOCAB / CTX_CONJ_ADV / INSERTION 一一对应；“改写”被放在 P7 最前，对应 VO.PARA 作为 P7 题型前置。

**B08 ETS 토익 정기시험 기출문제집 1000 RC（Vol.4/5）🟢**
- 仅 10 套真题+解析，无技巧章节；用作模考（ST.REVIEW.TIMED_MOCK）。

### 中国大陆（CN）

**B09 TOEIC 托业阅读专项突破（新东方指定，群言 2010.8，韩国 T 计划语言协会编）🔴 旧制**
- 目录：Part5/6 Grammar & Vocabulary 7 单元——名词和冠词 / 动词的种类·主动与被动 / 主谓一致·时态与虚拟语气 / 不定式·动名词·分词 / 形容词·副词·比较级 / 代词·关系代词 / 介词·连词；“常用搭配”“核心词汇 Training 1–8”。
- Part7：只按 7 种文本切分——Memorandum / Letter / E-mail & Fax / Notice & Announcement / Advertisement / Article & Report / Others。
- 旧制特征：2010 年出版、简介称“新托业”（=2006 版）；无句子插入、三篇、短信/群聊、意图题；“E-mail & Fax”中的传真文本现已少见。
- 进图谱：P5 语法单元（与 GR.* 对应）；不进：其 P6/P7 体例。

**B10 托业阅读全真模拟1000题（新东方大愚，群言 2011-04，Jim Lee 等，引进自韩国多乐园）🔴 旧制**
- 10 套模拟题，无技巧章节；简介强调正确答案特征与错项陷阱（→ST.ELIM.TRAP_TYPES 的旁证）。整套题型为旧制，不作为模考材料推荐。

**B11 托业词汇词根+联想记忆法（俞敏洪，群言 2013-07）⚪（旧制时期出版，词表本身不受影响）**
- Word List（重点/认知词汇）+ 语法精要；对应 FD.VOC.AFFIX、VO.BAND.*。其中“语法精要”若涉及题型说明按旧制，不采用。

**B12 托业考试官方指南（ETS，北语 2010-09）🔴 旧制**
- 2 套官方题 + 题型范例（P5 Incomplete Sentences / P6 Text Completion / P7 Reading Comprehension），为 2006 版格式；不作为现行格式参考。

**B13 新托业考试官方指南·听力 阅读（Grant Trew，外研社 2009-09；原书 Tactics for TOEIC）🔴 旧制**
- 28 单元螺旋式，每单元一个 Part 一个技能焦点。阅读相关单元（已核对目录）：
  - P5：U5 词性识别+时间利用 / U12 动名词与不定式+短语动词 / U19 前缀后缀 / U26 代词；
  - P6：U6 用上下文选动词形式和词义 / U13 形容词与副词词性 / U20 动词形式（将来、完成）/ U27 介词与连词；
  - P7：U7 先扫读题目决定先答哪些 / U14 语境词义题+推断 / U21 NOT 题及人名数字日期题 / U28 图表、表格、表单与双篇。
- 旧制特征：P7 最多到双篇；P6 无句子插入；无短信/群聊/意图题。
- 进图谱：P5 技能焦点（GR.POS、GR.NONFIN、FD.VOC.AFFIX、GR.PRON）与 P7 通用技巧（ST.LOCATE.QUESTION_FIRST、QT.P7.NOT_TRUE、QT.P7.SYNONYM）；不进：其 P6/P7 题量与体例。

### 日本（JP）

**B14 公式TOEIC Listening & Reading 問題集 1–13（IIBC）🟢**
- 每册 2 套官方题 + 解答解析（误答解说、Words & Phrases）+ 朗读音频；无技巧章节。→ ST.REVIEW.TIMED_MOCK、ST.REVIEW.AUDIO_SHADOW、ST.REVIEW.EXPLAIN_DISTRACTORS。

**B15 公式TOEIC L&R Part 7 速読演習（IIBC）🟢**
- 速读基础训练 3 法（斜线读、跟音频读、测时复读）+ 文本类型 9 单元 × 5 步 + Part7 实战 54 题。→ FD.READ.CHUNK、ST.REVIEW.SPEED_REPEAT、FD.READ.UNKNOWN_WORD、TX.*。

**B16 TOEIC L&R テスト 文法問題 でる1000問（TEX 加藤，アスク 2017/06 增補版）⚪**（已核对目录）
- 只收 P5 文法题（不含词汇题和 P6），7 章题数：①品詞 334 ②動詞 102 ③前置詞 or 接続詞 67 ④代名詞 37 ⑤前置詞 56 ⑥関係詞 16 ⑦ペア表現・語法・数・比較 47（合计 659 题）+ 文法模試 13 套（各 30 题，按现行 P5 题量）。
- 书内配比：词性 50.7%、动词 15.5%、介/连 10.2%、介词 8.5%、代词 5.6%、关系词 2.4%、其他 7.1%。与真题考频（词性占 P5 语法类约 40%）相比，**本书刻意加重词性题**；图谱 exam_weight 采用考频统计，不采用书内配比。
- 对象 500 分以上；“狭く深く（窄而深）”学法。

**B17 TOEIC L&R TEST 出る問特急 金の文法（TEX 加藤，朝日新聞出版）⚪**
- 同でる1000問 7 类题型；82 条“金のルール”。

**B18 TOEIC L&R TEST 出る単特急 金のフレーズ（TEX 加藤）⚪**
- 按目标分数段 600/730/860/990 切分 1000 词 + 补充专题；每条短语 ≤7 词。→ VO.BAND.B600–B990、VO.COLLO。

**B19 1駅1題 TOEIC L&R TEST 文法特急（花田徹也）⚪**
- 按分数段（550/730/900+）分章；第 0 章讲两种解题路径（構文先行型 / 文脈先行型）。→ QT.P5.IDENTIFY；target_band 参照。

**B20 TOEIC L&R テスト 究極のゼミ Part 5&6（ヒロ前田，アルク）🟢**
- Part5 按题型 6 类；Part6 分 独立型 / 文脈型（时态·词汇·代词·接续副词）/ 文選択（句子插入）。估计只靠本句可解的 P6 题约 4 题。→ QT.P6.CLASSIFY 及其子节点。

**B21 TOEIC L&R テスト 究極のゼミ Part 7（ヒロ前田，アルク）🟢**
- 15 次ゼミ：设问类型别 + パラフレーズ（改写）+ 错误选项识别；题型参照官方 Abilities Measured。→ VO.PARA.*、ST.ELIM.TRAP_TYPES、ST.REVIEW.DIAGNOSE_BY_TYPE。

### 新旧制一览

| 状态 | 书目 |
|---|---|
| 🟢 新制 | B01 HK、B05 SNP56、B07 ETSIN、B08 ETS1000、B14 IIBCQ、B15 IIBCP7、B20 K56、B21 K7 |
| 🟡 新制（推断） | B02 HK777、B03 SN、B04 SN56、B06 YST |
| ⚪ 不受影响 | B11 XDFVOC（词表）、B16 DERU、B17 KB、B18 KF、B19 BT |
| 🔴 旧制 | B09 XDFRD（2010）、B10 XDF1000（2011）、B12 XDFOG（2010）、B13 FLTRP（2009） |

结论：中文市场能找到的这几本主流书都是旧制时期出版（2009–2013），现行格式的 P6 句子插入、三篇、短信群聊与意图题，只能以韩日新制书和 ETS/IIBC 官方材料为依据。

## 2. 跨书合并：Part 5 细粒度考点清单

“书目”列 = books.json 中能对应该技巧的书（下限；多数只看到目录）。† = 旧制书（只采用其 P5 内容）。

| 考点 | 图谱 ID | 现行考频 | 覆盖书目 |
|---|---|---|---|
| 看选项判题型（结构先行/语境先行） | QT.P5.IDENTIFY | — | K56, DERU, BT, SN |
| 词性：位置定词性（名词/形容词/副词/动词位） | GR.POS.* / QT.P5.WORD_FORM | 20–27%（6–8 题） | SN, HK, DERU, KB, K56, YST, ETSIN, FLTRP†, XDFRD† |
| 名词细分：可数/不可数、人 vs 事物、复合名词 | GR.POS.NOUN_COUNT / NOUN_PERSON_THING / NOUN_COMPOUND | 含于词性 | HK, SN, K56, YST, ETSIN, XDFRD† |
| 句子结构：谓语与连接词计数、剥离修饰语 | FD.SENT.CLAUSE_COUNT / MODIFIER_STRIP | — | SN, HK, YST, ETSIN |
| 动词：数→态→时 | GR.VERB.* / QT.P5.VERB_FORM | 8–12%（2–4 题） | SN, HK, DERU, KB, K56, YST, ETSIN, XDFRD† |
| 动词句型（及物性、宾补、使役） | GR.VERB.VERB_PATTERN | 低 | HK, DERU, KB, SN |
| 非谓语：to do / -ing / 分词主被动 | GR.NONFIN.* | 分词约 4% | HK, SN, YST, ETSIN, XDFRD†, FLTRP† |
| 代词格、反身、所有代词、限定词 | GR.PRON.* / QT.P5.PRONOUN | 7–10%（2–3 题） | HK, SN, DERU, KB, K56, YST, ETSIN, FLTRP†, XDFRD† |
| 介词 vs 连词 vs 接续副词 | GR.CONN.PREP_VS_CONJ / QT.P5.CONNECTOR_MIX | 含于介/连 | DERU, KB, HK, SN, K56, YST, XDFRD†, FLTRP† |
| 介词（时间/地点/语义） | GR.CONN.PREP_* / QT.P5.PREP | 10–13%（3–4 题） | HK, SN, DERU, KB, YST |
| 从属连词、成对连词 | GR.CONN.CONJ_* / QT.P5.CONJ | 3–9%（1–3 题） | DERU, HK, SN, ETSIN |
| 关系词与名词从句 | GR.REL.* / QT.P5.RELATIVE | 0–3%（证据弱） | SN, HK, DERU, KB, K56, ETSIN, XDFRD† |
| 比较 | GR.COMP.* / QT.P5.COMPARATIVE | 1–3% | HK, SN, DERU, ETSIN, XDFRD† |
| 特殊句式：假设倒装、要求类原形、否定倒装、并列 | GR.VERB.SUBJUNCTIVE_DEMAND / CONDITIONAL_INVERSION / GR.SPECIAL.* | 低 | HK, SN, YST, XDFRD† |
| 副词功能（already/still/yet、so/such、also/too） | GR.POS.ADV_* / VO.CONF.ADV_* / SO_SUCH_TOO | 副词选择约 8% | HK, SN, SN56 |
| 数量表达与一致 | GR.VERB.AGREE_QUANT / VO.CONF.QUANT_WORDS | 低 | HK, DERU |
| 词汇题：先搭配后语义 | VO.LEX.* / VO.COLLO.* / QT.P5.VOCAB | 30–40%（9–12 题） | SN, HK, K56, SN56, YST, KF, XDFRD†, FLTRP† |
| 近义词与多义词商务义 | VO.CONF.* | 含于词汇 | HK, KF |
| 构词（后缀定词性） | FD.VOC.AFFIX | — | FLTRP†, XDFVOC |
| 按频率学、P5 限时 | ST.TIME.PER_ITEM_P5 | — | SN56, DERU, BT, KB, K56, SNP56, FLTRP† |

## 3. 跨书合并：Part 6 细粒度考点清单（只采新制书）

| 考点 | 图谱 ID | 现行考频（16 题中） | 覆盖书目 |
|---|---|---|---|
| 顺序通读全文、不只读空格句 | QT.P6.CLASSIFY（策略属性） | — | K56, SN56, HK（FLTRP† 只有“用上下文选动词”） |
| 独立型 vs 上下文型二分 | QT.P6.CLASSIFY | 约一半独立 | K56, SN56, HK, ETSIN |
| 独立型语法/词性 | QT.P6.INDEPENDENT | 3–5 | 同 P5 |
| 语境时态（以发信日期、时间线定） | QT.P6.CTX_TENSE | 约 2 | K56, ETSIN |
| 语境代词 | QT.P6.CTX_PRONOUN | 约 0–1 | K56, ETSIN |
| 语境词汇 | QT.P6.CTX_VOCAB | 5–8 | K56, ETSIN, HK |
| 接续副词 | QT.P6.CTX_CONJ_ADV | 约 1 | K56, ETSIN, HK, KF |
| 句子插入（文选择），每篇固定 1 题 | QT.P6.INSERTION（+ INS_OPENING / INS_TRANSITION / INS_CLOSING） | 4（固定） | SN, HK, K56, ETSIN, BT |

旧制 P6 只有 12 道填词/短语题，无句子插入；旧制书的 P6 章节不进图谱。

## 4. 跨书合并：Part 7 细粒度考点清单（只采新制书 + 通用技巧）

| 考点 | 图谱 ID | 现行考频（54 题中） | 覆盖书目 |
|---|---|---|---|
| 先读题干、带关键词定位 | ST.LOCATE.QUESTION_FIRST | — | IIBCP7, SN, ETS1000, FLTRP†（通用） |
| 主旨/目的 | QT.P7.MAIN_PURPOSE | 5–10 | SN, HK, HK777, YST, K7, ETSIN |
| 细节（5W1H、数字日期） | QT.P7.DETAIL / DETAIL_NUMBER | 20–25 | SN, HK, HK777, YST, K7, FLTRP†（通用） |
| 选项照合 / NOT | QT.P7.TRUE_INDICATED / NOT_TRUE | 照合约 10–12（与推断重叠）/ NOT 1–3 | SN, HK, HK777, YST, K7, FLTRP†（通用） |
| 推断（含身份、下一步） | QT.P7.INFERENCE / INFER_WHO / INFER_NEXT | 8–15 | SN, HK, HK777, YST, K7 |
| 意图（短信/群聊引语）**新制特有** | QT.P7.INTENT | 2 | SN, HK, HK777, YST, K7 |
| 句子位置 [1]–[4] **新制特有** | QT.P7.INSERTION | 2 | SN, HK, HK777, YST, K7 |
| 同义词（语境义） | QT.P7.SYNONYM | 2–4 | SN, HK, HK777, YST, K7, KF |
| 改写识别 | VO.PARA.* / ST.LOCATE.PARAPHRASE_MATCH | 约 70% 正解为改写 | K7, ETSIN |
| 错误选项套路 | ST.ELIM.TRAP_TYPES | — | K7（XDF1000† 简介旁证） |
| 文本类型结构与常考点 | TX.* / QT.P7X.* | 邮件+文章 50–60% | SN, HK, HK777, YST, ETSIN, IIBCP7（XDFRD† 7 类文本为旧制，缺短信/群聊） |
| 多篇连锁（双篇、**三篇为新制特有**） | QT.P7.CROSS_REF / QT.P7X.CROSS_REF.DOUBLE / .TRIPLE | 6–10 | SN, HK, HK777, YST, ETSIN, K7（FLTRP† 仅双篇） |
| P7 做题顺序与时间 | ST.ORDER.WITHIN_P7 / ST.TIME.PER_SET_P7 | — | HK, K7 |
| 速读训练（斜线读、生词不停、测时复读、先看母语概要） | FD.READ.CHUNK / UNKNOWN_WORD / ST.REVIEW.SPEED_REPEAT | — | IIBCP7, IIBCQ, SN |

## 5. 各书差异要点

1. **第一层切分维度不同**：语法范畴（HK、ETSIN、XDFRD†）、解题路径（SN“不翻译/翻译”、BT“構文先行/文脈先行”）、出题频率（SN56）、题型（DERU/KB 7 类、K56 6 类）、分数段（KF、BT）。图谱同时保留这几种维度：语法层按范畴，题型层按题型，`target_band` 按分数段，`exam_weight` 按频率。
2. **P6 的分法**：新制书（K56、ETSIN、HK）都把“句子插入”单列，并区分独立型/上下文型；旧制书（FLTRP†、XDFRD†）把 P6 当作 P5 的延伸，无插入句。
3. **P7 的组织**：韩国书普遍“设问 7–8 类 × 文本 6–9 类”二维组织（HK777、SN、YST）；日本 K7 以“改写 + 错误选项”为主线；IIBCP7 以速读训练为主线；中国旧制书只按文本类型（XDFRD† 7 类）。
4. **词性题的比重**：でる1000問书内词性占 50.7%，高于真题（P5 约 20–27%）；词汇题在纯文法书中完全缺席（DERU/KB 不收），需靠 KF/HK 词汇章节补。
5. **改写/同义替换**：只有 K7 与 ETSIN 把它作为独立单元（ETSIN 放在 P7 最前），其余书分散在各设问里 → 图谱把 VO.PARA 设为 P7 细节/照合/推断的前置。
6. **时间目标不一**：K56 P5&6 约 20 分钟、SNP56 15 分钟内、BT/KB 词性题 5–15 秒；图谱 `ST.TIME.TOTAL_PLAN` 取多来源共识（P5 10–12 / P6 8–10 / P7 ≥53–55）。
7. **盲区**：多数书只能看到目录，具体规则属整理推断；HK777、SN、SN56、YST 的出版年本轮未核实（标 🟡）。
