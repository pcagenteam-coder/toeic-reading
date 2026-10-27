# 难度重评 v2 报告（UX_SPEC_v2 §6）

- 方法：LLM（deepseek-v4.1-flash，Kunyou + igrok 双端点）按固定 rubric + 7 条锚定示例，P5 每 5 题一次、P6/P7 每篇一次调用；输出 ETS 风格特征（CEFR 最难词、干扰项强度 0–3、定位距离、认知类型、同义替换、句法复杂度、句长、用时）+ 0–100 难度分。
- 档位由分数固定映射：<35 基础(<500) / 35–54 进阶(500–650) / 55–74 熟练(650–800) / ≥75 真考+(800+)；新 difficulty_est(1–5)：<25→1, 25–39→2, 40–54→3, 55–69→4, ≥70→5。
- 文件：公开 `data/difficulty/difficulty_v2_open.json`；私有 `private_data/difficulty/difficulty_v2_private.json`（id→{score,band,diff1_5,features,chapter,technique_zh}）。

## 公开池

- 题数 1511，已评 1511，未评 0；LLM 自报档与分数映射不一致 1（以分数为准）。

### 分布：题源 × Part × 档

| 题源 | Part | 基础 <500 | 进阶 500–650 | 熟练 650–800 | 真考+ 800+ | 合计 | 均分 |
|---|---|---|---|---|---|---|---|
| kdeppaei | P5 | 84 | 167 | 73 | 4 | 328 | 44.2 |
| kdeppaei | P6 | 36 | 63 | 20 | 0 | 119 | 42.1 |
| kdeppaei | P7 | 152 | 130 | 71 | 4 | 357 | 39.8 |
| maximcuynat | P5 | 42 | 100 | 37 | 1 | 180 | 44.1 |
| maximcuynat | P6 | 20 | 38 | 38 | 0 | 96 | 48.7 |
| maximcuynat | P7 | 38 | 138 | 135 | 13 | 324 | 51.7 |
| pilot | P5 | 18 | 31 | 10 | 1 | 60 | 42.3 |
| pilot | P6 | 4 | 10 | 6 | 0 | 20 | 46.9 |
| pilot | P7 | 4 | 16 | 5 | 2 | 27 | 47.4 |
| **合计** | | **398** (26%) | **693** (46%) | **395** (26%) | **25** (2%) | **1511** | |

### 与旧 difficulty_est 对比

| 旧 est | n | 基础 | 进阶 | 熟练 | 真考+ | 新均分 | 新 est 均值 |
|---|---|---|---|---|---|---|---|
| 1 | 11 | 8 | 3 | 0 | 0 | 29.9 | 1.82 |
| 2 | 462 | 176 | 234 | 51 | 1 | 39.3 | 2.51 |
| 3 | 686 | 185 | 329 | 169 | 3 | 43.8 | 2.84 |
| 4 | 313 | 29 | 126 | 150 | 8 | 53.1 | 3.43 |
| 5 | 39 | 0 | 1 | 25 | 13 | 69.2 | 4.46 |

- 旧 est vs 新分 Spearman ρ = 0.396（n=1511）；est 值变动 920 题。
- **锚定（kdeppaei 题源自带 400/600/800 级）**：与 LLM 分 Spearman ρ = 0.416（n=804）；分 Part：P5 ρ=0.56，P6 ρ=0.22，P7 ρ=0.48
  - 各级 LLM 均分：400级 35.1（n=52），600级 35.3（n=300），800级 47.1（n=452）

### 特征 × 档（均值）

| 档 | 干扰项 0–3 | 句法 1–3 | 用时 s | 跨句/跨段/跨篇占比 | 推断/NOT/插入占比 | C1+ 词占比 |
|---|---|---|---|---|---|---|
| 基础 | 0.93 | 1.48 | 20 | 1% | 0% | 0% |
| 进阶 | 1.52 | 1.82 | 27 | 11% | 8% | 2% |
| 熟练 | 1.89 | 2.03 | 41 | 57% | 53% | 20% |
| 真考+ | 2.24 | 2.20 | 58 | 76% | 76% | 68% |

### 缺口：题型 × 档（公开池；<20 标红；规格目标公开池每档每题型 ≥30）

| 题型 | 基础 | 进阶 | 熟练 | 真考+ | 合计 | 缺口（补到 20 / 补到 30） |
|---|---|---|---|---|---|---|
| P5.VERB_FORM | 20 | 86 | 52 | <span style="color:red">**2**</span> | 160 | 18 / 38 |
| P5.WORD_FORM | 69 | 50 | <span style="color:red">**5**</span> | <span style="color:red">**0**</span> | 124 | 35 / 55 |
| P5.PREP | <span style="color:red">**19**</span> | 37 | <span style="color:red">**4**</span> | <span style="color:red">**0**</span> | 60 | 37 / 67 |
| P5.PAIR_GRAMMAR | <span style="color:red">**9**</span> | <span style="color:red">**18**</span> | 24 | <span style="color:red">**2**</span> | 53 | 31 / 67 |
| P5.VOCAB | <span style="color:red">**7**</span> | 26 | <span style="color:red">**17**</span> | <span style="color:red">**2**</span> | 52 | 34 / 68 |
| P5.CONNECTOR_MIX | <span style="color:red">**2**</span> | 32 | <span style="color:red">**4**</span> | <span style="color:red">**0**</span> | 38 | 54 / 84 |
| P5.RELATIVE | <span style="color:red">**3**</span> | 27 | <span style="color:red">**5**</span> | <span style="color:red">**0**</span> | 35 | 52 / 85 |
| P5.PRONOUN | <span style="color:red">**8**</span> | <span style="color:red">**7**</span> | <span style="color:red">**1**</span> | <span style="color:red">**0**</span> | 16 | 64 / 104 |
| P5.CONJ | <span style="color:red">**1**</span> | <span style="color:red">**10**</span> | <span style="color:red">**4**</span> | <span style="color:red">**0**</span> | 15 | 65 / 105 |
| P5.COMPARATIVE | <span style="color:red">**6**</span> | <span style="color:red">**5**</span> | <span style="color:red">**4**</span> | <span style="color:red">**0**</span> | 15 | 65 / 105 |
| P6.INDEPENDENT | 54 | 90 | <span style="color:red">**15**</span> | <span style="color:red">**0**</span> | 159 | 25 / 45 |
| P6.INSERTION | <span style="color:red">**0**</span> | <span style="color:red">**3**</span> | 39 | <span style="color:red">**0**</span> | 42 | 57 / 87 |
| P6.CTX_VOCAB | <span style="color:red">**2**</span> | <span style="color:red">**7**</span> | <span style="color:red">**5**</span> | <span style="color:red">**0**</span> | 14 | 66 / 106 |
| P6.CTX_TENSE | <span style="color:red">**2**</span> | <span style="color:red">**7**</span> | <span style="color:red">**0**</span> | <span style="color:red">**0**</span> | 9 | 71 / 111 |
| P6.CTX_CONJ_ADV | <span style="color:red">**0**</span> | <span style="color:red">**4**</span> | <span style="color:red">**5**</span> | <span style="color:red">**0**</span> | 9 | 71 / 111 |
| P6.CTX_PRONOUN | <span style="color:red">**2**</span> | <span style="color:red">**0**</span> | <span style="color:red">**0**</span> | <span style="color:red">**0**</span> | 2 | 78 / 118 |
| P7.DETAIL | 111 | 131 | 35 | <span style="color:red">**0**</span> | 277 | 20 / 30 |
| P7.CROSS_REF | <span style="color:red">**1**</span> | <span style="color:red">**9**</span> | 77 | <span style="color:red">**15**</span> | 102 | 35 / 65 |
| P7.MAIN_PURPOSE | 32 | 27 | <span style="color:red">**8**</span> | <span style="color:red">**0**</span> | 67 | 32 / 55 |
| P7.REASON | <span style="color:red">**10**</span> | 33 | <span style="color:red">**9**</span> | <span style="color:red">**0**</span> | 52 | 41 / 71 |
| P7.INFERENCE | <span style="color:red">**3**</span> | <span style="color:red">**14**</span> | 34 | <span style="color:red">**1**</span> | 52 | 42 / 72 |
| P7.DETAIL_NUMBER | 26 | <span style="color:red">**12**</span> | <span style="color:red">**2**</span> | <span style="color:red">**0**</span> | 40 | 46 / 80 |
| P7.REQUEST_ACTION | <span style="color:red">**7**</span> | 22 | <span style="color:red">**3**</span> | <span style="color:red">**0**</span> | 32 | 50 / 88 |
| P7.TRUE_INDICATED | <span style="color:red">**1**</span> | <span style="color:red">**18**</span> | <span style="color:red">**10**</span> | <span style="color:red">**0**</span> | 29 | 51 / 91 |
| P7.NOT_TRUE | <span style="color:red">**0**</span> | <span style="color:red">**5**</span> | <span style="color:red">**8**</span> | <span style="color:red">**0**</span> | 13 | 67 / 107 |
| P7.INTENT | <span style="color:red">**0**</span> | <span style="color:red">**2**</span> | <span style="color:red">**10**</span> | <span style="color:red">**0**</span> | 12 | 68 / 108 |
| P7.SYNONYM | <span style="color:red">**0**</span> | <span style="color:red">**7**</span> | <span style="color:red">**1**</span> | <span style="color:red">**0**</span> | 8 | 72 / 112 |
| P7.INSERTION | <span style="color:red">**0**</span> | <span style="color:red">**0**</span> | <span style="color:red">**7**</span> | <span style="color:red">**1**</span> | 8 | 72 / 112 |
| P7.INFER_NEXT | <span style="color:red">**0**</span> | <span style="color:red">**1**</span> | <span style="color:red">**5**</span> | <span style="color:red">**1**</span> | 7 | 73 / 113 |
| P7.INFER_WHO | <span style="color:red">**3**</span> | <span style="color:red">**2**</span> | <span style="color:red">**0**</span> | <span style="color:red">**0**</span> | 5 | 75 / 115 |
| P7.CALC_LOOKUP | <span style="color:red">**0**</span> | <span style="color:red">**1**</span> | <span style="color:red">**2**</span> | <span style="color:red">**1**</span> | 4 | 76 / 116 |

- 合计需补：到每格 20 题 1643 题；到每格 30 题 2691 题。

### 原创难题补充需求（公开池，按缺口排序前 20 格）

| 题型 | 档 | 现有 | 补到 30 |
|---|---|---|---|
| P7.TRUE_INDICATED | 真考+ | 0 | 30 |
| P7.SYNONYM | 真考+ | 0 | 30 |
| P7.SYNONYM | 基础 | 0 | 30 |
| P7.REQUEST_ACTION | 真考+ | 0 | 30 |
| P7.REASON | 真考+ | 0 | 30 |
| P7.NOT_TRUE | 真考+ | 0 | 30 |
| P7.NOT_TRUE | 基础 | 0 | 30 |
| P7.MAIN_PURPOSE | 真考+ | 0 | 30 |
| P7.INTENT | 真考+ | 0 | 30 |
| P7.INTENT | 基础 | 0 | 30 |
| P7.INSERTION | 进阶 | 0 | 30 |
| P7.INSERTION | 基础 | 0 | 30 |
| P7.INFER_WHO | 真考+ | 0 | 30 |
| P7.INFER_WHO | 熟练 | 0 | 30 |
| P7.INFER_NEXT | 基础 | 0 | 30 |
| P7.DETAIL_NUMBER | 真考+ | 0 | 30 |
| P7.DETAIL | 真考+ | 0 | 30 |
| P7.CALC_LOOKUP | 基础 | 0 | 30 |
| P6.INSERTION | 真考+ | 0 | 30 |
| P6.INSERTION | 基础 | 0 | 30 |

### 手册主章分布

第1章 236 / 第2章 187 / 第3章 122 / 第4章 58 / 第5章 152 / 第6章 57 / 第7章 4 / 第8章 391 / 第9章 123 / 第10章 80 / 第11章 101

## 私有池

- 题数 4855，已评 4855，未评 0；LLM 自报档与分数映射不一致 2（以分数为准）。

### 分布：题源 × Part × 档

| 题源 | Part | 基础 <500 | 进阶 500–650 | 熟练 650–800 | 真考+ 800+ | 合计 | 均分 |
|---|---|---|---|---|---|---|---|
| 2troll | P5 | 5 | 6 | 1 | 0 | 12 | 38.8 |
| 2troll | P6 | 3 | 4 | 1 | 0 | 8 | 41.5 |
| 2troll | P7 | 2 | 4 | 2 | 0 | 8 | 46.0 |
| asaiibowl | P5 | 19 | 35 | 31 | 10 | 95 | 50.8 |
| asaiibowl | P6 | 15 | 26 | 15 | 0 | 56 | 46.4 |
| asaiibowl | P7 | 27 | 66 | 70 | 2 | 165 | 50.0 |
| bonnie8536 | P5 | 58 | 155 | 80 | 7 | 300 | 46.4 |
| bonnie8536 | P6 | 45 | 87 | 47 | 1 | 180 | 45.7 |
| bonnie8536 | P7 | 36 | 106 | 88 | 5 | 235 | 49.6 |
| eddychang0630 | P5 | 25 | 49 | 17 | 2 | 93 | 43.6 |
| eddychang0630 | P6 | 1 | 5 | 6 | 0 | 12 | 55.2 |
| eddychang0630 | P7 | 2 | 10 | 11 | 1 | 24 | 53.8 |
| ets1000_vol4 | P5 | 126 | 145 | 29 | 0 | 300 | 38.5 |
| ets1000_vol4 | P6 | 28 | 78 | 53 | 1 | 160 | 47.7 |
| ets1000_vol4 | P7 | 49 | 241 | 229 | 21 | 540 | 52.4 |
| grittingleo_4tests | P5 | 13 | 61 | 45 | 1 | 120 | 49.9 |
| grittingleo_4tests | P6 | 9 | 30 | 24 | 1 | 64 | 49.1 |
| grittingleo_4tests | P7 | 18 | 88 | 103 | 7 | 216 | 53.5 |
| nahuly | P5 | 19 | 33 | 6 | 1 | 59 | 40.3 |
| nekonotestudio | P5 | 33 | 55 | 12 | 0 | 100 | 40.2 |
| ninejubu | P5 | 106 | 254 | 229 | 46 | 635 | 50.9 |
| ninejubu | P6 | 22 | 36 | 6 | 0 | 64 | 40.0 |
| ninejubu | P7 | 42 | 42 | 12 | 0 | 96 | 37.4 |
| seikaikyo | P5 | 23 | 40 | 15 | 1 | 79 | 43.2 |
| seikaikyo | P6 | 38 | 85 | 13 | 0 | 136 | 40.5 |
| seikaikyo | P7 | 23 | 47 | 28 | 0 | 98 | 45.4 |
| xdf2019_1000 | P5 | 73 | 144 | 78 | 5 | 300 | 45.1 |
| xdf2019_1000 | P6 | 11 | 75 | 72 | 2 | 160 | 52.8 |
| xdf2019_1000 | P7 | 30 | 201 | 275 | 34 | 540 | 55.8 |
| **合计** | | **901** (19%) | **2208** (45%) | **1598** (33%) | **148** (3%) | **4855** | |

### 与旧 difficulty_est 对比

| 旧 est | n | 基础 | 进阶 | 熟练 | 真考+ | 新均分 | 新 est 均值 |
|---|---|---|---|---|---|---|---|
| 1 | 49 | 9 | 34 | 6 | 0 | 41.3 | 2.61 |
| 2 | 556 | 227 | 227 | 101 | 1 | 40.5 | 2.62 |
| 3 | 2981 | 591 | 1526 | 783 | 81 | 46.6 | 3.00 |
| 4 | 1063 | 70 | 387 | 580 | 26 | 55.0 | 3.57 |
| 5 | 206 | 4 | 34 | 128 | 40 | 63.9 | 4.13 |

- 旧 est vs 新分 Spearman ρ = 0.370（n=4855）；est 值变动 2839 题。
- **锚定（私有 555 道题源自带 difficulty）**：与 LLM 分 Spearman ρ = 0.453，Pearson r = 0.438；分题源：bonnie8536 ρ=0.67(n=155)，grittingleo_4tests ρ=0.44(n=400)

### 特征 × 档（均值）

| 档 | 干扰项 0–3 | 句法 1–3 | 用时 s | 跨句/跨段/跨篇占比 | 推断/NOT/插入占比 | C1+ 词占比 |
|---|---|---|---|---|---|---|
| 基础 | 1.02 | 1.47 | 19 | 2% | 1% | 0% |
| 进阶 | 1.45 | 1.72 | 26 | 14% | 11% | 3% |
| 熟练 | 1.92 | 1.93 | 39 | 52% | 49% | 25% |
| 真考+ | 2.41 | 2.02 | 49 | 47% | 49% | 67% |

### 缺口：题型 × 档（私有池；<20 标红；规格目标公开池每档每题型 ≥30）

| 题型 | 基础 | 进阶 | 熟练 | 真考+ | 合计 | 缺口（补到 20 / 补到 30） |
|---|---|---|---|---|---|---|
| P5.VOCAB | 114 | 409 | 308 | 56 | 887 | 0 / 0 |
| P5.VERB_FORM | 87 | 199 | 133 | <span style="color:red">**10**</span> | 429 | 10 / 20 |
| P5.WORD_FORM | 128 | 82 | <span style="color:red">**14**</span> | <span style="color:red">**0**</span> | 224 | 26 / 46 |
| P5.PREP | 41 | 76 | <span style="color:red">**7**</span> | <span style="color:red">**0**</span> | 124 | 33 / 53 |
| P5.RELATIVE | 21 | 64 | 23 | <span style="color:red">**2**</span> | 110 | 18 / 44 |
| P5.PRONOUN | 61 | 24 | <span style="color:red">**6**</span> | <span style="color:red">**0**</span> | 91 | 34 / 60 |
| P5.CONNECTOR_MIX | <span style="color:red">**11**</span> | 53 | <span style="color:red">**17**</span> | <span style="color:red">**1**</span> | 82 | 31 / 61 |
| P5.CONJ | <span style="color:red">**5**</span> | 40 | 23 | <span style="color:red">**1**</span> | 69 | 34 / 61 |
| P5.COMPARATIVE | 24 | <span style="color:red">**14**</span> | <span style="color:red">**6**</span> | <span style="color:red">**0**</span> | 44 | 40 / 76 |
| P5.PAIR_GRAMMAR | <span style="color:red">**8**</span> | <span style="color:red">**16**</span> | <span style="color:red">**6**</span> | <span style="color:red">**3**</span> | 33 | 47 / 87 |
| P6.INDEPENDENT | 94 | 161 | 22 | <span style="color:red">**2**</span> | 279 | 18 / 36 |
| P6.CTX_VOCAB | 45 | 163 | 68 | <span style="color:red">**2**</span> | 278 | 18 / 28 |
| P6.INSERTION | <span style="color:red">**1**</span> | 22 | 133 | <span style="color:red">**1**</span> | 157 | 38 / 66 |
| P6.CTX_TENSE | 24 | 61 | <span style="color:red">**9**</span> | <span style="color:red">**0**</span> | 94 | 31 / 57 |
| P6.CTX_CONJ_ADV | <span style="color:red">**1**</span> | <span style="color:red">**12**</span> | <span style="color:red">**5**</span> | <span style="color:red">**0**</span> | 18 | 62 / 102 |
| P6.CTX_PRONOUN | <span style="color:red">**7**</span> | <span style="color:red">**7**</span> | <span style="color:red">**0**</span> | <span style="color:red">**0**</span> | 14 | 66 / 106 |
| P7.DETAIL | 78 | 235 | 168 | <span style="color:red">**6**</span> | 487 | 14 / 24 |
| P7.INFERENCE | <span style="color:red">**5**</span> | 72 | 175 | 43 | 295 | 15 / 25 |
| P7.MAIN_PURPOSE | 58 | 100 | 36 | <span style="color:red">**0**</span> | 194 | 20 / 30 |
| P7.TRUE_INDICATED | <span style="color:red">**11**</span> | 101 | 61 | <span style="color:red">**5**</span> | 178 | 24 / 44 |
| P7.NOT_TRUE | <span style="color:red">**1**</span> | 26 | 132 | <span style="color:red">**1**</span> | 160 | 38 / 62 |
| P7.SYNONYM | <span style="color:red">**5**</span> | 62 | 47 | <span style="color:red">**1**</span> | 115 | 34 / 54 |
| P7.DETAIL_NUMBER | 35 | 34 | 33 | <span style="color:red">**6**</span> | 108 | 14 / 24 |
| P7.REQUEST_ACTION | <span style="color:red">**16**</span> | 65 | <span style="color:red">**15**</span> | <span style="color:red">**1**</span> | 97 | 28 / 58 |
| P7.REASON | <span style="color:red">**6**</span> | 48 | 28 | <span style="color:red">**0**</span> | 82 | 34 / 56 |
| P7.INFER_WHO | <span style="color:red">**12**</span> | 35 | 22 | <span style="color:red">**2**</span> | 71 | 26 / 54 |
| P7.INTENT | <span style="color:red">**0**</span> | <span style="color:red">**17**</span> | 49 | <span style="color:red">**0**</span> | 66 | 43 / 73 |
| P7.INSERTION | <span style="color:red">**0**</span> | <span style="color:red">**0**</span> | 45 | <span style="color:red">**3**</span> | 48 | 57 / 87 |
| P7.INFER_NEXT | <span style="color:red">**2**</span> | <span style="color:red">**10**</span> | <span style="color:red">**7**</span> | <span style="color:red">**2**</span> | 21 | 59 / 99 |

- 合计需补：到每格 20 题 912 题；到每格 30 题 1593 题。

### 手册主章分布

第1章 612 / 第2章 426 / 第3章 400 / 第4章 233 / 第5章 1087 / 第6章 230 / 第7章 3 / 第8章 744 / 第9章 452 / 第10章 450 / 第11章 218

