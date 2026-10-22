#!/usr/bin/env python3
"""生成 data/templates/item_templates.json：每个 qtype 叶子节点一套出题模板（现行新制）。
P5/P6 手写；P7 用「设问族 × 文本类型」组合生成，每个 QT.P7X.* 叶子 + QT.P7.REASON 各一套。"""
import json, os
ROOT = "/workspace/projects/58061e9e-e075-4f3f-880c-32a61b21a72c"
G = json.load(open(f"{ROOT}/data/graph_v1.json"))
NODES = {n["id"]: n for n in G["nodes"]}

TRAPS = {
  # P5/P6 语法词汇
  "POS_MISMATCH": "词性错位：同词根的别的词性，放进空格语法不通",
  "TENSE_MISMATCH": "时态错位：与时间状语/上下文时间不一致",
  "VOICE_MISMATCH": "语态错位：主语和动词的主动/被动关系弄反",
  "AGREEMENT": "一致错：主谓单复数或数量词搭配不一致",
  "NONFINITE": "非谓语错：该用谓语却给了 -ing/to do/-ed，或反过来",
  "CONN_TYPE": "连接词类别错：介词/连词/副词混用（后面接名词还是句子）",
  "CONN_LOGIC": "逻辑关系错：转折/因果/让步/条件用反",
  "PRON_CASE": "代词格错：主格/宾格/所有格/反身混用",
  "PRON_REFERENT": "指代对象错：人称或单复数和前文不对应",
  "COLLOCATION": "近义但搭配不对：意思接近，但和空格前后的词不搭",
  "SEMANTIC_NEAR": "语义不合：同词性、语法通，但放进句子意思不对",
  "FORM_LOOKALIKE": "形近词：长得像，意思不同",
  "COUNT_NUMBER": "可数/不可数、单复数错",
  "PAIR_MISMATCH": "成对表达配错（both…and / either…or / so…that）",
  # P6 插入句
  "OFF_TOPIC": "话题无关：句子本身没错，但和这段话没关系",
  "BROKEN_LINK": "衔接断：句中的 this/they/it 在前文找不到对象，或与后句接不上",
  "CONTRADICT": "与上下文矛盾",
  "REPEAT_INFO": "重复已说过的信息，没有推进作用",
  # P7
  "VERBATIM_WRONG": "原文逐字重复但意思不对：照搬原文词，说的却是另一回事",
  "OVER_INFERENCE": "过度推断：听起来合理，原文推不出来",
  "NOT_MENTIONED": "未提及：原文没说",
  "PARTIAL": "部分正确：只对了一半",
  "MISATTRIBUTION": "张冠李戴：把 A 的信息安到 B 身上",
  "SCOPE": "范围陷阱：过宽/过窄/绝对化",
  "REVERSE": "与原文相反",
  "WRONG_DOC": "用错篇：多篇题里拿了另一篇的信息",
  "WRONG_NUMBER": "数字/时间/金额错位或算错",
  "LITERAL_MEANING": "意图题按字面意思理解，没看上下文",
  "POLYSEMY_OTHER_SENSE": "同义词题选了这个词的另一个常见义项",
  "WRONG_POSITION": "插入位置不对：放进去后指代或逻辑接不上",
}

def tmpl(tid, nodes, part, stem, opt_rule, traps, text_type, length, knobs, expl, extra=None):
    d = {"template_id": tid, "node_ids": nodes, "part": part, "stem_pattern": stem,
         "option_rules": opt_rule, "distractor_traps": traps, "text_type": text_type,
         "length": length, "difficulty_knobs": knobs, "explanation_template_zh": expl,
         "format_version": "current"}
    if extra: d.update(extra)
    return d

P5_LEN = {"unit": "words_in_stem", "min": 10, "max": 32}
P5_KNOBS_STRUCT = ["空格离判定词的距离（紧邻=易，被修饰语隔开=难）", "选项是否含两个看似都能用的词性（如名词 vs 动名词）", "句子长度/从句层数", "用词档次（NGSL 核心 → TSL）"]
P5_KNOBS_VOCAB = ["四个选项的语义距离（越近越难）", "是否需要搭配/介词才能区分", "是否用常用词的商务义", "语境线索数量（1 个=难，2 个以上=易）"]
P5_EXPL_STRUCT = "看选项：同一个词根的不同形式 → 词性题，只看空格前后。空格前是{前词}、后是{后词}，这里要{需要的词性}，所以选 {答案}。{干扰项逐个一句话}"
P5_EXPL_VOCAB = "四个选项词性一样 → 词汇题，要读懂句子。关键线索是 {线索}，意思是“{中文意思}”，只有 {答案} 说得通。{干扰项逐个一句话：它的意思/常见搭配是什么，为什么这里不行}"

T = []
# ---------- Part 5 ----------
T.append(tmpl("T5.IDENTIFY", ["QT.P5.IDENTIFY"], 5,
  "（元技能，不单独出题）所有 P5 题都附此标签：做题前先看四个选项判断是结构题还是语境题。",
  {"rule": "不生成选项；作为每道 P5 的附加标签，训练模式下先问“这是哪类题”"}, [], "single_sentence", P5_LEN,
  ["无"], "先看选项：同根不同形=词性题（只看空格前后，5–15 秒）；同词性不同义=词汇题（读全句）；介词/连词混排=看空格后接名词还是句子。",
  {"meta_tag_only": True}))
wf_slots = [
  ("T5.WORD_FORM.NOUN_SLOT", ["QT.P5.WORD_FORM", "GR.POS.NOUN_AFTER_DET", "GR.POS.NOUN_AFTER_PREP", "GR.POS.NOUN_SUBJ_OBJ"], "The ------- of the {名词短语} {谓语}… / … for her ------- to …", "冠词/所有格/介词后或主语位置缺名词"),
  ("T5.WORD_FORM.ADJ_SLOT", ["QT.P5.WORD_FORM", "GR.POS.ADJ_BEFORE_NOUN", "GR.POS.ADJ_COMPLEMENT", "GR.NONFIN.PARTICIPLE_ADJ"], "{主语} offers ------- {名词}. / … found the system very -------.", "名词前或系动词/宾补位置缺形容词（含 -ing/-ed 情感分词）"),
  ("T5.WORD_FORM.ADV_SLOT", ["QT.P5.WORD_FORM", "GR.POS.ADV_VERB", "GR.POS.ADV_ADJ", "GR.POS.ADV_AUX_SLOT", "GR.POS.ADV_SENTENCE"], "… has ------- completed … / -------, the shipment arrived …", "句子已完整，空格修饰动词/形容词/全句 → 副词"),
  ("T5.WORD_FORM.NOUN_TYPE", ["QT.P5.WORD_FORM", "GR.POS.NOUN_PERSON_THING", "GR.POS.NOUN_COUNT", "GR.POS.NOUN_COMPOUND", "VO.CONF.FORM_NOUN"], "All ------- at the conference must … (attendees vs attendance)", "名词位置已确定，要在人/物、可数/不可数、复合名词之间选"),
  ("T5.WORD_FORM.VERB_SLOT", ["QT.P5.WORD_FORM", "GR.POS.VERB_SLOT", "FD.SENT.CLAUSE_COUNT"], "The head of the department ------- the figures at every meeting.", "句子缺谓语 → 限定动词"),
]
for tid, nodes, stem, why in wf_slots:
  T.append(tmpl(tid, nodes, 5, stem,
    {"n_options": 4, "rule": "同一词根的 4 个形式（名/动/形/副或分词），只有一个词性能放进空格；不得出现两个语法都通的形式", "order": "随机，答案位置全卷均衡"},
    ["POS_MISMATCH", "NONFINITE", "COUNT_NUMBER", "FORM_LOOKALIKE"], "single_sentence", P5_LEN, P5_KNOBS_STRUCT, P5_EXPL_STRUCT,
    {"slot_rule_zh": why}))
vf = [
  ("T5.VERB_FORM.VOICE", ["QT.P5.VERB_FORM", "GR.VERB.VOICE_PASSIVE"], "The new rules ------- to all employees by e-mail last Monday.", "主语是动作承受者 → 被动；再用时间状语定时态"),
  ("T5.VERB_FORM.TENSE", ["QT.P5.VERB_FORM", "GR.VERB.TENSE_SIMPLE", "GR.VERB.TENSE_PERFECT", "GR.VERB.TENSE_FUTURE_CLAUSE"], "{人} ------- {宾语} next month. / As soon as …, we will …", "找时间状语（next month / for ten years before / as soon as）定时态"),
  ("T5.VERB_FORM.AGREE_MODAL", ["QT.P5.VERB_FORM", "GR.VERB.AGREE_SV", "GR.VERB.MODAL_BASE", "GR.VERB.SUBJUNCTIVE_DEMAND"], "The list of suppliers ------- updated … / must ------- / requested that he -------", "主谓一致（剥离 of 短语）、情态动词后原形、要求类 that 从句原形"),
]
for tid, nodes, stem, why in vf:
  T.append(tmpl(tid, nodes, 5, stem,
    {"n_options": 4, "rule": "同一动词的 4 个形态（时态/语态/单复数/非谓语），只有一个同时满足语态+时态+一致", "order": "随机"},
    ["TENSE_MISMATCH", "VOICE_MISMATCH", "AGREEMENT", "NONFINITE"], "single_sentence", P5_LEN, P5_KNOBS_STRUCT + ["时间线索是否明显"],
    "选项都是 {动词} 的不同形态 → 动词形态题。按顺序查：①要不要谓语 ②主动还是被动（{主语} 是做还是被做）③时间线索 {线索} → {时态} ④单复数。所以选 {答案}。",
    {"slot_rule_zh": why}))
vocab = [
  ("T5.VOCAB.VERB", ["QT.P5.VOCAB", "VO.LEX.VERB", "VO.COLLO.VERB_NOUN"]),
  ("T5.VOCAB.NOUN", ["QT.P5.VOCAB", "VO.LEX.NOUN"]),
  ("T5.VOCAB.ADJ", ["QT.P5.VOCAB", "VO.LEX.ADJ", "VO.COLLO.ADJ_PREP"]),
  ("T5.VOCAB.ADV", ["QT.P5.VOCAB", "VO.LEX.ADV", "VO.CONF.ADV_FOCUS", "VO.CONF.ADV_TIME"]),
  ("T5.VOCAB.PHRASE", ["QT.P5.VOCAB", "VO.COLLO.FIXED_PHRASE", "VO.CONF.BUSINESS_SENSE"]),
]
for tid, nodes in vocab:
  T.append(tmpl(tid, nodes, 5, "{场景主语} ------- {搭配宾语/补语}…（必须有 1–2 个语境线索锁定唯一答案）",
    {"n_options": 4, "rule": "4 个同词性、同形态、难度相近的词；答案与空格前后有固定搭配或语义唯一；干扰项至少 1 个近义但搭配不对、1 个形近或常见义陷阱", "order": "随机"},
    ["COLLOCATION", "SEMANTIC_NEAR", "FORM_LOOKALIKE"], "single_sentence", P5_LEN, P5_KNOBS_VOCAB, P5_EXPL_VOCAB,
    {"scene_tag": "每题另挂 1 个 VO.SCENE.* 场景节点"}))
conn = [
  ("T5.PREP", ["QT.P5.PREP", "GR.CONN.PREP_TIME", "GR.CONN.PREP_PLACE", "GR.CONN.PREP_MEANING", "GR.CONN.PREP_PHRASE_MULTI", "VO.COLLO.VERB_PREP", "VO.CONF.PREP_LOOKALIKE"],
   "… submitted ------- 5 P.M. on Friday. / comply ------- the rules", "4 个介词（或复合介词）；按时间/地点/语义/固定搭配只有一个对", ["SEMANTIC_NEAR", "COLLOCATION", "FORM_LOOKALIKE"],
   "选项都是介词 → 看空格后的名词和整句意思。{线索} 表示“{中文}”，要用 {答案}。{干扰项：各自表示什么}"),
  ("T5.CONNECTOR_MIX", ["QT.P5.CONNECTOR_MIX", "GR.CONN.PREP_VS_CONJ", "GR.CONN.CONJ_ADVERB"],
   "------- the heavy rain, the concert started on time.", "介词/连词/接续副词混排：先看后面接名词短语还是完整句子，再看逻辑", ["CONN_TYPE", "CONN_LOGIC"],
   "两步走：①空格后是{名词短语/句子} → 只能用{介词/连词/副词} ②前后是{转折/因果/让步}关系 → {答案}。{干扰项：类别错还是逻辑错}"),
  ("T5.CONJ", ["QT.P5.CONJ", "GR.CONN.CONJ_ADVERBIAL", "GR.CONN.CONJ_COORD"],
   "Please call us ------- you have any questions.", "4 个连词；按逻辑（条件/时间/让步/目的）唯一", ["CONN_LOGIC", "CONN_TYPE"],
   "空格连接两个句子 → 连词题，看两句关系：{关系}，所以用 {答案}。"),
]
for tid, nodes, stem, rule, traps, expl in conn:
  T.append(tmpl(tid, nodes, 5, stem, {"n_options": 4, "rule": rule, "order": "随机"}, traps, "single_sentence", P5_LEN,
    ["空格后结构是否一眼可辨", "逻辑关系是否需要读完两句", "是否混入同义不同类的词（despite/although）"], expl))
T.append(tmpl("T5.PRONOUN", ["QT.P5.PRONOUN", "GR.PRON.CASE", "GR.PRON.REFLEXIVE", "GR.PRON.DETERMINER_QUANT", "GR.PRON.INDEFINITE"], 5,
  "Ms. Ito asked them to send ------- the file. / ------- employee will receive …",
  {"n_options": 4, "rule": "同一人称的不同格，或 4 个数量限定词/不定代词；一致性和格位置唯一", "order": "随机"},
  ["PRON_CASE", "PRON_REFERENT", "AGREEMENT"], "single_sentence", P5_LEN, ["指代对象离空格的距离", "反身代词是否需要判断主语"],
  "选项都是代词/限定词 → 看位置：{动词后=宾格/名词前=所有格/主语=主格/主语自己=反身}；数量词看后面名词单复数。所以选 {答案}。"))
T.append(tmpl("T5.RELATIVE", ["QT.P5.RELATIVE", "GR.REL.REL_PRONOUN", "GR.REL.REL_ADVERB", "GR.REL.NOUN_CLAUSE"], 5,
  "Employees ------- cars are parked in Lot B … / The hotel ------- the dinner will be held …",
  {"n_options": 4, "rule": "who/whom/whose/which/where/what 等；看先行词是人/物/地点，从句缺不缺主语或宾语", "order": "随机"},
  ["PRON_CASE", "CONN_TYPE"], "single_sentence", P5_LEN, ["从句是否完整（缺成分=代词，完整=副词）", "先行词与空格之间是否有插入"],
  "先行词是 {先行词}，后面从句 {完整/缺主语/缺宾语/名词前缺所有格} → 用 {答案}。"))
T.append(tmpl("T5.COMPARATIVE", ["QT.P5.COMPARATIVE", "GR.COMP.COMPARATIVE", "GR.COMP.SUPERLATIVE", "GR.COMP.EQUATIVE"], 5,
  "… were ------- higher than expected. / the ------- rates of any bank",
  {"n_options": 4, "rule": "原级/比较级/最高级或程度副词（much/very/more/most）；由 than / of any / as…as 锁定", "order": "随机"},
  ["PAIR_MISMATCH", "SEMANTIC_NEAR"], "single_sentence", P5_LEN, ["比较标志词是否靠近空格"],
  "找比较标志：{than/of any/as…as} → {比较级/最高级/原级}；比较级前强调用 much/even/far，不用 very。选 {答案}。"))
T.append(tmpl("T5.PAIR_GRAMMAR", ["QT.P5.PAIR_GRAMMAR", "GR.CONN.CONJ_CORRELATIVE", "VO.CONF.SO_SUCH_TOO", "VO.CONF.QUANT_WORDS", "GR.VERB.AGREE_QUANT"], 5,
  "… either by mail ------- online / so light ------- / the ------- of customers",
  {"n_options": 4, "rule": "成对表达或数量名词：句中另一半（or/nor/that/of+可数复数）锁定唯一答案", "order": "随机"},
  ["PAIR_MISMATCH", "COUNT_NUMBER"], "single_sentence", P5_LEN, ["配对词与空格的距离"],
  "看句中的另一半：{配对词} → 只能和 {答案} 配。{干扰项各自的搭档}"))

# ---------- Part 6 ----------
P6_LEN = {"unit": "words_in_passage", "min": 80, "max": 190, "items_per_passage": 4, "insertion_per_passage": 1}
P6_TEXT = ["TX.EMAIL", "TX.LETTER", "TX.MEMO", "TX.NOTICE", "TX.ARTICLE", "TX.AD", "TX.WEB"]
p6 = [
  ("T6.INDEPENDENT", ["QT.P6.INDEPENDENT", "QT.P6.CLASSIFY"], "空格句内即可判定的词性/介词/动词形态题（同 P5 规则）",
   {"n_options": 4, "rule": "同 P5 结构题；只看空格所在句即可唯一"}, ["POS_MISMATCH", "TENSE_MISMATCH", "VOICE_MISMATCH", "CONN_TYPE"],
   "这题只看本句就能做（独立型）：{同 P5 解析}。"),
  ("T6.CTX_TENSE", ["QT.P6.CTX_TENSE", "QT.P6.CLASSIFY"], "空格句本身多个时态都通，要看发信日期/前后句判断事件已发生还是将发生",
   {"n_options": 4, "rule": "同一动词 4 个时态；只看本句至少 2 个通，必须用文中日期或前后句锁定"}, ["TENSE_MISMATCH", "VOICE_MISMATCH"],
   "只看这一句好几个时态都行，所以要看上下文：发信日期是 {日期}，事件在 {日期}，还没发生/已经发生 → {答案}。"),
  ("T6.CTX_PRONOUN", ["QT.P6.CTX_PRONOUN", "FD.READ.REFERENCE"], "空格是代词/所有格，指代对象在前句",
   {"n_options": 4, "rule": "人称/单复数/格不同的代词；对象必须在前 1–2 句里"}, ["PRON_REFERENT", "PRON_CASE"],
   "往前找它指谁：{对象} 是 {单数/复数/第几人称} → {答案}。"),
  ("T6.CTX_VOCAB", ["QT.P6.CTX_VOCAB"], "同词性词汇题，本句多个词都通，靠前后文话题锁定",
   {"n_options": 4, "rule": "4 个同词性词；至少 2 个在本句内语法语义都通，前后文决定唯一"}, ["SEMANTIC_NEAR", "COLLOCATION", "CONTRADICT"],
   "光看本句 {几个} 都说得通，但前文/后文讲的是 {话题}，所以只能是 {答案}。"),
  ("T6.CTX_CONJ_ADV", ["QT.P6.CTX_CONJ_ADV", "GR.CONN.CONJ_ADVERB", "FD.READ.DISCOURSE"], "句首接续副词 -------, …，判断前后两句逻辑",
   {"n_options": 4, "rule": "However / Therefore / In addition / For example / Instead / Otherwise 等 4 选 1；前后句关系唯一"}, ["CONN_LOGIC"],
   "前一句说 {A}，后一句说 {B}，两句是 {转折/因果/追加/举例} 关系 → {答案}。"),
]
for tid, nodes, stem, rule, traps, expl in p6:
  T.append(tmpl(tid, nodes, 6, stem, rule, traps, P6_TEXT, P6_LEN,
    ["上下文线索距离空格的句数", "篇章用词档次", "干扰项在本句内是否也通"], expl))
ins = [
  ("T6.INS_OPENING", ["QT.P6.INSERTION", "QT.P6.INS_OPENING", "FD.READ.DISCOURSE"], "段首/开篇缺一句：后文用 the/this/it 指向的东西必须由这句引出",
   "后文第一句就说 {the X / this}，前面必须先有人提到 {X}。只有 {答案} 引出了它。"),
  ("T6.INS_TRANSITION", ["QT.P6.INSERTION", "QT.P6.INS_TRANSITION", "FD.READ.REFERENCE", "FD.READ.DISCOURSE"], "段中缺一句：承接前句并引出后句（指代词/连接词是关键）",
   "前一句讲 {A}，后一句讲 {B}，中间要一句把两者接上。{答案} 里的 {关键词} 正好接住前句、引出后句。"),
  ("T6.INS_CLOSING", ["QT.P6.INSERTION", "QT.P6.INS_CLOSING"], "结尾缺一句：行动号召/联系方式/致谢，必须与前文主题一致",
   "最后一句一般是让读者做什么或怎么联系。{答案} 里的 {it/this offer} 指前文 {对象}，所以放这里。"),
]
for tid, nodes, stem, expl in ins:
  T.append(tmpl(tid, nodes, 6, stem,
    {"n_options": 4, "rule": "4 个完整句子，长度相近（差 ≤6 词），都与文章同一行业场景；正确句含指向前后文的线索词；每篇固定 1 道", "order": "随机"},
    ["OFF_TOPIC", "BROKEN_LINK", "CONTRADICT", "REPEAT_INFO"], P6_TEXT, P6_LEN,
    ["干扰句与主题的相关度（同场景=难）", "线索词是否显性（this/it/such vs 纯语义衔接）", "是否需要读前后两句以上"], expl))

# ---------- Part 7 ----------
FAM = {
 "MAIN_PURPOSE": ("What is the purpose of the {doc}? / What is the {doc} mainly about? / Why did {person} write …?",
   "正确项是全文目的的概括改写（多在第一段或 I am writing to…）；干扰项取文中细节或扩大范围",
   ["VERBATIM_WRONG", "PARTIAL", "SCOPE", "NOT_MENTIONED"], "目的题看开头：{原文句}，意思是“{中文}”。{答案} 是它的概括说法。{干扰项：只是细节/没提到}"),
 "DETAIL": ("According to the {doc}, what/when/where/who …?",
   "正确项是原文的同义改写（换词或换说法）；干扰项照搬原文词、张冠李戴或未提及",
   ["VERBATIM_WRONG", "MISATTRIBUTION", "NOT_MENTIONED", "WRONG_NUMBER"], "用题干关键词 {关键词} 回文定位到 {原文句}。原文说 {原文}，{答案} 换了个说法：{改写对照}。"),
 "DETAIL_NUMBER": ("When / How many / How much / What time …?",
   "正确项为文中数字（或换算后）；干扰项用文中其他数字或单位/时间错位",
   ["WRONG_NUMBER", "VERBATIM_WRONG", "MISATTRIBUTION"], "数字题先锁定是哪一行/哪一项：{行}，对应 {数字}。别的数字属于 {别的项}。"),
 "REQUEST_ACTION": ("What is {person} asked to do? / What are employees asked to do by …?",
   "定位 please / be asked to / must / should 句；正确项为改写；干扰项为文中其他动作",
   ["VERBATIM_WRONG", "MISATTRIBUTION", "NOT_MENTIONED"], "要求类题找 please/must/should：{原文句} → {答案}。"),
 "TRUE_INDICATED": ("What is indicated/stated about {X}?",
   "正确项为文中某处的改写；需逐项排除，干扰项多为部分正确或细节错位",
   ["PARTIAL", "VERBATIM_WRONG", "NOT_MENTIONED", "OVER_INFERENCE"], "照合题逐项核对：A {对/错因}、B …；只有 {答案} 和原文 {原文句} 一致。"),
 "NOT_TRUE": ("What is NOT mentioned/included/listed …?",
   "三个选项在文中能找到（多为改写），一个未提及；正确项常为“合理但没说”",
   ["NOT_MENTIONED"], "NOT 题反着做：A 在第 {} 句、B 在 …、C 在 …都提到了，只有 {答案} 没提到。"),
 "INFERENCE": ("What is suggested/implied about {X}? / What will most likely …?",
   "正确项需结合 1–2 处原文推一步；干扰项为过度推断或照搬原文",
   ["OVER_INFERENCE", "VERBATIM_WRONG", "REVERSE", "SCOPE"], "原文 {原文句} 说明 {事实}，只能推出 {答案}。{干扰项：推太远/原文没说}"),
 "INFER_WHO": ("For whom is the {doc} intended? / Who most likely is {person}? / What kind of business …?",
   "由称呼、场景词、职责推身份/读者；干扰项为文中出现的其他角色",
   ["MISATTRIBUTION", "OVER_INFERENCE", "NOT_MENTIONED"], "看场景词：{词1}、{词2} → 读者/身份是 {答案}。"),
 "INFER_NEXT": ("What will {person} most likely do next?",
   "答案在最后几句的承诺/计划（I'll… / Let me…）；干扰项是别人的动作",
   ["MISATTRIBUTION", "REVERSE", "OVER_INFERENCE"], "下一步看最后：{人} 说 {原文}，所以下一步是 {答案}；别的动作是别人说的。"),
 "INTENT": ("At {time}, what does {person} mean when he/she writes, \"{quote}\"?",
   "引号里多为口语短句（Leave that to me / That works / I'm on it）；必须看前一句在说什么；干扰项按字面意思",
   ["LITERAL_MEANING", "MISATTRIBUTION", "OVER_INFERENCE"], "意图题看引号前一句：{前一句} 在问/说 {事}，所以 “{quote}” 在这里的意思是 {答案}，不是字面的 {字面}。"),
 "INSERTION": ("In which of the positions marked [1], [2], [3], and [4] does the following sentence best belong? \"{sentence}\"",
   "选项固定为 [1]–[4]；插入句含指代/连接线索，只有一个位置前后都接得上",
   ["WRONG_POSITION"], "插入句里有 {线索词}，它指的是 {对象}，{对象} 出现在 [{n}] 前一句，所以放 [{n}]。其他位置前面没有 {对象}。"),
 "SYNONYM": ("The word \"{w}\" in paragraph {p}, line {l}, is closest in meaning to",
   "目标词是多义常用词，选项含它的其他常见义项；正确项放回原句意思不变",
   ["POLYSEMY_OTHER_SENSE", "SEMANTIC_NEAR"], "把选项放回原句：{原句}。这里 {w} 的意思是“{中文}”，只有 {答案} 放进去意思不变；{干扰项} 是 {w} 的别的意思。"),
 "CALC_LOOKUP": ("How much will {person} most likely pay? / Which session can {person} attend?",
   "需要表格查值 + 一条规则（折扣/免运费/时间冲突）计算；干扰项为未应用规则或应用错",
   ["WRONG_NUMBER", "VERBATIM_WRONG", "PARTIAL"], "先查表：{项目} = {数}；再套规则 {规则} → {算式} = {答案}。直接抄总价/漏算是陷阱。"),
 "CROSS_REF": ("（需两篇信息）What is true about …? / Which … will {person} …?",
   "答案必须由 A 篇规则 + B 篇个案结合得出；单看一篇会选到干扰项",
   ["WRONG_DOC", "PARTIAL", "MISATTRIBUTION", "WRONG_NUMBER"], "这是跨篇题：第 {x} 篇说 {规则}，第 {y} 篇说 {个案}，两者一合 → {答案}。只看一篇会选 {陷阱项}。"),
 "REASON": ("Why …?", "正确项为原因句（because/due to/since/as a result）的改写",
   ["VERBATIM_WRONG", "REVERSE", "NOT_MENTIONED"], "原因题找 because/due to/so：{原文句} → 原因是 {答案}。"),
}
TXLEN = {
 "TX.EMAIL": (90, 260), "TX.LETTER": (100, 260), "TX.MEMO": (80, 230), "TX.NOTICE": (50, 200), "TX.AD": (60, 220),
 "TX.JOB_POSTING": (80, 240), "TX.ARTICLE": (150, 320), "TX.WEB": (70, 240), "TX.REVIEW": (60, 200),
 "TX.INSTRUCTIONS": (70, 230), "TX.INVOICE": (30, 180), "TX.SCHEDULE": (30, 180), "TX.APP_FORM": (40, 200),
 "TX.FORM": (30, 200), "TX.TEXT_MSG": (35, 150), "TX.CHAT": (70, 230), "TX.DOUBLE": (220, 450), "TX.TRIPLE": (300, 620),
 "TX.MULTI": (220, 620)}
TXMAP = {"EMAIL": "TX.EMAIL", "LETTER": "TX.LETTER", "MEMO": "TX.MEMO", "NOTICE": "TX.NOTICE", "AD": "TX.AD",
 "JOB_POSTING": "TX.JOB_POSTING", "ARTICLE": "TX.ARTICLE", "WEB": "TX.WEB", "REVIEW": "TX.REVIEW", "INSTRUCTIONS": "TX.INSTRUCTIONS",
 "INVOICE": "TX.INVOICE", "SCHEDULE": "TX.SCHEDULE", "FORM": "TX.FORM", "TEXT_MSG": "TX.TEXT_MSG", "CHAT": "TX.CHAT",
 "DOUBLE": "TX.DOUBLE", "TRIPLE": "TX.TRIPLE", "MULTI": "TX.MULTI"}
P7_KNOBS = ["正确项改写程度（原词→同义词→概括）", "定位句位置（开头=易，中段/跨段=难）", "干扰项与原文用词重合度", "需要整合的句数/篇数", "文本长度与用词档次"]
for n in G["nodes"]:
  nid = n["id"]
  if n["is_group"] or not (nid.startswith("QT.P7X.") or nid == "QT.P7.REASON"):
    continue
  if nid == "QT.P7.REASON":
    fam, tx = "REASON", None
  else:
    _, _, fam, tx = nid.split(".", 3)
  stem, rule, traps, expl = FAM[fam]
  txnode = TXMAP.get(tx) if tx else None
  lo, hi = TXLEN.get(txnode, (60, 300)) if txnode else (50, 620)
  nodes = [nid] + ([txnode] if txnode and txnode in NODES else [])
  if fam == "CROSS_REF": nodes.append("ST.LOCATE.PARAPHRASE_MATCH")
  if fam in ("DETAIL", "REQUEST_ACTION", "REASON"): nodes.append("ST.LOCATE.QUESTION_FIRST")
  if fam == "NOT_TRUE": nodes.append("ST.ELIM.OPTIONS")
  extra = {}
  if fam == "INSERTION": extra["fixed_options"] = ["[1]", "[2]", "[3]", "[4]"]; extra["only_in"] = "single passage, set of 3–4 questions, last question of set"
  if fam == "INTENT": extra["only_in"] = "TX.TEXT_MSG / TX.CHAT；引号原话必须在文中逐字出现并带时间戳"
  if tx in ("DOUBLE", "TRIPLE", "MULTI"): extra["set_size"] = 5
  T.append(tmpl(f"T7.{fam}.{tx}" if tx else "T7.REASON", nodes, 7, stem,
    {"n_options": 4, "rule": rule, "order": "随机（INSERTION 固定 [1]–[4]；数字选项按从小到大）", "option_length": "四项长度相近，正确项不得明显最长"},
    traps, txnode or "any", {"unit": "words_in_set_text", "min": lo, "max": hi}, P7_KNOBS, expl, extra))

out = {"version": "templates_v1", "built": "2026-10-21", "format_version": "current",
  "scope": "TOEIC L&R Reading 现行线性版：P5 30 / P6 16（每篇 4 题含 1 句插入）/ P7 54（单篇 29：10 篇各 2–4 题；多篇 25：双篇 2 组+三篇 3 组，各 5 题）",
  "numbering": {"P5": [101, 130], "P6": [131, 146], "P7_single": [147, 175], "P7_multi": [176, 200]},
  "target_time_sec_base": {"P5": 26.4, "P6": 33.8, "P7": 67.4, "source": "EdNet 中位用时（work/ednet_prior_by_part.csv）"},
  "trap_types": TRAPS, "templates": T}
os.makedirs(f"{ROOT}/data/templates", exist_ok=True)
json.dump(out, open(f"{ROOT}/data/templates/item_templates.json", "w"), ensure_ascii=False, indent=1)
leaf_q = [n["id"] for n in G["nodes"] if n["layer"] == "qtype" and not n["is_group"]]
covered = {x for t in T for x in t["node_ids"]}
print(len(T), "templates; qtype leaves", len(leaf_q), "uncovered:", [x for x in leaf_q if x not in covered])
bad = [x for t in T for x in t["node_ids"] if x not in NODES]
print("unknown node ids:", bad)
