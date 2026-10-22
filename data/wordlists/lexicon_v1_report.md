# lexicon_v1 报告（A6 词表清洗）

生成：`python3 data/wordlists/build_lexicon.py`（ECDICT 模式：full；随机种子 20261022）

## 产出
| 文件 | 内容 | 许可 |
|---|---|---|
| `data/wordlists/lexicon_v1.json` | 9950 词条（单词 8501，短语 1449）；字段 headword/pos/zh(≤20 字简体)/forms/tier/source/license/kind/item_freq/lists | CC BY 4.0 整体署名（含 MIT 内容） |
| `data/wordlists/lexicon_v1_sa.json` | 981 条 kknono668 托业语境释义覆盖层（只对主文件 source=ED 的词） | CC BY-SA 4.0（独立文件） |
| `data/wordlists/vocab_test_pool.json` | 真词 400（每档 100）+ 假词 71（15.1%） | 同主文件 |
| `data/wordlists/ecdict_items_supplement.csv` | ECDICT 子集外、本词典用到的行（无完整 ECDICT 时复跑用） | MIT |
| `data/wordlists/BSL_120_*.csv`、`NGSL_12_stats.csv` | 从 handoff 副本拷入（原 newgeneralservicelist.com），只用名单/排名 | CC BY-SA 4.0（原样） |

## 释义来源（按词条）
- LEE-WHITE（CC BY，托业语境）：7883
- EnglishCoach（MIT，托业语境）：474
- ECDICT（MIT，通用兜底）：1575
- 项目自编补充（CC BY，ECDICT 未收的 app/webinar 等）：18
- 按题内 token 计：LW 55.8% / EC 8.8% / ED 34.7%

## 清洗
- 繁→简：OpenCC `tw2sp`（含台湾用语转换，如 軟體→软件）；去括注，按义项累加截到 ≤20 字。
- 读入原始条目：LEE-WHITE 9537，EnglishCoach 3600。
- 删除：人名/地名 343（例：LW:vancouver, LW:samsung, LW:soleil, LW:helga, LW:amanda, LW:detroit, LW:frodo, LW:andrew）；句型/占位符/非法词头 33（例：LW:entrust A with B, LW:blame A on B, LW:do A a favor, LW:give A an advance, LW:have something to do with）；空释义 1。
- 纯变形词并入词元：1262（例：questions->question, employees->employee, customers->customer, products->product, sales->sale, companies->company, services->service, details->detail, problems->problem, items->item）；-ed/-ing 且原库标为形容词/介词等的保留为独立词条（following、qualified 类）。词元判定：NGSL/TSL/BSL 词形表 → ECDICT exchange。
- 词典里查无此词（LLM 拼错/混入西里尔字母等）：130（例：LW:infographic, LW:edinborough, LW:jetryan, LW:aybelline, LW:toiec, LW:citidine, LW:ponzi, LW:doenim）。
- 人工改正：ever→曾经；永远；究竟（EnglishCoach 错释“从未”）。
- 题库里出现、但三份托业词表没有的词，用 ECDICT 补词条（去掉只有人名/地名义项、只有大写专名条目的）。

## 分档（自建，NGSL/TSL/BSL 名单 + 公开题库词频）
题库文本：items_open_kdeppaei.json（26841 token）, items_open_maximcuynat.json（38339 token）, items_pilot_v1.json（3560 token）, items_v0.json（432 token）；只取 stem/q/options/text/header/thread/title 英文字段。

| 档 | 词数 | 题内 token | 累计 token 覆盖 |
|---|---|---|---|
| core | 1000 | 46336 | 69.1% |
| 600 | 1532 | 9631 | 83.5% |
| 730 | 1742 | 8612 | 96.3% |
| 860 | 1349 | 1156 | 98.1% |
| 未分档（只供查词） | 4327 | 1543 | — |

规则：core=NGSL 前 1000；600=NGSL 1001–2000 + TSL 前 400 或题内≥3；730=其余 TSL + 题内出现的 NGSL 2001+ + BSL 前 600 或题内≥3 + 非名单词题内≥5；860=其余 NGSL + BSL（题内出现或前 1200）+ 题内≥2 + LEE-WHITE 4★+ 且题内出现。短语不分档。kknono668 分数段没有参与（避免 SA 与 LLM 标签）。

## 覆盖率（全部公开题 4 个文件）
- 计入 token 67041（另有专名 1347、单字母 512 不计）
- **离线释义 token 覆盖率 99.97%**（含专名为分母时 98.00%）；覆盖到的不同词元 3753
- 未覆盖 20 token / 15 种，前 40：fjallstigen(5), halversenglass(2), thoroughest(1), hourlyness(1), afternoonly(1), interdepartmentally(1), conciser(1), harborviewhotel(1), generative-ai(1), kettleandkin(1), meridianworks(1), harlowtrade(1), retendering(1), packhouses(1), torvaldfields(1)
- 专名示例（判定：首字母大写且全文从未小写出现、词典无普通义）：Priya, Ferreira, Lindqvist, Halvorsen, Adeyemi, Okonkwo, Ingrid, Solheim, Daniel, Fenwick, Raghunathan, Oyelaran, Ravi, Northgate, Okonjo, Ashgrove, Omar, Ortiz, Marcus, Nwachukwu, TL, Becker, Dana, Aguirre, Tobias

## 词汇量测试题池
- 每档 100 真词（按题内频次 5 层均匀抽，排除虚词、NGSL 前 150）+ 71 假词。
- 假词例：alloweely, antrunt, attly, auckwarede, aulagesse, autsoccurn, birstathug, closion, comict, conequent, contiont, coomly, cormary, covist, ditcherse

## 遗留 / 注意
- 释义来自 LLM 生成词表（LEE-WHITE/EnglishCoach），只抽查过；ECDICT 兜底释义是通用义，托业语境不一定贴切（可加载 SA 覆盖层改善 981 词）。
- 词元归并依赖词形表，同形异义（found/left/rose）会并到高频词元；-ed/-ing 形容词只按原库词性保留，可能有漏。
- 分档阈值是推断设计（题库仅约 1,500 题，频次稀疏），需要后续用真实答题数据校准。
- 专名识别是启发式：句首大写的生僻真词若词典没有，会被算专名而不计入分母。
- 无完整 ECDICT 时复跑，假词过滤只能用子集+补充表，结果会略有不同（释义不变）。
