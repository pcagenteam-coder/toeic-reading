# -*- coding: utf-8 -*-
"""TOEIC Reading 能力图谱 v1 —— 节点定义（第一部分：基础层 + 语法层）。
est = 现行线性版（100题/75分钟）每份试卷中"该节点是决定性考点"的估计题数。
basis: stat_composite / stat_single / derived / wordlist_freq / impact_estimate / aggregate
"""
NODES = []

def N(id, name, layer, parent, prereqs, parts, band, desc, ex, est=None, w=None,
      basis="derived", v0=(), src=""):
    NODES.append(dict(id=id, name_zh=name, layer=layer, parent=parent,
                      prereqs=list(prereqs), parts=list(parts), target_band=band,
                      description_zh=desc, example_pattern=ex, est_items=est,
                      weight_override=w, basis=basis, mapped_from_v0=list(v0),
                      weight_note=src))

P5, P6, P7 = [5], [6], [7]
P56, P567, P67 = [5, 6], [5, 6, 7], [6, 7]
ST = "exam_pattern_stats.json composite"

# ---------------------------------------------------------------- foundation
L = "foundation"
N("FD", "基础层（读懂句子与篇章的底层能力）", L, None, [], P567, 400,
  "不直接对应某一题型，但决定 Part5/6/7 全部题目的读题速度与理解深度。", "—", basis="aggregate")
N("FD.SENT", "句子结构基础", L, "FD", [], P567, 400, "识别句子成分与主干，是语法题“结构先行”解法的前提。", "—", basis="aggregate")
N("FD.SENT.CORE", "主谓宾/五种基本句型识别", L, "FD.SENT", [], P567, 400,
  "能指出句子的主语、谓语动词、宾语/补语，判断句子是否完整。",
  "The manager [S] approved [V] the budget [O].", w=0.55, basis="impact_estimate",
  src="影响全部 P5/6 结构题（约 15–18 题）及 P7 精读；非直接计题")
N("FD.SENT.CLAUSE_COUNT", "谓语与连接词计数", L, "FD.SENT", ["FD.SENT.CORE"], P56, 400,
  "一句话有 n 个谓语就需要 n−1 个连接词；据此判断空格应填谓语、非谓语还是连接词（书目技巧 P5-03）。",
  "------- the report is finished, we will send it. → 两个谓语缺连接词 → Once", w=0.4, basis="impact_estimate",
  src="决定连词/介词/非谓语/关系词约 7–9 题")
N("FD.SENT.MODIFIER_STRIP", "剥离修饰语找主干", L, "FD.SENT", ["FD.SENT.CORE"], P567, 400,
  "先划掉介词短语、分词短语、插入从句，再看空格成分（P5-16）。",
  "The list [of approved vendors for the project] ------- updated. → is", w=0.4, basis="impact_estimate",
  src="主谓一致、词性题干扰的主要来源")
N("FD.SENT.LONG", "长难句拆分（多层从句/后置修饰）", L, "FD.SENT",
  ["FD.SENT.MODIFIER_STRIP", "GR.REL.REL_PRONOUN"], P67, 700,
  "能把嵌套关系从句、分词后置、同位语的长句拆成核心命题，P7 文章/多篇常见。",
  "Applicants who have not received the forms that were mailed last week should contact HR.", w=0.5,
  basis="impact_estimate", src="P7 文章、三篇题精读")
N("FD.READ", "阅读流畅度", L, "FD", [], P67, 400, "顺读、速读与篇章追踪能力。", "—", basis="aggregate")
N("FD.READ.CHUNK", "意群切分顺读（斜线读法）", L, "FD.READ", ["FD.SENT.CORE"], P67, 400,
  "按意群从左到右理解，不回读、不逐词翻译（IIBC 速读演习、P7-15）。",
  "Please submit / your expense report / by Friday / to the accounting team.", w=0.45,
  basis="impact_estimate", src="决定能否做完 P7（ETS RM-17-05：做不完多为配速问题）")
N("FD.READ.SPEED_150", "阅读速度 ≥150 词/分", L, "FD.READ", ["FD.READ.CHUNK"], P67, 600,
  "以约 150 wpm 读完 P7 单篇，是 600–700 段做完大部分 P7 的门槛（经验估计）。",
  "300 词的邮件+3 题 ≈ 2.5–3 分钟内完成", w=0.6, basis="impact_estimate",
  src="P7 54 题能否作答；经验阈值，非官方数据", v0=["S1"])
N("FD.READ.SPEED_200", "阅读速度 ≥200 词/分", L, "FD.READ", ["FD.READ.SPEED_150"], P67, 800,
  "800+ 需在约 55 分钟内读完 P7 全部文本并留检查时间（经验估计）。",
  "三篇题组（约 600 词）+5 题 ≈ 5–6 分钟", w=0.5, basis="impact_estimate", src="经验阈值", v0=["S1"])
N("FD.READ.SCAN", "扫读（带关键词找信息）", L, "FD.READ", ["FD.READ.CHUNK"], P7, 400,
  "用人名、数字、日期、专有名词等关键词快速定位原文。",
  "Q: When will the store reopen? → 扫 'reopen' / 日期", w=0.5, basis="impact_estimate",
  src="服务细节题约 18 题")
N("FD.READ.SKIM", "略读（抓段落大意与篇章结构）", L, "FD.READ", ["FD.READ.CHUNK"], P67, 400,
  "读首句/首段与段落首句把握主旨和走向，服务主旨题、插入句、P6 上下文题。",
  "首段 'I am writing to inform you of a change...' → 目的=通知变更", w=0.4, basis="impact_estimate")
N("FD.READ.UNKNOWN_WORD", "生词不停（语境猜义/跳读）", L, "FD.READ", ["FD.READ.CHUNK"], P67, 600,
  "遇生词靠上下文把握大意，读完再查（P7-16 '虫食い読み'）。",
  "The firm will ------- [生词: refurbish] the lobby, so the entrance will be closed. → 推测=翻修",
  w=0.3, basis="impact_estimate")
N("FD.READ.REFERENCE", "指代追踪（代词/this/such/the former）", L, "FD.READ",
  ["FD.SENT.CORE", "GR.PRON.CASE"], P67, 600,
  "能把 it/they/this/such changes 等指回前文具体对象，是 P6 代词题、插入句与 P7 推断的基础。",
  "We upgraded the software. This should reduce delays. → This = 升级这件事", w=0.45,
  basis="impact_estimate")
N("FD.READ.DISCOURSE", "篇章逻辑信号（转折/因果/追加/举例/顺序）", L, "FD.READ",
  ["FD.READ.REFERENCE"], P67, 600,
  "识别 however/as a result/in addition/for example/first 等信号，把握句间关系。",
  "Sales rose. ------- , profits fell. → However", w=0.4, basis="impact_estimate")
N("FD.VOC", "词汇底座", L, "FD", [], P567, 400, "核心词量与构词知识。", "—", basis="aggregate")
N("FD.VOC.NGSL_CORE", "NGSL 核心通用词（约 2,800 词）", L, "FD.VOC", [], P567, 400,
  "NGSL 1.2 覆盖一般英语文本约 92% 词次；TOEIC 文本中还需 TSL/BSL 补充。",
  "make, provide, available, require, receive...", w=0.7, basis="impact_estimate",
  src="影响全部 100 题；覆盖率数据来自 NGSL 项目说明")
N("FD.VOC.AFFIX", "构词：后缀定词性、前缀定词义", L, "FD.VOC", ["FD.VOC.NGSL_CORE"], P567, 400,
  "-tion/-ment/-ness→名词，-ive/-able/-ful→形容词，-ly→副词，-ize/-en→动词；un-/re-/pre-（P5-17）。",
  "compet-itive (adj) / compet-ition (n) / compet-itor (n) / compet-itively (adv)", w=0.35,
  basis="impact_estimate", src="词性题 6–8 题的识别前提", v0=["G1"])

# ---------------------------------------------------------------- grammar
L = "grammar"
N("GR", "语法层（Part5/6 语法考点）", L, None, [], P56, 400,
  "按 P5/P6 实际出题切分的语法考点；P5 语法类合计约 15–18 题，P6 约 3–5 题。", "—", basis="aggregate")
# --- 词性
N("GR.POS", "词性（品词）判断", L, "GR", ["FD.SENT.CORE", "FD.VOC.AFFIX"], P56, 400,
  "根据空格位置定词性；P5 词性题约 20–27%（6–8 题），P6 每篇约 1 题。", "—", basis="aggregate",
  v0=["G1"], src=ST)
pos = [
 ("NOUN_AFTER_DET", "限定词/冠词/所有格后填名词", 400, "a/the/this/its/their 后、形容词后，空格是名词。",
  "We appreciate your ------- in this matter. (cooperation)", 1.6),
 ("NOUN_AFTER_PREP", "介词后填名词（或动名词）", 400, "介词宾语位置填名词；若空格后还有宾语则选动名词。",
  "Thank you for your ------- of our services. (recommendation)", 0.8),
 ("NOUN_SUBJ_OBJ", "主语/宾语位置填名词", 400, "谓语前缺主语、及物动词后缺宾语时填名词。",
  "------- of the new plant will begin in May. (Construction)", 0.7),
 ("NOUN_COUNT", "可数/不可数与单复数", 600, "a/an+单数可数；many/several+复数；information/equipment 不可数（P5-10）。",
  "The store sells a wide range of office -------. (equipment)", 0.4),
 ("NOUN_PERSON_THING", "人名词 vs 事物名词", 600, "applicant/application、attendee/attendance：按语义与冠词/单复数选。",
  "All ------- must register by Friday. (participants)", 0.6),
 ("NOUN_COMPOUND", "复合名词（名词+名词）", 700, "safety regulations、customer satisfaction、job opening 等，前一个名词作修饰。",
  "Please review the ------- guidelines. (safety)", 0.4),
 ("ADJ_BEFORE_NOUN", "名词前填形容词", 400, "冠词/限定词与名词之间、副词修饰之后填形容词。",
  "She gave a ------- presentation. (persuasive)", 1.0),
 ("ADJ_COMPLEMENT", "be/系动词/宾补位置填形容词", 600, "be, become, remain, seem 后；make/keep/find + O + adj。",
  "The new policy has made the process more -------. (efficient)", 0.6),
 ("ADV_VERB", "修饰动词的副词", 400, "完整句中修饰谓语动词，位于动词前后或句末。",
  "Sales increased ------- last quarter. (significantly)", 1.1),
 ("ADV_ADJ", "修饰形容词/分词/副词的副词", 600, "副词+形容词/过去分词：highly qualified、newly renovated。",
  "The hotel is ------- located near the station. (conveniently)", 0.7),
 ("ADV_AUX_SLOT", "助动词与动词之间的副词", 600, "has ___ been、will ___ announce、be ___ done 中间填副词。",
  "The order has ------- been shipped. (already)", 0.5),
 ("ADV_SENTENCE", "修饰全句的副词/句首副词", 700, "句子已完整、句首或逗号前后的副词，如 Unfortunately, Additionally。",
  "-------, the shipment was delayed by the storm. (Unfortunately)", 0.3),
 ("VERB_SLOT", "缺谓语时填限定动词", 600, "句中没有谓语，选项中只有限定动词形式可选（排除 -ing/to do）。",
  "The committee ------- the proposal next week. (will review)", 0.6),
]
for k, nm, b, d, ex, est in pos:
    pre = ["GR.POS"] if b == 400 else ["GR.POS", "GR.POS.NOUN_AFTER_DET"]
    if k.startswith("ADV"): pre = ["GR.POS.ADV_VERB"] if k != "ADV_VERB" else ["GR.POS"]
    if k.startswith("ADJ_COMP"): pre = ["GR.POS.ADJ_BEFORE_NOUN"]
    if k == "VERB_SLOT": pre = ["GR.POS", "FD.SENT.CLAUSE_COUNT"]
    v = ["G1"]
    if k.startswith(("ADJ", "ADV")): v = ["G1", "G2"]
    N("GR.POS." + k, nm, L, "GR.POS", pre, P56, b, d, ex, est=est, basis="derived", v0=v,
      src="P5 词性 6–8 题按位置拆分（get-toeic：名词位10%/形容词位4%/副词位8%）+P6 约 1–2 题")
# --- 动词
N("GR.VERB", "动词形态（数·态·时）", L, "GR", ["FD.SENT.CORE"], P56, 400,
  "动词题按“数→态→时”三步排查（P5-04）；P5 约 8–12%（2–4 题），P6 语境时态约 2 题。", "—",
  basis="aggregate", src=ST)
verb = [
 ("AGREE_SV", "主谓一致", 400, ["GR.VERB", "FD.SENT.MODIFIER_STRIP"], "主语核心词定单复数，介词短语/关系从句为干扰。",
  "The results of the survey ------- encouraging. (are)", 0.7, ["G3"]),
 ("AGREE_QUANT", "数量表达与一致（each/a number of/the number of）", 600, ["GR.VERB.AGREE_SV"],
  "each/every+单数；a number of+复数；the number of+单数谓语（P5-22）。",
  "Each of the rooms ------- a private balcony. (has)", 0.3, ["G3"]),
 ("TENSE_SIMPLE", "一般时态与时间状语", 400, ["GR.VERB"], "yesterday/last→过去；next/soon→将来；every/usually→现在。",
  "Mr. Lee ------- the client last Tuesday. (visited)", 0.8, ["G4"]),
 ("TENSE_PERFECT", "完成时（since/for/by the time/already）", 600, ["GR.VERB.TENSE_SIMPLE"],
  "since/for+时段→现在完成；by the time+过去→过去完成；by+将来时间→将来完成。",
  "By next month, we ------- 500 units. (will have sold)", 0.5, ["G4"]),
 ("TENSE_FUTURE_CLAUSE", "时间/条件从句以现在代将来", 600, ["GR.VERB.TENSE_SIMPLE"],
  "when/once/as soon as/if 引导的从句用一般现在时表将来。",
  "Once the payment ------- , we will ship the item. (is received)", 0.3, ["G4"]),
 ("VOICE_PASSIVE", "主动 vs 被动语态", 400, ["GR.VERB.TENSE_SIMPLE"], "看空格后有无宾语、主语是否为动作承受者。",
  "The documents ------- to all staff yesterday. (were sent)", 0.9, ["G5"]),
 ("MODAL_BASE", "情态动词/助动词 + 动词原形", 400, ["GR.VERB"], "can/should/must/will/do 后接原形。",
  "Visitors should ------- at the front desk. (sign in)", 0.2, ["G4"]),
 ("VERB_PATTERN", "动词句型（及物/不及物/双宾/宾补）", 700, ["GR.VERB.VOICE_PASSIVE"],
  "rise 不及物 vs raise 及物；make/let/have+O+原形；ask/require+O+to do（P5-21）。",
  "The manager asked us ------- the report early. (to submit)", 0.4, ["G5"]),
 ("SUBJUNCTIVE_DEMAND", "要求/建议类 that 从句用原形", 800, ["GR.VERB.MODAL_BASE"],
  "request/recommend/require/It is essential that + 主语 + 动词原形（P5-18）。",
  "The director requested that every employee ------- the training. (attend)", 0.2, ["G4"]),
 ("CONDITIONAL_INVERSION", "假设语气与省略 if 倒装", 800, ["GR.VERB.TENSE_PERFECT"],
  "Should you have questions = If you should...；Had we known = If we had known（P5-18）。",
  "------- you need assistance, please call the front desk. (Should)", 0.3, ["G4"]),
]
for k, nm, b, pre, d, ex, est, v in verb:
    N("GR.VERB." + k, nm, L, "GR.VERB", pre, P56, b, d, ex, est=est, v0=v,
      src="P5 动词 2–4 题（composite）按子类拆分；scordia 题库子类占比参考")
# --- 非谓语
N("GR.NONFIN", "非谓语（to do / -ing / 分词）", L, "GR", ["GR.VERB", "FD.SENT.CLAUSE_COUNT"], P56, 600,
  "已有谓语时空格选非谓语；分词按与被修饰名词的主被动关系选（P5-08）。", "—", basis="aggregate")
nonfin = [
 ("TO_INF", "to 不定式（目的/只接 to do 的词）", 600, "in order to；plan/decide/aim/be able/be eager to do；名词后 to do 表用途。",
  "We are pleased ------- our new branch. (to announce)", 0.4),
 ("GERUND", "动名词（介词后/只接 -ing 的词）", 600, "consider/avoid/recommend+-ing；look forward to/be committed to + -ing。",
  "We look forward to ------- with you. (working)", 0.4),
 ("PARTICIPLE_MODIFIER", "分词作后置/前置修饰（主动 -ing / 被动 -ed）", 700, "名词与动词为主动关系用 -ing，被动用 -ed。",
  "Please complete the form ------- to this e-mail. (attached)", 0.5),
 ("PARTICIPLE_CLAUSE", "分词构句与连词+分词", 800, "When/Before/Once/If + -ing/-ed 省略主语；主句主语即逻辑主语。",
  "When ------- the device, follow the instructions carefully. (installing)", 0.3),
 ("PARTICIPLE_ADJ", "情感/状态分词形容词（-ing vs -ed）", 600, "exciting/excited、detailed/experienced/leading/rising。",
  "Only ------- candidates will be contacted. (qualified)", 0.3),
]
for k, nm, b, d, ex, est in nonfin:
    pre = ["GR.NONFIN"] if k in ("TO_INF", "GERUND") else ["GR.NONFIN", "GR.VERB.VOICE_PASSIVE"]
    N("GR.NONFIN." + k, nm, L, "GR.NONFIN", pre, P56, b, d, ex, est=est, v0=["G5"] if "PARTI" in k else [],
      src="get-toeic 分词约4%（~1.2 题）+不定式/动名词零星")
# --- 代词/限定词
N("GR.PRON", "代词与限定词", L, "GR", ["FD.SENT.CORE"], P56, 400,
  "先看位置定格，再看指代对象单复数与人/物（P5-06）；P5 约 7–10%（2–3 题）。", "—", basis="aggregate",
  v0=["G8"], src=ST)
pron = [
 ("CASE", "人称代词格（主格/宾格/所有格）", 400, "名词前用所有格 their；动词/介词后用宾格 them；谓语前用主格。",
  "Ms. Kim will present ------- findings tomorrow. (her)", 0.9),
 ("POSSESSIVE_PRONOUN", "名词性物主代词（mine/theirs/ours）", 600, "代替“所有格+名词”，独立作主宾语。",
  "Our prices are lower than -------. (theirs)", 0.2),
 ("REFLEXIVE", "反身代词（by oneself / 强调）", 600, "主宾同一用反身；完整句末强调或 by oneself=独自。",
  "Mr. Diaz prepared the budget by -------. (himself)", 0.4),
 ("DETERMINER_QUANT", "数量限定词（each/every/all/most/few/little）", 600, "按后接名词可数性与单复数选：every+单数，few+复数，little+不可数。",
  "------- employees have already signed up. (Most)", 0.6),
 ("INDEFINITE", "不定代词（another/the other/others/one）", 700, "another+单数；the others=剩余全部；one of + 复数。",
  "One copy is for you, and ------- is for the client. (the other)", 0.3),
 ("DEMONSTRATIVE", "指示代词（those who / that of）", 800, "those who=那些……的人；比较中 that/those of 代替前文名词。",
  "The award is given to ------- who show outstanding service. (those)", 0.2),
]
for k, nm, b, d, ex, est in pron:
    pre = ["GR.PRON"] if k == "CASE" else ["GR.PRON.CASE"]
    if k in ("DETERMINER_QUANT", "INDEFINITE"): pre = ["GR.PRON", "GR.POS.NOUN_COUNT"]
    N("GR.PRON." + k, nm, L, "GR.PRON", pre, P56, b, d, ex, est=est, v0=["G8"],
      src="代词 ~2 题/卷（toeicstory、get-toeic 6%）+限定词 ~1 题")
# --- 介词与连词
N("GR.CONN", "介词与连词（连接成分）", L, "GR", ["FD.SENT.CLAUSE_COUNT"], P56, 400,
  "空格后接名词→介词；接完整从句→连词；两句间仅逻辑衔接→接续副词（P5-05）。P5 介词 10–13%、连词 3–9%。", "—",
  basis="aggregate", v0=["G7"], src=ST)
conn = [
 ("PREP_TIME", "时间介词（at/on/in/by/until/within/during/for）", 400, [],
  "by=截止前完成，until=持续到；within+时段；during+名词时段。", "Submit the form ------- Friday. (by)", 0.9),
 ("PREP_PLACE", "地点/方位介词（at/in/on/across/throughout/along）", 400, [],
  "throughout the building；across from；along the river。", "Branches are located ------- the country. (throughout)", 0.4),
 ("PREP_MEANING", "按语义选介词（despite/due to/regarding/except/prior to）", 600, ["GR.CONN.PREP_TIME"],
  "原因 because of/due to；让步 despite；关于 regarding/concerning；之前 prior to（P5-11）。",
  "------- the delay, the event was a success. (Despite)", 1.5),
 ("PREP_PHRASE_MULTI", "复合介词（in addition to/on behalf of/in accordance with）", 700, ["GR.CONN.PREP_MEANING"],
  "多词介词整体记忆，常与 vocab 搭配题重叠。", "I am writing ------- behalf of the board. (on)", 0.6),
 ("PREP_VS_CONJ", "介词 vs 连词（despite/although, during/while, because of/because）", 400, ["FD.SENT.CLAUSE_COUNT"],
  "同义的介词与连词成对出现，按空格后是名词还是从句区分。",
  "------- the store was busy, service was quick. (Although)", 1.1),
 ("CONJ_ADVERBIAL", "从属连词（although/unless/once/as soon as/provided that/so that）", 600, ["GR.CONN.PREP_VS_CONJ"],
  "按主从句逻辑（条件/让步/时间/目的）选连词。",
  "You may return the item ------- it is unused. (provided that)", 1.0),
 ("CONJ_COORD", "并列连词（and/but/or/yet/so）", 400, [], "连接对等成分；yet 表转折，so 表结果。",
  "The room is small ------- comfortable. (but)", 0.2),
 ("CONJ_CORRELATIVE", "成对连词（both–and/either–or/neither–nor/not only–but also/whether–or）", 600, ["GR.CONN.CONJ_COORD"],
  "看搭档词直接选（P5-19）。", "Applicants must have ------- a degree and experience. (both)", 0.4),
 ("CONJ_ADVERB", "接续副词（however/therefore/in addition/otherwise）", 600, ["GR.CONN.PREP_VS_CONJ", "FD.READ.DISCOURSE"],
  "连接两个独立句的逻辑副词，不能单独连接两个从句；P6 每卷约 1 题（P6-05）。",
  "The venue is booked. -------, we need a new date. (Therefore)", 1.2),
]
for k, nm, b, pre, d, ex, est in conn:
    N("GR.CONN." + k, nm, L, "GR.CONN", ["GR.CONN"] + pre, P56, b, d, ex, est=est, v0=["G7"],
      src="P5 介词 3–4 题、连词 1–3 题（composite）+P6 接续副词 ~1")
# --- 关系词/名词从句
N("GR.REL", "关系词与名词从句", L, "GR", ["GR.CONN.PREP_VS_CONJ", "GR.PRON.CASE"], P56, 600,
  "看先行词有无、指人/物，再看后面从句是否完整（P5-07）；P5 约 0–3%。", "—", basis="aggregate",
  v0=["G6"], src=ST)
rel = [
 ("REL_PRONOUN", "关系代词（who/which/that/whose）", 600, [], "先行词为人→who；物→which；后接名词且表所属→whose。",
  "Employees ------- cars are parked in Lot B must move them. (whose)", 0.4),
 ("REL_ADVERB", "关系副词（where/when）与 介词+which", 800, ["GR.REL.REL_PRONOUN"], "后接完整从句且先行词为地点/时间。",
  "This is the office ------- the meeting will be held. (where)", 0.1),
 ("REL_WHAT", "what vs that（先行词有无）", 800, ["GR.REL.REL_PRONOUN"], "无先行词且从句缺成分→what。",
  "------- the client wants is a lower price. (What)", 0.1),
 ("NOUN_CLAUSE", "名词从句连接词（whether/if/that/wh-）", 700, ["GR.REL.REL_PRONOUN"], "作主宾语的从句；whether 可接 or not。",
  "We have not decided ------- the event will be held outdoors. (whether)", 0.3),
 ("COMPOUND_REL", "复合关系词（whoever/whatever/however）", 900, ["GR.REL.REL_WHAT"], "whoever=anyone who；however+形容词=无论多么。",
  "------- finishes first will receive a prize. (Whoever)", 0.1),
]
for k, nm, b, pre, d, ex, est in rel:
    N("GR.REL." + k, nm, L, "GR.REL", ["GR.REL"] + pre, P56, b, d, ex, est=est, v0=["G6"],
      src="composite 关系词 0–1 题（弱证据）")
# --- 比较
N("GR.COMP", "比较结构", L, "GR", ["GR.POS.ADJ_BEFORE_NOUN"], P5, 600,
  "看标志词：than→比较级；the+…of/in/among→最高级；as…as→原级（P5-09）；P5 约 1–3%。", "—",
  basis="aggregate", src=ST)
for k, nm, b, d, ex, est in [
 ("COMPARATIVE", "比较级与强调（much/even/far + -er）", 600, "than 前用比较级；much/even/far/still 修饰比较级。",
  "The new model is ------- lighter than the old one. (much)", 0.3),
 ("SUPERLATIVE", "最高级（the most…of/in/ever）", 600, "the + 最高级 + of/in/among/ever。", "It is the ------- hotel in the area. (largest)", 0.2),
 ("EQUATIVE", "原级比较（as…as / as many as）", 700, "as + 原级 + as；as soon as possible。", "Please reply as ------- as possible. (soon)", 0.1)]:
    N("GR.COMP." + k, nm, L, "GR.COMP", ["GR.COMP"], P5, b, d, ex, est=est, src="composite 比较 0–1 题")
# --- 特殊句式
N("GR.SPECIAL", "特殊句式", L, "GR", ["FD.SENT.CORE", "GR.VERB"], P56, 700,
  "倒装、并列一致、省略等低频高难考点（P5-18）。", "—", basis="aggregate")
for k, nm, b, pre, d, ex, est in [
 ("INVERSION_NEG", "否定/only 前置倒装", 900, ["GR.VERB.CONDITIONAL_INVERSION"], "Not only/Rarely/Only after 置句首时主谓倒装。",
  "Only after the review ------- the contract be signed. (will)", 0.1),
 ("PARALLEL", "并列结构一致", 700, [], "and/or 前后词性、形式一致。", "The job requires planning, organizing, and ------- events. (promoting)", 0.2),
 ("ELLIPSIS", "省略结构（as requested/if necessary/when needed）", 800, ["GR.NONFIN.PARTICIPLE_CLAUSE"], "连词+过去分词/形容词的固定省略。",
  "Please revise the draft as -------. (needed)", 0.2)]:
    N("GR.SPECIAL." + k, nm, L, "GR.SPECIAL", ["GR.SPECIAL"] + pre, P56, b, d, ex, est=est,
      src="scordia 题库倒装 5.3%（练习题库，偏高）；真题约 0–1 题")
