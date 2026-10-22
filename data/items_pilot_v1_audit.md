# 试点题 v1 审题报告（items_pilot_v1）

更新：2026-10-21。脚本：`work/item_audit.py`（结果 JSON：`work/pilot/audit_final.json`）。题源：`work/pilot/src_p5.py`、`src_p67.py`，组装：`work/pilot/build_pilot.py`。

## 1. 结论

- 题数 **107**（P5 60 / P6 20（5 篇）/ P7 27（8 组：单篇 6、双篇 1、三篇 1）），bundle 13 个。
- 最终通过率 **107/107 = 100%**，0 警告。首轮 107 题中 50 题未通过（几乎全是专名误判 + 4 处篇幅不足 + 6 个真超纲词），修正后两轮全过。
- 原创性：与 items_v0（18 段）和外部参考题库（24632 条，data/external/toeic_items）做 3-gram 比对，无 J≥0.3 的相似项。
- 自检：故意注入超纲词、抄一道外部题、删选项、答案越界，脚本 4 处全部报错（J=0.93 识别出抄题）。

## 2. 超纲词修正（NGSL 1.2 + TSL 1.2）

| 题/篇 | 原词 | 处理 |
|---|---|---|
| PL5-007 | repayment | → reimbursement（TSL） |
| PL5-060 | mobile app | → shop at our online store |
| PL7-T1-2 | incorrect | → a mistake |
| P7-S2 | fridge | → refrigerator |
| P7-T1 | shiny | → high-quality |
| PL5-003 | complementary | 保留，登记为 vocab_exceptions：形近词陷阱本身就是考点，只作干扰项 |

- 允许的派生形式（仅词性题选项）：informatively←informative
- 视为专名豁免 74 个（人名/公司/地名，人工已过目）。

## 3. 篇幅修正

P6-B3（70→82 词）、P6-B5（69→84 词）、P7-D1（195→235 词）、P7-T1（199→324 词）补足到模板下限。P6 篇幅仍偏短（80–98 词，真题约 100–150），下一批建议加长。

## 4. 答案分布

| Part | A | B | C | D | 最长连续同答案 |
|---|---|---|---|---|---|
| P5 | 15 | 15 | 15 | 15 | 2 |
| P6 | 5 | 5 | 5 | 5 | 1 |
| P7 | 8 | 6 | 6 | 7 | 2 |

P7 插入题固定 [1]–[4]、数字选项按从小到大，其余随机均衡。

## 5. 节点覆盖

- 共覆盖 **162** 个图谱节点（按层：qtype 45、vocab 54、grammar 39、foundation 7、texttype 14、strategy 3）。
- qtype 叶子 44/67 个被覆盖。
- 可贴题节点（qtype/grammar/vocab/texttype，不含词汇档位）中权重前 60：覆盖 54/60。未覆盖：VO.TITLES_DEPTS(0.2)、VO.SCENE.SALES_DEAL(0.16)、TX.AD(0.16)、VO.SCENE.RND_PRODUCT(0.12)、VO.SCENE.MEDIA_PUBLISH(0.106)、TX.APP_FORM(0.1)
- 策略层（ST.*）、阅读速度（FD.READ.SPEED_*）、词汇档位（VO.BAND.*）属于训练方式而非单题考点，没有直接贴题；FD.READ.REFERENCE/DISCOURSE/SKIM、ST.LOCATE.* 等已按需贴上。

用到的模板（题数）：T5.COMPARATIVE 2、T5.CONJ 3、T5.CONNECTOR_MIX 3、T5.PAIR_GRAMMAR 3、T5.PREP 6、T5.PRONOUN 4、T5.RELATIVE 2、T5.VERB_FORM.AGREE_MODAL 3、T5.VERB_FORM.TENSE 3、T5.VERB_FORM.VOICE 1、T5.VOCAB.ADJ 3、T5.VOCAB.ADV 3、T5.VOCAB.NOUN 4、T5.VOCAB.PHRASE 2、T5.VOCAB.VERB 4、T5.WORD_FORM.ADJ_SLOT 3、T5.WORD_FORM.ADV_SLOT 4、T5.WORD_FORM.NOUN_SLOT 3、T5.WORD_FORM.NOUN_TYPE 3、T5.WORD_FORM.VERB_SLOT 1、T6.CTX_CONJ_ADV 2、T6.CTX_PRONOUN 2、T6.CTX_TENSE 2、T6.CTX_VOCAB 4、T6.INDEPENDENT 5、T6.INS_CLOSING 2、T6.INS_OPENING 1、T6.INS_TRANSITION 2、T7.CALC_LOOKUP.INVOICE 2、T7.CROSS_REF.DOUBLE 2、T7.CROSS_REF.TRIPLE 2、T7.DETAIL.ARTICLE 1、T7.DETAIL.DOUBLE 1、T7.DETAIL.EMAIL 1、T7.DETAIL.NOTICE 1、T7.DETAIL.TEXT_MSG 1、T7.DETAIL.TRIPLE 2、T7.DETAIL_NUMBER.FORM 1、T7.INFER_NEXT.CHAT 1、T7.INFER_WHO.CHAT 1、T7.INFER_WHO.NOTICE 1、T7.INSERTION.ARTICLE 1、T7.INTENT.CHAT 1、T7.INTENT.TEXT_MSG 1、T7.MAIN_PURPOSE.ARTICLE 1、T7.MAIN_PURPOSE.EMAIL 1、T7.MAIN_PURPOSE.MULTI 1、T7.REASON 1、T7.REQUEST_ACTION.EMAIL 1、T7.SYNONYM.ARTICLE 1、T7.SYNONYM.MULTI 1

## 6. 难度与用时

- P5 难度分布 1:8 2:29 3:16 4:7；平均目标用时 25.2 秒
- P6 难度分布 2:10 3:9 4:1；平均目标用时 38.5 秒
- P7 难度分布 1:1 2:11 3:9 4:4 5:2；平均目标用时 79.7 秒

用时 = EdNet 中位（P5 26.4 / P6 33.8 / P7 67.4 秒）× 题型系数（词性 0.7、词汇 1.1、P6 插入 1.3、双篇 1.2、三篇 1.3）× 难度系数（0.9–1.3）。难度为人工估计，待作答数据校准。

## 7. 干扰项套路使用次数

SEMANTIC_NEAR 56、POS_MISMATCH 40、COLLOCATION 24、TENSE_MISMATCH 20、CONN_LOGIC 19、NOT_MENTIONED 17、PRON_CASE 14、NONFINITE 11、PAIR_MISMATCH 11、MISATTRIBUTION 11、VERBATIM_WRONG 10、CONN_TYPE 9、CONTRADICT 8、REVERSE 8、AGREEMENT 7、WRONG_NUMBER 7、OVER_INFERENCE 6、OFF_TOPIC 5、REPEAT_INFO 5、PARTIAL 5、WRONG_DOC 5、VOICE_MISMATCH 4、PRON_REFERENT 4、POLYSEMY_OTHER_SENSE 4、COUNT_NUMBER 3、WRONG_POSITION 3、FORM_LOOKALIKE 2、LITERAL_MEANING 2、SCOPE 1

## 8. 审题脚本没覆盖的（需人工或下一版）

- “唯一答案”只能查字段与错因是否齐全，不能自动判断语义上是否另有可选项；本批已人工逐题过一遍，建议上线前再找人盲做一遍。
- 专名用大写启发式识别，句首单个陌生大写词会被当成超纲词（偏严）。
- 试点卷不足一整套：P7 只有 27 题，P6 第 5 篇放在 P6-B 卷 131–134。