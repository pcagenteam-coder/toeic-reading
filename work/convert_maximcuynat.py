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
SCENES = {
    'VO.SCENE.OFFICE_ADMIN': r'\b(form|paperwork|file|filing|document|office|stationery|photocop\w*|printer|desk|staff|personnel)\b',
    'VO.SCENE.MEETING_SCHEDULE': r'\b(meeting|agenda|schedul\w*|reschedul\w*|appointment|postpone\w*|conference call|minutes)\b',
    'VO.SCENE.RECRUIT': r'\b(applicant|candidate|hiring|hire|résumé|resume|interview\w*|vacanc\w*|position|job posting|recruit\w*|qualification)\b',
    'VO.SCENE.HR_TRAINING': r'\b(training|workshop|promot\w*|benefit|performance review|employee|orientation|mentor\w*|appraisal)\b',
    'VO.SCENE.PURCHASE_QUOTE': r'\b(quote|quotation|purchase order|supplier|vendor|procure\w*|bulk)\b',
    'VO.SCENE.ORDER_SHIP': r'\b(order|shipment|ship\w*|deliver\w*|courier|parcel|package|tracking|dispatch\w*)\b',
    'VO.SCENE.INVENTORY_PRODUCTION': r'\b(inventory|stock|warehouse|factory|plant|production|assembly|manufactur\w*)\b',
    'VO.SCENE.MARKETING_AD': r'\b(marketing|advertis\w*|campaign|promotion\w*|brand|survey|launch)\b',
    'VO.SCENE.SALES_DEAL': r'\b(contract|negotiat\w*|sales|client|deal|proposal|agreement)\b',
    'VO.SCENE.CUSTOMER_SERVICE': r'\b(complain\w*|refund|exchange|warranty|customer service|customer care|apolog\w*|return\w*)\b',
    'VO.SCENE.FINANCE_ACCOUNT': r'\b(budget|expense\w*|accounting|audit\w*|revenue|profit|finance|financial|reimburs\w*|tax)\b',
    'VO.SCENE.BANK_PAYMENT': r'\b(invoice|payment|bank|account number|credit card|balance|deposit|bill\w*|fee)\b',
    'VO.SCENE.CORP_STRATEGY': r'\b(merger|acqui\w*|expan\w*|branch\w*|headquarters|shareholder|quarter\w*|board)\b',
    'VO.SCENE.TECH_IT': r'\b(software|system|portal|password|server|app|online|website|upgrade|technical|IT|laptop|computer)\b',
    'VO.SCENE.RND_PRODUCT': r'\b(prototype|research|product\w*|design\w*|laborator\w*|develop\w*)\b',
    'VO.SCENE.TRAVEL_FLIGHT': r'\b(flight|airport|travel\w*|trip|itinerar\w*|boarding|airline|train|luggage)\b',
    'VO.SCENE.HOTEL_LODGING': r'\b(hotel|room|reservation|check-in|check-out|guest|lodging|suite|booking)\b',
    'VO.SCENE.DINING_CATERING': r'\b(restaurant|menu|catering|chef|dinner|lunch|meal|café|cafe|food)\b',
    'VO.SCENE.EVENT_CONFERENCE': r'\b(conference|event|festival|exhibit\w*|seminar|venue|register\w*|registration|attendee\w*|speaker)\b',
    'VO.SCENE.REAL_ESTATE': r'\b(lease|tenant|rent\w*|landlord|property|apartment|office space|premises)\b',
    'VO.SCENE.CONSTRUCTION_MAINT': r'\b(renovat\w*|construct\w*|repair\w*|maintenance|contractor|install\w*|building work|plumb\w*)\b',
    'VO.SCENE.LEGAL_COMPLIANCE': r'\b(regulation\w*|complian\w*|legal|policy|law|permit|licen[cs]e\w*|certif\w*)\b',
    'VO.SCENE.SAFETY': r'\b(safety|hazard\w*|inspection|protective|emergency|evacuat\w*|accident)\b',
    'VO.SCENE.HEALTH_MEDICAL': r'\b(clinic|patient|doctor|medical|health|dental|pharmac\w*|hospital)\b',
    'VO.SCENE.MEDIA_PUBLISH': r'\b(magazine|publish\w*|editor|article|journal\w*|newspaper|press|subscri\w*|author)\b',
    'VO.SCENE.COMMUNITY_CULTURE': r'\b(community|museum|librar\w*|volunteer\w*|resident\w*|council|gallery|concert|pool|park)\b',
    'VO.SCENE.RETAIL_SHOPPING': r'\b(store|shop\w*|retail\w*|discount|customer\w*|membership|purchase\w*|sale)\b',
    'VO.SCENE.ENVIRONMENT_ENERGY': r'\b(energy|power|electricity|recycl\w*|environment\w*|sustainab\w*|emission\w*|solar|outage)\b',
    'VO.SCENE.TRANSPORT_COMMUTE': r'\b(parking|commut\w*|bus|traffic|transport\w*|road|vehicle|bicycle|shuttle)\b',
}
SCENE_RE = {k: re.compile(v, re.I) for k, v in SCENES.items()}


def scenes(text, top=2, min_hits=2):
    sc = []
    for k, rx in SCENE_RE.items():
        hits = {m.group(0).lower() for m in rx.finditer(text)}
        if len(hits) >= min_hits:
            sc.append((len(hits), k))
    sc.sort(reverse=True)
    return [k for _, k in sc[:top]]


# ---------- P5/P6 语法细分 ----------
DETS = r'(the|a|an|its|their|his|her|our|your|my|this|that|these|those|each|every|any|some|no)'
PREPS = r'(of|for|in|on|at|by|with|without|from|to|about|after|before|during|through|upon|into|despite|within|regarding)'
TIME_PREPS = {'since', 'for', 'during', 'within', 'by', 'until', 'till', 'at', 'on', 'in', 'throughout', 'prior to', 'ahead of'}
PLACE_PREPS = {'across', 'throughout', 'along', 'beside', 'among', 'between', 'near', 'opposite', 'behind', 'above', 'below', 'inside', 'outside'}
CONJ_ADV = {'however', 'therefore', 'moreover', 'furthermore', 'consequently', 'nevertheless', 'meanwhile', 'otherwise',
            'instead', 'thus', 'accordingly', 'besides', 'likewise', 'similarly', 'in addition', 'as a result',
            'for example', 'for instance', 'in fact', 'in contrast', 'on the other hand', 'even so', 'after all',
            'in the meantime', 'afterward', 'afterwards', 'still', 'then', 'also', 'as well', 'nonetheless', 'hence', 'indeed'}
PURE_CONJ = {'although', 'though', 'even though', 'because', 'whereas', 'unless', 'as soon as', 'so that', 'provided that',
             'now that', 'even if', 'whether', 'while'}
PREP_LIKE = {'despite', 'in spite of', 'because of', 'due to', 'owing to', 'during', 'regardless of', 'instead of',
             'according to', 'prior to', 'in addition to', 'except for', 'without', 'following', 'given'}


def pre_blank(stem):
    m = re.search(r"([A-Za-z'’]+)\s*-------", stem)
    return m.group(1).lower() if m else ''


def post_blank(stem):
    m = re.search(r"-------\s*([A-Za-z'’]+)", stem)
    return m.group(1).lower() if m else ''


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
    if re.search(r'(ize|ise|ify|ate|en)$', w):
        return 'verb'
    return None


def word_form_nodes(stem, ans, opts):
    out = ['FD.VOC.AFFIX']
    pre, post = pre_blank(stem), post_blank(stem)
    p = pos_of(ans)
    if p == 'adv':
        if post and pos_of(post) == 'adj' or post.endswith('ed') and pre in ('be', 'is', 'are', 'was', 'were', 'been', 'being'):
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
    return out


def tense_nodes(stem, ans):
    a = ans.lower()
    if re.search(r'\b(has|have|had|will have)\b', a) or re.search(r'\b(since|by the time|already|so far|for the past|yet)\b', stem, re.I):
        return ['GR.VERB.TENSE_PERFECT']
    if re.search(r'\b(as soon as|once|when|before|after|until|if|unless)\b', stem, re.I) and not a.startswith('will') \
            and re.search(r'\b(will|next|tomorrow)\b', stem, re.I):
        return ['GR.VERB.TENSE_FUTURE_CLAUSE']
    return ['GR.VERB.TENSE_SIMPLE']


def prep_nodes(stem, ans, opts):
    a = ans.lower()
    if any(o.lower() in PURE_CONJ or o.lower() in CONJ_ADV for o in opts) and any(o.lower() in PREP_LIKE for o in opts):
        return ['GR.CONN.PREP_VS_CONJ'], 'mix'
    if len(a.split()) >= 2:
        return ['GR.CONN.PREP_PHRASE_MULTI'], None
    if a in TIME_PREPS and re.search(r'\b(\d|year|month|week|day|hour|minute|morning|afternoon|evening|monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december|noon|quarter|period|season|summer|winter|deadline)', stem, re.I):
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
        return 'QT.P5.VERB_FORM', ['GR.VERB.VOICE_PASSIVE']
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
        return 'QT.P5.WORD_FORM', ['GR.NONFIN.PARTICIPLE_ADJ']
    if tag == 'preposition':
        ns, k = prep_nodes(stem, ans, opts)
        return ('QT.P5.CONNECTOR_MIX' if k == 'mix' else 'QT.P5.PREP'), ns
    if tag == 'conjunction':
        ns, k = conj_nodes(stem, ans, opts)
        return ('QT.P5.CONNECTOR_MIX' if k in ('mix', 'adv') else 'QT.P5.CONJ'), ns
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
    elif t0 in P6_QT:
        prim = P6_QT[t0]
        if t0 == 'pronoun':
            gr.append('FD.READ.REFERENCE')
    else:
        prim = 'QT.P6.INDEPENDENT'
    return prim, ns + gr + [tx]


def p7_type(q, tags):
    t = q
    if 'sentence-insertion' in tags or re.search(r'positions marked \[1\]', t):
        return 'INSERTION'
    if 'vocabulary' in tags or re.search(r'closest in meaning', t, re.I):
        return 'SYNONYM'
    if re.search(r'mean when (he|she|they) (writes?|says?)|most likely mean', t, re.I):
        return 'INTENT'
    if 'not-question' in tags or re.search(r'\bNOT\b', t):
        return 'NOT_TRUE'
    if 'purpose' in tags or 'main-idea' in tags or re.search(r'\b(purpose|main (topic|idea|subject)|mainly (about|discuss)|primarily (about|discuss)|why was .* (written|sent))', t, re.I):
        return 'MAIN_PURPOSE'
    if re.search(r'\b(for whom|who most likely|who (is|are) .* most likely|most likely (work|an?|the) |intended (for|audience)|what (kind of|type of) (business|company|organi[sz]ation)|what (is|was) .* (job|occupation|profession|position)|what industry)', t, re.I):
        return 'INFER_WHO'
    if re.search(r'(most likely|probably) (do|happen|take place) next|will .* most likely (do|happen)|what will .* (probably|most likely)|what (is|are) .* (likely|expected) to (do|happen)', t, re.I):
        return 'INFER_NEXT'
    if re.search(r'\b(asked|requested|advised|encouraged|instructed|invited|reminded|told|required|expected|recommended) to\b|what (does|do|did) .* (ask|request|recommend|suggest|advise|instruct)\b.* to do|what .* (suggest|recommend)s? .* do', t, re.I):
        return 'REQUEST_ACTION'
    if 'inference' in tags or re.search(r'\b(suggested|implied|inferred|most likely|probably)\b', t, re.I):
        return 'INFERENCE'
    if re.search(r'\b(indicated|stated|true|mentioned|noted|said|reported)\b.*\babout\b|\bwhat is (indicated|stated|true|mentioned)\b', t, re.I):
        return 'TRUE_INDICATED'
    if re.search(r'^\s*why\b', t, re.I):
        return 'REASON'
    if re.search(r'^\s*(when|how much|how many|how long|how often|what time|on what (date|day)|by what date|what (date|day|year|percentage|amount|price|fee|discount))\b', t, re.I):
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


def tag_p7(qtext, tags, bundle_tx, doc_txs, kind):
    qt = p7_type(qtext, tags)
    group = QT_P7.get(qt, 'QT.P7.' + qt)
    ns = []
    x = p7x(qt, bundle_tx if kind != 'single' else doc_txs[0])
    if x:
        ns.append(x)
    if kind == 'single':
        ns.append(doc_txs[0])
    else:
        ns += [bundle_tx] + sorted(set(doc_txs))
    if qt == 'DETAIL_NUMBER' and any(t in ('TX.INVOICE', 'TX.SCHEDULE', 'TX.APP_FORM') for t in doc_txs):
        c = p7x('CALC_LOOKUP', next(t for t in doc_txs if t in ('TX.INVOICE', 'TX.SCHEDULE', 'TX.APP_FORM')))
        ns.append(c or 'QT.P7.CALC_LOOKUP')
    if 'cross-reference' in tags:
        cr = 'QT.P7X.CROSS_REF.' + ('TRIPLE' if kind == 'triple' else 'DOUBLE')
        if kind == 'single':
            cr = 'QT.P7.CROSS_REF'
        prim = cr
        ns = [group] + ns
    else:
        prim = group
    ns += PARA_HINT.get(qt, [])
    return prim, ns, qt


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
                        it['blank_n'] = blank[q['number']]
                        if q.get('text'):
                            it['stem'] = q['text']
                    else:
                        qtext = (q.get('text') or '').strip()
                        if not qtext:
                            skipped.append((pre, q['number'], 'P7 缺题干')); continue
                        prim, ns, _ = tag_p7(qtext, q['tags'], btx, doc_txs, kind)
                        it['q'] = qtext
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
                  '新增 explain_en（原英文解析）、src_tags（原题型标签）、source；无 difficulty_est/target_time_sec/distractor_reasons（build.py 用默认值）',
        'forms': ['MXT%02d' % t for t in range(1, 7)],
        'node_tagging': '规则粗打（work/convert_maximcuynat.py：原 tags + 题干/选项规则 + 场景关键词），未人工校对',
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
