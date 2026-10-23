#!/usr/bin/env python3
"""把 data/open_items/maximcuynat_toeic-practice/data/reading-test-1..6.json（MIT，© 2026 Maxim Cuynat）
转成与 data/items_pilot_v1.json 兼容的 schema → data/items_open_maximcuynat.json。

- id: MXC-Txx-<qnum>；form: MXT01..MXT06；source: maximcuynat_mit
- 保留英文解析为 explain_en；explain_zh 留空；原始 tags 存 src_tags
- P5 空位 ______ → -------（pilot 约定）；P6 空位 {{qnum}} → [n] + blank_n（n = 本篇第 n 个空）
- P7 插入位置 [1]–[4] 原样保留
- bundles: kind single/double/triple、text_type（单篇=文本类型，多篇=TX.DOUBLE/TX.TRIPLE）、docs[{doc_type,title,header?,text}]
- node/node_ids：按题型 tags + 题干规则打 graph_v1 节点，只用存在的节点 ID（脚本末尾校验，未知节点直接报错）
用法：python3 work/convert_maximcuynat.py
"""
import json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, 'data', 'open_items', 'maximcuynat_toeic-practice', 'data')
OUT = os.path.join(ROOT, 'data', 'items_open_maximcuynat.json')
G = {n['id']: n for n in json.load(open(os.path.join(ROOT, 'data', 'graph_v1.json'), encoding='utf-8'))['nodes']}

DOC_TYPE = {
    'e-mail': 'TX.EMAIL', 'letter': 'TX.LETTER', 'letter to the editor': 'TX.LETTER', 'memo': 'TX.MEMO',
    'notice': 'TX.NOTICE', 'information': 'TX.NOTICE', 'policy': 'TX.NOTICE', 'advertisement': 'TX.AD',
    'job posting': 'TX.JOB_POSTING', 'article': 'TX.ARTICLE', 'press release': 'TX.ARTICLE',
    'invoice': 'TX.INVOICE', 'receipt': 'TX.INVOICE', 'schedule': 'TX.SCHEDULE', 'agenda': 'TX.SCHEDULE',
    'itinerary': 'TX.SCHEDULE', 'form': 'TX.APP_FORM', 'survey results': 'TX.APP_FORM',
    'text-message chain': 'TX.TEXT_MSG', 'online chat discussion': 'TX.CHAT', 'web page': 'TX.WEB',
    'customer review': 'TX.REVIEW', 'response': 'TX.REVIEW',
}
# P7X 交叉节点的文本后缀：先试具体类型，再试上位类
TX_SUFFIX = {'TX.INVOICE': ['INVOICE', 'FORM'], 'TX.SCHEDULE': ['SCHEDULE', 'FORM'], 'TX.APP_FORM': ['FORM'],
             'TX.DOUBLE': ['DOUBLE', 'MULTI'], 'TX.TRIPLE': ['TRIPLE', 'MULTI']}

# ---------- 场景词包（关键词粗打，命中 ≥2 个不同关键词才打） ----------
SCENES = {   # A2-QC：去掉歧义大的词（customer/purchase/room/policy/power/order 的 in order to/board/position/resume/IT 大小写等）
    'VO.SCENE.OFFICE_ADMIN': r'\b(paperwork|filing|stationery|photocop\w*|printers?|copiers?|office supplies|supply (room|closet|cabinet)|front desk|reception desk|mail ?room|filing cabinets?)\b',
    'VO.SCENE.MEETING_SCHEDULE': r'\b(meetings?|agendas?|reschedul\w*|appointments?|postpone\w*|conference call|meeting minutes|calendar)\b',
    'VO.SCENE.RECRUIT': r'\b(applicants?|candidates?|hiring|résumés?|interview\w*|vacanc\w*|job (posting|opening|offer)s?|recruit\w*|qualifications?|job applications?)\b',
    'VO.SCENE.HR_TRAINING': r'\b(training|workshops?|promoted|promotion to|performance reviews?|orientation|mentor\w*|appraisals?|benefits package|human resources|new hires?|onboarding)\b',
    'VO.SCENE.PURCHASE_QUOTE': r'\b(quotes?|quotation|purchase orders?|suppliers?|vendors?|procure\w*|bulk orders?)\b',
    'VO.SCENE.ORDER_SHIP': r'\b(orders?|ordered|shipments?|shipp\w*|deliver\w*|couriers?|parcels?|tracking number|dispatch\w*)\b',
    'VO.SCENE.INVENTORY_PRODUCTION': r'\b(inventory|in stock|out of stock|stock levels?|warehouses?|factor(y|ies)|manufacturing plant|production line|assembly|manufactur\w*)\b',
    'VO.SCENE.MARKETING_AD': r'\b(marketing|advertis\w*|campaigns?|promotional|brand(ing)?|market research|focus groups?|launch(es|ed)?)\b',
    'VO.SCENE.SALES_DEAL': r'\b(contracts?|negotiat\w*|sales (team|figures|representative|department)|clients?|business deals?|proposals?|agreements?)\b',
    'VO.SCENE.CUSTOMER_SERVICE': r'\b(complain\w*|refunds?|warrant(y|ies)|customer service|customer care|customer support|apolog\w*|return policy|replacement)\b',
    'VO.SCENE.FINANCE_ACCOUNT': r'\b(budgets?|expense\w*|accounting|accountants?|audit\w*|revenue|profits?|financ\w*|reimburs\w*|tax(es)?)\b',
    'VO.SCENE.BANK_PAYMENT': r'\b(invoices?|payments?|bank\w*|account number|credit card|balance due|deposits?|billing|bills?|fees?|paid)\b',
    'VO.SCENE.CORP_STRATEGY': r'\b(mergers?|acqui(re|red|sition)\w*|expan(d|sion)\w*|branch(es)?|headquarters|shareholders?|quarterly|board of directors|annual report)\b',
    'VO.SCENE.TECH_IT': r'\b(software|portal|passwords?|servers?|network|IT department|IT|upgrade[sd]?|technical support|tech support|log ?in|database|app|cybersecurity|firewall)\b',
    'VO.SCENE.RND_PRODUCT': r'\b(prototypes?|research(ers)?|laborator(y|ies)|R&D|product development|engineers?|engineering|patents?|testing phase|new product line)\b',
    'VO.SCENE.TRAVEL_FLIGHT': r'\b(flights?|airport|business trip|trips?|itinerar\w*|boarding|airlines?|train|luggage|baggage|travel(ers|ling|ing)?)\b',
    'VO.SCENE.HOTEL_LODGING': r'\b(hotels?|check-in|check-out|guests?|lodging|suites?|room reservations?|front desk|inn)\b',
    'VO.SCENE.DINING_CATERING': r'\b(restaurants?|menus?|catering|caterer|chefs?|dinner|lunch(eon)?|meals?|café|cafe|food|dining|banquet)\b',
    'VO.SCENE.EVENT_CONFERENCE': r'\b(conferences?|events?|festivals?|exhibit\w*|seminars?|venues?|registration|register(ed)?|attendees?|speakers?|keynote|trade show)\b',
    'VO.SCENE.REAL_ESTATE': r'\b(leases?|tenants?|rent|rented|renting|landlords?|propert(y|ies)|apartments?|office space|premises|real estate)\b',
    'VO.SCENE.CONSTRUCTION_MAINT': r'\b(renovat\w*|construct\w*|repair\w*|maintenance|contractors?|install\w*|plumb\w*|elevators?|resurfac\w*)\b',
    'VO.SCENE.LEGAL_COMPLIANCE': r'\b(regulations?|regulatory|complian\w*|legal|law|lawyers?|permits?|licen[cs]e[sd]?|certif\w*|attorneys?)\b',
    'VO.SCENE.SAFETY': r'\b(safety|hazard\w*|inspection|inspectors?|protective|emergency|evacuat\w*|accidents?|fire drill)\b',
    'VO.SCENE.HEALTH_MEDICAL': r'\b(clinics?|patients?|doctors?|medical|health|dental|dentist|pharmac\w*|hospitals?)\b',
    'VO.SCENE.MEDIA_PUBLISH': r'\b(magazines?|publish(er|ers|ing)|editors?|journal\w*|newspapers?|press release|press|subscribers?|readers|authors?|reporters?|broadcast\w*)\b',
    'VO.SCENE.COMMUNITY_CULTURE': r'\b(community|museums?|librar(y|ies)|volunteer\w*|residents?|city council|council|galler(y|ies)|concerts?|swimming pool|(?<!car )(?<!business )(?<!industrial )park|art)\b',
    'VO.SCENE.RETAIL_SHOPPING': r'\b(stores?|shops|shopping|shoppers?|retail\w*|discounts?|on sale|sales event|checkout|coupons?|cashiers?|merchandise)\b',
    'VO.SCENE.ENVIRONMENT_ENERGY': r'\b(energy|electricity|recycl\w*|environment\w*|sustainab\w*|emissions?|solar|power outages?|power cuts?|carbon|renewable)\b',
    'VO.SCENE.TRANSPORT_COMMUTE': r'\b(parking|commut\w*|bus(es)?|traffic|public transport\w*|roads?|vehicles?|bicycles?|shuttle|subway)\b',
}
SCENE_RE = {k: re.compile(v, re.I) for k, v in SCENES.items()}
CASE_SENS = {'IT', 'R&D'}   # A2-QC：IT 不能忽略大小写（否则 it 全命中）



def scenes(text, top=2, min_hits=2):
    sc = []
    text = re.sub(r'\bin order (to|for)\b', ' ', text, flags=re.I)   # A2-QC：in order to 不是订单
    for k, rx in SCENE_RE.items():
        hits = {m.group(0) if m.group(0).upper() in CASE_SENS else m.group(0).lower() for m in rx.finditer(text)}
        hits = {h for h in hits if h.upper() not in CASE_SENS or h in CASE_SENS}
        if len(hits) >= min_hits:
            sc.append((len(hits), k))
    sc.sort(reverse=True)
    return [k for _, k in sc[:top]]


# ---------- P5/P6 语法细分 ----------
DETS = r'(the|a|an|its|their|his|her|our|your|my|this|that|these|those|each|every|any|some|no|several|many|few|various|both|all|numerous)'  # A2: + 数量限定词
PREPS = r'(of|for|in|on|at|by|with|without|from|to|about|after|before|during|through|upon|into|despite|within|regarding)'
TIME_PREPS = {'since', 'for', 'during', 'within', 'by', 'until', 'till', 'at', 'on', 'in', 'throughout', 'prior to', 'ahead of'}
PLACE_PREPS = {'across', 'throughout', 'along', 'beside', 'among', 'between', 'near', 'opposite', 'behind', 'above', 'below', 'inside', 'outside'}
CONJ_ADV = {'however', 'therefore', 'moreover', 'furthermore', 'consequently', 'nevertheless', 'meanwhile', 'otherwise',
            'instead', 'thus', 'accordingly', 'besides', 'likewise', 'similarly', 'in addition', 'as a result',
            'for example', 'for instance', 'in fact', 'in contrast', 'on the other hand', 'even so', 'after all',
            'in the meantime', 'afterward', 'afterwards', 'still', 'then', 'also', 'as well', 'nonetheless', 'hence', 'indeed'}
PURE_CONJ = {'although', 'though', 'even though', 'because', 'whereas', 'unless', 'as soon as', 'so that', 'provided that',
             'now that', 'even if', 'whether', 'while', 'if', 'once', 'as long as', 'in case', 'provided', 'providing'}   # A2-QC: + if/once
PREP_LIKE = {'despite', 'in spite of', 'because of', 'due to', 'owing to', 'during', 'regardless of', 'instead of',
             'according to', 'prior to', 'in addition to', 'except for', 'without', 'following', 'given'}


def pre_blank(stem):
    m = re.search(r"([A-Za-z'’]+)\s*-------", stem)
    return m.group(1).lower() if m else ''


def post_blank(stem):
    m = re.search(r"-------\s*([A-Za-z'’]+)", stem)
    return m.group(1).lower() if m else ''


AL_NOUNS = {'approval', 'approvals', 'proposal', 'proposals', 'arrival', 'arrivals', 'renewal', 'renewals', 'removal', 'rental', 'rentals',
            'referral', 'referrals', 'withdrawal', 'disposal', 'survival', 'trial', 'trials', 'dismissal', 'refusal', 'retrieval',
            'appraisal', 'tutorial', 'manual', 'manuals', 'interval', 'intervals', 'festival', 'portal', 'deal', 'meal', 'signal', 'journal'}


def pos_of(word):
    w = word.lower().strip()
    if ' ' in w:
        return None
    if w.endswith('ly') and not w.endswith(('ply', 'ally')) or w.endswith('ally'):
        return 'adv'
    if re.search(r'(tion|sion|ment|ance|ence|ity|ness|ship|ism|ure|ist|ee|ency|ancy|age)s?$', w):
        return 'noun'
    if re.search(r'(able|ible|ive|ful|ous|al|ent|ant|ic|ary|less|ish|ical)$', w):
        return 'adj'
    if w in AL_NOUNS:   # A2：approval/proposal/arrival 是名词，不是 -al 形容词
        return 'noun'
    if w.endswith(('cise', 'wise')):   # A2: concise/precise/otherwise 不是动词
        return 'adj' if w.endswith('cise') else 'adv'
    if w in ADJ_ATE or w.endswith('ulate') and w in ('immaculate',):   # A2-QC：accurate/appropriate 是形容词
        return 'adj'
    if re.search(r'(ize|ise|ify|ate|en)$', w):
        return 'verb'
    return None


ADJ_ATE = {'accurate', 'appropriate', 'adequate', 'separate', 'fortunate', 'unfortunate', 'immediate', 'private', 'considerate',
           'moderate', 'deliberate', 'legitimate', 'ultimate', 'intricate', 'elaborate', 'approximate', 'inaccurate', 'inappropriate',
           'compassionate', 'passionate', 'desperate', 'delicate', 'intimate', 'innate', 'ornate', 'corporate', 'literate', 'affordable'}
PART_ADJ = {'pleased', 'interested', 'satisfied', 'excited', 'delighted', 'disappointed', 'surprised', 'concerned', 'worried',
            'impressed', 'qualified', 'confused', 'amazed', 'thrilled', 'frustrated', 'encouraged', 'committed', 'dedicated'}


def word_form_nodes(stem, ans, opts):
    out = ['FD.VOC.AFFIX']
    pre, post = pre_blank(stem), post_blank(stem)
    p = pos_of(ans)
    a = ans.lower()
    BE = ('be', 'is', 'are', 'was', 'were', 'been', 'being')
    # A2：has/have/had + 过去分词 = 完成时；be + -ed/-en = 被动（选项同词族时属动词形态，不是词性槽）
    if pre in ('has', 'have', 'had') and re.search(r'(ed|en|wn)$', a) and p != 'adv':
        return out + ['GR.VERB.TENSE_PERFECT']
    if pre in BE and a in PART_ADJ:
        return out + ['GR.NONFIN.PARTICIPLE_ADJ']   # A2：be pleased/interested = 情感分词形容词
    if pre in BE and re.search(r'(ed|en|wn)$', a) and p not in ('adv', 'adj', 'noun'):
        return out + ['GR.VERB.VOICE_PASSIVE']
    if p == 'adv':
        if post and pos_of(post) == 'adj' or post.endswith('ed') and pre in BE \
                or pre in BE and post and not re.search(r'(ed|ing|en)$', post) and not re.fullmatch(PREPS, post):   # A2: is deceptively simple
            out.append('GR.POS.ADV_ADJ')
        elif pre in ('will', 'has', 'have', 'had', 'can', 'should', 'must', 'may', 'would', 'could', 'is', 'are', 'was', 'were', 'be', 'been'):
            out.append('GR.POS.ADV_AUX_SLOT')
        elif not pre or stem.strip().startswith('-------'):
            out.append('GR.POS.ADV_SENTENCE')
        else:
            out.append('GR.POS.ADV_VERB')
    elif p == 'noun' or (ans.lower().endswith('s') and p is None and pre in DETS.strip('()').split('|')):
        if re.fullmatch(DETS, pre or '-'):
            out.append('GR.POS.NOUN_AFTER_DET')
        elif re.fullmatch(PREPS, pre or '-'):
            out.append('GR.POS.NOUN_AFTER_PREP')
        elif re.search(r'(er|or|ant|ent|ist|ee)s?$', ans.lower()) and not re.search(r'(ment|ence|ance)s?$', ans.lower()) and any(re.search(r'(tion|ment|ance|ence)s?$', o.lower()) for o in opts):
            out.append('GR.POS.NOUN_PERSON_THING')
        else:
            out.append('GR.POS.NOUN_SUBJ_OBJ')
    elif p == 'adj' or ans.lower().endswith(('ed', 'ing')) and post and pos_of(post) == 'noun':
        if not post or re.fullmatch(PREPS + r'|than|and|or|enough', post):
            out.append('GR.POS.ADJ_COMPLEMENT')
        elif pre in ('be', 'is', 'are', 'was', 'were', 'been', 'become', 'remain', 'seem', 'appear', 'look', 'stay', 'keep', 'make', 'find'):
            out.append('GR.POS.ADJ_COMPLEMENT')
        else:
            out.append('GR.POS.ADJ_BEFORE_NOUN')
    elif p == 'verb' or pre in ('to', 'will', 'can', 'should', 'must', 'may', 'might', 'would', 'could', 'please'):
        out.append('GR.POS.VERB_SLOT')
    elif re.search(r'(er|or|ant|ist)s?$', ans.lower()):
        out.append('GR.POS.NOUN_PERSON_THING')
    elif p is None and re.fullmatch(DETS, pre or '-'):   # A2-QC：its ------- response → 形容词；the ------- of → 名词
        out.append('GR.POS.NOUN_AFTER_DET' if not post or re.fullmatch(PREPS, post) else 'GR.POS.ADJ_BEFORE_NOUN')
    elif p is None and pre in ('more', 'most', 'less', 'least', 'very', 'highly', 'and', 'extremely', 'so', 'too'):   # A2-QC：a more ------- analysis / highly ------- with
        out.append('GR.POS.ADJ_COMPLEMENT' if not post or re.fullmatch(PREPS + r'|than|and|or|enough', post) else 'GR.POS.ADJ_BEFORE_NOUN')
    return out


def tense_nodes(stem, ans):
    a = ans.lower()
    if pre_blank(stem) in ('has', 'have', 'had') or re.search(r'\b(has|have|had|will have)\b', a) or re.search(r'\b(since|by the time|already|so far|for the past|yet)\b', stem, re.I):
        return ['GR.VERB.TENSE_PERFECT']
    if re.search(r'\b(as soon as|once|when|before|after|until|if|unless)\b', stem, re.I) and not a.startswith('will') \
            and re.search(r'\b(will|next|tomorrow)\b', stem, re.I):
        return ['GR.VERB.TENSE_FUTURE_CLAUSE']
    return ['GR.VERB.TENSE_SIMPLE']


ADJ_PREP_HEADS = {'responsible', 'interested', 'eligible', 'aware', 'capable', 'familiar', 'compatible', 'consistent', 'subject',
                  'dependent', 'accustomed', 'comparable', 'equivalent', 'exempt', 'proud', 'similar', 'satisfied', 'concerned',
                  'committed', 'dedicated', 'accountable', 'suitable', 'appropriate', 'available', 'essential', 'relevant',
                  'different', 'inclusive', 'due', 'acceptable', 'grateful', 'superior', 'inferior', 'opposed', 'related', 'free',
                  'beneficial', 'sensitive', 'resistant', 'typical', 'critical', 'close', 'full', 'involved', 'unaware', 'ineligible',
                  'accessible', 'applicable', 'mindful', 'confident', 'skilled', 'experienced', 'renowned', 'famous', 'known'}   # A2-QC


def prep_nodes(stem, ans, opts):
    a = ans.lower()
    if any(o.lower() in PURE_CONJ or o.lower() in CONJ_ADV for o in opts) and any(o.lower() in PREP_LIKE for o in opts):
        return ['GR.CONN.PREP_VS_CONJ'], 'mix'
    if len(a.split()) >= 2:
        return ['GR.CONN.PREP_PHRASE_MULTI'], None
    if pre_blank(stem) in ADJ_PREP_HEADS:   # A2: responsible for / familiar with …
        return ['VO.COLLO.ADJ_PREP'], None
    after = ' '.join(re.split(r'-------', stem, 1)[1].split()[:4]) if '-------' in stem else stem
    if a in TIME_PREPS and (re.search(r'(\d|\b(the end|years?|months?|weeks?|days?|hours?|minutes?|mornings?|afternoons?|evenings?|nights?|mondays?|tuesdays?|wednesdays?|thursdays?|fridays?|saturdays?|sundays?|january|february|march|april|june|july|august|september|october|november|december|noon|midnight|quarter|period|season|summer|winter|spring|autumn|deadline|weekend|today|tomorrow|yesterday|next|last|this|the (first|second|third|last|past|previous|coming)|a (period|week|month|year|day))\b)', after, re.I)
                            or re.search(r'\bMay\b', after)):   # A2：只看空格后 4 个词（on the basis of … five years 不是时间介词）
        return ['GR.CONN.PREP_TIME'], None
    if a in PLACE_PREPS:
        return ['GR.CONN.PREP_PLACE'], None
    return ['GR.CONN.PREP_MEANING'], None


def conj_nodes(stem, ans, opts):
    a = ans.lower()
    lo = [o.lower() for o in opts]
    if re.search(r'\b(both|either|neither|not only|whether)\b', stem, re.I) and a in ('and', 'or', 'nor', 'but also', 'but'):
        return ['GR.CONN.CONJ_CORRELATIVE'], None
    if a in CONJ_ADV:
        return ['GR.CONN.CONJ_ADVERB'], 'adv'
    if a in ('before', 'after', 'since', 'until', 'upon', 'without', 'despite', 'during') and post_blank(stem).endswith('ing') \
            or all(o in PREP_LIKE or o in PLACE_PREPS or o in ('among', 'besides', 'beside', 'upon', 'within', 'throughout') for o in lo):
        return ['GR.CONN.PREP_TIME' if a in TIME_PREPS | {'before', 'after'} else 'GR.CONN.PREP_MEANING'], 'prep'   # A2: before closing = 介词+动名词
    if any(o in PREP_LIKE for o in lo) and any(o in PURE_CONJ or o in CONJ_ADV for o in lo):
        return ['GR.CONN.PREP_VS_CONJ'], 'mix'
    if a in ('and', 'but', 'or', 'yet', 'so', 'nor'):
        return ['GR.CONN.CONJ_COORD'], None
    if a in ('whether', 'if', 'that') and re.search(r'\b(know|ask|decide|determine|confirm|wonder|sure|check)\w*\s+-------', stem, re.I):
        return ['GR.REL.NOUN_CLAUSE'], None
    return ['GR.CONN.CONJ_ADVERBIAL'], None


def rel_nodes(ans):
    a = ans.lower()
    if a in ('where', 'when') or re.match(r'(in|at|on|to|by|for|with|from) (which|whom)', a):
        return ['GR.REL.REL_ADVERB']
    if a == 'what':
        return ['GR.REL.REL_WHAT']
    if a.startswith(('whoever', 'whatever', 'whichever', 'however', 'wherever', 'whenever')):
        return ['GR.REL.COMPOUND_REL']
    if a in ('whether', 'if'):
        return ['GR.REL.NOUN_CLAUSE']
    return ['GR.REL.REL_PRONOUN']


def comp_nodes(stem, ans):
    a = ans.lower()
    if re.search(r'\bas\b.*-------.*\bas\b', stem, re.I) or re.search(r'\bas -------', stem, re.I):
        return ['GR.COMP.EQUATIVE']
    if a.startswith('most') or a.endswith('est') or re.search(r'\bthe -------', stem, re.I) and not re.search(r'\bthan\b', stem, re.I):
        return ['GR.COMP.SUPERLATIVE']
    return ['GR.COMP.COMPARATIVE']


def pron_nodes(ans):
    a = ans.lower()
    if a.endswith(('self', 'selves')):
        return ['GR.PRON.REFLEXIVE']
    if a in ('mine', 'yours', 'his', 'hers', 'ours', 'theirs'):
        return ['GR.PRON.POSSESSIVE_PRONOUN']
    if a in ('another', 'other', 'others', 'the other', 'the others', 'one', 'ones', 'some', 'any', 'anyone', 'someone', 'everyone', 'none'):
        return ['GR.PRON.INDEFINITE']
    if a in ('those', 'that', 'these', 'this'):
        return ['GR.PRON.DEMONSTRATIVE']
    return ['GR.PRON.CASE']


def lex_node(stem, ans, opts):
    ps = [pos_of(o) for o in opts]
    p = pos_of(ans)
    if p and ps.count(p) >= 3:
        return {'adv': 'VO.LEX.ADV', 'noun': 'VO.LEX.NOUN', 'adj': 'VO.LEX.ADJ', 'verb': 'VO.LEX.VERB'}[p]
    if pre_blank(stem) in ('to', 'will', 'can', 'should', 'must', 'may', 'would', 'could', 'please'):
        return 'VO.LEX.VERB'
    cnt = Counter(x for x in ps if x).most_common()
    if cnt and cnt[0][1] >= 2 and (len(cnt) == 1 or cnt[1][1] < cnt[0][1]) and p in (None, cnt[0][0]):   # A2-QC：已知词性多数即取之
        return {'adv': 'VO.LEX.ADV', 'noun': 'VO.LEX.NOUN', 'adj': 'VO.LEX.ADJ', 'verb': 'VO.LEX.VERB'}[cnt[0][0]]
    if all(re.fullmatch(r'[a-z]+ed', o.lower()) for o in opts):   # A2-QC：四个 -ed 选项 = 动词（被动/完成）
        return 'VO.LEX.VERB'
    pre = pre_blank(stem)
    if pre in ('to', 'will', 'can', 'should', 'must', 'may', 'would', 'could', 'please', 'not') or \
            all(re.fullmatch(r'[a-z]+(ed|s)?', o.lower()) for o in opts) and pre in ('has', 'have', 'had', 'been'):
        return 'VO.LEX.VERB'
    if re.fullmatch(DETS, pre or '-'):
        return 'VO.LEX.NOUN'
    return None


def gram_nodes(tag, stem, ans, opts):
    """返回 (P5 题型节点, [语法节点])"""
    if tag == 'word-form':
        return 'QT.P5.WORD_FORM', word_form_nodes(stem, ans, opts)
    if tag == 'verb-tense':
        return 'QT.P5.VERB_FORM', tense_nodes(stem, ans)
    if tag == 'passive-voice':
        return 'QT.P5.VERB_FORM', ['GR.VERB.VOICE_PASSIVE'] + (['GR.VERB.TENSE_PERFECT'] if re.search(r'\b(has|have|had) been\b', ans.lower()) else [])
    if tag == 'subject-verb-agreement':
        return 'QT.P5.VERB_FORM', ['GR.VERB.AGREE_SV'] + (['FD.SENT.MODIFIER_STRIP'] if re.search(r'\b(of|with|in)\b', stem.split('-------')[0]) else [])
    if tag == 'modal':
        return 'QT.P5.VERB_FORM', ['GR.VERB.MODAL_BASE']
    if tag == 'conditional':
        return 'QT.P5.VERB_FORM', ['GR.VERB.CONDITIONAL_INVERSION']
    if tag == 'gerund-infinitive':
        a = ans.lower()
        return 'QT.P5.VERB_FORM', ['GR.NONFIN.TO_INF' if a.startswith('to ') else 'GR.NONFIN.GERUND' if a.endswith('ing') else 'GR.VERB.VERB_PATTERN']
    if tag == 'participle-adjective':
        if re.match(r'\s*-------\s+[^,]{2,60},', stem):   # A2：句首 “Sent in a plain envelope, …” = 分词构句
            return 'QT.P5.VERB_FORM', ['GR.NONFIN.PARTICIPLE_CLAUSE']
        return 'QT.P5.WORD_FORM', ['GR.NONFIN.PARTICIPLE_ADJ']
    if tag == 'preposition':
        ns, k = prep_nodes(stem, ans, opts)
        return ('QT.P5.CONNECTOR_MIX' if k == 'mix' else 'QT.P5.PREP'), ns
    if tag == 'conjunction':
        ns, k = conj_nodes(stem, ans, opts)
        return ('QT.P5.CONNECTOR_MIX' if k in ('mix', 'adv') else 'QT.P5.PREP' if k == 'prep' else 'QT.P5.CONJ'), ns
    if tag == 'relative-clause':
        return 'QT.P5.RELATIVE', rel_nodes(ans)
    if tag == 'comparative':
        return 'QT.P5.COMPARATIVE', comp_nodes(stem, ans)
    if tag == 'quantifier':
        return 'QT.P5.PAIR_GRAMMAR', ['GR.PRON.DETERMINER_QUANT'] + (['GR.VERB.AGREE_QUANT'] if re.search(r'number of|each|every', stem + ans, re.I) else [])
    if tag == 'pronoun':
        return 'QT.P5.PRONOUN', pron_nodes(ans)
    if tag == 'vocabulary':
        n = lex_node(stem, ans, opts)
        return 'QT.P5.VOCAB', [n] if n else []
    return None, []


P6_QT = {'verb-tense': 'QT.P6.CTX_TENSE', 'pronoun': 'QT.P6.CTX_PRONOUN', 'vocabulary': 'QT.P6.CTX_VOCAB'}


def tag_p5(q, stem, ans, opts):
    tags = q['tags']
    prim, ns = gram_nodes(tags[0], stem, ans, opts)
    for t in tags[1:]:
        p2, n2 = gram_nodes(t, stem, ans, opts)
        ns += ([p2] if p2 else []) + n2
    return prim, ns + scenes(stem, top=1)


def tag_p6(q, text, qnum, ans, opts, tx):
    tags = q['tags']
    marker = '{{%d}}' % qnum
    pos = text.find(marker) / max(1, len(text))
    # 题干上下文：空位所在句
    sent = ''
    m = re.search(r'([^.!?\n]*' + re.escape(marker) + r'[^.!?\n]*)', text)
    if m:
        sent = m.group(1).replace(marker, '-------')
    for k in re.findall(r'\{\{\d+\}\}', sent):
        sent = sent.replace(k, '')
    ns = ['QT.P6.CLASSIFY']
    if 'sentence-insertion' in tags:
        sub = 'QT.P6.INS_OPENING' if pos < 0.15 else 'QT.P6.INS_CLOSING' if pos > 0.8 else 'QT.P6.INS_TRANSITION'
        return 'QT.P6.INSERTION', ns + [sub, 'FD.READ.DISCOURSE', 'FD.READ.REFERENCE', tx]
    t0 = tags[0]
    _, gr = gram_nodes(t0, sent, ans, opts)
    for t in tags[1:]:
        p2, n2 = gram_nodes(t, sent, ans, opts)
        gr += n2
    if t0 == 'conjunction' and ans.lower().rstrip(',') in CONJ_ADV:
        prim = 'QT.P6.CTX_CONJ_ADV'; gr = ['GR.CONN.CONJ_ADVERB', 'FD.READ.DISCOURSE']
    elif t0 == 'verb-tense' and pre_blank(sent) in ('has', 'have', 'had', 'be', 'been', 'being', 'is', 'are', 'was', 'were', 'will', 'would', 'can', 'could', 'must', 'should', 'may', 'might', 'to'):
        prim = 'QT.P6.INDEPENDENT'   # A2：空格紧跟助动词，只考形式，不需上下文判时态
    elif t0 in P6_QT:
        prim = P6_QT[t0]
        if t0 == 'pronoun':
            gr.append('FD.READ.REFERENCE')
    else:
        prim = 'QT.P6.INDEPENDENT'
    return prim, ns + gr + [tx]


def p7_type(q, tags, ans=None):
    # A2：去掉 “According to (the notice|Document 1), …” 前缀后再判题型
    t = re.sub(r'^\s*(according to|based on|in) (the )?[^,?]{1,60},\s*', '', q, flags=re.I)
    t = t[:1].upper() + t[1:]
    if 'sentence-insertion' in tags or re.search(r'positions marked \[1\]', t):
        return 'INSERTION'
    if 'vocabulary' in tags or re.search(r'closest in meaning', t, re.I):
        return 'SYNONYM'
    if re.search(r'(mean|imply|suggest|indicate) when (he|she|they) (writes?|says?)|most likely mean', t, re.I):   # A2-QC：imply when he writes “…” 也是意图题
        return 'INTENT'
    if 'not-question' in tags or re.search(r'\bNOT\b', t):
        return 'NOT_TRUE'
    # A2：“Why does X mention/include/say …” 问的是某处细节的用意 → 推断，不是全文主旨
    if re.search(r'^\s*why (does|do|did|might|would) .*\b(mention|say|says|note|point out|refer to|ask about)\b', t, re.I):
        return 'INFERENCE'
    # A2：“Why did X write/contact …”“What is being announced/advertised” = 全文目的/主题
    if 'purpose' in tags or 'main-idea' in tags or re.search(
            r'\b(purpose|main (topic|idea|subject)|mainly (about|discuss)|primarily (about|discuss)|why was .* (written|sent))'
            r'|^\s*what (is|was) (being )?(advertised|announced|described|offered|promoted|reported)\?'
            r'|^\s*what (service|product|event|change|program|opportunity) is (being )?(advertised|announced|described|offered|promoted)\?'
            r'|^\s*what (is|are|was) [^?]* announcing\b|^\s*what did [^?]* announce\b|^\s*what is the [^?]{1,40} (mainly )?about\?', t, re.I):
        return 'MAIN_PURPOSE'
    # A2：“Why did X write/contact Y?” 答案是 “To …” 时问的是来信目的；答案是原因陈述时仍算原因题
    if re.search(r'^\s*why (did|does|is|has) [^?]*\b(write|writing|written|contact|contacting|contacted)\b', t, re.I) and (ans is None or re.match(r'\s*to\b', ans, re.I)) and not re.search(r'most likely|probably', t, re.I):
        return 'MAIN_PURPOSE'
    # A2：“What does the paragraph/report suggest?” = 暗示（推断），不是建议
    if re.search(r'^\s*what (does|do|did) [^?]*\b(paragraph|article|notice|e-?mail|letter|report|data|survey|chart|table|results?|review|page|information|figures?|memo|message|line|invoice|schedule|agenda|form|receipt|graph|entry|record|statement|summary)\b[^?]* (suggest|imply|indicate)\??$', t, re.I):
        return 'INFERENCE'
    # A2：“What is indicated/stated about the position” 是照合题，不是身份推断（“most likely true” 仍算推断）
    if not re.search(r'most likely|probably', t, re.I) and re.search(r'\b(indicated|stated|true|mentioned|noted|said|reported)\b.*\babout\b|^\s*what is (indicated|stated|true|mentioned)\b', t, re.I):
        return 'TRUE_INDICATED'
    if re.search(r"\b(for whom|who most likely|who (is|are) .* most likely|most likely (work|an?|the) |intended (for|audience)|what (kind of|type of) (business|company|organi[sz]ation)|what (is|was) (most likely )?[^?]*'s? (job|occupation|profession)\b|what (job|occupation|profession)\b|what industry)", t, re.I):   # A2-QC：listed in the job posting 不是身份题
        return 'INFER_WHO'
    if re.search(r'(most likely|probably) (do|happen|take place) next|what will (most likely|probably) happen|^\s*what will [^?]* do next|will .* most likely (do|happen)|what will .* (probably|most likely)|what (is|are) .* (likely|expected) to (do|happen)', t, re.I):
        return 'INFER_NEXT'
    # A2：去掉 expected（“expected to be at its noisiest” 不是要求行动）；补 suggest/recommend/request/ask X to
    if re.search(r'\b(asked|requested|advised|encouraged|instructed|invited|reminded|told|required|recommended) to\b'
                 r'|what (does|do|did) .* (ask|request|recommend|suggest|advise|instruct)\b.* to do'
                 r'|what .* (suggest|recommend)s? .* do|^\s*what (does|do|did) [^?]* (suggest|recommend|request|propose)\??$'
                 r'|^\s*what (does|do|did) [^?]* (ask|tell|remind|instruct)s? [^?]* to\b', t, re.I):
        return 'REQUEST_ACTION'
    if 'inference' in tags or re.search(r'\b(suggested|implied|inferred|most likely|probably|likely|might|best (be )?described)\b', t, re.I):
        return 'INFERENCE'
    if re.search(r'^\s*why\b', t, re.I):
        return 'REASON'
    TIMEY = r'\d|\b(a\.m|p\.m|noon|midnight|morning|afternoon|evening|night|today|tomorrow|yesterday|weeks?|months?|years?|days?|hours?|minutes?|quarter|season|spring|summer|autumn|fall|winter|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december|weekend|weekday|immediately|annually|daily|weekly|monthly)\b'
    if re.search(r'^\s*(when|by when)\b', t, re.I) and ans is not None and not re.search(TIMEY, ans, re.I):
        return 'DETAIL'   # A2-QC：When may tools be renewed? → 答“条件”而非时间，归细节题
    if re.search(r'^\s*(when|how much|how many|how long|how often|how far in advance|what time|at what time|by when|on what (date|day)|by what (date|time)|what (date|day|year|percentage|amount|price|fee|discount))\b'
                 r'|^\s*what (is|was|will be) the [^?]*(maximum|minimum|total|amount|charge|fee|cost|price|number of|deadline)\b', t, re.I):
        return 'DETAIL_NUMBER'
    return 'DETAIL'


def p7x(qtype, tx):
    for suf in TX_SUFFIX.get(tx, [tx.split('.', 1)[1]]):
        nid = 'QT.P7X.%s.%s' % (qtype, suf)
        if nid in G:
            return nid
    return None


PARA_HINT = {'SYNONYM': ['VO.CONF.POLYSEMY_CONTEXT', 'VO.PARA.WORD_SYNONYM'], 'INTENT': ['FD.READ.DISCOURSE'],
             'INSERTION': ['FD.READ.REFERENCE', 'FD.READ.DISCOURSE'], 'NOT_TRUE': ['ST.ELIM.OPTIONS'],
             'MAIN_PURPOSE': ['FD.READ.SKIM'], 'DETAIL': ['FD.READ.SCAN'], 'DETAIL_NUMBER': ['FD.READ.SCAN', 'VO.PARA.NUMBER_TIME'],
             'TRUE_INDICATED': ['VO.PARA.WORD_SYNONYM'], 'INFERENCE': ['VO.PARA.GENERALIZE'], 'INFER_WHO': ['VO.PARA.ROLE_REFERENCE'],
             'INFER_NEXT': [], 'REQUEST_ACTION': ['FD.READ.SCAN'], 'REASON': ['VO.PARA.CAUSE_EFFECT']}
# QT.P7.<TYPE> 本身是分组节点；xdf 题主节点也用这些分组节点（engine 按节点 id 统计，分组节点可作主节点）
QT_P7 = {'REASON': 'QT.P7.REASON'}


def tag_p7(qtext, tags, bundle_tx, doc_txs, kind, ans=None):
    qt = p7_type(qtext, tags, ans)
    group = QT_P7.get(qt, 'QT.P7.' + qt)
    ns = []
    x = p7x(qt, bundle_tx if kind != 'single' else doc_txs[0])
    if x:
        ns.append(x)
    if kind == 'single':
        ns.append(doc_txs[0])
    else:
        ns += [bundle_tx] + sorted(set(doc_txs))
    calc = None
    if qt == 'DETAIL_NUMBER' and any(t in ('TX.INVOICE', 'TX.SCHEDULE', 'TX.APP_FORM') for t in doc_txs):
        c = p7x('CALC_LOOKUP', next(t for t in doc_txs if t in ('TX.INVOICE', 'TX.SCHEDULE', 'TX.APP_FORM')))
        ns.append(c or 'QT.P7.CALC_LOOKUP')
        if c and re.search(r'\b(in total|total|altogether|combined|how much more|how much less|difference|save|saved|after (the )?discount)\b', qtext, re.I):
            calc = c   # A2-QC：需要计算（合计/差额/折后）→ 计算对照题为主节点
    if calc and not ('cross-reference' in tags and kind != 'single'):
        prim = calc
        ns = [group] + [n for n in ns if n != calc]
    elif 'cross-reference' in tags and kind != 'single':   # A2-QC：单篇不可能跨篇
        prim = 'QT.P7X.CROSS_REF.' + ('TRIPLE' if kind == 'triple' else 'DOUBLE')
        ns = [group] + ns
    elif x:
        prim = x   # A2-QC：主节点用叶节点（题型×文本 交叉节点，与 pilot 一致），分组节点放 node_ids
        ns = [group] + [n for n in ns if n != x]
    else:
        prim = group   # 该题型×文本无交叉叶节点（QT.P7.REASON 本身是叶节点）
    ns += PARA_HINT.get(qt, [])
    return prim, ns, qt


BAND_D = {400: 2, 600: 3, 700: 3, 800: 4, 900: 5}


def p7_rule_diff(kind, nwords, qt, cross):
    """P7 规则难度 1–5：篇章形态 + 设问类型 + 篇幅（kdeppaei 的 p7_diff 与原难度档 2:1 加权；maximcuynat 无原档，直接用规则分）"""
    r = 2 if kind == 'single' else 3
    if qt in ('INFERENCE', 'INFER_WHO', 'INFER_NEXT', 'INTENT', 'INSERTION', 'NOT_TRUE'):
        r += 1
    if cross:   # A2-QC：跨篇与高阶设问分别加分（三篇跨篇推断 = 5）
        r += 1
    if nwords > (250 if kind == 'single' else 550):   # A2-QC：多篇本来就长，篇幅加分门槛提高
        r += 1
    if kind == 'single' and nwords < 90 and qt in ('DETAIL', 'DETAIL_NUMBER', 'MAIN_PURPOSE', 'REASON', 'REQUEST_ACTION'):
        r -= 1
    return max(1, min(5, r))


def p56_rule_diff(part, node_ids, nwords):
    """P5/P6 规则难度 1–5：取考点节点（GR/VO.LEX/VO.COLLO/QT.P6）的最高 target_band → 2/3/3/4/5；
    P5 题干 ≥ 25 词 +1；P6 句子插入至少 3。"""
    bands = [G[n]['target_band'] for n in node_ids if n.startswith(('GR.', 'VO.LEX', 'VO.COLLO', 'QT.P6.INS', 'QT.P6.CTX')) and n in G]
    d = BAND_D.get(max(bands), 3) if bands else 3
    if part == 5 and nwords >= 25:
        d += 1
    return max(1, min(5, d))


def split_header(content):
    lines = content.split('\n')
    hdr = []
    for ln in lines:
        if re.match(r'^(To|From|Date|Subject|Sent|Re|Cc|Attachment)\s*:', ln.strip()):
            hdr.append(ln.strip())
        else:
            break
    if len(hdr) >= 2:
        rest = lines[len(hdr):]
        while rest and not rest[0].strip():
            rest = rest[1:]
        return '\n'.join(hdr), '\n'.join(rest)
    return '', content


def uniq(seq):
    out = []
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out


def main():
    items, bundles, skipped = [], [], []
    for t in range(1, 7):
        d = json.load(open(os.path.join(SRC_DIR, 'reading-test-%d.json' % t), encoding='utf-8'))
        form = 'MXT%02d' % t
        pre = 'MXC-T%02d' % t
        for part in d['parts']:
            p = part['part']
            if p == 5:
                for q in part['questions']:
                    opts = q['choices']; a = 'ABCD'.index(q['answer']); ans = opts[a]
                    stem = re.sub(r'_{3,}', '-------', q['text'])
                    if stem.count('-------') != 1:
                        skipped.append((pre, q['number'], 'P5 题干空位数 ≠ 1')); continue
                    prim, ns = tag_p5(q, stem, ans, opts)
                    items.append({'id': '%s-%d' % (pre, q['number']), 'part': 5, 'form': form, 'qnum': q['number'],
                                  'stem': stem, 'options': opts, 'answer': a, 'answer_letter': q['answer'],
                                  'node': prim, 'node_ids': uniq([prim] + ns),
                                  'difficulty_est': p56_rule_diff(5, uniq([prim] + ns), len(re.findall(r"[A-Za-z']+", stem))),
                                  'explain_en': q['explanation'], 'explain_zh': '', 'src_tags': q['tags'],
                                  'template_id': None, 'source': 'maximcuynat_mit', 'format_version': 'current'})
                continue
            for blk in part['blocks']:
                qs = sorted(blk['questions'], key=lambda x: x['number'])
                qn = [x['number'] for x in qs]
                bid = '%s-%s' % (pre, blk['id'].upper())
                n_doc = len(blk['passages'])
                kind = {1: 'single', 2: 'double', 3: 'triple'}.get(n_doc)
                doc_txs = [DOC_TYPE.get(ps['type']) for ps in blk['passages']]
                if not kind or None in doc_txs:
                    skipped += [(pre, n, '未知文本类型/篇数 %s' % [ps['type'] for ps in blk['passages']]) for n in qn]; continue
                btx = doc_txs[0] if kind == 'single' else {'double': 'TX.DOUBLE', 'triple': 'TX.TRIPLE'}[kind]
                docs, alltext = [], ''
                blank = {}
                for ps in blk['passages']:
                    text = ps['content']
                    if p == 6:
                        for k, n in enumerate(qn, 1):
                            mk = '{{%d}}' % n
                            if text.count(mk) == 1:
                                text = text.replace(mk, '[%d]' % k); blank[n] = k
                    hdr, body = split_header(text)
                    doc = {'doc_type': DOC_TYPE[ps['type']], 'title': ps['type'][0].upper() + ps['type'][1:]}
                    if hdr:
                        doc['header'] = hdr
                    doc['text'] = body
                    docs.append(doc)
                    alltext += ps['content'] + '\n'
                if p == 6 and len(blank) != len(qn):
                    skipped += [(pre, n, 'P6 空位标记缺失或重复') for n in qn]; continue
                if re.search(r'\{\{\d+\}\}', ''.join(d_['text'] + d_.get('header', '') for d_ in docs)):
                    skipped += [(pre, n, '残留空位标记') for n in qn]; continue
                bsc = scenes(alltext)
                b = {'bundle_id': bid, 'part': p, 'form': form, 'kind': kind, 'text_type': btx, 'docs': docs,
                     'qnums': qn, 'node_ids': uniq(([btx] if kind != 'single' else []) + doc_txs + bsc),
                     'refer_to': blk['passages'][0].get('label') or '', 'format_version': 'current',
                     'source': 'maximcuynat_mit'}
                if p == 6:
                    b['blank_marker'] = '[n] = 第 n 个空格（显示时替换为 -------）'
                bundles.append(b)
                for q in qs:
                    opts = q['choices']; a = 'ABCD'.index(q['answer']); ans = opts[a]
                    it = {'id': '%s-%d' % (pre, q['number']), 'part': p, 'form': form, 'qnum': q['number'],
                          'bundle_id': bid, 'options': opts, 'answer': a, 'answer_letter': q['answer']}
                    if p == 6:
                        prim, ns = tag_p6(q, alltext, q['number'], ans, opts, btx)
                        it['difficulty_est'] = p56_rule_diff(6, [prim] + ns, 0)
                        it['blank_n'] = blank[q['number']]
                        if q.get('text'):
                            it['stem'] = q['text']
                    else:
                        qtext = (q.get('text') or '').strip()
                        if not qtext:
                            skipped.append((pre, q['number'], 'P7 缺题干')); continue
                        prim, ns, qt = tag_p7(qtext, q['tags'], btx, doc_txs, kind, ans)
                        it['q'] = qtext
                        it['difficulty_est'] = p7_rule_diff(kind, len(re.findall(r"[A-Za-z']+", alltext)), qt, prim.startswith('QT.P7X.CROSS'))
                    it.update({'node': prim, 'node_ids': uniq([prim] + ns + bsc[:1]),
                               'explain_en': q['explanation'], 'explain_zh': '', 'src_tags': q['tags'],
                               'template_id': None, 'source': 'maximcuynat_mit', 'format_version': 'current'})
                    items.append(it)
    # ---- 校验：节点必须存在 ----
    bad = [(i['id'], n) for i in items for n in i['node_ids'] if n not in G] + \
          [(b['bundle_id'], n) for b in bundles for n in b['node_ids'] if n not in G]
    if bad:
        print('UNKNOWN NODES', bad[:20]); sys.exit(1)
    assert all(i['node'] in i['node_ids'] for i in items)
    assert len({i['id'] for i in items}) == len(items)
    cnt = Counter('P%d' % i['part'] for i in items)
    out = {'meta': {
        'built': '2026-10-22', 'version': 'open-maximcuynat-v1', 'format_version': 'current',
        'source': 'maximcuynat_mit',
        'source_desc': 'github.com/maximcuynat/toeic-practice data/reading-test-1..6.json（6 套新制完整阅读，各 100 题）',
        'license': 'MIT, © 2026 Maxim Cuynat（见 data/open_items/maximcuynat_toeic-practice/LICENSE）',
        'compat': 'items_pilot_v1 字段 id/part/form/qnum/stem|q/options/answer/answer_letter/explain_zh/bundle_id/node/node_ids/blank_n；'
                  '新增 explain_en（原英文解析）、src_tags（原题型标签）、source、difficulty_est（A2-QC 规则估计：P5/P6 按考点节点 target_band，P7 按篇章形态+设问类型+篇幅）；无 target_time_sec/distractor_reasons（build.py 用默认值）',
        'forms': ['MXT%02d' % t for t in range(1, 7)],
        'node_tagging': '规则打标（work/convert_maximcuynat.py）+ A2 全量人工复核修正（data/items_open_qc_fixes.json，由 work/qc/apply_qc_fixes.py 应用）',
        'counts': dict(cnt), 'skipped': [{'form': s[0], 'qnum': s[1], 'reason': s[2]} for s in skipped]},
        'items': items, 'bundles': bundles}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
    nc = Counter(n for i in items for n in i['node_ids'])
    leaf = {k for k, v in G.items() if not v['is_group']}
    print('items', len(items), dict(cnt), 'bundles', len(bundles), 'skipped', len(skipped))
    print('forms', dict(Counter(i['form'] for i in items)))
    print('kinds', dict(Counter((b['part'], b['kind']) for b in bundles)))
    print('distinct nodes', len(nc), 'leaf nodes covered', len(set(nc) & leaf), '/', len(leaf))
    print('primary', Counter(i['node'] for i in items).most_common())
    for s in skipped:
        print('SKIP', s)


if __name__ == '__main__':
    main()
