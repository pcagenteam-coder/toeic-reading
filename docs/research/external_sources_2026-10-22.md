# 外部资源补充检索（2026-10-22）

范围：在 `private_data/sources/github_inventory.md`（G1–G50）、`data/datasets_inventory.md`（D1–D10、R1–R17）、`data/strategies/strategy_library_v1.md` 之外，补查 ① 有开源许可的新制阅读题库 ② 日韩中阅读技巧与“目标分→最低必需”策略 ③ 带中文释义、有许可的 TOEIC 词表。
方法：GitHub 搜索 API（未认证，按 license 过滤 + `pushed:>2026-10-19`）、Hugging Face datasets API（`search=toeic` 等）、Kaggle（web_search）、web_search/web_fetch；下载一律用 `git clone --depth 1 --filter=blob:none --sparse` 或 HF `resolve/main` 直链，没有用 GitHub API 下载。
技巧部分见 `data/strategies/strategy_additions_v1_1.md`。

**一句话结论**
- **没有找到新的、有明确开源许可的新制阅读题库。** GitHub 带 MIT/Apache/CC 许可且名称含 TOEIC 的新仓库只有词汇 App；HF 上 13 个 `toeic` 数据集里有许可的全是词表；Kaggle 唯一题库 `tientd95/toeic-test` 许可为 Unknown（且就是已收录的 G7）。
- **sbljsc/toeic-practice-studio（G26）已用 sparse clone 拉下题库**：阅读 1,000 题（P5 300 / P6 160 / P7 540，10 套完整新制，全部带中文解析），但**与私有池已有的 `items_xdf1000.json` 是同一套书**（P5 300/300、P6 160/160、P7 539/540 选项逐字相同）→ **新增 0 题**，只作副本存档。
- **词表有实质收获**：找到 3 份有许可、带中文释义的 TOEIC 词表 + 1 份 MIT 通用英汉词典子集，已下载到公开池；并查明原 D6（`toeic_vocab_tw.json`，“许可不明”）就是 HF `kknono668/toeic-vocab-tw`，许可为 **CC BY-SA 4.0**。

---

## 1. 题库（P5/P6/P7）

| 资源 | 许可 | 内容 / 数量（实测） | 新制? | 建议用途 | 本次处理 |
|---|---|---|---|---|---|
| [sbljsc/toeic-practice-studio](https://github.com/sbljsc/toeic-practice-studio)（commit `74f0270`，2026-10-22） | 代码：自定“个人非商业学习”条款（非 OSI）；**题目/解析不授权**，`CONTENT-NOTICE.md` 自述“来源是一套第三方托业教材” | 全库 2,000 题/1,030 组；阅读 **1,000 题**：P5 300、P6 160（40 篇，39 篇第 4 空为整句插入）、P7 540（150 组：2 题组 32、3 题组 46、4 题组 22、5 题组 50）；1,000 题带中文翻译+解析；含意图/位置题 28 道 | ✅ 10 套完整新制 | **私有池（仅自用）**；与 `private_data/items/items_xdf1000.json` 重复，**不重复入库** | sparse clone 只拉 `content/question-pool/parts/part-5..7/*.md` + `pool.json`（过滤成 `pool_reading.json`），**未拉音频**；放 `private_data/sources/github/sbljsc_toeic-practice-studio/`（7.2 MB） |
| [kdeppaei/toeic-question-ocean](https://github.com/kdeppaei/toeic-question-ocean)（已在清单 G4） | MIT（代码与作者原创题） | sbljsc 维护者的核查（`question-sources.md`，2026-10-22）：按真实加载顺序共 1,443 题；其中 **336 题逐字取自 ESL Lounge**（`sourceType:"user"`，ESL Lounge 条款禁止转载）；剔除后 1,107 题，阅读 P5 328 / P6 120 / P7 357 | ✅ | 原创部分 **可进公开池候选**（需先按 `sourceType`/`sourceUrl` 剔除 ESL Lounge 题）；ESL Lounge 部分只能私有 | 未重复下载（私有池已有）；**修正 G4 结论**：不能整库当 MIT 用 |
| [Scordia](https://scordia.net/quiz) 网站 | 无开源许可（站方声明 AI 生成+编辑审校的原创题） | 阅读 2,992 题（文法 546 / 语汇 624 / P6 497 / P7 1,325）+ 模考 13 回 858 题，全部日文解析 | ✅ | **仅参考/外链**（解析写法、题型标签可借鉴，不抓取） | 未下载 |
| IIBC 官方样题 [sample05–07](https://www.iibc-global.org/toeic/test/lr/about/format/sample05.html)、ETS Sample Test PDF | ETS 版权，禁止复制 | 阅读样题若干；无解析 | ✅ | **仅外链**（模考前热身） | 未下载 |
| Kaggle [tientd95/toeic-test](https://www.kaggle.com/datasets/tientd95/toeic-test) | License: **Unknown** | 998 KB `toeic_test.json`，3,625 道 P5（CMU DSE 论文也引用此数） | 通用 | 已是 G7 `tranvien98/fill_toeic` 同一份 → 私有池 | 不处理 |
| HF `dddodddiiddoddo/toeic`、`cuongtm/Toeic_hacker_vol3`、`cuongtm/hacker_toeic_RC`、`messithanh2k/toeic`、`nggiabao19/toeic-tutor-v1` | 无许可（cardData 为空） | 出版物扫描件/合集 | — | **不用**（按既有规则，出版物盗版资源不下载） | 不处理 |
| GitHub 新仓库（MIT/Apache，2026-10 推送）：`ted23777/toeic-prep`（法语讲义 JSON）、`thinh12a10/Toeic_coach`（口语）、`lingo-sphere/frontend-web`（前端壳）、`potsung-yen/Toeic*`（词汇小游戏）、`meomun1/laura-toeic-ai-agent`、`Shinichi0713/english-study` | MIT / Apache-2.0 | 没有阅读题库文件 | — | **不用** | 已用 blob:none clone 列文件确认 |
| `nghiaxh/learn-toeic`（G50） | — | 仓库已删除/私有（clone 要求认证） | — | 不用 | 再次确认拿不到 |

**题库结论**：许可干净、可进**公开池**的完整新制套题，目前仍只有已入库的 **maximcuynat 6 套 600 题（MIT）**；下一步能扩公开池的只有 **kdeppaei 剔除 ESL Lounge 后的原创阅读约 805 题**（需写过滤脚本并抽查）。要再扩，只能自产（`data/templates` + LLM 出题 + 人工审）。

---

## 2. 词表（中文释义 / 按目标分分层）

| 资源 | 许可 | 内容 / 数量（实测） | 中文? | 分层? | 建议用途 | 位置 |
|---|---|---|---|---|---|---|
| [LEE-WHITE/toeic-vocab-tw](https://huggingface.co/datasets/LEE-WHITE/toeic-vocab-tw)（v110.5，2026-01-10） | **CC BY 4.0** | 9,537 词条（9,453 个不同词），每条：繁中释义、词性、词形变化、中英例句、15 个商务主题；按 5★–1★ 分组（5★ 420 / 4★ 2,695 / 3★ 4,784 / 2★ 1,314 / 1★ 324） | 繁中 | 星级（重要度），无分数段 | **公开池**：点词即查的 TOEIC 语境释义主库（署名即可，无传染） | `data/open_items/LEE-WHITE_toeic-vocab-tw/`（8.4 MB，原样） |
| [kknono668/toeic-vocab-tw](https://huggingface.co/datasets/kknono668/toeic-vocab-tw)（v112.0，2026-02-05）；同内容镜像 `jcoffice/`、`AnthonyLiu/`、`moomoosir/`（均 CC BY-SA 4.0） | **CC BY-SA 4.0** | 11,238 条（11,154 个不同词），比 LEE-WHITE 多 `toeic_score_range` 和 `exam_tips`；分数段：0-400 1,345 / 400-600 3,590 / 600-780 3,521 / 780-900 2,104 / 900+ 678 | 繁中 | ✅ **按分数段** | **公开池**（衍生词表须同样 CC BY-SA 4.0 发布、署名）；“按目标分分层”的现成来源 | `data/open_items/kknono668_toeic-vocab-tw/`（json.gz 6.3 MB） |
| ↳ 原 D6 `private_data/sources/toeic_vocab_tw.json` | 原记“来源/许可不明” → **就是 kknono668 版**（11,238 条一致，11,185 条释义逐字相同） | — | — | — | **许可已查明：CC BY-SA 4.0**，可从私有池升级；但“疑似 LLM 生成”的判断仍成立（见 §2.1） | 不动原文件，只更新记录 |
| [chunchiech/EnglishCoach](https://github.com/chunchiech/EnglishCoach)（commit `6efe6c7`，2026-10-21） | **MIT** | `toeic_3600.csv` 3,600 词：音标、繁中释义、英例句+繁中译、词性、主题/子主题、Part 标签；分级 `toeic_basic` 1,200 / `toeic_advanced` 1,400 / `toeic_gold` 1,000，难度 1–5 | 繁中 | 三级（对应分数未说明） | **公开池**：例句+译文最整齐的小词表，适合做“每日词包”；与 kknono668 重叠 3,501 词 | `data/open_items/chunchiech_EnglishCoach/`（只拿 csv+LICENSE） |
| [skywind3000/ECDICT](https://github.com/skywind3000/ECDICT)（commit `bc015ed`） | **MIT** | 全库 770,611 词条；本次按 NGSL/TSL 词形 + 上述 3 份 TOEIC 词表 + 公开题库出现过的词（共 20,532 个）过滤出 **17,894 条**（覆盖 87%，缺的多为短语/罕见词形），字段：音标、**简体中文释义**、柯林斯星级、牛津 3000、考试标签、BNC/COCA 词频、词形变化 `exchange` | **简中** | 无 TOEIC 分层（有词频） | **公开池**：点词即查的**兜底词典**（任何词都能查到、离线、简体），`exchange` 可把 offered→offer 还原 | `data/open_items/skywind3000_ECDICT/ecdict_toeic_subset.csv`（2.0 MB） |
| [aalmaz1/pixelwordhunter](https://github.com/aalmaz1/pixelwordhunter) | MIT | 600 个商务词，俄/韩释义，无中文 | ✗ | 按主题 | 仅参考 | 未下载 |
| `KyleBing/english-vocabulary`（BSD-3）、`kajweb/dict`（无许可，有道词书含 BEC） | BSD-3 / 无 | 无 TOEIC 词书（前者只有中高考/四六级/托福等） | 简中 | — | 不用 | — |
| Kaggle [jimregan/toeic-service-list](https://www.kaggle.com/datasets/jimregan/toeic-service-list) | CC BY-SA 4.0 | 即 TSL（已有 D5） | ✗ | — | 已有 | — |

### 2.1 质量与使用提醒（抽样，未逐条审）
- **kknono668 / LEE-WHITE / chunchiech 三份都有明显 LLM 生成痕迹**：词条里混有屈折形（`careers`、`expanding`、`believed`、`airports`）、人名（`tony` 被放在 900+）、句型（`A be followed by B`）；chunchiech 有个别错释（`ever` 释成“從未”）。随机抽 20+12 条，其余释义基本正确。→ **释义可用，分层和“高频”标签不可当真题统计依据**。
- **繁→简**：三份 TOEIC 词表都是繁体，建议构建时用 OpenCC（Apache-2.0）`t2s` 转换后再入 App。
- **ShareAlike**：只要 App 内置的词表文件含 kknono668 内容，该文件就得以 CC BY-SA 4.0 发布并署名；代码不受影响。只需星级/释义时优先用 LEE-WHITE（CC BY），分数段字段才去 kknono668 取。

### 2.2 推荐组合（点词即查 + 分层）
1. **查词顺序**：词形还原（ECDICT `exchange` + TSL/NGSL 词形表）→ LEE-WHITE（TOEIC 语境繁中→简）→ ECDICT（简中兜底）。离线包预计 < 5 MB（压缩后）。
2. **按目标分分层（我们自己的分层，比 LLM 标签可信）**：以研究型频率表为骨架、LLM 词表只补释义——
   - 目标 <600：NGSL 核心 ~2,800 词里出现在 TOEIC 题里的部分 + kknono668 `0-400/400-600` 与之交集；
   - 600–730：TSL 1,250（TOEIC 专属）+ kknono668 `600-780` 交集；
   - 730–860：BSL（商务）+ kknono668 `780-900` 交集；900+ 不做。
   - 每档再用我们题库（maximcuynat + 私有题）的实际出现次数排序，只推“题里真出现过的词”。这一步是推断设计，尚未实现。

---

## 3. 技巧来源（摘要，详见 strategy_additions_v1_1.md）

| 来源 | 地区 | 性质 | 用到的内容 |
|---|---|---|---|
| [旺文社 英語の友：リーディングの時間配分（470/600/730/860）](https://eigonotomo.com/toeic/toeic-lr_reading) | 日 | 出版社（濵﨑潤之輔等“奪取の方法”系列配套） | 分数档时间表、各 Part 目标正答率、低分档“只答第一题”、语汇题即涂 |
| [ふみ英語：600点狙いの塗り絵と捨て問](https://fumi-eigo.com/toeic-skip-question/) | 日 | 社会人博主（875→485→830） | 塗り絵数量按目标分、600 档弃题清单、最后 3 分钟停笔涂卡 |
| [トイガイド：捨てる問題はどれ？](http://toiguide.jp/reading-abandon/) | 日 | 980 分作者 | 各档可弃题数与所需答对数、P7“终点线”（175/185）、时间紧时优先同义词题 |
| [原田英語：塗り絵戦略](https://www.haradaeigo.com/studyhack/column/toeic3-guessing-strategy-time-shortage/) | 日 | 教学站 | 统一字母、短文本优先、残余时间怎么选 |
| [시원스쿨LAB：600점대 목표라면 '이것'은 포기](https://m.blog.naver.com/siwonschoollab/221907410585) | 韩 | 培训机构讲师 | R200≈43 题、P5/6/7 各档目标数、P5 语法范围裁剪、双/三篇全弃 |
| [해커스 박영선：Part7 단기간 고득점 비법](https://hackers.ac/community/secret-method/218892) | 韩 | Hackers 讲师（2015，旧制题数，方法仍适用） | 按每篇题数分配速度、4–5 题篇只先读两题、改写笔记、对题也复盘 |
| [YBM 하나쌤 RC 特讲](https://www.youtube.com/watch?v=paE50R6hog8) | 韩 | YBM 讲师 | P5“最多想三次”、先结构后翻译 |
| [mikan：Part5 目标点数别時間](https://mikan.com/eigo-note/toeic-part5-guide)、[motitown：Part5 满分解法](https://motitown.com/vocabulary/topics/toeic/toeic-part-5-perfect-score/) | 日 | 教学站 | P5 按目标分配时（600:15 / 700:12 / 800+:10 分钟）；各题型秒数（已与 SL-P5-02 重合） |
| [Fog's Blog 托业经验](https://f0ghua.github.io/toeic_experience/)、[Power TOEIC 中文](https://power-toeic.com/zh-TW/tips/reading) | 中 | 个人/教学站 | 来不及就放弃“需要看全篇才能答”的题；目的题看前 1–2 句（已有） |

**中文来源的缺口**：本轮能打开的知乎/新东方页面大多是 2016–2022 年泛泛的“先看题”“别想当然”，和 v1 里已有的新东方/B 站 49 条重复，没有找到“按目标分弃题”的中文高赞细则（知乎多为专栏营销文）。中文侧的价值主要已在 v1 吸收。

---

## 4. 本次落盘文件

公开仓库 `toeic-reading/`：
- `docs/research/external_sources_2026-10-22.md`（本文）
- `data/strategies/strategy_additions_v1_1.md`
- `data/open_items/LEE-WHITE_toeic-vocab-tw/`（LICENSE、README.md、toeic_vocabulary.json、SOURCE.md）
- `data/open_items/kknono668_toeic-vocab-tw/`（LICENSE、README.md、toeic_vocabulary.json.gz、SOURCE.md）
- `data/open_items/chunchiech_EnglishCoach/`（LICENSE、toeic_3600.csv、SOURCE.md）
- `data/open_items/skywind3000_ECDICT/`（LICENSE、ecdict_toeic_subset.csv、SOURCE.md）

私有仓库 `toeic-reading/private_data/`：
- `sources/github/sbljsc_toeic-practice-studio/`（parts/part-5..7 共 490 个 md、pool_reading.json、LICENSE.md、CONTENT-NOTICE.md、README.md、question-sources.md、vocab_reference_ccby_from_LEE-WHITE.json）
- `sources/github_inventory.md`：G4、G26 结论更新

## 5. 建议下一步
1. 写 `kdeppaei` 过滤脚本：剔除 `sourceType=user`/`esl-lounge.com` 题，剩余原创阅读题抽查 50 道后进公开池。
2. 做离线查词包：OpenCC 繁→简 + 合并 LEE-WHITE 与 ECDICT 子集 → `app/` 用的单文件 JSON（署名页列出 CC BY / MIT 来源）。
3. 按 §2.2 用 NGSL/TSL/BSL × 题库出现频次生成自有分层词包，kknono668 只作参考字段。
4. sbljsc 副本无需再处理；如以后要用它的 md 格式题组结构（`blanks` + `{{blank:N}}`），可参考 `md-question-store` 设计。
