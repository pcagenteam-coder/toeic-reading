# -*- coding: utf-8 -*-
"""合并五路技巧（书籍 / 新东方·B站 / 中文论坛 / 英文·ETS / 日韩）→ data/strategies/strategy_library_v1.json
用法：python3 work/strategies/build_strategy_library.py
只读：data/strategies/books.json, xdf_bilibili.json, data/graph_v1.json；summary 三路按 work/reports/strategy_findings_summary.md 手工编码。
"""
import json, math, os, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)

graph = json.load(open(P('data/graph_v1.json')))
NODES = {n['id']: n for n in graph['nodes']}
books = json.load(open(P('data/strategies/books.json')))
BK = {t['id']: t for t in books['techniques']}
XB = {t['id']: t for t in json.load(open(P('data/strategies/xdf_bilibili.json')))}

# ---- 汇总渠道来源（strategy_findings_summary.md 中的三路 + ETS 官方）----
SUMMARY_SOURCES = {
    'SUM:FORUM': {'channel': 'forum', 'desc': '中文论坛 24 来源汇总（知乎/B站专栏/PTT/etogether 等），见 work/reports/strategy_findings_summary.md', 'count_rule': '报告未给逐条来源数，按 1 计（下限）'},
    'SUM:EN': {'channel': 'en', 'desc': '英文备考站约 35 来源汇总（engoo/990prep/bestmytest 等）', 'count_rule': '用报告括号里的来源数（如 12 源）；未给数的按 1 计'},
    'SUM:JK': {'channel': 'jk', 'desc': '日韩约 81 来源汇总（trankyblog/toiguide/english-route/toeicstory/hackers 等）', 'count_rule': '未给逐条来源数，按 1 计（下限）'},
    'ETS:HANDBOOK': {'channel': 'ets', 'desc': 'ETS 考生手册 https://www.ets.org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf', 'count_rule': '1'},
    'ETS:RM-17-05': {'channel': 'ets', 'desc': 'ETS RM-17-05 https://www.ets.org/Media/Research/pdf/RM-17-05.pdf（各 Part p 值、完成率）', 'count_rule': '1'},
}

def src(sid, n=None):
    """返回 (source_id, mention_count)。BK/XB 用原文件 mention_count；SUM 用传入数或 1。"""
    if sid.startswith('BK:'):
        return sid, BK[sid[3:]]['mention_count']
    if sid.startswith('XB:'):
        return sid, XB[sid[3:]]['mention_count']
    return sid, (n or 1)

ALL5 = [5, 6, 7]
U, C = 'universal', 'current'
E = []  # entries

def add(id, title, rule, parts, band, fmt, sources, consensus, work_rule, qt=(), tx=(), st=(), sk=(),
        practice=True, mock=True, mode_note='', counter='', suggest=None, note=''):
    E.append(dict(id=id, title_zh=title, rule_zh=rule, parts=parts, qtype_nodes=list(qt), texttype_nodes=list(tx),
                  strategy_nodes=list(st), skill_nodes=list(sk), target_band=band, format_version=fmt,
                  _sources=sources, consensus=consensus, work_rule=work_rule, practice_mode=practice,
                  mock_mode=mock, mode_note=mode_note, counter_examples=counter, suggested_new_node=suggest, note=note))

LOW, MID, HIGH = '<600', '600-800', '800+'
H, M, I = '高', '中', '个人经验'

# ======================= Part 5 =======================
add('SL-P5-01', '看选项判题型', '先扫四个选项判断题型（词性/动词形态/介连副/代词/词汇），语法类只看空格周边，词汇类读全句。',
    [5, 6], [LOW], U, [src('BK:P5-01'), src('XB:XB-12'), src('SUM:FORUM'), src('SUM:JK')], H,
    '先看四个选项，再决定这句读多少。', qt=['QT.P5.IDENTIFY', 'QT.P6.INDEPENDENT'], st=['ST.LOCATE.DEPTH_BY_QTYPE'],
    counter='选项看似词性题、但同词性的两个都合语法（如 -ion/-ant 人与物）时，仍要读意思。')
add('SL-P5-02', '词性题看空格位置', '限定词/介词后→名词；名词前、be/系动词后→形容词；完整句中修饰动词/形容词/全句→副词；a/an(+very)+adj+n、adj and adj 同词性。',
    [5, 6], [LOW], U, [src('BK:P5-02'), src('XB:XB-13'), src('SUM:FORUM'), src('SUM:JK')], H,
    '只看空格前后两三个词定词性，5–15 秒交卷。', qt=['QT.P5.WORD_FORM', 'QT.P6.INDEPENDENT'],
    st=['ST.TIME.PER_ITEM_P5'],
    sk=['GR.POS', 'GR.POS.NOUN_AFTER_DET', 'GR.POS.NOUN_AFTER_PREP', 'GR.POS.ADJ_BEFORE_NOUN', 'GR.POS.ADJ_COMPLEMENT', 'GR.POS.ADV_VERB', 'GR.POS.ADV_ADJ', 'GR.POS.ADV_AUX_SLOT', 'GR.POS.ADV_SENTENCE'],
    counter='副词位置常有多个合法位置；形容词 vs 分词形容词（-ing/-ed）要看主被动/情感对象。')
add('SL-P5-03', '同是名词再辨人/物与可数', '填名词时再看可数/不可数、限定词搭配、人名词 vs 事物名词、复合名词。',
    [5], [MID], U, [src('BK:P5-10')], M, '名词定了别急着选：人还是物？要不要加 s？',
    qt=['QT.P5.WORD_FORM'], sk=['GR.POS.NOUN_COUNT', 'GR.POS.NOUN_PERSON_THING', 'GR.POS.NOUN_COMPOUND'])
add('SL-P5-04', '数谓语和连接词', '先数句子的谓语动词与连接词：缺谓语填限定动词；已有谓语则填非谓语或连接成分。',
    [5, 6], [LOW, MID], U, [src('BK:P5-03')], M, '数一数：一个连接词配两个谓语，少了谁就补谁。',
    qt=['QT.P5.VERB_FORM', 'QT.P5.CONNECTOR_MIX'], sk=['FD.SENT.CLAUSE_COUNT', 'GR.POS.VERB_SLOT'])
add('SL-P5-05', '删修饰找主干', '先划掉介词短语、分词短语、插入从句，找到主谓宾后再判断空格成分。',
    [5, 6, 7], [LOW, MID], U, [src('BK:P5-16'), src('XB:XB-15')], H, '长句先砍枝叶，只留主干再填空。',
    qt=['QT.P5.WORD_FORM', 'QT.P5.VERB_FORM'], sk=['FD.SENT.MODIFIER_STRIP', 'FD.SENT.LONG'],
    mode_note='练习模式可在屏幕上把修饰语变灰；模考模式只能心里删（题本禁止写画）。',
    counter='空格本身就在修饰语里（如分词短语中缺词）时，要在该短语内部判断。')
add('SL-P5-06', '动词题四步排查', '先判谓语还是非谓语 → 再定主动/被动 → 再定时态 → 最后查主谓一致（数）。',
    [5, 6], [LOW, MID], U, [src('BK:P5-04'), src('XB:XB-14')], H, '动词题按“谓语？→主被动→时态→单复数”过四道闸。',
    qt=['QT.P5.VERB_FORM', 'QT.P6.CTX_TENSE'],
    sk=['GR.VERB', 'GR.VERB.AGREE_SV', 'GR.VERB.VOICE_PASSIVE', 'GR.VERB.TENSE_SIMPLE', 'GR.VERB.TENSE_PERFECT', 'GR.VERB.TENSE_FUTURE_CLAUSE'],
    counter='Part 6 时态以全文时间线为准，本句时间状语缺失时不能只靠本句（见 SL-P6-03）。',
    note='冲突：书籍为“数→态→时”，青藤/Cindy 为“谓语→态→时→数”。取后者：先排除非谓语选项最省时；数一致可随时顺手查。')
add('SL-P5-07', '非谓语看搭配与主被动', '记住只接 to do / 只接 -ing 的词；分词按与被修饰名词的主被动关系选 -ing 或 -ed。',
    [5], [MID], U, [src('BK:P5-08')], M, 'to do 还是 -ing 看前面的词；-ing/-ed 看名词是主动做还是被做。',
    qt=['QT.P5.VERB_FORM'], sk=['GR.NONFIN', 'GR.NONFIN.TO_INF', 'GR.NONFIN.GERUND', 'GR.NONFIN.PARTICIPLE_MODIFIER', 'GR.NONFIN.PARTICIPLE_CLAUSE', 'GR.NONFIN.PARTICIPLE_ADJ'])
add('SL-P5-08', '动词句型与宾补', '掌握及物/不及物、双宾与宾补动词；make/let/have 后宾补用原形，其他多用 to do；近义动词句型不同（inform sb of / explain sth）。',
    [5], [MID, HIGH], U, [src('BK:P5-21')], M, '先看动词后面能跟什么，再看选项。',
    qt=['QT.P5.VERB_FORM', 'QT.P5.VOCAB'], sk=['GR.VERB.VERB_PATTERN', 'VO.CONF.SYN_VERB_PATTERN', 'GR.VERB.MODAL_BASE'])
add('SL-P5-09', '介/连/副看空格后面', '介词、连词、副词混排时：后接名词(短语)→介词；后接完整主谓→连词；两句已完整只缺逻辑衔接→接续副词。',
    [5, 6], [LOW, MID], U, [src('BK:P5-05')], M, '看空格后面：名词用介词，整句用连词，前后两句都完整用副词。',
    qt=['QT.P5.CONNECTOR_MIX', 'QT.P5.CONJ', 'QT.P5.PREP'], sk=['GR.CONN.PREP_VS_CONJ', 'GR.CONN.CONJ_ADVERBIAL', 'GR.CONN.CONJ_ADVERB'],
    counter='结构确定词类后，同类里多个选项仍需按语义（因果/让步/条件）二选一。')
add('SL-P5-10', '介词题先搭配后语义', '先按空格前后搭配解（时间点/时段、地点、固定介词），搭配不明再按语义（原因/让步/目的/关于）选。',
    [5, 6], [LOW, MID], U, [src('BK:P5-11')], M, '介词先想“固定跟谁搭”，想不到再翻译。',
    qt=['QT.P5.PREP'], sk=['GR.CONN.PREP_TIME', 'GR.CONN.PREP_PLACE', 'GR.CONN.PREP_MEANING', 'GR.CONN.PREP_PHRASE_MULTI', 'VO.CONF.PREP_LOOKALIKE'])
add('SL-P5-11', '代词题先定格再定指代', '先看位置定格（主格/宾格/所有格/名词性物主/反身），再看所指对象的单复数与人/物。',
    [5, 6], [LOW], U, [src('BK:P5-06')], M, '代词先看站哪儿（格），再看替谁（单复数）。',
    qt=['QT.P5.PRONOUN', 'QT.P6.CTX_PRONOUN'], sk=['GR.PRON.CASE', 'GR.PRON.POSSESSIVE_PRONOUN', 'GR.PRON.REFLEXIVE', 'GR.PRON.INDEFINITE', 'GR.PRON.DEMONSTRATIVE'])
add('SL-P5-12', '关系词看先行词与从句完整度', '看有无先行词、指人还是物，再看后面从句缺不缺成分（缺主宾→关系代词，完整→关系副词/that 名词从句）。',
    [5], [MID], U, [src('BK:P5-07')], M, '关系词问两件事：前面有没有名词？后面缺不缺东西？',
    qt=['QT.P5.RELATIVE'], sk=['GR.REL', 'GR.REL.REL_PRONOUN', 'GR.REL.REL_ADVERB', 'GR.REL.REL_WHAT', 'GR.REL.NOUN_CLAUSE', 'GR.REL.COMPOUND_REL'])
add('SL-P5-13', '比较题看标志词', 'than→比较级；the…of/in/among/ever→最高级；as…as→原级；强调比较级用 much/even/far/still。',
    [5], [LOW, MID], U, [src('BK:P5-09')], M, '找 than / the / as 三个信号，秒选。',
    qt=['QT.P5.COMPARATIVE'], sk=['GR.COMP.COMPARATIVE', 'GR.COMP.SUPERLATIVE', 'GR.COMP.EQUATIVE'],
    counter='新制考频很低（约 1–2%），600 前不必专练。')
add('SL-P5-14', '成对表达找搭档词', 'both–and、either–or、neither–nor、not only–but (also)、whether–or：看到一半就找另一半。',
    [5], [LOW], U, [src('BK:P5-19')], M, '看到 both/either/neither/whether，先去句子里找它的搭档。',
    qt=['QT.P5.PAIR_GRAMMAR'], sk=['GR.CONN.CONJ_CORRELATIVE'], note='书评称近年出题减少。')
add('SL-P5-15', '数量词与单复数一致', 'each/every + 单数；a number of + 复数；the number of + 单数谓语；amount/number、few/little 区分可数。',
    [5], [MID], U, [src('BK:P5-22')], M, '先看数量词，再决定名词和动词要不要 s。',
    qt=['QT.P5.PAIR_GRAMMAR', 'QT.P5.PRONOUN'], sk=['GR.VERB.AGREE_QUANT', 'GR.PRON.DETERMINER_QUANT', 'VO.CONF.QUANT_WORDS'])
add('SL-P5-16', '特殊句式记固定形式', '要求/建议类 that 从句用动词原形；省略 if 的倒装（Should/Had…）；并列结构前后同形；否定词/only 前置倒装；as requested 类省略。',
    [5], [HIGH], U, [src('BK:P5-18')], M, '见到 request/suggest that、句首 Should，直接套模板。',
    qt=['QT.P5.VERB_FORM', 'QT.P5.PAIR_GRAMMAR'],
    sk=['GR.VERB.SUBJUNCTIVE_DEMAND', 'GR.VERB.CONDITIONAL_INVERSION', 'GR.SPECIAL.PARALLEL', 'GR.SPECIAL.INVERSION_NEG', 'GR.SPECIAL.ELLIPSIS'],
    counter='单项考频 <1%，800 前收益低。')
add('SL-P5-17', '副词按功能辨', '时间副词（already/still/yet）、焦点副词（just/only/even）、so/such/too/enough、also/too/either 按功能和位置辨；never 可直接放动词前，not 需借助动词。',
    [5], [MID], U, [src('BK:P5-20'), src('XB:XB-18')], M, '副词不看中文意思，先看它管时间、强调还是程度。',
    qt=['QT.P5.VOCAB', 'QT.P5.WORD_FORM'], sk=['VO.CONF.ADV_TIME', 'VO.CONF.ADV_FOCUS', 'VO.CONF.SO_SUCH_TOO'])
add('SL-P5-18', '词汇题先找搭配', '词汇题先找搭配与语法线索（介词搭配、及物性、固定短语）“不翻译解”；副/形词义题先把句子压成“修饰词+中心词”；线索不足再读全句。',
    [5, 6], [LOW, MID], U, [src('BK:P5-12'), src('XB:XB-16'), src('XB:XB-17')], H,
    '词汇题先看空格跟谁搭，搭不上的先划掉，再看意思。', qt=['QT.P5.VOCAB', 'QT.P6.CTX_VOCAB'],
    sk=['VO.COLLO', 'VO.COLLO.VERB_PREP', 'VO.COLLO.VERB_NOUN', 'VO.COLLO.ADJ_NOUN', 'VO.COLLO.ADV_VERB_ADJ', 'VO.LEX', 'VO.LEX.VERB', 'VO.LEX.NOUN', 'VO.LEX.ADJ', 'VO.LEX.ADV'],
    counter='Part 6 词汇题几个选项本句都通时，以全文为准（SL-P6-06）。')
add('SL-P5-19', '常用词记商务义', '成组辨析近义词，记住常见词的商务义项（address=处理、issue=期刊/发放、term=条款）。',
    [5, 7], [MID, HIGH], U, [src('BK:P5-13')], M, '熟词别按日常意思选，先想它在公司里是什么意思。',
    qt=['QT.P5.VOCAB', 'QT.P7.SYNONYM'], sk=['VO.CONF.BUSINESS_SENSE', 'VO.CONF.POLYSEMY_CONTEXT', 'VO.CONF.SYN_NOUN', 'VO.CONF.SYN_ADJ'])
add('SL-P5-20', '词缀猜词性', '后缀定词性（-tion/-ment 名词、-ive/-able 形容词、-ly 副词、-ize 动词），词根词缀辅助记忆。',
    [5], [LOW], U, [src('BK:P5-17')], M, '不认识的词先看尾巴，尾巴决定词性。',
    qt=['QT.P5.WORD_FORM'], sk=['FD.VOC.AFFIX', 'VO.CONF.FORM_ADJ', 'VO.CONF.FORM_NOUN'],
    counter='-ly 结尾的形容词（timely/costly/friendly）、-al 结尾的名词（approval/proposal）是例外陷阱。')
add('SL-P5-21', 'P5 单题限时', 'P5 词性题约 5–15 秒、语法 15 秒、词汇 ≤20–30 秒；超时直接选一个往下走。',
    [5], [LOW, MID], U, [src('BK:P5-15'), src('XB:XB-19'), src('SUM:EN', 5), src('SUM:FORUM'), src('SUM:JK')], H,
    '每张 P5 工单有倒计时，铃响就交。', qt=['QT.P5.IDENTIFY'], st=['ST.TIME.PER_ITEM_P5', 'ST.GIVEUP.CUTOFF_RULE'],
    mode_note='练习模式显示单题计时；模考模式不显示，只在检查点提示。',
    note='秒数口径不一（5–20 秒 / 20–30 秒），取“按题型分档”：词性 15、语法 20、词汇 30 秒为上限。')
add('SL-P5-22', '按考频排学习顺序', '先攻高频题型（词汇约 30%、词性约 25%、介词约 11%、接续/动词/副词/代词各 7–9%），比较、特殊句式后补。',
    [5], [LOW, MID], U, [src('BK:P5-14'), src('SUM:JK')], M, '先练常考的活，冷门活放到后面。',
    qt=['QT.P5.VOCAB', 'QT.P5.WORD_FORM', 'QT.P5.PREP'], st=['ST.REVIEW.DIAGNOSE_BY_TYPE'], mock=False,
    mode_note='引擎层排课规则，用户无需执行。', note='比例来自日韩合算 240 题口径（strategy_findings_summary.md）。')
add('SL-P5-23', 'P5 瓶颈转练 P6/P7', 'P5 稳定只错 3–4 题后再刷 P5 收益很小，改为大量做 P6/P7 积累地道表达。',
    [5, 6, 7], [HIGH], U, [src('XB:XB-21')], I, 'P5 已经很稳，就把时间挪给长文。',
    st=['ST.REVIEW.DIAGNOSE_BY_TYPE'], mock=False, suggest='ST.REVIEW.PLATEAU_SWITCH（瓶颈期换练）')

# ======================= Part 6 =======================
add('SL-P6-01', 'P6 顺着读全文', 'Part 6 按顺序通读，不只读空格所在句：新制每篇 4 题，约 65% 需上下文，只靠本句能解的很少。',
    [6], [LOW, MID], C, [src('BK:P6-01'), src('SUM:EN', 5), src('SUM:JK')], H, 'P6 从头顺着读，读到空就填。',
    qt=['QT.P6.CLASSIFY'], tx=['TX.EMAIL', 'TX.LETTER', 'TX.MEMO', 'TX.NOTICE', 'TX.AD', 'TX.ARTICLE', 'TX.WEB'],
    st=['ST.LOCATE.DEPTH_BY_QTYPE'], counter='独立型词性题（如 the ___ of）可秒做，不必等读完。',
    note='与已弃用的旧制做法 XB-27“P6 只看空格句”冲突，按新制取本条。')
add('SL-P6-02', 'P6 两类分流', '把 P6 题分为“句内独立可解”和“需上下文”两类：前者按 P5 方法速答；后者（时态/代词/接续副词/词汇/插入句）必须看前后文。',
    [6], [LOW, MID], C, [src('BK:P6-02'), src('XB:XB-23')], H, '先分拣：本句能解的秒做，要看上下文的放慢。',
    qt=['QT.P6.CLASSIFY', 'QT.P6.INDEPENDENT'])
add('SL-P6-03', '时态看全文时间线', 'P6 时态题本句语法上多个都通时，以全文时间线为准：看发信日期、前后句、事件是否已发生。',
    [6], [MID], C, [src('BK:P6-03')], M, '先看这封信是哪天写的，事情发生了没有。',
    qt=['QT.P6.CTX_TENSE'], sk=['GR.VERB.TENSE_SIMPLE', 'GR.VERB.TENSE_PERFECT', 'GR.VERB.TENSE_FUTURE_CLAUSE'])
add('SL-P6-04', '代词回前文找指代', 'P6 代词题回前文找所指对象，按单复数、人/物、公司/个人选代词。',
    [6], [MID], C, [src('BK:P6-04')], M, '代词题往回找“它/他们”到底指谁。',
    qt=['QT.P6.CTX_PRONOUN'], sk=['FD.READ.REFERENCE', 'GR.PRON.CASE'])
add('SL-P6-05', '接续副词判前后逻辑', '判断前后两句关系（转折/因果/追加/举例/顺序），再选 however/therefore/in addition/for example 等。',
    [6], [MID], C, [src('BK:P6-05'), src('XB:XB-23')], H, '先给两句关系贴标签：转折、因果还是追加。',
    qt=['QT.P6.CTX_CONJ_ADV'], sk=['GR.CONN.CONJ_ADVERB', 'FD.READ.DISCOURSE'])
add('SL-P6-06', '语境词汇以全文为准', 'P6 词汇题几个选项本句都通顺时，以全文主题和前后信息决定。',
    [6], [MID], C, [src('BK:P6-06')], M, '本句都通？回头看整篇在讲什么。',
    qt=['QT.P6.CTX_VOCAB'], sk=['VO.CONF.POLYSEMY_CONTEXT'])
add('SL-P6-07', '插入句看衔接线索', '句子插入题先抓全文主题和段落走向，再用候选句里的代词（this/these/they）、连接词、新旧信息检查能否接上前后句。',
    [6], [MID, HIGH], C, [src('BK:P6-07'), src('XB:XB-24'), src('SUM:FORUM'), src('SUM:JK'), src('SUM:EN', 5)], H,
    '插入句先看候选句里的 this/they/also，问它在指前面哪件事。',
    qt=['QT.P6.INSERTION', 'QT.P6.INS_OPENING', 'QT.P6.INS_TRANSITION', 'QT.P6.INS_CLOSING'], sk=['FD.READ.REFERENCE', 'FD.READ.DISCOURSE'],
    counter='候选句的代词在前文找不到对象，再“顺”也排除。')
add('SL-P6-08', '插入句按位置预测句型', '空在段首多为引入/目的句，在段中为衔接/举例句，在末尾多为“请联系/欢迎/行动号召”句。',
    [6], [MID, HIGH], C, [src('SUM:JK')], I, '空在开头找“开场白”，空在结尾找“请联系我们”。',
    qt=['QT.P6.INS_OPENING', 'QT.P6.INS_TRANSITION', 'QT.P6.INS_CLOSING'],
    counter='只是倾向（toiguru.jp 统计），必须再用 SL-P6-07 的衔接线索验证。')
add('SL-P6-09', '插入句后做、没把握就猜', '插入句是每篇最难的一题：先做本篇其他 3 题再回来；600–700 目标没把握直接猜，不恋战。',
    [6], [LOW, MID], C, [src('XB:XB-25'), src('XB:XB-06'), src('SUM:JK')], M, '插入句最后做，30 秒没头绪就先猜一个。',
    qt=['QT.P6.INSERTION'], st=['ST.ORDER.HARD_ITEMS_LAST', 'ST.GIVEUP.CUTOFF_RULE', 'ST.GIVEUP.TARGET_BASED'],
    counter='800+ 目标不应放弃插入句；且先做其余 3 题本身就能提供解插入句的上下文。')
add('SL-P6-10', 'P6 是否需要专项', '平均每篇错 ≤1 题按常规练；错误率超过约 1/3 再开 P6 专项。',
    [6], [LOW, MID], C, [src('XB:XB-26')], I, 'P6 每篇错两题以上，才开专项训练。',
    qt=['QT.P6.CLASSIFY'], st=['ST.REVIEW.DIAGNOSE_BY_TYPE'], mock=False, mode_note='引擎诊断阈值。')

# ======================= Part 7 =======================
add('SL-P7-01', '先题后文', '先读题干（必要时连选项），判断题型并记住人名/日期/数字/动作词，再回原文扫读定位、在定位句前后细读比对。',
    [7], [LOW, MID], U,
    [src('BK:P7-01'), src('XB:XB-28'), src('SUM:FORUM'), src('SUM:EN', 12), src('SUM:JK')], H,
    '先看题，再进文找答案。', qt=['QT.P7.DETAIL', 'QT.P7.DETAIL_NUMBER', 'QT.P7.REQUEST_ACTION', 'QT.P7.REASON'],
    st=['ST.LOCATE.QUESTION_FIRST'],
    mode_note='练习模式可高亮题干关键词；模考模式不能在题本上划（ETS 禁止），只能记在脑中。',
    counter='短信/表格等很短的文本可先扫全文；主旨、推断题仍需读相关段落。',
    note='XB-28 原步骤“划出人名、日期…”违反纸笔考题本禁写规定，已改写为“记住”。论坛对先题还是先文有分歧，见 md 冲突表。')
add('SL-P7-02', '题序≈文序，两题一组', '设问顺序大体与原文顺序一致：两题一组读题，再在对应区间一次找完。',
    [7], [MID], C, [src('SUM:JK'), src('SUM:FORUM')], M, '一次拿两道题进文，顺路把两个答案都找出来。',
    qt=['QT.P7.DETAIL'], st=['ST.LOCATE.QUESTION_ORDER'],
    counter='主旨题、NOT 题、跨篇题不按文序；多篇的跨篇题位置不固定（SL-P7-18）。')
add('SL-P7-03', '细节题用锚点扫读', '细节(5W1H)题用题干里的专名、数字、日期、独特名词作锚点扫读，只精读锚点附近一两句；选项通常是改写。',
    [7], [LOW], U, [src('BK:P7-03'), src('XB:XB-30')], H, '拿专名和数字当路标，找到路标只读它前后两句。',
    qt=['QT.P7.DETAIL', 'QT.P7.DETAIL_NUMBER', 'QT.P7X.DETAIL.EMAIL', 'QT.P7X.DETAIL.ARTICLE', 'QT.P7X.DETAIL.NOTICE', 'QT.P7X.DETAIL.WEB', 'QT.P7X.DETAIL_NUMBER.FORM', 'QT.P7X.DETAIL_NUMBER.SCHEDULE', 'QT.P7X.DETAIL.TEXT_MSG'],
    st=['ST.LOCATE.KEYWORD_SCAN'], sk=['FD.READ.SCAN'],
    counter='题干关键词在文中被改写（job→position）时扫不到原词，要按意思找。')
add('SL-P7-04', '按改写匹配，同词选项要警惕', '正确选项多是原文的同义改写（约 70%）；照搬原文词语的选项常是陷阱，要核对意思。',
    [5, 6, 7], [LOW, MID], U,
    [src('BK:P7-09'), src('XB:XB-31'), src('SUM:FORUM'), src('SUM:EN', 6), src('SUM:JK')], H,
    '答案通常换了说法；和原文一字不差的选项先多看一眼。',
    qt=['QT.P7.DETAIL', 'QT.P7.TRUE_INDICATED', 'QT.P7.INFERENCE', 'QT.P7.REASON'],
    st=['ST.LOCATE.PARAPHRASE_MATCH', 'ST.ELIM.TRAP_TYPES'],
    sk=['VO.PARA', 'VO.PARA.WORD_SYNONYM', 'VO.PARA.WORD_TO_PHRASE', 'VO.PARA.GENERALIZE', 'VO.PARA.POS_SHIFT', 'VO.PARA.SUMMARY_NOMINAL', 'VO.PARA.ROLE_REFERENCE'],
    counter='约 30% 正解保留原词；数字/日期/专名题常原样出现，不能一见原词就排除。',
    note='新东方课程认为改写“没有技巧，只能靠词汇和语法”，因此本条配合 VO.PARA 词包训练。')
add('SL-P7-05', '主旨/目的题看开头', '主旨/目的题答案多在开头（I am writing to / in regard to / We are pleased to / Please be advised）。',
    [7], [LOW], U, [src('BK:P7-02'), src('XB:XB-32')], H, '问“为什么写这封信”，先看第一段。',
    qt=['QT.P7.MAIN_PURPOSE', 'QT.P7X.MAIN_PURPOSE.EMAIL', 'QT.P7X.MAIN_PURPOSE.LETTER', 'QT.P7X.MAIN_PURPOSE.NOTICE', 'QT.P7X.MAIN_PURPOSE.MEMO', 'QT.P7X.MAIN_PURPOSE.ARTICLE', 'QT.P7X.MAIN_PURPOSE.AD', 'QT.P7X.MAIN_PURPOSE.MULTI'],
    tx=['TX.EMAIL', 'TX.LETTER', 'TX.NOTICE', 'TX.MEMO'],
    counter='2023–2026 新题有时首段全是铺垫，答案在第二段中部（XB-38，个人考后观察）；开头找不到就往下读到第一个“请求/通知”句。')
add('SL-P7-06', '选项太宽太窄先怀疑', '主旨、照合、推断题中，范围过宽、过窄或带绝对化词（always/only/all）的选项先排除。',
    [7], [MID], U, [src('BK:P7-02'), src('SUM:JK')], M, '选项说得太大、太小、太绝对，先打问号。',
    qt=['QT.P7.MAIN_PURPOSE', 'QT.P7.TRUE_INDICATED', 'QT.P7.INFERENCE'], st=['ST.ELIM.SCOPE'],
    counter='原文本身就用了 only/all 时，绝对化选项可能正确。')
add('SL-P7-07', 'NOT/TRUE 题逐项核对', 'NOT/TRUE 题把四个选项逐一回原文核对，找到的划掉，剩下未提及（或唯一相符）的就是答案。',
    [7], [LOW, MID], U, [src('BK:P7-04'), src('XB:XB-34'), src('SUM:EN', 6)], H, 'NOT 题四个选项挨个对账，对上的划掉。',
    qt=['QT.P7.NOT_TRUE', 'QT.P7.TRUE_INDICATED', 'QT.P7X.NOT_TRUE.AD', 'QT.P7X.NOT_TRUE.ARTICLE', 'QT.P7X.NOT_TRUE.JOB_POSTING'],
    st=['ST.ELIM.OPTIONS'], mode_note='练习模式可在选项上打勾/叉；模考模式题本不能写，只能心里记。')
add('SL-P7-08', '耗时题放到本组最后', 'NOT/TRUE、无关键词的照合题、长选项推断题耗时，先跳过，做完本组其他题再回来。',
    [7], [LOW, MID], U, [src('BK:P7-04'), src('BK:P7-13'), src('SUM:EN', 5)], H, '费时的题“稍后处理”，先拿好拿的分。',
    qt=['QT.P7.NOT_TRUE', 'QT.P7.TRUE_INDICATED', 'QT.P7.INFERENCE'], st=['ST.ORDER.HARD_ITEMS_LAST'],
    counter='先做其他题时已读过大部分原文，回头做 NOT 题反而更快；不要跳到下一组再回来（涂卡易错位）。')
add('SL-P7-09', 'indicated 题四步', '“What is indicated about X”：先吃透 about 后的对象 → 回文定位所有提到 X 的地方 → 理解后推断 → 找同义替换选项；Note that / Please note 后的句子必读。',
    [7], [MID], C, [src('XB:XB-33')], I, '先认清问的是谁，把文中提到它的地方都找出来再比选项。',
    qt=['QT.P7.TRUE_INDICATED', 'QT.P7X.TRUE_INDICATED.ARTICLE', 'QT.P7X.TRUE_INDICATED.WEB', 'QT.P7X.TRUE_INDICATED.REVIEW', 'QT.P7X.TRUE_INDICATED.JOB_POSTING'],
    st=['ST.LOCATE.KEYWORD_SCAN'], sk=['VO.COLLO.REQUEST_EXPR'])
add('SL-P7-10', '推断要有原文依据', '推断题答案必须能在原文找到依据，是原文信息的稳妥推论，不靠常识或想象；过度推断是最常见陷阱。',
    [7], [MID], U, [src('BK:P7-05'), src('ETS:RM-17-05')], H, '能指出原文哪句话撑腰才选，脑补的不选。',
    qt=['QT.P7.INFERENCE', 'QT.P7.INFER_WHO', 'QT.P7.INFER_NEXT', 'QT.P7X.INFERENCE.ARTICLE', 'QT.P7X.INFERENCE.EMAIL', 'QT.P7X.INFERENCE.REVIEW', 'QT.P7X.INFER_WHO.NOTICE', 'QT.P7X.INFER_WHO.JOB_POSTING', 'QT.P7X.INFER_WHO.CHAT', 'QT.P7X.INFER_NEXT.CHAT'],
    st=['ST.ELIM.TRAP_TYPES'], mode_note='练习模式要求“划依据”句（仅练习）；模考模式不划。',
    note='ETS RM-17-05：推断题是 Part 7 题量最大的一类。')
add('SL-P7-11', '按题型决定读多少', '主旨和有关键词的细节题只读相关部分；NOT/TRUE、推断题要读完相关段甚至全文才能确定，单独留时间；寻读找信息、略读按意群抓主题。',
    [6, 7], [MID], U, [src('BK:P7-14'), src('XB:XB-35'), src('XB:XB-42'), src('SUM:EN', 5), src('SUM:FORUM')], H,
    '细节题读一句，推断题读一段。', qt=['QT.P7.DETAIL', 'QT.P7.INFERENCE', 'QT.P7.NOT_TRUE', 'QT.P7.MAIN_PURPOSE'],
    st=['ST.LOCATE.DEPTH_BY_QTYPE'], sk=['FD.READ.SCAN', 'FD.READ.SKIM'])
add('SL-P7-12', '意图题看前后消息', '短信/群聊里引号句的意图：看前后几条消息确定语境，判断这句话在当时的作用（同意/拒绝/确认/惊讶）。',
    [7], [MID, HIGH], C, [src('BK:P7-06'), src('ETS:HANDBOOK')], H, '引号里那句话，先看上一条在问什么。',
    qt=['QT.P7.INTENT', 'QT.P7X.INTENT.TEXT_MSG', 'QT.P7X.INTENT.CHAT'], tx=['TX.TEXT_MSG', 'TX.CHAT'],
    counter='不要按字面义选（如 "I\'ll say" 是强烈同意）；群聊要先分清每条是谁说的。',
    note='ETS 考生手册官方样题 Q153 为意图题。')
add('SL-P7-13', '句子位置题先读待插句', '先读要插入的句子，抓其中的指代词、连接词、冠词等线索，预测它前面应出现什么内容，再到 [1]–[4] 验证。',
    [7], [MID, HIGH], C, [src('BK:P7-07'), src('SUM:EN', 5)], H, '先读那句“外来句”，猜它前面该说过什么，再去 [1]–[4] 对号。',
    qt=['QT.P7.INSERTION', 'QT.P7X.INSERTION.ARTICLE', 'QT.P7X.INSERTION.EMAIL', 'QT.P7X.INSERTION.LETTER'],
    st=['ST.ORDER.HARD_ITEMS_LAST'], sk=['FD.READ.REFERENCE', 'FD.READ.DISCOURSE'],
    counter='新题插入位置不再固定靠后（XB-38）；线索不足时放到本组最后。')
add('SL-P7-14', '同义词题选语境义', '“closest in meaning” 题按原文语境选义，不要选该词最常见的意思（多义词陷阱，如 top=favorite）。',
    [7], [MID], U, [src('BK:P7-08'), src('SUM:EN', 5), src('ETS:HANDBOOK')], H, '把选项代回原句读一遍，通的才对。',
    qt=['QT.P7.SYNONYM', 'QT.P7X.SYNONYM.ARTICLE', 'QT.P7X.SYNONYM.EMAIL', 'QT.P7X.SYNONYM.MULTI'],
    sk=['VO.CONF.POLYSEMY_CONTEXT', 'VO.CONF.BUSINESS_SENSE'])
add('SL-P7-15', '认文本类型、按结构预测考点', '先认文本类型：邮件/信=称呼-目的-要求-落款；广告=产品特点-优惠-购买方式；公告/备忘=目的-要求；文章/新闻=5W1H、首段细读；表格/日程按栏位找；聊天看情境。',
    [6, 7], [LOW, MID], U, [src('BK:P7-11'), src('XB:XB-29'), src('XB:XB-41')], H, '先认是什么文件，再去它通常放答案的位置找。',
    qt=['QT.P7.MAIN_PURPOSE', 'QT.P7.DETAIL'],
    tx=['TX.EMAIL', 'TX.LETTER', 'TX.MEMO', 'TX.NOTICE', 'TX.AD', 'TX.JOB_POSTING', 'TX.ARTICLE', 'TX.FORM', 'TX.SCHEDULE', 'TX.TEXT_MSG', 'TX.CHAT', 'TX.WEB', 'TX.REVIEW', 'TX.INSTRUCTIONS'],
    suggest='ST.LOCATE.TEXT_STRUCTURE（按文本结构预测考点）')
add('SL-P7-16', '文体常考细节', '邮件/信：附件(enclosed/attached)、收发件人职位（常被改写）、FYI/BTW 等缩写常考；广告/表格：最后一句常给申请/购买办法或最强优惠。',
    [7], [LOW, MID], U, [src('XB:XB-40'), src('XB:XB-39')], I, '邮件看附件和职位，广告看最后一句。',
    qt=['QT.P7.DETAIL', 'QT.P7.INFER_WHO', 'QT.P7.REQUEST_ACTION', 'QT.P7X.REQUEST_ACTION.EMAIL', 'QT.P7X.REQUEST_ACTION.MEMO'],
    tx=['TX.EMAIL', 'TX.LETTER', 'TX.AD', 'TX.FORM'], sk=['VO.TITLES_DEPTS'],
    note='XB-39 中“招聘广告里‘打电话应聘’可排除”为讲师经验法则、无官方依据，未收入（见排除表）。')
add('SL-P7-17', '多篇预判跨篇连锁', '双篇/三篇先预判跨篇题：一篇给条件（折扣规则、日程、价目），另一篇给具体数据，答题时两篇对照；三篇常需 1↔3 篇对比、常带图表；每组约 1–2 道跨篇题。',
    [7], [MID, HIGH], C, [src('BK:P7-12'), src('XB:XB-38'), src('SUM:JK')], H, '多篇题先问：条件在哪篇，数据在哪篇？',
    qt=['QT.P7.CROSS_REF', 'QT.P7X.CROSS_REF.DOUBLE', 'QT.P7X.CROSS_REF.TRIPLE', 'QT.P7.CALC_LOOKUP', 'QT.P7X.CALC_LOOKUP.INVOICE', 'QT.P7X.CALC_LOOKUP.SCHEDULE'],
    tx=['TX.MULTI', 'TX.DOUBLE', 'TX.TRIPLE', 'TX.INVOICE', 'TX.SCHEDULE'],
    suggest='ST.LOCATE.MULTI_DOC_ROUTING（多篇按题定篇/跨篇对照）')
add('SL-P7-18', '多篇按题定篇', '多篇先看 5 道题分别指向哪篇（题干里的 e-mail/notice/article 等），精读被问最多的那篇，其余寻读；跨篇题不按先后顺序出。',
    [7], [MID], C, [src('XB:XB-36')], M, '先给 5 道题分配文件，再决定精读哪篇。',
    qt=['QT.P7X.DETAIL.DOUBLE', 'QT.P7X.DETAIL.TRIPLE', 'QT.P7X.MAIN_PURPOSE.MULTI', 'QT.P7.CROSS_REF'],
    tx=['TX.MULTI', 'TX.DOUBLE', 'TX.TRIPLE'], st=['ST.LOCATE.QUESTION_FIRST'],
    suggest='ST.LOCATE.MULTI_DOC_ROUTING（多篇按题定篇/跨篇对照）',
    note='XB-36 有新东方课程、杨老师、邹老师 3 位作者，判“中”。与已弃用 XB-37（旧制“双篇多数题只读一篇”）区别：新制跨篇题更多。')
add('SL-P7-19', '意群顺读', '用意群斜线读法训练顺序直读（不回读、不逐词翻译），可跟着题目音频按目标速度读。',
    [6, 7], [LOW, MID], U, [src('BK:P7-15')], M, '按意群一块一块往前读，不回头。',
    sk=['FD.READ.CHUNK', 'FD.READ.SPEED_150'], st=['ST.REVIEW.AUDIO_SHADOW'], mock=False, mode_note='训练方法，模考中不刻意执行。')
add('SL-P7-20', '生词不停', '遇到生词不停下，先靠上下文把握大意，读完再查。',
    [6, 7], [LOW], U, [src('BK:P7-16')], I, '生词先跳过，读完再回来查。', sk=['FD.READ.UNKNOWN_WORD'],
    counter='生词恰好是题目问的词（同义词题）或题干关键词时，要停下用上下文猜义。')
add('SL-P7-21', '测时后重复同篇提速', '先测自己读一篇的用时，再以目标用时反复练同一篇（测时→抓要点→斜线读→答题→提速）。',
    [7], [LOW, MID], U, [src('BK:P7-17')], I, '同一篇读三遍，每遍限时更短。', st=['ST.REVIEW.SPEED_REPEAT'],
    sk=['FD.READ.SPEED_150', 'FD.READ.SPEED_200'], mock=False)
add('SL-P7-22', '信号句预测下文', '700+ 提速：精读 although/while/unless 后的转折、关系从句里 who 后的谓语、whoever/whatever 结构；announce/ensure/note that 后的内容常是考点。',
    [7], [HIGH], U, [src('XB:XB-45')], I, '看到 although、note that，后面那句重点读。',
    qt=['QT.P7.TRUE_INDICATED', 'QT.P7.DETAIL'], sk=['FD.READ.DISCOURSE', 'FD.SENT.LONG', 'GR.REL.COMPOUND_REL'])
add('SL-P7-23', '先看中文概要再读英文', '基础阶段先读中文概要再读英文原文，建立“英文能顺读”的感觉。',
    [7], [LOW], U, [src('BK:P7-18')], I, '新手先看中文提要，再读英文。', sk=['FD.READ.SKIM'], mock=False,
    mode_note='只在练习模式、<600 档提供“中文提要”开关。', suggest='ST.REVIEW.L1_PRIMING（母语预读）',
    counter='600 以上应关闭，否则依赖中文。')
add('SL-P7-24', '记题干选项常见词与职位名', '专门记题干和选项里的高频词，以及部门、职位名称，读题更快。',
    [7], [LOW, MID], U, [src('BK:V-03')], I, '先认熟题目里反复出现的词和职位名。',
    qt=['QT.P7.INFER_WHO'], sk=['VO.TITLES_DEPTS'], mock=False)

# ======================= 全卷：时间 / 顺序 / 放弃 / 涂卡 / 复盘 / 词汇 / 规则 =======================
add('SL-ALL-01', '整卷配速', 'P5 约 10–12 分钟、P6 约 8–10 分钟（合计 ≤20），P7 留 ≥53–55 分钟；开考约 20 分钟时应翻到第 147 题。',
    [5, 6, 7], [LOW, MID], C, [src('BK:P5-15'), src('XB:XB-01'), src('SUM:FORUM'), src('SUM:EN', 12), src('SUM:JK')], H,
    'P5、P6 合计 20 分钟内交差，剩下的全给 P7。', st=['ST.TIME.TOTAL_PLAN'],
    mode_note='模考模式默认；练习模式按 5/20 分钟会话缩放。',
    note='冲突：XB-02/日韩 900 档主张压到 15–18 分钟（见 SL-ALL-02）；黄琳达为 15–20+P7 50+检查 5。按分段取舍。')
add('SL-ALL-02', '高分档加速配速', '目标 800+ 或 P7 常做不完：P5+P6 压到 15–18 分钟（900 目标各 ≤8 分钟），三篇每组留 6–7 分钟。',
    [5, 6, 7], [HIGH], C, [src('XB:XB-02'), src('SUM:JK')], M, '冲高分：P5、P6 合计 16 分钟左右。', st=['ST.TIME.TOTAL_PLAN'],
    counter='P5 正确率 <80% 时压时间会丢 P5 分，先提 P5 准确率。', note='理由：近年三篇篇幅变长（邹老师个人观察）。')
add('SL-ALL-03', 'P7 分段配时', '单篇 147–175（29 题）≤25–30 分钟，多篇 176–200（25 题）≥25 分钟，三篇每组约 6–7 分钟；单篇尽快做完把时间留给多篇。',
    [7], [MID], C, [src('XB:XB-03'), src('XB:XB-43'), src('SUM:JK')], M, '单篇别恋战，留够 25 分钟给多篇。',
    tx=['TX.DOUBLE', 'TX.TRIPLE'], st=['ST.TIME.PER_SET_P7', 'ST.ORDER.WITHIN_P7'],
    note='韩国 hackers 为单篇 28/双篇 11/三篇 17 分钟，与本条一致；XB-11（单篇 20/双 10/三 20）题数口径与新制不符，已弃用。')
add('SL-ALL-04', '分阶段看表', '不每篇都看表：每做 3–4 篇（或到 P6 开头、147、176 题）对一次检查点，落后就启用放弃线。',
    [5, 6, 7], [MID], C, [src('XB:XB-04'), src('XB:XB-01'), src('SUM:JK')], M, '只在几个检查站看表，落后就提速或猜。',
    st=['ST.TIME.CHECKPOINTS'])
add('SL-ALL-05', '不留空', '答错不扣分，任何题都不要空着；最后来不及就统一猜同一个字母。',
    [5, 6, 7], [LOW], U, [src('ETS:HANDBOOK'), src('SUM:EN', 8), src('SUM:FORUM'), src('SUM:JK')], H, '每张工单都要交，空着等于白扔分。',
    st=['ST.GIVEUP.NO_BLANK'])
add('SL-ALL-06', '卡住就猜，先跳后回', '设放弃线：一题超时（P5 约 30 秒、P7 约 1 分钟）先选一个最像的，标记后继续，有余时间再回看；不要因一题耽误后面的简单题。',
    [5, 6, 7], [LOW, MID], U, [src('ETS:HANDBOOK'), src('SUM:EN', 7), src('SUM:FORUM'), src('XB:XB-44'), src('SUM:JK')], H,
    '卡住就先猜一个，挂“稍后处理”，往下走。', st=['ST.GIVEUP.CUTOFF_RULE'],
    mode_note='机考/应用里可用“稍后处理”标签；纸笔模考不能在题本标记，只能记题号。')
add('SL-ALL-07', '时间不够做三蒙二', '剩余时间不够做完时，每组 5 题只挑词义题和直接定位的细节题做 2–3 道，其余快速排除后猜，先保证全部涂满。',
    [7], [MID], C, [src('XB:XB-05')], I, '时间不够：每组只做最容易的两三题，其余先猜。',
    st=['ST.GIVEUP.TARGET_BASED', 'ST.TIME.PER_SET_P7'], tx=['TX.DOUBLE', 'TX.TRIPLE'], practice=False,
    mode_note='只在模考/限时会话触发（剩余时间 < 所需时间）。', note='3 个视频同一作者（邹老师），故判“个人经验”。')
add('SL-ALL-08', '按目标分决定放弃哪些题', '只求过线/600–700 目标：难题集中区（P5 后段、P6 插入句、P7 单篇后段长文）不会就猜，可战略性放弃部分多篇；多篇每组都有易得分题要先抓。',
    [5, 6, 7], [LOW, MID], C, [src('XB:XB-07'), src('XB:XB-06'), src('ETS:RM-17-05')], M,
    '先拿自己够得着的分，够不着的题批量猜。', st=['ST.GIVEUP.TARGET_BASED'],
    counter='800+ 目标不适用；题号区间（121–130、165–175）是个人经验，ETS 未公布难度顺序。',
    note='ETS RM-17-05：多篇 p 值 0.42–0.51，低于 P5 的 0.65–0.68，支持“低分段优先保 P5”。')
add('SL-ALL-09', 'Part 间按顺序做', '默认按 P5→P6→P7 顺序做，不跳着先做双篇；要预期 P7 篇型顺序被打乱。',
    [5, 6, 7], [LOW, MID], C, [src('XB:XB-08'), src('SUM:FORUM'), src('SUM:EN')], M, '按顺序开工，别东一块西一块。',
    st=['ST.ORDER.PART_SEQUENCE'],
    counter='规则上允许先做 P7（toeic.ai 说“不能先做 P7”是错的）；P5 准确率高、P7 常做不完的人可试倒序，但涂卡错位风险更高。')
add('SL-ALL-10', 'P7 内先易后难，多篇不整块留后', 'P7 内先拿把握大的题/篇；多篇里先做单文档题，跨篇题后做；但不要把多篇整块留到最后。',
    [7], [MID], U, [src('BK:P7-13'), src('SUM:EN', 5)], H, '先做单篇就能答的，跨篇题放在组内最后。',
    tx=['TX.MULTI'], st=['ST.ORDER.WITHIN_P7'],
    counter='与 SL-ALL-09“按序做”的取舍：组内调序可以，跨组跳着做不建议。')
add('SL-ALL-11', '分段涂卡、最后 5 分钟涂完', '纸笔考每 30 题或每个 Part 集中涂一次；倒计时 5 分钟停下，把已做题全部涂完，剩余题统一猜涂。',
    [5, 6, 7], [LOW, MID], U, [src('XB:XB-09'), src('SUM:FORUM'), src('SUM:JK')], H, '每做完一段就涂卡；还剩 5 分钟立刻全部涂满。',
    st=['ST.BUBBLE.BATCH', 'ST.BUBBLE.FINAL_MINUTES'], practice=False,
    mode_note='仅纸笔模考模式（中国大陆纸笔考）；日韩 toeicstory 建议整卷涂卡 ≤3 分钟。')
add('SL-ALL-12', '按题型统计正确率找弱项', '按题型统计正确率诊断薄弱点，再针对弱项练（可对照官方 Abilities Measured 5 项）。',
    [5, 6, 7], [LOW, MID], U, [src('BK:G-01'), src('SUM:EN', 5)], H, '先看绩效报表：哪类工单错得多就练哪类。',
    st=['ST.REVIEW.DIAGNOSE_BY_TYPE'], mock=False, mode_note='引擎自动完成，展示在“薄弱点榜”。')
add('SL-ALL-13', '错题按原因分类', '每套记录各 Part 错几题、每种原因错几题（词汇/语法/定位/时间/改写没认出），按原因而不是按题复习。',
    [5, 6, 7], [LOW, MID, HIGH], U, [src('XB:XB-49'), src('XB:XB-20'), src('SUM:JK'), src('SUM:FORUM')], H,
    '每道错题贴一个错因标签。', st=['ST.REVIEW.ERROR_CAUSE_LOG'], mock=False)
add('SL-ALL-14', '讲清每个错误选项为何错', '复盘时逐个说明每个错误选项为什么错，能给别人讲清“为什么选这个、不选另外三个”才算懂。',
    [5, 6, 7], [MID, HIGH], U, [src('BK:G-02'), src('XB:XB-20')], H, '复盘时把四个选项都“结案”。',
    st=['ST.REVIEW.EXPLAIN_DISTRACTORS'], mock=False, mode_note='练习模式复盘页可选“说给 AI 听”检验。')
add('SL-ALL-15', '认熟错误选项套路', '掌握错误选项套路（原文没提、部分正确、张冠李戴、过度推断、照搬原词、因果颠倒）并在复盘时归类。',
    [5, 6, 7], [MID], U, [src('BK:P7-10'), src('SUM:JK')], M, '错误选项就那几种套路，认出来就划掉。',
    qt=['QT.P7.TRUE_INDICATED', 'QT.P7.INFERENCE', 'QT.P7.DETAIL'], st=['ST.ELIM.TRAP_TYPES', 'ST.ELIM.OPTIONS'],
    sk=['VO.PARA.CAUSE_EFFECT', 'VO.PARA.NEGATION_SHIFT'])
add('SL-ALL-16', '限时整卷模考', '用官方/仿真题严格 75 分钟整卷模考（含涂卡），不在题本写答案以便重做；留 1–2 套新题考前做；每次模考后用一天复盘。',
    [5, 6, 7], [LOW, MID, HIGH], C, [src('BK:G-03'), src('XB:XB-48'), src('SUM:FORUM'), src('SUM:EN', 5), src('SUM:JK')], H,
    '定期来一次 75 分钟“季度考核”，第二天专门复盘。', st=['ST.REVIEW.TIMED_MOCK'], practice=False)
add('SL-ALL-17', '用题目音频复习阅读', 'Part 5/6 听音频写出空格，Part 7 跟着音频读原文。',
    [5, 6, 7], [MID], U, [src('BK:G-04')], H, '做完的题再听一遍、跟读一遍。', st=['ST.REVIEW.AUDIO_SHADOW'],
    sk=['FD.READ.CHUNK'], mock=False, note='7 本书提及，但只来自书籍一路。')
add('SL-ALL-18', '生词从题里摘', '生词本从做过的题里摘，只记托业考到的词义；每篇挑 2–3 个词记；先用词表 App 过一遍，再转自建生词本。',
    [5, 6, 7], [LOW, MID], U, [src('XB:XB-47'), src('SUM:FORUM')], H, '每篇做完挑两三个词放进词卡。',
    st=['ST.REVIEW.VOCAB_FROM_ITEMS'], sk=['FD.VOC.NGSL_CORE'], mock=False,
    note='论坛分歧：要不要专门背单词。取舍：NGSL/TSL 词包打底 + 从题里摘，两者并用。')
add('SL-ALL-19', '按分数段分层背词', '先背目标分以下各段的词，提分后再扩展。',
    [5, 6, 7], [LOW, MID, HIGH], U, [src('BK:V-01')], M, '先背自己这一档的词。',
    sk=['VO.BAND', 'VO.BAND.B600', 'VO.BAND.B730', 'VO.BAND.B860', 'VO.BAND.B990'], mock=False)
add('SL-ALL-20', '按搭配记词', '以短语/搭配为单位记词（每条不超过 7 个词），兼顾 P5 搭配题和 P7 阅读。',
    [5, 6, 7], [LOW, MID], U, [src('BK:V-02')], H, '背词背整个短语，不背单个词。',
    qt=['QT.P5.VOCAB'], sk=['VO.COLLO', 'VO.COLLO.FIXED_PHRASE', 'VO.COLLO.VERB_NOUN', 'VO.COLLO.PHRASAL_VERB'], mock=False)
add('SL-ALL-21', '生词多先补词再模考', '每篇生词 ≥5 个说明词汇未过关，应先补词汇再做模考。',
    [6, 7], [LOW], U, [src('XB:XB-46')], I, '一篇里生词超过 5 个，先回词汇区。',
    sk=['FD.VOC.NGSL_CORE', 'VO.BAND.B600'], mock=False, suggest='ST.REVIEW.VOCAB_GATE（生词密度阈值）')
add('SL-ALL-22', '按目标选材料难度', '官方题集 P5/P6 难度接近真题，但 P7 偏易；冲 800+ 需要更难的 P7 材料。',
    [5, 6, 7], [HIGH], C, [src('XB:XB-22')], I, '冲高分时 P7 要练更难的文章。', mock=False,
    suggest='ST.REVIEW.MATERIAL_LEVEL（材料难度匹配）', note='“偏易 30–50%”是个人主观估计（2026-04 日本场）。')
add('SL-ALL-23', '分数波动 35 分以内看作噪音', '官方 SEM 约 ±25，两次成绩相差 35 分以内可能只是测量误差，不据此大改计划。',
    [5, 6, 7], [LOW, MID, HIGH], U, [src('ETS:HANDBOOK')], M, '模考分涨跌 35 分以内，别激动也别泄气。',
    st=['ST.REVIEW.TIMED_MOCK'], practice=False, mode_note='用于“绩效评估”页显示预测区间。',
    suggest='ST.REVIEW.SCORE_NOISE（分数误差解读）')
add('SL-ALL-24', '高分段正向确认，排除作后备', '800+ 不靠消去法：先在原文找到支持正确选项的依据再选，排除法只用于犹豫的两选一。',
    [7], [HIGH], U, [src('SUM:JK')], I, '高手先找证据再选，不是靠划掉别的。', st=['ST.ELIM.OPTIONS'],
    counter='NOT/TRUE 题本质就是逐项核对（SL-P7-07），不适用本条。', note='来源 IIBC methods07（日本官方机构文章）。与 SL-P7-07 的冲突按题型取舍。')
add('SL-ALL-25', '考场规则：题本不写画、只在阅读时间做阅读', '题本禁止划线/笔记，无草稿纸；听力时间不得翻做阅读（可取消成绩）；平时练习就不在题本写字。',
    [5, 6, 7], [LOW, MID, HIGH], U, [src('ETS:HANDBOOK'), src('XB:XB-10'), src('XB:XB-48')], H,
    '模考里不能在卷子上写字，练习里养成习惯。', practice=True, mock=True,
    mode_note='模考模式强制：关闭高亮/划线/笔记工具；练习模式允许“划依据”。', suggest='ST.RULES.EXAM_CONDUCT（考场规则）',
    note='XB-10 中“在答题卡题号旁轻点、结束前擦掉”属规则边缘行为，未收入（见排除表）。')

# ======================= 弃用（旧制）与排除 =======================
DEPRECATED = [
    dict(id='DEP-01', from_source='XB:XB-27', rule_zh='（旧制）P6 无需通读全文，看空格所在句即可，做法与 P5 一致',
         format_version='deprecated', reason='旧制 P6 每篇 3 空、无句子插入；新制每篇 4 题含插入句，须读上下文', replaced_by='SL-P6-01'),
    dict(id='DEP-02', from_source='XB:XB-37', rule_zh='（旧制）双篇大部分题只需读一篇，约 10% 的题需要两篇都读',
         format_version='deprecated', reason='旧制双篇 20 题、无三篇；新制含三篇且跨篇题更多，比例不成立', replaced_by='SL-P7-17'),
    dict(id='DEP-03', from_source='XB:XB-11', rule_zh='P7 按篇型配时：单篇约 20 分钟、双篇约 10 分钟、三篇约 20 分钟（同视频称“前 40 题语法+填空 15 分钟”）',
         format_version='deprecated', reason='题数口径（40 题）是旧制 P5，与新制 46 题不符，配时整体偏紧；来源可信度低', replaced_by='SL-ALL-03'),
]
EXCLUDED = [
    dict(id='EXC-01', rule_zh='利用听力时间偷做 Part 5/阅读题', source='SUM:EN / ETS:HANDBOOK（论坛偶见）', reason='ETS 规定未授权时段作答可取消成绩'),
    dict(id='EXC-02', rule_zh='在试题册/题本上划线、圈关键词、写答案', source='XB:XB-28 原步骤“划出人名、日期…”；论坛常见', reason='ETS 禁止在题本做任何标记；已把 XB-28 改写为“记住关键词”，练习模式内的高亮不受影响'),
    dict(id='EXC-03', rule_zh='在答题卡题号旁轻点标记、结束前擦净', source='XB:XB-10', reason='规则边缘行为，邹老师本人也提示有被提醒风险；最稳妥是不标记'),
    dict(id='EXC-04', rule_zh='招聘广告选项中“打电话应聘”通常可排除', source='XB:XB-39（后半句）', reason='讲师经验法则，无官方依据，可靠性低，作为规则会误导'),
]

# ======================= 计算 sources / 权重 / 校验 =======================
CONS_SCORE = {H: 1.0, M: 0.6, I: 0.3}
def freq_of(e):
    ws = [NODES[i]['exam_weight'] for i in e['qtype_nodes'] + e['strategy_nodes'] if i in NODES and not NODES[i].get('is_group')]
    basis = 'qtype/strategy 节点'
    if not ws:
        ws = [NODES[i]['exam_weight'] for i in e['skill_nodes'] + e['texttype_nodes'] if i in NODES and not NODES[i].get('is_group')]
        basis = 'skill/texttype 节点'
    if not ws:
        return 0.2, '无可用节点，按 0.2 计'
    m = max(ws)
    return m, f'{basis}最大 exam_weight={m}'

errors = []
lib = []
for e in E:
    srcs = e.pop('_sources')
    e['sources'] = [s for s, _ in srcs]
    e['mention_breakdown'] = {s: n for s, n in srcs}
    e['mention_count'] = sum(n for _, n in srcs)
    channels = sorted({('books' if s.startswith('BK:') else 'xdf_bili' if s.startswith('XB:') else SUMMARY_SOURCES[s]['channel']) for s in e['sources']})
    e['channels'] = channels
    f, fb = freq_of(e)
    fn = min(1.0, f / 0.6)
    mf = min(1.0, e['mention_count'] / 15)
    w = round(0.5 * fn + 0.3 * CONS_SCORE[e['consensus']] + 0.2 * mf, 2)
    e['weight'] = w
    e['weight_basis'] = f'0.5×考频({fb}，÷0.6 封顶 1 → {fn:.2f}) + 0.3×共识({e["consensus"]}={CONS_SCORE[e["consensus"]]}) + 0.2×提及(min(1, {e["mention_count"]}/15)={mf:.2f})'
    for k in ('qtype_nodes', 'texttype_nodes', 'strategy_nodes', 'skill_nodes'):
        for nid in e[k]:
            if nid not in NODES:
                errors.append(f'{e["id"]}: 节点不存在 {nid}')
    for nid in e['qtype_nodes']:
        if nid in NODES and NODES[nid]['layer'] != 'qtype': errors.append(f'{e["id"]}: {nid} 不是 qtype')
    for nid in e['texttype_nodes']:
        if nid in NODES and NODES[nid]['layer'] != 'texttype': errors.append(f'{e["id"]}: {nid} 不是 texttype')
    for nid in e['strategy_nodes']:
        if nid in NODES and NODES[nid]['layer'] != 'strategy': errors.append(f'{e["id"]}: {nid} 不是 strategy')
    if e['format_version'] not in ('current', 'universal'): errors.append(f'{e["id"]}: format_version 非法')
    for s in e['sources']:
        if s.startswith('BK:') and s[3:] not in BK: errors.append(f'{e["id"]}: 无此书籍条目 {s}')
        if s.startswith('XB:') and (s[3:] not in XB or XB[s[3:]]['deprecated'] is True): errors.append(f'{e["id"]}: XB 来源不存在或已弃用 {s}')
    order = ['id', 'title_zh', 'rule_zh', 'work_rule', 'parts', 'qtype_nodes', 'texttype_nodes', 'strategy_nodes', 'skill_nodes',
             'target_band', 'weight', 'weight_basis', 'format_version', 'sources', 'mention_count', 'mention_breakdown', 'channels',
             'consensus', 'practice_mode', 'mock_mode', 'mode_note', 'counter_examples', 'suggested_new_node', 'note']
    lib.append({k: e[k] for k in order})

ids = [e['id'] for e in lib]
dup = [i for i, c in collections.Counter(ids).items() if c > 1]
if dup: errors.append(f'重复 id: {dup}')
dep_src = {d['from_source'] for d in DEPRECATED}
for e in lib:
    if set(e['sources']) & dep_src: errors.append(f'{e["id"]}: 引用了弃用来源')
# 覆盖：每条书籍/XB 原始条目都被用到、弃用或排除
used = {s for e in lib for s in e['sources']} | dep_src
unused_bk = [k for k in BK if 'BK:' + k not in used]
unused_xb = [k for k in XB if 'XB:' + k not in used]
if unused_bk or unused_xb: errors.append(f'未使用来源 BK={unused_bk} XB={unused_xb}')

st_nodes = [n['id'] for n in graph['nodes'] if n['layer'] == 'strategy' and not n.get('is_group')]
st_used = collections.Counter(n for e in lib for n in e['strategy_nodes'])
st_uncovered = [n for n in st_nodes if n not in st_used]
qt_leaf = [n['id'] for n in graph['nodes'] if n['layer'] == 'qtype' and not n.get('is_group')]
qt_used = {n for e in lib for n in e['qtype_nodes']}
qt_uncovered = [n for n in qt_leaf if n not in qt_used]
tx_leaf = [n['id'] for n in graph['nodes'] if n['layer'] == 'texttype' and n['id'] != 'TX']
tx_used = {n for e in lib for n in e['texttype_nodes']}
tx_uncovered = [n for n in tx_leaf if n not in tx_used]
suggested = collections.defaultdict(list)
for e in lib:
    if e['suggested_new_node']: suggested[e['suggested_new_node']].append(e['id'])

validation = dict(passed=not errors, errors=errors, n_entries=len(lib), n_deprecated=len(DEPRECATED), n_excluded=len(EXCLUDED),
                  all_node_ids_exist=not any('节点不存在' in x for x in errors), unique_ids=not dup,
                  deprecated_not_in_main=not any('弃用' in x for x in errors),
                  strategy_nodes_without_technique=st_uncovered, qtype_leaves_without_technique=qt_uncovered,
                  texttype_without_technique=tx_uncovered)

out = dict(
    meta=dict(version='1.0', built='2026-10-21', exam_format='TOEIC L&R 阅读现行线性新制（P5 30 / P6 16 / P7 54，75 分钟 100 题）',
              inputs=['data/strategies/books.json', 'data/strategies/xdf_bilibili.json', 'data/strategies/xdf_bilibili_sources.md',
                      'work/reports/strategy_findings_summary.md', 'data/strategies/exam_pattern_stats.json（经 graph_v1 exam_weight 间接使用）', 'data/graph_v1.json'],
              builder='work/strategies/build_strategy_library.py',
              field_notes=dict(
                  format_version='current=只适用现行新制（依赖 P6 插入句、三篇、群聊、新制题号等）；universal=新旧制通用。旧制条目标 deprecated，单列在 deprecated[]，不进 entries[]',
                  target_band='<600 / 600-800 / 800+，表示从哪个目标分段开始值得用（可多选）',
                  weight='0–1，价值权重 = 0.5×考频 + 0.3×共识 + 0.2×提及数；考频取所绑定 qtype/strategy 叶子节点 exam_weight 最大值 ÷0.6 封顶 1（无则用 skill/texttype 节点）；每条 weight_basis 写明算式',
                  mention_count='跨来源合计：BK/XB 用原文件 mention_count（多少本书/视频提到）；SUM:* 汇总渠道用报告给的来源数，未给按 1 计（下限）；ETS 文件各计 1。是下限，且同一作者多个视频会重复计数',
                  consensus='高=≥3 个独立渠道或 ≥3 位独立作者/书；中=2 个渠道或 2–3 位作者；个人经验=单一作者（即使有多个视频）。人工判定',
                  work_rule='游戏里的“工作规则”，大白话一句',
                  practice_mode_mock_mode='该规则在练习/模考模式是否可用或触发；mode_note 说明差异（如“划依据”仅练习模式，模考禁止题本标记）',
                  qtype_texttype_strategy_skill_nodes='均为 graph_v1 节点 ID（已校验存在）；skill_nodes 为 grammar/vocab/foundation 层的辅助绑定')),
    source_registry=dict(summary_channels=SUMMARY_SOURCES,
                         books='BK:<technique id> → data/strategies/books.json techniques[]',
                         xdf_bili='XB:<id> → data/strategies/xdf_bilibili.json（原始视频/专栏见 xdf_bilibili_sources.md）'),
    entries=lib, deprecated=DEPRECATED, excluded=EXCLUDED, validation=validation)
json.dump(out, open(P('data/strategies/strategy_library_v1.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(validation, ensure_ascii=False, indent=1))
print('suggested', dict(suggested))
print('st_used', dict(st_used))
