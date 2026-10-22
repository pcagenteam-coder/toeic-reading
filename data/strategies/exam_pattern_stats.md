# TOEIC 阅读（Part5–7）题型分布统计

更新：2026-10-21。数据源：`data/strategies/exam_pattern_stats.json`（170 条：source 146 条、composite 24 条；生成脚本 `work/build_exam_pattern_stats.py`）。本文所有数字以该 JSON 为准；与任务给定区间逐条比对后**全部一致**，JSON 额外多出的条目在 §3 中标注“JSON 补充”。

**读法**
- `source` = 单一来源的原始说法；`composite` = 多源合成的估计区间（可信度统一标为 estimate）。
- ETS / IIBC **不公布**题型比例；所有比例来自日韩机构、教师博客和学位论文对官方题集/真题的二次统计。
- `scordia.net`（32 条）是网站自己的 **AI 生成练习库**统计，**不是考试数据**，只列出、不参与合成。
- 份额口径差异大（尤其“词汇”是否包括介词/连词选择），比较前先看口径列。

---

## 1. 按 Part 的来源对照表

### 1.1 全卷格式（官方，可信度高）

| 项目 | 内容 | 来源 |
|---|---|---|
| Part5 | 30 题 | [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) |
| Part6 | 16 题 = 4 篇 × 4 题；答案可为词、短语或句子 | IIBC |
| Part7 单篇 | 29 题；10 篇，每篇 2–4 题 | IIBC；[ETS 考生手册](https://www.ets.org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf) |
| Part7 多篇 | 25 题；5 组 × 5 题 = 双篇 2 组（10 题）+ 三篇 3 组（15 题） | IIBC；ETS 手册；[東洋経済](https://toyokeizai.net/articles/-/109179?page=4) |
| Part7 文档数 | 10 + 2×2 + 3×3 = **23 篇/卷**（JSON composite 推算） | — |
| 难度（ETS 试测 p 值） | P5 .67/.68；P6 .55/.57；P7 .48/.55（单篇 .53/.62，多篇 .42/.45） | [ETS RM-17-05](https://www.ets.org/Media/Research/pdf/RM-17-05.pdf) |

### 1.2 Part5（30 题）——各来源换算为占比（%）

| 来源（年份，样本） | 词汇（同词性词义） | 词性 | 介词 | 连词 | 动词形态 | 代词/限定词 | 关系词 | 比较 | 口径/可信度 |
|---|---|---|---|---|---|---|---|---|---|
| [get-toeic](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/)（2021，ETS 韩国既出問題集3） | 33（动/形/名/副 8/8/8/9）+ 短语 5 = **38**；含介词/连词时 53 | 22（名10 形4 副8） | 10 | 5 | 10（时态6 分词4） | 9（代词6 限定3） | 未单列（“其他语法”6） | 未单列 | 中高；介词/连词计入词汇 |
| [trankyblog](https://trankyblog.com/toeic_part5)（2023，公式7–9，6 套 180 题） | 30.0 | 25.6 | 10.6 | 9.4 | 7.7 | 7.2 | — | 1.1 | 中；另有“副词选择”8.3 |
| [eigo-koryaku](https://eigo-koryaku.com/?p=528)（2016，1 套 30 题） | 40.0 | 16.7 | 13.3 | 3.3 | 10.0 | 6.7 | — | 6.7 | 低；样本太小，副词 3.3 |
| [toeicstory 999](https://www.toeicstory.co.kr/999)（2018，YBM 기출 分析，每套题数） | 动/名/形/副各 2–3 → 约 27–40 | 名词 2–3 题 | ~3 题（10） | 有的卷 0 | 时态~2 + 分词~1（≈10） | 代词~2 + 限定~1（≈10） | — | — | 中高 |
| [toeicstory 464](https://www.toeicstory.co.kr/464)（2016） | 词汇 ~10 / 语法 ~20 | | | | | | | | 中；改版初期专家说法 |
| [釜山大硕论](https://www.dbpia.co.kr/journal/detail?nodeId=T16857240)（2023，29 套 870 题） | **11.8**（严格：四选项同词性） | 语法 88.2 | 频次：名>形>副>介>从句/连>限定/代>时态>被动>不定式>情态 | | | | | | 中；定义不同→离群 |
| [youlinguista](https://youlinguista.com/toeic-part5-tips/)（2022，2 套） | <40 | 语法 >60 | | | | | | | 中；数字只在图里 |
| [englishtalk](https://www.englishtalk.jp/025-toeic-part5-overview-parts-of-speech/)（2025） | 30 | 25 | | | | | | | 低；其他语法 45 |
| [toeic-taisaku-lab](https://toeic-taisaku-lab.com/toeic-part5-grammar-strategy/)（2026） | ~25 | ~30 | | | | 代词+关系 ~10 | | | 低；无样本；固定搭配 ~10 |
| [prepedu](https://prepedu.com/zh-hant/blog/toeic-reading-part-5)（2025） | 30–40 | 25–30 | | | | | | | 低；自称“ETS 官方统计”（不实） |
| [常春藤 ivy](https://www.ivy.com.tw/column/cont/2025110517562325969)（2025，台） | ~2/3 | 语法 ~1/3 | | | | | | | 低；介词/连词计入词汇 |
| [990prep](https://990prep.com/en/guides/toeic-part-5-strategies)（2025） | ~25 | ~30 | | 连接词 ~10 | | | | | 低；其他语法 ~35 |
| scordia（2026，AI 练习库 546 题） | — | 10.1 | 12.5 | 10.1 | 动词形 7.1、时态 6.2、被动 6.2… | — | 8.2 | — | **非考试数据，不用** |

趋势类（定性）：[Herald 经济 2014](https://biz.heraldcorp.com/article/145160) 纯语法题 ≤10 题/卷（原 10–12），更多需看语义的题；[toeicstory 2577（2026）](https://www.toeicstory.co.kr/2577) 形近词（diagnostic vs diagnosable）、一词多义、更宽的同义替换增多。

### 1.3 Part6（16 题）

| 来源（年份） | 插入句 | 词汇 | 语法（词性/形态/代词） | 时态（语境） | 连接副词 | 其他口径 | 可信度 |
|---|---|---|---|---|---|---|---|
| [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) | **4（每篇 1，固定）** | | | | | | 高 |
| [桐原 KIRIHARA](https://academy.kirihara.co.jp/blog/toeic/toeic-part6/)（2022） | ~4 | ~6 | ~3 | ~2 | ~1 | | 中 |
| [fumi-eigo](https://fumi-eigo.com/toeic-part6/)（2025） | ~4 | ~6 | ~3 | ~2 | ~1 | 与桐原表完全相同，疑抄录，不算独立来源 | 低 |
| [toeicstory 999](https://www.toeicstory.co.kr/999)（2018） | 4 | ~8（每篇 ~2） | ~4（每篇 ~1） | | | 词汇里动/名/副/短语各 1–2；词性 名/形 > 副 | 中高 |
| [kumata-eigo](https://kumata-eigo.create-more.net/toeic_part6/)（2019） | 4 | ~7（略少于一半） | 其余（~5） | | | | 低 |
| [mikan](https://mikan.com/eigo-note/toeic-part6-guide)（2025） | 4 | | | | | 按解题方式：不依赖语境 ~8，依赖语境 ~4 | 中 |
| [ALC](https://ej.alc.co.jp/tag/TOEIC/toeic-auth-part6-20250622)（2025） | | | | | | 单句即可解 约一半 | 中 |
| scordia（2026） | | | | | | 书信/邮件体裁占练习题 48–54% | **非考试数据** |

### 1.4 Part7（54 题）

| 来源（年份） | 细节 | 选项比对/是非（indicated/true） | 推断 | 主旨/目的 | 同义词 | NOT | 意图 | 插入句 | 跨篇关联 | 可信度 |
|---|---|---|---|---|---|---|---|---|---|---|
| [junpei-english](https://junpei-english.com/toeic-part7/)（2025） | ~20 | ~12 | ~8 | ~5 | ~3 | ~2 | ~2 | ~2 | | 中；合计 54 |
| [mikan](https://mikan.com/eigo-note/toeic-part7-guide)（2026-07 更新） | 20–25 | | ~15 | 8–10 | | 0–3 | ~2 | 2（单篇内） | | 中；“难题”合计 21–23 |
| [STUDYing](https://studying.jp/toeic/about-more/part7-2.html)（2025） | | | | | | | 2 | | | 中 |
| [toeicstory 999](https://www.toeicstory.co.kr/999)（2018） | | | | | 多出现在多篇 | | | | 双篇 ~1、三篇 ~2 → **~8/卷** | 中高 |
| [碁峰 gotop](https://dlcenter.gotop.com.tw/PDFSample/ARE001800.pdf)（~2020，台） | | | | | | | 每篇 2/4 题的聊天/短信各 1 | 每篇 3/4 题的单篇各 1（多为文章/邮件） | 双篇 1–2、三篇 2–3（→ 8–13/卷） | 中 |
| [Hackers 讲师](https://www.hackers.co.kr/?c=s_toeic%2Ftoeic_board%2FB_TOEIC_QA&keywd=mheng_boardbanner_afterjumsu_241215&logger_kw=mheng_boardbanner_afterjumsu_241215&uid=1235120)（2025-01-26 韩国场次） | | | “What is concluded” 多 | | 3 | | | | 单篇题数 2-2-3-2-3-3-4-4-3-4 | 中；单场 |
| scordia（2026，AI 练习库 1,325 题） | 57.3% | | 16.3% | 7.8% | 10.6% | 5.9% | 3.8% | 0.8% | 3.5% | **非考试数据** |

Part7 文本类型：

| 来源 | 内容 | 可信度 |
|---|---|---|
| [toeicstory 999](https://www.toeicstory.co.kr/999)（2018） | 邮件/书信 + 文章 占 **50–60%** 篇数 | 中高（唯一定量来源） |
| [mikan](https://mikan.com/eigo-note/toeic-part7-guide)（2026） | 体裁清单：邮件/书信、广告、通知、文章、短信、表格/发票/日程、说明/保修、网页（无数量） | 中 |
| [ETS 手册](https://www.ets.org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf) | 示例：杂志/报纸文章、电子邮件、即时消息 | 高 |
| scordia（2026） | 邮件 11.6%、短信/聊天 10.1%、通知 7.2%、政策 6.3%、备忘录 3.9%、文章 3.5%、评论 3.2%、招聘 3.2%、广告 3.1%（478 题未标） | **非考试数据** |

完整 146 条 source 记录见文末附录。

---

## 2. 冲突说明

1. **Part5“词汇”占比 11.8% ~ 67%，主要是口径冲突，不是事实冲突。**
   - 把介词/连词选择也算“词汇”：get-toeic 53%、常春藤 ~2/3。
   - 只算同词性实词词义（+短语）：get-toeic 扣除介词/连词后 38%、trankyblog 30%、eigo-koryaku 40%、YBM 约 27–40%。
   - 严格定义（四个选项同词性才算词汇）：釜山大硕论 11.8%，语法 88.2%。
   - 合成值采用第二种口径，硕论作离群值剔除（JSON composite 备注）。
2. **词性题 16.7% ~ 30%**：eigo-koryaku 只有 1 套题（16.7%，偏低）；低可信度博客（taisaku、990prep）给 ~30%，无样本。合成 20–27% 以 get-toeic 22% 和 trankyblog 25.6% 为锚。
3. **连词 3.3% ~ 9.4%**：trankyblog 9.4% 把从属连词、并列连词和连接副词都算进来；get-toeic 5% 只算词义连词；YBM 说有的卷为 0。合成 3–9% 覆盖了这个差异；介词+连词合计 13–20%。
4. **比较级 1.1% vs 6.7%**：6.7% 来自 1 套 30 题中的 2 题，样本噪声；合成 1–3%。
5. **关系词**：只有 AI 练习库给出 8.2%（不用）；真题分析都没单列，归在“其他语法”。合成 0–3%，证据弱。
6. **trankyblog 的“副词选择”8.3%**单列一类，其他来源多归入词汇；合成表里没有单独区间，按词汇处理（推断）。
7. **Part6 词汇 ~6 vs ~8**：桐原 ~6（另把时态 ~2、连接副词 ~1 分开）；YBM ~8（每篇 ~2）。fumi-eigo 与桐原表完全一致，疑抄录，不算独立证据。mikan/ALC 按“是否依赖语境”分类，不能和题型分类直接相加。
8. **Part7 推断 ~8 vs ~15、主旨 ~5 vs 8–10**：junpei 单列了“选项比对/是非”~12 题，而 mikan 把很多“What is indicated/true”题归为推断。两者合计推断+是非 ≈ 20 vs 15，口径不同而非矛盾。合成区间：推断 8–15，是非 ~10–12（与推断重叠）。
9. **跨篇关联题**：YBM 算 ~8/卷；碁峰按每组 1–2/2–3 推算可达 8–13；JSON 合成给 **6–10**。**以 JSON 为准**，但注意碁峰推算上限高于合成上限，三篇题组较难时可能偏多。跨篇题与细节/推断等题型重叠，不可相加。
10. **AI 练习库（scordia）与真题差距明显**：例如插入句 0.8%（真题固定 2/54 ≈ 3.7%）、细节 57.3%。已全部排除。

---

## 3. 综合区间表（JSON composite，以 JSON 为准）

与任务给定区间逐项比对：**全部一致**。下表加入 JSON 的备注和补充条目。

### Part5（30 题）

| 题型 | 区间 | 约题数 | 主要依据 / 备注 |
|---|---|---|---|
| 词汇（同词性词义，含短语，不含介词/连词） | **30–40%** | 9–12 | tranky 30、eigo 40、get-toeic 38；硕论 11.8% 剔除 |
| 词性（名/形/副/动词槽位） | **20–27%** | 6–8 | 名词槽位最常见（硕论排序、YBM） |
| 介词（含介词 vs 连词辨析） | **10–13%** | 3–4 | |
| 连词（从属/关联/连接副词） | **3–9%** | 1–3 | 介词+连词合计 13–20% |
| 动词形态（时态/语态/一致/分词/非谓语） | **8–12%** | 2–4 | |
| 代词/限定词（格/反身/限定/数量词） | **7–10%** | 2–3 | |
| 关系词 | **0–3%** | 0–1 | 证据弱，多归入“其他语法” |
| 比较级/最高级 | **1–3%** | 0–1 | |

区间中点合计约 98%，可直接用作出题配比（中点：词汇 35 / 词性 23.5 / 介词 11.5 / 动词 10 / 代词 8.5 / 连词 6 / 比较 2 / 关系 1.5）。

### Part6（16 题）

| 题型 | 区间 | 备注 |
|---|---|---|
| 插入句 | **4（25%，固定）** | 格式规定，每篇 1 题 |
| 词汇（语境中的词/短语义） | **5–8（31–50%）** | |
| 语法（词性 + 动词时态/形态 + 代词） | **3–5** | 其中语境时态 ~2 |
| 连接副词（however/therefore…） | **~1（0–2）** | 单一来源（桐原） |

### Part7（54 题；各项互有重叠，不可相加）

| 题型 | 区间（题数） | 备注 |
|---|---|---|
| 细节/具体信息 | **20–25**（37–46%） | |
| 推断（suggested/implied/most likely/concluded） | **8–15** | |
| 主旨/目的 | **5–10** | |
| 同义词 | **2–4** | 多在多篇题组 |
| NOT | **1–3** | |
| 意图（聊天中引用语句） | **2** | |
| 插入句 | **2** | 单篇中 |
| 跨篇关联 | **6–10** | 与上面题型重叠 |
| JSON 补充：是非/选项比对（What is indicated/true） | **~10–12** | 与推断重叠，仅 junpei 单列 |
| JSON 补充：文本类型——邮件/书信 + 文章 | **约 23 篇中的 50–60%（约 12–14 篇）** | 单一来源 |
| JSON 补充：文本类型——短信/在线聊天 | **≥2 篇** | 由 2 道意图题推断 |
| JSON 补充：广告/通知-备忘录/表格-发票-日程/网页/评论 | **余下约 7–9 篇，无分类型计数** | 缺口 |

---

## 4. 2016 改版与趋势

**改版（新制 2016）**
- Part5：40 → **30** 题（[ETS RM-17-05](https://www.ets.org/Media/Research/pdf/RM-17-05.pdf)）。
- Part6：12 → **16** 题，每篇新增 1 道句子选择（插入句）题（RM-17-05；Cengage、toeicstory 248）。
- Part7：48 → **54** 题；单篇 9 篇（每篇 2–5 题，共 28 题）→ 10 篇（每篇 2–4 题，共 29 题）；多篇 4 组双篇（20 题）→ 2 组双篇 + 3 组三篇（25 题）（[toeicstory 102](https://www.toeicstory.co.kr/102)）。
- 新题型：短信/在线聊天（多人对话）、意图题、插入句、三篇阅读（[Cengage TOEIC 4e](https://ngl.cengage.com/assets/downloads/toeic4e9781337396530/toeic4e-intro.pdf)；新东方 2018 同列）。
- 实施时间：日本/韩国 2016-05-29；其他地区公开考试 2018-04 起（[新东方](http://toeic.xdf.cn/201803/10761795.html) 转述 ETS 2018-01 通知）。

**趋势（多为定性，可信度中低）**
- Part5：纯语法题减少（≤10 题/卷，2014 Herald），需要看语义的题增多；2026 YBM：形近词、一词多义、更宽的同义替换增多。
- Part7：干扰项更多“部分匹配”、正确答案更抽象（日本高分博客 2026）；多篇文本更长，需要通读，“What is concluded”问法增多（Hackers 2025 单场复盘）。
- 难度：ETS 试测 Part7 多篇 p 值最低（.42/.45），是最难的部分。

---

## 5. 缺口

1. **Part7 文本类型篇数基本没有数据**：只有 YBM 一个来源给出“邮件/书信 + 文章 50–60%”；短信/聊天 ≥2 篇是推断；广告、通知、表格、网页、评论等约 7–9 篇没有任何分类型计数。建议用官方题集自行统计（每套 23 篇）。
2. **中国大陆来源很少**：170 条中只有 1 条来自大陆（新东方，且只讲改版实施时间），没有大陆机构的题型分布统计；繁体中文来源 3 条（碁峰、常春藤为台湾出版方/媒体；prepedu 为繁中页面，所属地区未核）。主要证据来自日本（get-toeic 转韩国既出、trankyblog、mikan、junpei、桐原）和韩国（YBM toeicstory、釜山大）。
3. **Part7 题型分布只有两个日本来源（junpei、mikan）**，都没写样本量；没有大样本真题统计。
4. **Part6 没有大样本计数**，桐原是主要来源，fumi-eigo 为抄录。
5. **Part5 关系词、比较级证据弱**；大样本真题统计只有 trankyblog（180 题）和釜山大（870 题，口径不同）。
6. **时效**：最新的定量真题分析是 2023 年（trankyblog、釜山大），2024–2026 只有定性趋势。
7. ETS/IIBC 官方不公布题型比例；prepedu 等自称“官方统计”的说法不可信。

---

## 附录：source 记录全表（按 Part）

#### ALL（15 条）

| 类别 | 子类 | 份额/数量 | 年份 | 来源 | 可信度 | 备注 |
|---|---|---|---|---|---|---|
| format | Part5 questions | 30 | 2025 | [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) | high | IIBC official format page |
| format | Part6 questions | 16 (4 texts x 4; answers are word, phrase or sentence) | 2025 | [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) | high | IIBC official |
| format | Part7 single-passage questions | 29 | 2025 | [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) | high | IIBC official; also states sentence-insertion questions exist |
| format | Part7 multiple-passage questions | 25 | 2025 | [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) | high | IIBC official |
| format | Part7 single passages | 10 texts, 2-4 questions each | 2025 | [ETS](https://www.ets.org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf) | high | ETS Examinee Handbook (paper) |
| format | Part7 multiple passages | 5 sets (double or triple) x 5 questions | 2025 | [ETS](https://www.ets.org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf) | high | ETS Examinee Handbook |
| format | Part7 double/triple split | double 2 sets=10q; triple 3 sets=15q | 2016 | [東洋経済](https://toyokeizai.net/articles/-/109179?page=4) | high | also toeicstory_102 (2015) and mikan_p7 |
| 2016_change | Part5 count | 40 -> 30 | 2017 | [ETS](https://www.ets.org/Media/Research/pdf/RM-17-05.pdf) | high | ETS research memo, pre-update vs updated |
| 2016_change | Part6 count | 12 -> 16 (+1 sentence-choice item per text) | 2017 | [ETS](https://www.ets.org/Media/Research/pdf/RM-17-05.pdf) | high | ETS RM-17-05; sentence item per text: cengage_intro, toeicstory_248 |
| 2016_change | Part7 count | 48 -> 54 | 2017 | [ETS](https://www.ets.org/Media/Research/pdf/RM-17-05.pdf) | high | ETS RM-17-05 |
| 2016_change | Part7 single passages | 9 passages (2-5q, 28q) -> 10 passages (2-4q, 29q) | 2015 | [toeicstory（YBM）](https://www.toeicstory.co.kr/102) | high | YBM Korea TOEIC Committee blog |
| 2016_change | Part7 multiple passages | 4 double sets (20q) -> 2 double + 3 triple sets (25q) | 2015 | [toeicstory（YBM）](https://www.toeicstory.co.kr/102) | high |  |
| 2016_change | Part7 new item types | text-message/online chat (multi-writer), writer-intent items, sentence-insertion, triple passages | 2016 | [Cengage](https://ngl.cengage.com/assets/downloads/toeic4e9781337396530/toeic4e-intro.pdf) | high | Cengage TOEIC 4e intro; same list in xdf_2018 |
| 2016_change | rollout dates | Japan/Korea 2016-05-29; other public tests from 2018-04 | 2018 | [新东方](http://toeic.xdf.cn/201803/10761795.html) | high | 新东方 relays ETS 2018-01 release |
| difficulty | p-value by part (updated pilot forms E/F) | P5 .67/.68; P6 .55/.57; P7 .48/.55 (P7 single .53/.62, multi .42/.45) | 2017 | [ETS](https://www.ets.org/Media/Research/pdf/RM-17-05.pdf) | high | proportion correct; useful as difficulty prior, not frequency |

#### Part5（65 条）

| 类别 | 子类 | 份额/数量 | 年份 | 来源 | 可信度 | 备注 |
|---|---|---|---|---|---|---|
| grammar | tense | 6% (~1.8/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| grammar | pronoun | 6% (~1.8/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| grammar | determiner (those/each/whose...) | 3% (~0.9/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| grammar | participle | 4% (~1.2/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| grammar | other grammar | 6% (~1.8/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| word_form | noun slot | 10% (3/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| word_form | adjective slot | 4% (1.2/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| word_form | adverb slot | 8% (2.4/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| vocabulary | verb | 8% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| vocabulary | adjective | 8% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| vocabulary | noun | 8% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| vocabulary | adverb | 9% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| vocabulary | preposition (meaning) | 10% (3/30) | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| vocabulary | conjunction (meaning) | 5% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| vocabulary | phrase/idiom | 5% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high | Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here |
| grammar | TOTAL | 25% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high |  |
| word_form | TOTAL | 22% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high |  |
| vocabulary | TOTAL (incl. prep/conj/phrase) | 53% | 2021 | [get-toeic（韩 既出問題集3）](https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/) | medium-high |  |
| type | vocabulary | 30.0% (54/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | word_form | 25.6% (46/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | preposition | 10.6% (19/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | conjunction | 9.4% (17/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | adverb (choice) | 8.3% (15/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | verb form (tense/voice) | 7.7% (14/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | pronoun | 7.2% (13/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | comparative | 1.1% (2/180) | 2023 | [trankyblog（公式7-9）](https://trankyblog.com/toeic_part5) | medium | 公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification |
| type | vocabulary | 40.0% (12/30) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | word_form | 16.7% (5) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | preposition | 13.3% (4) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | verb | 10.0% (3) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | pronoun | 6.7% (2) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | comparative | 6.7% (2) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | adverb | 3.3% (1) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | conjunction | 3.3% (1) | 2016 | [eigo-koryaku](https://eigo-koryaku.com/?p=528) | low | one official problem-book test (30 q); tiny sample; tense/article 0 |
| type | grammar vs vocabulary | grammar >60%, vocabulary <40% | 2022 | [youlinguista.com](https://youlinguista.com/toeic-part5-tips/) | medium | 公式問題集7, 2 tests (60 q); exact figures only in chart image |
| grammar | tense | ~2 per test | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| grammar | pronoun | ~2 per test | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| grammar | determiner | ~1 per test | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| grammar | participle | ~1 per test | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| vocabulary | verb / noun / adjective / adverb | 2-3 each per test | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| vocabulary | preposition | ~3 per test | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| vocabulary | conjunction / phrase | 0 in some tests | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| word_form | noun | 2-3 per test | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis |
| type | grammar vs vocabulary | grammar ~20 / vocabulary ~10 (of 30) | 2016 | [toeicstory（YBM）](https://www.toeicstory.co.kr/464) | medium | expert quote, first months after 2016 update |
| type | grammar vs vocabulary | grammar 767/870 (88.2%), vocabulary 103/870 (11.8%) | 2023 | [釜山大硕论](https://www.dbpia.co.kr/journal/detail?nodeId=T16857240) | medium (definition differs) | Busan Nat'l Univ MA thesis; 29 YBM 기출 tests post-2016; VOCAB defined strictly as all 4 options same POS -> much lower vocab share than other sources |
| grammar_rank | frequency order of grammar categories | noun > adjective > adverb > preposition > clause/conjunction > determiner/pronoun > tense > passive > to-infinitive > modal | 2023 | [釜山大硕论](https://www.dbpia.co.kr/journal/detail?nodeId=T16857240) | medium | rank only; counts behind paywall |
| type | vocab / word_form / other grammar | 9-10 (30%) / 7-8 (25%) / 13-14 (45%) | 2025 | [www.englishtalk.jp](https://www.englishtalk.jp/025-toeic-part5-overview-parts-of-speech/) | low | claims IIBC reference but IIBC does not publish breakdown |
| type | word_form / vocab / pronoun+relative / paired expressions | ~30% / ~25% / ~10% / ~10% | 2026 | [toeic-taisaku-lab.com](https://toeic-taisaku-lab.com/toeic-part5-grammar-strategy/) | low | no sample stated |
| type | grammar vs vocabulary | grammar 60-70%, vocabulary 30-40%; word_form 25-30% | 2025 | [prepedu](https://prepedu.com/zh-hant/blog/toeic-reading-part-5) | low | claims 'ETS official stats' (unverified; ETS publishes none) |
| type | grammar vs vocabulary | grammar ~1/3, vocabulary ~2/3 | 2025 | [常春藤（台）](https://www.ivy.com.tw/column/cont/2025110517562325969) | low | Taiwan teacher column (常春藤); counts prep/conj choices as vocab |
| type | vocab / word_form / grammar / connectors | ~25% / ~30% / ~35% / ~10% | 2025 | [990prep.com](https://990prep.com/en/guides/toeic-part-5-strategies) | low | no sample stated |
| grammar_sub (practice bank) | preposition | 12.5% of 546 grammar items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | conjunction | 10.1% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | word-form | 10.1% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | relative pronoun | 8.2% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | verb pattern | 7.3% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | verb form | 7.1% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | gerund | 6.2% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | passive | 6.2% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | tense | 6.2% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | subject-verb agreement | 5.9% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | conditional | 5.3% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| grammar_sub (practice bank) | inversion | 5.3% | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part5-grammar-distribution) | very low | NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight |
| trend | grammar-only items | <=10 per test (was 10-12); more meaning-dependent items, e.g. two noun options after 'the' | 2014 | [Herald 经济](https://biz.heraldcorp.com/article/145160) | medium | pre-2016 Korean trend article |
| trend | vocabulary style | more confusable similar-form words (diagnostic vs diagnosable), polysemy, wider paraphrase | 2026 | [toeicstory（YBM）](https://www.toeicstory.co.kr/2577) | medium | YBM 2026 trend article (qualitative) |

#### Part6（20 条）

| 类别 | 子类 | 份额/数量 | 年份 | 来源 | 可信度 | 备注 |
|---|---|---|---|---|---|---|
| sentence_insertion | sentence choice | 4 per test (1 per text) = 25% | 2025 | [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html) | high | fixed by format; confirmed cengage_intro, toeicstory_248, mikan_p6 |
| type | vocabulary | ~6 of 16 | 2022 | [桐原 KIRIHARA](https://academy.kirihara.co.jp/blog/toeic/toeic-part6/) | medium | 桐原 KIRIHARA Online Academy |
| type | vocabulary | ~6 of 16 | 2025 | [fumi-eigo（抄桐原）](https://fumi-eigo.com/toeic-part6/) | low | identical table to KIRIHARA (likely copied) |
| type | sentence choice | ~4 of 16 | 2022 | [桐原 KIRIHARA](https://academy.kirihara.co.jp/blog/toeic/toeic-part6/) | medium | 桐原 KIRIHARA Online Academy |
| type | sentence choice | ~4 of 16 | 2025 | [fumi-eigo（抄桐原）](https://fumi-eigo.com/toeic-part6/) | low | identical table to KIRIHARA (likely copied) |
| type | grammar (Part5-type) | ~3 of 16 | 2022 | [桐原 KIRIHARA](https://academy.kirihara.co.jp/blog/toeic/toeic-part6/) | medium | 桐原 KIRIHARA Online Academy |
| type | grammar (Part5-type) | ~3 of 16 | 2025 | [fumi-eigo（抄桐原）](https://fumi-eigo.com/toeic-part6/) | low | identical table to KIRIHARA (likely copied) |
| type | tense (context) | ~2 of 16 | 2022 | [桐原 KIRIHARA](https://academy.kirihara.co.jp/blog/toeic/toeic-part6/) | medium | 桐原 KIRIHARA Online Academy |
| type | tense (context) | ~2 of 16 | 2025 | [fumi-eigo（抄桐原）](https://fumi-eigo.com/toeic-part6/) | low | identical table to KIRIHARA (likely copied) |
| type | connective / conjunctive adverb | ~1 of 16 | 2022 | [桐原 KIRIHARA](https://academy.kirihara.co.jp/blog/toeic/toeic-part6/) | medium | 桐原 KIRIHARA Online Academy |
| type | connective / conjunctive adverb | ~1 of 16 | 2025 | [fumi-eigo（抄桐原）](https://fumi-eigo.com/toeic-part6/) | low | identical table to KIRIHARA (likely copied) |
| type | vocabulary | ~2 per text (~8/test) | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM; vocab: verb/noun/adverb/phrase 1-2 each; word_form noun/adj > adverb |
| type | word_form / grammar | ~1 per text (~4/test) | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM; vocab: verb/noun/adverb/phrase 1-2 each; word_form noun/adj > adverb |
| type | sentence choice | 1 per text (4/test) | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM; vocab: verb/noun/adverb/phrase 1-2 each; word_form noun/adj > adverb |
| solve_type | context-independent grammar | ~8 of 16 | 2025 | [mikan](https://mikan.com/eigo-note/toeic-part6-guide) | medium | mikan 英語ノート |
| solve_type | context-dependent (tense/pronoun/conj/vocab) | ~4 of 16 | 2025 | [mikan](https://mikan.com/eigo-note/toeic-part6-guide) | medium | mikan 英語ノート |
| solve_type | sentence insertion | 4 of 16 | 2025 | [mikan](https://mikan.com/eigo-note/toeic-part6-guide) | medium | mikan 英語ノート |
| type | vocabulary / sentence / grammar | vocab just under half (~7), sentence 4, rest grammar | 2019 | [kumata-eigo.create-more.net](https://kumata-eigo.create-more.net/toeic_part6/) | low |  |
| solve_type | independent (single-sentence solvable) | about half | 2025 | [ej.alc.co.jp](https://ej.alc.co.jp/tag/TOEIC/toeic-auth-part6-20250622) | medium | ALC English Journal |
| passage_type | letter/email ('Dear') | 48-54% of practice items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part6-question-types) | very low | NOT exam data (AI practice bank) |

#### Part7（46 条）

| 类别 | 子类 | 份额/数量 | 年份 | 来源 | 可信度 | 备注 |
|---|---|---|---|---|---|---|
| question_type | detail / content (内容把握) | ~20 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | option-matching / true (選択肢照合) | ~12 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | inference (推測) | ~8 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | main idea / purpose (テーマ) | ~5 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | synonym (語彙) | ~3 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | NOT | ~2 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | intent (意図) | ~2 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | sentence insertion (文挿入) | ~2 of 54 | 2025 | [junpei-english](https://junpei-english.com/toeic-part7/) | medium | ゼロから極める英語塾; per-test approximation, sums to 54 |
| question_type | whole-text (purpose/theme) | 8-10 of 54 | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | mikan 英語ノート (updated 2026-07) |
| question_type | detail (who/when/where/what) | 20-25 of 54 | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | mikan 英語ノート (updated 2026-07) |
| question_type | hard items total | 21-23 of 54 | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | mikan 英語ノート (updated 2026-07) |
| question_type | inference (suggested/implied/most likely) | ~15 of 54 | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | mikan 英語ノート (updated 2026-07) |
| question_type | NOT | 0-3 of 54 | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | mikan 英語ノート (updated 2026-07) |
| question_type | intent | ~2 of 54 | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | mikan 英語ノート (updated 2026-07) |
| question_type | sentence insertion | 2 (single passages) of 54 | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | mikan 英語ノート (updated 2026-07) |
| question_type | intent | 2 of 54 | 2025 | [studying.jp](https://studying.jp/toeic/about-more/part7-2.html) | medium | STUDYing |
| distribution | synonym location | mostly in double/triple passages | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM |
| distribution | cross-reference (linking) items | ~1 per double set, ~2 per triple set (=> ~8/test) | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | also hackers_blog_p7 (2024): double 1, triple ~2 |
| distribution | cross-reference (linking) items | 1-2 per double set, 2-3 per triple set | 2020 | [碁峰（台）](https://dlcenter.gotop.com.tw/PDFSample/ARE001800.pdf) | medium | 碁峰 (Taiwan) TOEIC mock-test book sample PDF; year approx. |
| distribution | intent item location | 1 in each 2-q or 4-q single passage that is text-message chain / online chat | 2020 | [碁峰（台）](https://dlcenter.gotop.com.tw/PDFSample/ARE001800.pdf) | medium | implies >=2 chat/text passages per test (inferred) |
| distribution | sentence-insertion location | 1 in each 3-q or 4-q single passage; usually article / email-letter | 2020 | [碁峰（台）](https://dlcenter.gotop.com.tw/PDFSample/ARE001800.pdf) | medium |  |
| question_type | synonym (one real test, 2025-01-26 KR) | 3 | 2025 | [Hackers 讲师](https://www.hackers.co.kr/?c=s_toeic%2Ftoeic_board%2FB_TOEIC_QA&keywd=mheng_boardbanner_afterjumsu_241215&logger_kw=mheng_boardbanner_afterjumsu_241215&uid=1235120) | medium | Hackers instructor live review; single-passage q-count pattern 2-2-3-2-3-3-4-4-3-4; many 'What is concluded' items |
| passage_type | email/letter + article | 50-60% of passages | 2018 | [toeicstory（YBM）](https://www.toeicstory.co.kr/999) | medium-high | YBM, from 기출문제집 analysis |
| passage_type | genres listed | email/letter, ad, notice, article, text message, form/invoice/schedule, instructions/warranty, web page | 2026 | [mikan](https://mikan.com/eigo-note/toeic-part7-guide) | medium | no counts |
| passage_type | ETS directions examples | magazine/newspaper articles, e-mails, instant messages | 2025 | [ETS](https://www.ets.org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf) | high |  |
| question_type (practice bank) | detail | 57.3% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | inference | 16.3% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | synonym | 10.6% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | purpose | 7.8% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | calculation | 6.9% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | NOT | 5.9% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | reason | 4.5% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | intent | 3.8% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | cross-reference | 3.5% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| question_type (practice bank) | sentence insertion | 0.8% of 1325 items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data (AI-generated practice bank); multi-tag |
| passage_type (practice bank) | email | 11.6% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | text message / chat | 10.1% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | notice/announcement | 7.2% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | policy | 6.3% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | memo | 3.9% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | article | 3.5% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | review | 3.2% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | job posting | 3.2% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| passage_type (practice bank) | advertisement | 3.1% of items | 2026 | [scordia（AI 练习库）](https://scordia.net/blog/toeic-part7-question-types) | very low | NOT exam data; 478 items untagged |
| trend | distractors | more partial-match options and abstract correct answers | 2026 | [note.com](https://note.com/muu_toeic/n/n765255e9672b?hl=en) | low | Japanese high scorer blog (qualitative) |
| trend | linked passages | longer; whole-passage reading needed; 'What is concluded' wording rising | 2025 | [Hackers 讲师](https://www.hackers.co.kr/?c=s_toeic%2Ftoeic_board%2FB_TOEIC_QA&keywd=mheng_boardbanner_afterjumsu_241215&logger_kw=mheng_boardbanner_afterjumsu_241215&uid=1235120) | low | single test review |
