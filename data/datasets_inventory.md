# 数据集盘点（托业阅读提分应用 · 个人自用、非商用）

更新：2026-10-21。已下载部分全部用 `ls -la / du / wc -l / head / pandas` 在本目录实际核对；未下载部分为此前已核实的外部资源（本轮未重新联网核实，许可以列中写法为准）。

**使用边界（先读）**
- 本项目仅个人自用、非商用。CC BY-NC / NC-SA / "non-commercial research only" 类资源在此前提下可用；任何对外分发或商用前须逐项重审。
- **HuggingFace 上 Hackers / ETS / Tomato 等出版物题目资源属盗版，不下载、不使用。**
- `data/external/toeic_items/` 下 Part5 题库**均无明确许可**，仅作自用参考（风格、干扰项模式、自测），不得再分发，不作为 App 内置题库主体。
- `toeic_vocab_tw.json` 疑似 LLM 生成，使用前需抽查释义与例句。
- EdNet `tags` 的含义 Riiid 未公开（共 189 个标签值，含 `-1`）；Part5 常见 74/85/77/76/83，Part7 常见 177/178/176。只能当匿名技能 ID 用，含义需自行从题目反推。

用途代号：**诊断校准**（难度/用时先验、开局诊断）· **知识追踪**（KT 模型训练/评估）· **出题风格** · **干扰项** · **词汇** · **语料**（商务邮件/阅读文本）

---

## 1. 总表

### 1.1 已下载（data/external/，共约 114 MB）

| # | 名称 | 位置 | 规模（实测） | 许可 | 用途 | 状态 |
|---|---|---|---|---|---|---|
| D1 | EdNet-Contents（题目元数据） | `ednet/contents/*.csv`（+ 原始 `EdNet-Contents.zip` 174 KB） | questions 13,169 题 / 9,534 bundle；lectures 1,021；coupons 91；payments 190 | CC BY-NC 4.0 | 诊断校准、知识追踪 | ✅ 已下载、已解压 |
| D2 | EdNet HF 派生题目统计 | `ednet/hf_derived_item_stats.parquet`（407 KB）、`hf_derived_answer_distributions.parquet`（158 KB）、`hf_derived_summary.json` | 11,843 题；基于 50 万条作答抽样（HF `mgor/EDNet`） | 派生自 EdNet，按 CC BY-NC 4.0 对待 | 诊断校准、干扰项（选项分布） | ✅ 已下载、已分析（见 §3） |
| D3 | ASSISTments 2009 Skill Builder (corrected) | `kt/assistments2009_skill_builder_corrected.zip`（8.7 MB，解压 63 MB） | 401,756 行 × 30 列 | 研究免费使用，需引用（未本轮复核） | 知识追踪（基线/调参，非英语） | ✅ 已下载，未解压 |
| D4 | Part5 题库（4 个来源） | `toeic_items/` | EthanJYK 11,414 题；Hwanseok 7,115 题；wonwooo 5,185+915 题；graykode 3 题；去重后约 11,377 题 | **无许可，仅自用参考** | 出题风格、干扰项 | ✅ 已下载 |
| D5 | TSL 1.2 / BSL 1.20 / NGSL 1.2 / SUP | `wordlists/`（+ `data/wordlists/` 另有 TSL/NGSL 词形表） | TSL 1,250 词；BSL 1,744 词；NGSL 2,809 词；SUP 51 词 | CC BY-SA 4.0（NGSL 项目，未本轮复核） | 词汇 | ✅ 已下载 |
| D6 | toeic_vocab_tw.json（繁中 TOEIC 词表） | `wordlists/toeic_vocab_tw.json`（22.6 MB） | 11,238 条，84 条英文词重复 | 来源/许可不明 | 词汇 | ⚠️ 已下载，**疑似 LLM 生成需抽查** |
| D7 | CLOTH（cleaned） | `distractor/CLOTH_{train,valid,test}_cleaned.json`（20 MB） | 76,850 / 11,067 / 11,516 个空 | 非商用研究（官方声明，未本轮复核） | 干扰项 | ✅ 已下载 |
| D8 | RACE | `distractor/RACE.tar.gz`（25 MB） | 约 27,933 篇文章（train 25,137 / dev 1,389 / test 1,407） | 非商用研究（官方声明，未本轮复核） | 干扰项、出题风格（阅读题） | ✅ 已下载，未解压 |
| D9 | EnronSent v1.0 | `corpora/enronsentv1.tar.gz`（26 MB，解压约 88 MB） | 45 个文件，96,107 封邮件，2,205,910 行，13.8M 词 | 源数据经 FERC 公开（README 称 public domain）；注意隐私 | 语料（商务邮件） | ✅ 已下载，未解压 |
| D10 | AESLC（邮件主题行） | `corpora/aeslc_{train,validation,test}.parquet`（7.9 MB） | 14,436 / 1,960 / 1,906 封；正文中位 424 字符 | 基于 Enron；许可未核实 | 语料（短邮件，Part7 邮件体裁） | ✅ 已下载 |

### 1.2 已核实、未下载

| # | 名称 | 位置/链接 | 规模 | 许可 | 用途 | 状态 |
|---|---|---|---|---|---|---|
| R1 | EdNet KT1 | github.com/riiid/ednet；Google Drive id `1AmGcOs5U31wIIqvthn9ARqJMrMTFTcaw` | 1.2 GB（压缩）/ 5.6 GB；约 1.31 亿次作答、78.4 万学生 | CC BY-NC 4.0 | 知识追踪、诊断校准 | ⏳ 未下载（Top 3） |
| R2 | EdNet KT2 | Drive id `1qQQshbzyULW5RjMi7u-IhUr2dT_6uMXA` | 含作答过程中的 action（选项改动等） | CC BY-NC 4.0 | 知识追踪（行为细节） | ⏳ 未下载 |
| R3 | EdNet KT3 | Drive id `1TVyGIWU1Mn3UCjjeD6bcZ57YspByUV7-` | 加入讲解/讲座消费行为 | CC BY-NC 4.0 | 知识追踪（学习行为） | ⏳ 未下载 |
| R4 | EdNet KT4 | Drive id `1HHZwpeqMSowWhgEu0URBQQ3FizR9o9mT` | 全量 action（含付费、浏览等） | CC BY-NC 4.0 | 知识追踪（全行为） | ⏳ 未下载 |
| R5 | IRW `choi_2020_ednet_reading` | `pip install irw`；数据托管 Redivis | Part5–7：5,452 万次作答、7,620 题 | 随 EdNet（CC BY-NC 4.0）；**需免费 Redivis 账号** | 诊断校准（阅读题 IRT 标定） | ⏳ 未下载（Top 2） |
| R6 | Riiid Answer Correctness Prediction（Kaggle） | kaggle.com/c/riiid-test-answer-prediction | 约 1 亿条作答 | **Competition Use Only** | 知识追踪（方案参考为主） | ⏳ 只读论文/代码 |
| R6a | 1st：Last Query Transformer RNN | arXiv 2102.05038 | AUC 0.820 | 论文 | 知识追踪方案 | 参考 |
| R6b | 2nd：LSTM-SAKT | arXiv 2102.00845 | — | 论文 | 知识追踪方案 | 参考 |
| R6c | 3rd：riiid-acp-pub | github.com/jamarju/riiid-acp-pub | — | 见仓库 | 知识追踪方案 | 参考 |
| R6d | SAINT+ | arXiv 2010.12042 | — | 论文 | 知识追踪（含用时/滞后特征） | 参考 |
| R6e | 分数预测（Riiid） | arXiv 2005.05021 | 提出 7–11 题开局诊断即可估分 | 论文 | 诊断校准（开局诊断题数依据） | 参考 |
| R7 | ASSISTments 2009 | — | 已下载（见 D3） | — | — | ✅ |
| R8 | Junyi Academy | — | 数学练习日志 | CC BY-NC-SA | 知识追踪（基线） | ⏳ 低优先 |
| R9 | Eedi NeurIPS 2020 Education Challenge | — | 数学诊断题作答 | **许可未核实** | 知识追踪、诊断设计 | ⏳ 先核许可 |
| R10 | Eedi Misconceptions（Kaggle） | — | 数学误解标注干扰项 | 竞赛条款（未核） | 干扰项（误解→干扰项映射思路） | ⏳ 低优先 |
| R11 | Enron Email 全量 | cs.cmu.edu/~enron | 443 MB | 公开（FERC） | 语料 | ⏳ 已有 EnronSent/AESLC 子集，暂不需要 |
| R12 | Kaggle `tientd95/toeic-test` | kaggle.com/datasets/tientd95/toeic-test | — | 未核实，疑似来自出版物 | 出题风格 | ⏳ 慎用 |
| R13 | COCA collocates | english-corpora.org | — | **付费** | 词汇（搭配） | ✗ 暂不购买 |
| R14 | PHaVE List（短语动词） | Garnier & Schmitt 2015 | 150 个高频短语动词 + 义项 | 学术发布（未核） | 词汇 | ⏳ 待下载 |
| R15 | DG_Survey | github.com/Distractor-Generation/DG_Survey | 干扰项生成综述 + 数据集清单 | 见仓库 | 干扰项（方法） | 参考 |
| R16 | DGen | github.com/DRSY/DGen | 填空题干扰项生成代码 | 见仓库 | 干扰项 | 参考 |
| R17 | D-GEN | github.com/emorynlp/D-Gen | 干扰项生成/评测 | 见仓库 | 干扰项 | 参考 |
| ✗ | HF 上 Hackers / ETS / Tomato 题目 | HuggingFace | — | **盗版** | — | ✗ 不用 |

---

## 2. 每项说明

### D1 EdNet-Contents
- `questions.csv` 字段：`question_id, bundle_id, explanation_id, correct_answer, part, tags, deployed_at`（13,169 行，无题干文本）。
- 按 Part 题数（括号内为 bundle 数）：P1 643(643)、P2 1,662(1,661)、P3 1,266(422)、P4 1,158(386)、**P5 5,703(5,703)**、**P6 1,335(334)**、**P7 1,402(385)**。阅读部分合计 8,440 题。
- P6 bundle 基本都是 4 题（333 个 4 题 + 1 个 3 题），符合新题型；P7 bundle 大小 2/3/4/5 题分别 94/76/89/126 个。
- 正确答案分布 a 3,499 / b 3,624 / c 3,415 / d 2,631（d 少是因为 Part2 只有三选一）。
- `lectures.csv`：`lecture_id, part, tags, video_length, deployed_at`，1,021 条；`coupons.csv`、`payments.csv` 是商业元数据，对本项目无用（payments 字段名原文拼写为 `duaration`）。
- tags：共 189 个值（`-1` 到 300），含义未公开。Part5 前五：74(676)、85(485)、77(396)、76(330)、83(306)，另有 440 题标 `-1`；Part6：143(303)、179(167)、77(127)、85(119)；Part7：177(637)、178(375)、176(345)、149(333)、155(294)。P5/P6 共用 74/76/77/85，推测为语法/词汇技能（推断）。
- zip 内含 `__MACOSX`、`.DS_Store` 垃圾文件，解压目录已干净。

### D2 EdNet HF 派生统计
- 来源 HF `mgor/EDNet`，按 summary 为 KT1 的 **50 万条作答抽样**（全量 1.31 亿）；抽样方式未说明，可能不是随机抽样。
- `hf_derived_item_stats.parquet`：`question_id, n_responses, p_value, mean_elapsed_ms, bundle_id, explanation_id, correct_answer, part, tags, deployed_at`，11,843 题（questions.csv 中 1,326 题无作答）。
- `hf_derived_answer_distributions.parquet`：每题 `count_a…count_d`，可直接看哪个干扰项最“吸引人”。
- 每题作答数中位仅 27（P7 中位 13），单题 p 值噪声大，适合做 **Part 级先验**，单题标定需 KT1/IRW。

### D3 ASSISTments 2009
- 字段 30 列：`order_id, assignment_id, user_id, problem_id, correct, attempt_count, ms_first_response, skill_id, skill_name, hint_count, opportunity …`。数学题，KT 领域标准基线；仅用于验证 KT 管线，不迁移内容。

### D4 Part5 题库（无许可，仅自用参考）
- `EthanJYK_toeic_part5_question_data_v2.csv`：`questions, answers, A, B, C, D, full_sentence`，11,414 行（题干去重 11,329）。
- `Hwanseok_part5_5000plus2000.csv`：`내용,1,2,3,4,답`（韩文表头，带 BOM），7,115 行。
- `wonwooo_Part5_training.json` 5,185 + `_test.json` 915：`question, answer, 1–4`。
- `graykode_test_sample.json`：3 题样例（toeicbert 仓库）。
- **重叠严重**：按题干前 60 字母归一化比对，Hwanseok 与 Ethan 重叠 6,969、Ethan 与 wonwooo 重叠 5,986，三者去重合计约 11,377 题，实际是同一批题的不同转存，出处不明（有出版物来源嫌疑）。只作风格/干扰项模式参考与个人自测，不入库分发。

### D5 TSL / BSL / NGSL / SUP
- TSL 1.2（TOEIC Service List）1,250 词，`Word, TSL Rank, SFI, U`；`TSL_12_definitions.xlsx` 1,246 条英文释义；说明文件列出语料来源（TOEIC 教材与模考题）。
- BSL 1.20（Business Service List）1,744 词，含 Band/SFI/U；教学版和研究版两种词形表。
- NGSL 1.2 2,809 词，含 SFI 与每百万频次；带英文释义 xlsx。
- SUP：51 个补充词（星期、月份等）。
- `data/wordlists/` 下另有 `NGSL_12_lemmatized_for_research.csv`、`TSL_12_stats.csv`、`TSL_lemma.csv`（较早下载的版本，与 external 互补）。
- 研究版 CSV 前几行以 `##` 开头为说明，读入时需跳过。

### D6 toeic_vocab_tw.json（需抽查）
- 字段：`english_word, chinese_definition, star_rating(1–5), toeic_score_range, category, parts_of_speech, word_forms, examples[{english, chinese}], exam_tips`。
- 分类前几：辦公日常 2,980、營運管理 1,461、溝通互動 1,342、一般專業 1,137；分数段 0-400 1,345 / 400-600 3,590 / 600-780 3,521 / 780-900 2,104 / 900+ 678。
- 随机抽 5 条释义基本正确，但例句模板化、字段齐整度过高，且有 "A be followed by B" 这类非词条，**推断为 LLM 生成**。使用前建议抽 100 条人工核对释义/词性/例句，并与 TSL/BSL 交叉比对，不作为“真题高频”依据。

### D7 CLOTH / D8 RACE
- CLOTH cleaned：每条 `answer, distractors[3], sentence(含 [MASK])`；中国初高中英语完形填空，干扰项为人工命题，适合训练/评估 Part5/6 风格干扰项生成。
- RACE：中国初高中阅读理解（middle/high），文章 + 4 选项题，可借鉴 Part7 推断/主旨题干扰项写法；体裁偏叙事，与商务文本有差距。

### D9 EnronSent / D10 AESLC
- EnronSent：96,107 封“已发送”邮件的清洗文本，13.8M 词，适合抽商务邮件句式、搭配，做 Part6/7 邮件体裁语料。README 提醒尊重涉事个人隐私——生成题目时应去名化。
- AESLC：`email_body, subject_line`，短邮件 + 主题行，可直接做 Part7“邮件目的/主旨”题的素材。

### R1–R4 EdNet KT1–KT4
- KT1 是核心：`timestamp, solving_id, question_id, user_answer, elapsed_time`，每个用户一个 CSV。KT2–4 逐级增加行为粒度，本项目暂只需 KT1。
- 下载：Google Drive 大文件需确认页，可用 `gdown <id>`。

### R5 IRW choi_2020_ednet_reading
- Item Response Warehouse 把 EdNet 阅读部分（Part5–7）整理为标准 IRT 长表：5,452 万次作答、7,620 题。直接拿来做 1PL/2PL 标定，比自己从 KT1 清洗省事。需注册免费 Redivis 账号后用 `irw` 包拉取。

### R6 Riiid 竞赛与方案
- 数据为 Competition Use Only，不下载数据本体；只读方案：1st Last Query Transformer（AUC 0.820）、2nd LSTM-SAKT、3rd jamarju 开源代码、SAINT+（加入 elapsed time / lag time 嵌入）。
- arXiv 2005.05021（Riiid 分数预测）指出 7–11 题的开局诊断就能给出可用估分，支持我们“短诊断”设计。

### R8–R10 Junyi / Eedi
- 均为数学领域；Junyi CC BY-NC-SA 可作 KT 基线；Eedi NeurIPS 2020 许可未核实，用前先核；Eedi Misconceptions 的“误解→干扰项”标注思路可借鉴到语法误区干扰项。

### R11–R17 其他
- Enron 全量 443 MB：已有子集足够，暂不下。
- Kaggle tientd95/toeic-test：来源不明，可能来自出版物，慎用。
- COCA collocates：付费，暂不购；搭配可先用 EnronSent 自行统计。
- PHaVE List：150 高频短语动词，补 Part5 短语题。
- DG_Survey / DGen / D-GEN：干扰项生成方法与代码参考。

---

## 3. EdNet 难度/用时先验

数据：`ednet/contents/questions.csv` × `ednet/hf_derived_item_stats.parquet`（50 万条作答抽样，11,843 题有统计）。p_value = 单题正确率；用时 = `mean_elapsed_ms`/1000（秒）。汇总表另存于 `work/ednet_prior_by_part.csv`。

### 3.1 p_value（正确率）分布，按题目统计

| Part | 题数 | 作答数 | 每题作答中位 | 均值 | SD | Q1 | 中位 | Q3 | 作答加权均值 | 仅 n≥30 题均值（题数） |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 641 | 36,425 | 36 | 0.798 | 0.163 | 0.712 | 0.836 | 0.923 | 0.724 | 0.766 (450) |
| 2 | 1,612 | 100,476 | 56 | 0.720 | 0.185 | 0.619 | 0.731 | 0.833 | 0.691 | 0.713 (1,108) |
| 3 | 1,148 | 40,347 | 29 | 0.730 | 0.194 | 0.615 | 0.756 | 0.875 | 0.683 | 0.686 (573) |
| 4 | 1,032 | 38,529 | 26 | 0.697 | 0.221 | 0.560 | 0.734 | 0.873 | 0.606 | 0.648 (378) |
| **5** | 5,130 | 209,330 | 25 | **0.662** | 0.197 | 0.533 | 0.676 | 0.800 | 0.606 | 0.611 (2,108) |
| **6** | 1,208 | 51,989 | 27 | **0.677** | 0.205 | 0.558 | 0.723 | 0.833 | 0.653 | 0.655 (545) |
| **7** | 1,072 | 22,904 | 13 | **0.707** | 0.236 | 0.556 | 0.750 | 0.890 | 0.643 | 0.660 (172) |
| 全部 | 11,843 | 500,000 | 27 | 0.693 | 0.204 | 0.568 | 0.714 | 0.842 | 0.644 | 0.662 (5,334) |

难度段占比（p <0.4 / 0.4–0.6 / 0.6–0.8 / ≥0.8）：P5 9.6% / 24.9% / 38.7% / 26.9%；P6 11.9% / 17.8% / 36.7% / 33.6%；P7 10.0% / 18.8% / 29.5% / 41.7%。

### 3.2 平均用时（秒/题）分布

| Part | 均值 | Q1 | 中位 | Q3 | 作答加权均值 | 5–95% 截尾均值 | P10–P90 | >120 s 题占比 |
|---|---|---|---|---|---|---|---|---|
| 1 | 21.8 | 20.1 | 21.6 | 22.9 | 22.3 | 21.6 | 18.9–24.2 | 0% |
| 2 | 22.8 | 16.9 | 18.3 | 20.4 | 20.0 | 19.4 | 16.0–24.8 | 0.4% |
| 3 | 23.1 | 20.8 | 22.8 | 25.4 | 24.0 | 23.1 | 18.7–28.1 | 0% |
| 4 | 22.7 | 20.3 | 22.5 | 25.1 | 22.7 | 22.7 | 18.2–27.7 | 0% |
| **5** | 30.0 | 21.2 | **26.4** | 32.6 | 28.9 | 27.6 | 17.0–39.7 | 0.8% |
| **6** | 35.7 | 28.6 | **33.8** | 39.6 | 37.9 | 34.6 | 24.8–45.3 | 0.3% |
| **7** | 83.0 | 56.8 | **67.4** | 82.5 | 71.5 | 75.8 | 47.0–115.8 | 9.4% |

### 3.3 解读与用法
- **难度顺序与 ETS 不一致**：ETS RM-17-05 试测 p 值 P5 .67/.68 > P6 .55/.57 > P7 .48/.55；EdNet 中 P5 最难（0.662）、P7 反而 0.707。原因推断：Santa 是自适应练习、学生自选/被推荐题、P7 作答少且偏向较强学生（P7 每题作答中位仅 13），存在选择偏差。**作答加权后 P5 0.606 / P6 0.653 / P7 0.643，与 ETS 量级更接近。** 先验建议：P5 取 ~0.61–0.66，P6 ~0.65–0.68，P7 用 ETS 的 0.48–0.55 下调 EdNet 值。
- **用时口径**：同一 bundle 内各题 `mean_elapsed_ms` 完全相同（P3/4/6/7 组内标准差中位为 0），且 P7 bundle 从 2 题到 5 题，中位用时只从 62 s 增到 70 s——说明记录的是 **bundle 级用时、近似“每题平均”**，而不是整组总时长（推断，EdNet 文档未明说；Riiid Kaggle 的 `prior_question_elapsed_time` 也是按组内每题平均）。
- **配速先验**：P5 中位 ~26 s/题（30 题 ≈ 13 分钟），P6 ~34 s/题（16 题 ≈ 9 分钟），P7 ~67 s/题（54 题 ≈ 60 分钟）。常见考场配速建议（见 `work/reports/strategy_findings_summary.md`）为 75 分钟内 P5 ~10–12 分、P6 ~8–10 分、P7 ≥53–55 分，EdNet 学习者的练习节奏比考场目标慢约 10–20%，可用作“练习常模”，并以考场配速为目标线。
- 均值受极端值影响（单题最长 2,360 s），App 内建议用**中位数或截尾均值**。
- 单题统计仅 50 万条抽样，单题 p 值置信区间宽；正式题目标定请走 IRW（R5）或 KT1（R1）。

---

## 4. 推荐优先级 Top 8

1. **EdNet contents + item_stats（D1+D2，已在手）**：立即用作 Part 级难度/用时先验与干扰项吸引度；tags 作为匿名技能 ID。
2. **IRW choi_2020_ednet_reading（R5）**：注册 Redivis 后拉取，Part5–7 的 7,620 题做 IRT 标定，支撑开局诊断题选择。
3. **EdNet KT1（R1）**：训练/验证知识追踪与估分模型（5.6 GB，按需抽用户子集）。
4. **Riiid 方案（R6a–e）**：照 SAINT+ / Last Query Transformer 设计 KT 特征（用时、间隔），按 2005.05021 做 7–11 题开局诊断。
5. **TSL / BSL / NGSL（D5）**：词汇主干——TSL 定 TOEIC 专属词，BSL 补商务，NGSL 作通用底座。
6. **Part5 题库（D4，仅自用）**：归纳干扰项模式与题型分布、个人自测；去重后约 1.1 万题，不分发。
7. **CLOTH / RACE（D7/D8）**：训练/评估干扰项生成和推断题干扰项写法。
8. **EnronSent / AESLC（D9/D10）**：商务邮件语料，供 Part6/7 原创文本与搭配统计。

其余（KT2–4、Junyi、Eedi、PHaVE、DG 系列代码）按需取用；COCA 付费暂缓；tientd95 与 HF 出版物资源不用。

---

## 5. GitHub 扩展检索（2026-10-21 追加）

详见 `data/external/github_inventory.md`。按用户 2026-10-21 新规则：GitHub 上能拿到的都可以自用（不外传），许可证只记录、不作否决条件。TastyHeadphones/TOEIC 由另一个子任务处理。

- 检索：GitHub API 搜索去重 295 个仓库（含 toeic 的 182 个）+ web_search 新增 4 个；细查 51 个。**可入库 24 / 仅参考 14 / 不用 12 / 已收录 1**。
- 已下载到 `data/external/github/<owner_repo>/`（约 34 MB），阅读题合计约 8,200 题（没有去重），其中完整新制套题 23 套约 2,300 题：
  - G1 ETS 정기시험 기출 1000 Vol.4（真题转录，1,000 题，10 套；已抽成 `ets1000_vol4_rc_extracted.json`）→ 只当模考/校准锚题
  - G2 maximcuynat 6 套 600 题（MIT 原创）、G3 asaiibowl 3 套 300 题、G5 marcvasseur 4 套约 400 题（HTML）
  - G4 kdeppaei 约 570 题（繁中解析，含 ESL Lounge P6/P7）、G6 bonnie8536 715 题 + 28 题诊断卷（P6 缺插入句）
  - G7 tranvien98/fill_toeic 3,625 道 P5（和 D4 只重叠 719 道；推断和 Kaggle R12 tientd95 是同一份）
  - 词表：weiz30 3,000 词、SYZBZ vocabulary.json、ringooai TOEIC 繁中/日文、600 Essential Words 615 词
  - 估分：lumi-open-data 答对数→量表分近似表（CC-BY-4.0）
  - 参考代码：`_reference_code/`（FSRS v4.5 JS、估分模型 TS、LLM 出题提示词）
- 没下成：sbljsc/toeic-practice-studio（自称 2,000 题，仓库 >120 MB，tarball 被截断）。
- 新技巧 11 条（N1–N11），见 github_inventory.md §4。
- 风险：大部分题目没有逐题抽查；G1、G4 的 ESL Lounge 部分、G7、G21 是出版物/网站内容，只能自用。

---

## 6. 外部资源补充检索（2026-10-22 追加）

详见 `docs/research/external_sources_2026-10-22.md`。
- 没有找到新的、有明确开源许可的新制阅读题库；sbljsc（G26）阅读 1,000 题已拉下，但与私有 xdf1000 重复。
- G4 kdeppaei：336 题来自 ESL Lounge，MIT 只覆盖其余约 1,107 题。
- **D6 许可已查明**：即 HF `kknono668/toeic-vocab-tw`，CC BY-SA 4.0。
- 新入公开池的词表（`data/open_items/`）：LEE-WHITE/toeic-vocab-tw（CC BY 4.0，9,537 条繁中）、kknono668/toeic-vocab-tw（CC BY-SA 4.0，11,238 条，含分数段）、chunchiech/EnglishCoach toeic_3600（MIT，3,600 条繁中+例句）、ECDICT 子集（MIT，17,894 条简中）。
- 技巧增补 16 条：`data/strategies/strategy_additions_v1_1.md`。
