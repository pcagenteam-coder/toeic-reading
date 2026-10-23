#!/usr/bin/env python3
"""kdeppaei/toeic-question-ocean（MIT，© 2026 Chun-Hsiung Luo）→ data/items_open_kdeppaei.json（工作包 A1）

输入：private_data/sources/github/kdeppaei_toeic-question-ocean/（本地副本，private_data/ 不进公开仓库）
- banks/question-bank*.js + question-annotations-v31.js：按版本顺序用 node 执行 → BUILTIN_BANK（1,107 题，作者原创）
- modules/part5-exercise-guides.js、modules/reading-exercise-guides.js：ESL Lounge Student 题（P5 120 + P6 120 + P7 96 = 336），
  原站条款禁止转载 → 整个模块不读入；另做 8-gram 文本比对，确认 banks 里没有 ESL Lounge 文本的副本
处理：只取 P5/P6/P7 → 统一 schema（与 items_open_maximcuynat 相同）→ 丢弃答案缺失/格式坏 → 与 pilot、maximcuynat、自身去重
     （题干/篇章文本归一化后完全相同或 3-gram Jaccard ≥ 0.8）→ 按 graph_v1 规则粗打节点（复用 work/convert_maximcuynat.py 的规则函数）
- 解析：原繁体中文 explanation → OpenCC t2s 简体 → explain_zh；原中文翻译 → translation_zh；v3.1 标注的英文证据句 → evidence_en
- form：非整套题，按 part 切成迷你卷（每卷 < 90 题，不会被 engine 当成整套模考）：P5 每卷 30 题（101–130）、
  P6 每卷 4 篇（131–146）、P7 每卷 ≤ 54 题（147 起，bundle 不拆）
用法：python3 data/items_open_kdeppaei_convert.py   （需要 node；opencc-python-reimplemented 可选，没有则保留繁体）
"""
import json, os, re, sys, subprocess, importlib.util, collections, random, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'private_data', 'sources', 'github', 'kdeppaei_toeic-question-ocean')
OUT = os.path.join(ROOT, 'data', 'items_open_kdeppaei.json')
LOG = os.path.join(ROOT, 'data', 'items_open_kdeppaei_log.json')
SOURCE = 'kdeppaei_mit'
DIFF = {'400': 2, '600': 3, '800': 4}   # 原作者难度档（目标分）→ difficulty_est 1–5

spec = importlib.util.spec_from_file_location('cm', os.path.join(ROOT, 'work', 'convert_maximcuynat.py'))
cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)
G = cm.G

try:
    import opencc
    _cc = opencc.OpenCC('t2s')
    t2s = _cc.convert
    T2S = 'OpenCC t2s'
except Exception:
    t2s = lambda s: s
    T2S = 'none（未装 opencc，保留繁体）'

ORDER = (['question-bank.js'] + ['question-bank-v%d.js' % v for v in range(15, 30)] + ['question-bank-v210.js', 'question-bank-v30.js',
         'question-annotations-v31.js'] + ['question-bank-v%d.js' % v for v in (31, 32, 33, 34, 40, 41, 42, 43, 44, 45, 46, 47, 50)])

NODE_DUMP = r"""
const fs=require('fs'),vm=require('vm');const [D,order,mods]=[process.argv[1],JSON.parse(process.argv[2]),process.argv[3]];
const all=fs.readdirSync(D+'/banks').filter(f=>f.startsWith('question-'));
const miss=all.filter(f=>!order.includes(f)); if(miss.length){console.error('unordered bank files',miss);process.exit(2);}
const ctx={window:{}};vm.createContext(ctx);const fileOf={};
for(const f of order){vm.runInContext(fs.readFileSync(D+'/banks/'+f,'utf8'),ctx,{filename:f});for(const q of ctx.window.BUILTIN_BANK) if(!fileOf[q.id]) fileOf[q.id]=f;}
const m={window:{}};vm.createContext(m);
for(const f of ['part5-exercise-guides.js','reading-exercise-guides.js']) vm.runInContext(fs.readFileSync(D+'/modules/'+f,'utf8'),m);
process.stdout.write(JSON.stringify({bank:ctx.window.BUILTIN_BANK.map(q=>Object.assign({},q,{_file:fileOf[q.id]})),annot:ctx.window.TOEIC_V31_ANNOTATION_COUNT,
 esl:{p5:m.window.TOEIC_PART5_EXERCISE_GUIDES,rd:m.window.TOEIC_READING_EXERCISE_GUIDES}}));
"""


def load_source():
    r = subprocess.run(['node', '-e', NODE_DUMP, SRC, json.dumps(ORDER)], capture_output=True, text=True)
    if r.returncode:
        sys.exit('node dump failed: ' + r.stderr)
    return json.loads(r.stdout)


# ---------- 文本工具 ----------
def words(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def norm(s):
    s = re.sub(r'-{3,}|_{3,}|\[\d\]|\(\d\)', ' ', s.lower())
    return ' '.join(re.findall(r"[a-z0-9']+", s))


def sh3(s):
    w = norm(s).split()
    return {' '.join(w[i:i + 3]) for i in range(len(w) - 2)} or {' '.join(w)}


def jacc(a, b):
    return len(a & b) / max(1, len(a | b))


def esl_ngrams(esl, n=8):
    out = set()
    def add(s):
        w = words(s or '')
        out.update(' '.join(w[i:i + n]) for i in range(len(w) - n + 1))
    for e in esl['p5']['exercises']:
        for q in e['questions']:
            add(q['prompt']); add(q.get('completedSentence'))
    for part in esl['rd'].values():
        for e in part['exercises']:
            for d in e['documents']:
                add(d.get('text')); add(d.get('completedText'))
                for q in d.get('questions', []):
                    add(q.get('prompt'))
    return out


def esl_count(esl):
    n5 = sum(len(e['questions']) for e in esl['p5']['exercises'])
    nr = {k: sum(len(d.get('questions', [])) for e in v['exercises'] for d in e['documents']) for k, v in esl['rd'].items()}
    return n5, nr


# ---------- P5 节点 ----------
CAT_TAG = [  # (类别关键词, maximcuynat 题型 tag)
    ('倒裝', 'inversion'), ('假設', 'conditional'), ('條件', 'conditional'), ('分詞構句', 'participle-clause'), ('分詞片語', 'participle-clause'),
    ('省略', 'reduced'), ('平行', 'parallel'), ('名詞子句', 'noun-clause'), ('關係', 'relative-clause'), ('whose', 'relative-clause'),
    ('同位語', 'noun-clause'), ('比較', 'comparative'), ('最高級', 'comparative'), ('代名詞', 'pronoun'), ('所有格', 'pronoun'),
    ('數量', 'quantifier'), ('限定詞', 'quantifier'), ('一致', 'subject-verb-agreement'), ('被動', 'passive-voice'),
    ('不定詞', 'gerund-infinitive'), ('動名詞', 'gerund-infinitive'), ('分詞形容詞', 'participle-adjective'), ('分詞', 'participle'),
    ('時態', 'verb-tense'), ('完成式', 'verb-tense'), ('動詞型態', 'verb-form'), ('動詞原形', 'verb-form'), ('be動詞', 'verb-form'),
    ('連接副詞', 'conjunction'), ('連接詞', 'conjunction'), ('子句', 'conjunction'), ('目的', 'conjunction'), ('讓步', 'conjunction'),
    ('原因片語', 'preposition'), ('例外', 'preposition'), ('介系詞', 'preposition'),
    ('詞性', 'word-form'), ('副詞位置', 'word-form'), ('形容詞補語', 'word-form'), ('可數名詞', 'word-form'),
    ('搭配', 'collocation'), ('固定', 'collocation'), ('字彙', 'vocabulary'), ('語意', 'vocabulary'), ('選擇', 'vocabulary'),
]
COLLO_PREP = re.compile(r'\b(of|for|with|to|in|on|at|from|about)\b')


def family(opts):
    """四个选项是否同一词族（词性题）"""
    ws = [o.lower().split()[-1] if o.strip() else o.lower() for o in opts]   # A2-QC：more careful → careful
    if any(' ' in w for w in ws):
        return False
    stem = min(ws, key=len)[:4]
    return sum(w.startswith(stem) for w in ws) >= 3


def p5_tag(q, stem, ans, opts):
    cat = q.get('category', ''); tags = set(q.get('tags') or [])
    for k, t in CAT_TAG:
        if k in cat:
            break
    else:
        t = None
    if t in (None, 'vocabulary', 'collocation') and family(opts) and t != 'collocation':
        t = 'word-form'
    if cat in ('副詞', '形容詞', '名詞', '動詞'):
        t = 'word-form' if family(opts) else 'vocabulary'
    if t is None:
        t = 'word-form' if family(opts) else 'vocabulary'
    return t


def tag_p5(q, stem, ans, opts):
    t = p5_tag(q, stem, ans, opts)
    a = ans.lower(); tags = set(q.get('tags') or [])
    NEG_FRONT = r'^\s*(rarely|seldom|never|not until|not only|at no time|only|hardly|little|under no|in no|nowhere|neither|nor|no sooner|scarcely|so)\b'
    VERB_OPTS = {'is', 'are', 'was', 'were', 'has', 'have', 'had', 'does', 'do', 'did'}
    if a in VERB_OPTS and sum(o.lower() in VERB_OPTS for o in opts) >= 3 and re.search(r'\b(either|neither|both|not only)\b', stem, re.I) \
            and t != 'inversion' or 'subject-verb' in tags and t != 'inversion':
        # A2：either/neither … or/nor + 动词 = 就近一致（主谓一致），不是连词题
        ns = ['GR.VERB.AGREE_SV'] + (['GR.CONN.CONJ_CORRELATIVE'] if re.search(r'\b(either|neither|both|not only)\b', stem, re.I) else [])
        return 'QT.P5.VERB_FORM', ns + cm.scenes(stem, top=1), 'subject-verb-agreement'
    if t == 'collocation' and family(opts) and any(o.lower().startswith('to ') or o.lower().endswith('ing') for o in opts):
        # A2：scheduled ------- (to begin/begin/began/beginning) 选项同词族 → 非谓语形式题
        pre = cm.pre_blank(stem)
        n = 'GR.NONFIN.TO_INF' if a.startswith('to ') or pre == 'to' else 'GR.NONFIN.GERUND' if a.endswith('ing') else \
            'GR.VERB.MODAL_BASE' if pre in ('will', 'can', 'must', 'should', 'may', 'might', 'would', 'could') else 'GR.VERB.VERB_PATTERN'
        return 'QT.P5.VERB_FORM', [n] + (['VO.COLLO.FIXED_PHRASE'] if a.startswith('to ') else []) + cm.scenes(stem, top=1), 'gerund-infinitive'
    if t == 'inversion':
        neg = 'negative-fronting' in tags or re.search(NEG_FRONT, stem, re.I)
        if not neg and (re.search(r'^(had|should|were)\b', a) or re.match(r'\s*-------\s', stem) and a in ('had', 'should', 'were') or 'conditional-inversion' in tags):
            prim, ns = 'QT.P5.VERB_FORM', ['GR.VERB.CONDITIONAL_INVERSION']
        else:
            prim, ns = 'QT.P5.PAIR_GRAMMAR', ['GR.SPECIAL.INVERSION_NEG']
    elif t == 'conditional' and a in ('unless', 'if', 'provided', 'providing', 'as long as', 'in case', 'provided that', 'only if', 'even if', 'once'):
        prim, ns = cm.gram_nodes('conjunction', stem, ans, opts)   # A2-QC：选连词（unless/if）是连词题，不是假设语气
    elif t == 'conditional':
        dem = re.search(r'\b(ask|asked|asks|request\w*|requir\w*|recommend\w*|suggest\w*|insist\w*|demand\w*|propos\w*|urg\w*|essential|imperative|important|vital|necessary|mandatory|advis\w*)\s+that\b', stem, re.I)
        prim, ns = 'QT.P5.VERB_FORM', ['GR.VERB.SUBJUNCTIVE_DEMAND' if ('要求' in q.get('category', '') or 'mandative-subjunctive' in tags or dem) else 'GR.VERB.CONDITIONAL_INVERSION']   # A2-QC：asked that + 原形 = 要求类虚拟
    elif t == 'participle-clause':
        prim, ns = 'QT.P5.VERB_FORM', ['GR.NONFIN.PARTICIPLE_CLAUSE', 'FD.SENT.CLAUSE_COUNT']
    elif t == 'participle':
        clause = re.match(r'\s*-------\s+[^,]{2,80},', stem)   # A2-QC：句首分词短语 + 逗号 = 分词构句
        prim, ns = 'QT.P5.VERB_FORM', ['GR.NONFIN.PARTICIPLE_CLAUSE' if clause else 'GR.NONFIN.PARTICIPLE_MODIFIER']
    elif t == 'reduced':
        if re.search(r"\b(once|while|when|whenever|unless|if|although|though|until|before|after|as|than)\s*-------", stem, re.I):
            prim, ns = 'QT.P5.PAIR_GRAMMAR', ['GR.SPECIAL.ELLIPSIS', 'GR.NONFIN.PARTICIPLE_CLAUSE']   # 连词 + 分词（Once approved / While installing）
        else:   # A2-QC：Employees ------- at …（省略关系词的后置分词）= 分词修饰，不是省略结构
            prim, ns = 'QT.P5.VERB_FORM', ['GR.NONFIN.PARTICIPLE_MODIFIER']
    elif t == 'parallel':
        prim, ns = 'QT.P5.PAIR_GRAMMAR', ['GR.SPECIAL.PARALLEL']
    elif t == 'noun-clause':
        prim, ns = 'QT.P5.RELATIVE', ['GR.REL.NOUN_CLAUSE']
    elif t == 'verb-form':
        prim, ns = 'QT.P5.VERB_FORM', ['GR.VERB.MODAL_BASE' if re.search(r'\b(will|can|must|should|may|could|would)\s+-------', stem, re.I) else 'GR.VERB.VERB_PATTERN']
    elif t == 'collocation':
        pre = cm.pre_blank(stem); post = cm.post_blank(stem)
        if ' ' not in a and a in ('of', 'for', 'with', 'to', 'in', 'on', 'at', 'from', 'about', 'by'):
            prim, ns = 'QT.P5.PREP', ['VO.COLLO.ADJ_PREP' if pre and cm.pos_of(pre) == 'adj' or pre in cm.ADJ_PREP_HEADS else
                                      'VO.COLLO.BE_PP_PREP' if pre.endswith('ed') else 'VO.COLLO.VERB_PREP']   # A2-QC：familiar/similar with = 形容词+介词
        else:
            n = cm.lex_node(stem, ans, opts)
            prim, ns = 'QT.P5.VOCAB', ['VO.COLLO.FIXED_PHRASE'] + ([n] if n else [])
    else:
        prim, ns = cm.gram_nodes(t, stem, ans, opts)
        if prim is None:
            n = cm.lex_node(stem, ans, opts)
            prim, ns = 'QT.P5.VOCAB', [n] if n else []
    return prim, ns + cm.scenes(stem, top=1), t


def p7_diff(kind, nwords, qt, cross, src):
    """A2：P7 难度重估。原库 P7 没有 400 档、800 档占 2/3（三句话的单篇细节题也标 800），直接映射会把 P7 整体抬到 4。
    规则分 = 篇章形态 + 设问类型 + 篇幅；再与原档 2:1 加权，四舍五入到 1–5。"""
    r = cm.p7_rule_diff(kind, nwords, qt, cross)
    d = DIFF.get(str(src), 3)
    return max(1, min(5, int((2 * r + d) / 3 + 0.5)))


# ---------- P6 ----------
P6_TAG_FROM_TAGS = [('sentence-insertion', 'sentence-insertion'), ('word-form', 'word-form'), ('verb-form', 'verb-tense'),
                    ('present-perfect', 'verb-tense'), ('passive', 'passive-voice'), ('gerund', 'gerund-infinitive'),
                    ('connector', 'conjunction'), ('adverb', 'word-form'), ('adjective', 'word-form'), ('vocabulary', 'vocabulary')]


def p6_srctags(q, ans, opts):
    tags = q.get('tags') or []
    if all(len(o.split()) >= 4 for o in opts):
        return ['sentence-insertion']
    lo = [o.lower().rstrip(',') for o in opts]
    REL = {'who', 'whom', 'whose', 'which', 'that', 'where', 'when', 'what'}
    if ans.lower() in REL and sum(o in REL for o in lo) >= 3:
        return ['relative-clause']   # A2：who/whom/whose/which 不是词性题
    QUANT = {'every', 'each', 'all', 'another', 'other', 'others', 'each of', 'many', 'much', 'few', 'little', 'several', 'any', 'some', 'most'}
    if ans.lower() in QUANT and sum(o in QUANT for o in lo) >= 3:
        return ['quantifier']
    if ans.lower().rstrip(',') in cm.CONJ_ADV or sum(o in cm.CONJ_ADV or o in cm.PURE_CONJ or o in cm.PREP_LIKE for o in lo) >= 2:
        return ['conjunction']
    if len({cm.pos_of(o) for o in opts} - {None}) >= 3:
        return ['word-form']   # A2：strengthen/strength/strongly/stronger 词性各异 → 词性题
    if family(opts):
        if any(re.search(r'\b(ed|ing)$', o) for o in lo) and any(o.endswith(('s',)) for o in lo) and cm.pos_of(ans) not in ('adj', 'adv', 'noun'):
            return ['verb-tense']
        return ['word-form']
    if all(re.fullmatch(r"(has|have|had|will|is|are|was|were|be|been|being|would)?\s?\w+(ed|en|ing|s)?( \w+)?", o.lower()) for o in opts) and \
            len({o.split()[-1][:4].lower() for o in opts}) == 1:
        return ['verb-tense']
    PREPS1 = ('by', 'at', 'from', 'among', 'during', 'within', 'until', 'on', 'in', 'for', 'of', 'with', 'to', 'throughout', 'despite', 'without', 'through')
    if ' ' not in ans and ans.lower() in PREPS1 and sum(o.lower() in PREPS1 for o in opts) >= 3:
        return ['preposition']
    if ans.lower() in ('it', 'they', 'them', 'their', 'its', 'this', 'these', 'those', 'he', 'she', 'his', 'her', 'we', 'our', 'us'):
        return ['pronoun']
    for k, t in P6_TAG_FROM_TAGS:
        if k in tags and not (t == 'sentence-insertion' and any(len(o.split()) < 4 for o in opts)):   # A2-QC：组级 tag，选项不是句子就不是插入题
            return [t]
    return ['vocabulary']


def build_p6(qs):
    """返回 (header, text_with_[n], {qid: n}) 或 (None, reason)"""
    qs = list(qs)
    ps = [q['passage'] for q in qs]
    blanks = lambda s: re.findall(r'_{3,}', s)
    # 形式 D：(n) _____ / _____ (n)
    if len(set(ps)) == 1 and re.search(r'\(\d\)\s*_{3,}|_{3,}\s*\(\d\)', ps[0]):
        t = ps[0]
        t = re.sub(r'\((\d)\)\s*_{3,}|_{3,}\s*\((\d)\)', lambda m: '[%s]' % (m.group(1) or m.group(2)), t)
        mp = {}
        for q in qs:
            m = re.search(r'blank \((\d)\)', q['prompt'])
            if not m:
                return None, 'P6 题干未标空号'
            mp[q['id']] = int(m.group(1))
        return t, mp
    # 形式 E：逐题揭示（v2.8）：第 k 题的篇章只在第 k 空写 "(k) _____"，其余空已填答案（部分带 "(j) " 标号）
    if len(set(ps)) == len(qs) and all(re.search(r'\(\d\)\s*_{3,}', p) for p in ps):
        mp, filled, ctx = {}, [], []
        for q, p in zip(qs, ps):
            m = re.search(r'blank \((\d)\)', q['prompt'])
            if not m:
                return None, 'P6 题干未标空号'
            k = int(m.group(1)); mp[q['id']] = k
            p2 = re.sub(r'\((?!%d\))\d\)\s*' % k, '', p)
            parts = re.split(r'\(%d\)\s*_{3,}' % k, p2)
            if len(parts) != 2:
                return None, 'P6 逐题揭示篇章空位 (%d) 不唯一' % k
            L, R = parts; ans = q['choices'][q['answer']]
            if ans.endswith(('.', '!', '?')) and R.startswith('.'):
                R = R[1:]
            filled.append(L + ans + R); ctx.append((k, L[-30:], ans, R[:25]))
        base = max(filled, key=len)   # 前面的题看不到后面才插入的句子 → 用最完整的一版
        spans = []
        for k, l, ans, r in ctx:
            i = base.find(l + ans + r)
            if i < 0 or base.find(l + ans + r, i + 1) >= 0:
                return None, 'P6 逐题揭示无法唯一定位空位 (%d)' % k
            spans.append((i + len(l), i + len(l) + len(ans), k))
        out, pos = '', 0
        for s_, e_, k in sorted(spans):
            out += base[pos:s_] + '[%d]' % k; pos = e_
        return out + base[pos:], mp
    # 形式 A：每题一段（同信头不同片段，各含 1 空）→ 信头 + 片段按题序拼接
    if len(set(ps)) == len(qs) and all(len(blanks(p)) == 1 for p in ps):
        has_h = ['\n\n' in p for p in ps]
        if all(has_h):
            heads = [p.partition('\n\n')[0] for p in ps]; bodies = [p.partition('\n\n')[2] for p in ps]
            if len(set(heads)) != 1:
                return None, 'P6 片段信头不一致'
            head = heads[0] + '\n\n'
        elif not any(has_h):
            head, bodies = '', ps
        else:
            return None, 'P6 片段信头不一致'
        # A2-QC：部分题组每个片段都重复同一句开场白（G05–G07）→ 只在第一个片段保留
        cp = os.path.commonprefix([b.strip() for b in (bodies[1:] if len(bodies) > 2 else bodies)]) if len(bodies) > 1 else ''
        cut = max((m.end() for m in re.finditer(r'(?<![A-Z]\.[A-Z])(?<!\b[A-Z])(?<!Mr)(?<!Ms)(?<!Dr)[.!?]\s+(?=[A-Z])', cp + 'X')), default=0)
        if cut and not re.search(r'_{3,}', cp[:cut]):
            bodies = [bodies[0]] + [b.strip()[cut:] for b in bodies[1:]]
        body = ' '.join(bodies[i].strip().replace(blanks(bodies[i])[0], '[%d]' % (i + 1), 1) for i in range(len(qs)))
        return head + body, {q['id']: i + 1 for i, q in enumerate(qs)}
    # 形式 B/C：同一篇章 + 裸 _____；用每题题干句定位空位（篇章缺空时按题干把答案词替换成空）
    if len(set(ps)) == 1:
        t = ps[0]; mp = {}; spans = []
        for q in qs:
            pr = q['prompt']
            if pr.count('_____') != 1 and len(re.findall(r'_{3,}', pr)) != 1:
                return None, 'P6 题干无空位'
            left, right = re.split(r'_{3,}', pr, maxsplit=1)
            ans = q['choices'][q['answer']]
            rx_blank = re.escape(left.strip()[-40:]) + r'\s*_{3,}\s*' + re.escape(right.strip()[:30])
            rx_ans = re.escape(left.strip()[-40:]) + r'\s*' + re.escape(ans) + r'\s*' + re.escape(right.strip()[:30])
            m = re.search(rx_blank, t)
            if m:
                s = m.start() + m.group(0).index('_')
                e = s + len(re.match(r'_+', t[s:]).group(0))
            else:
                m = re.search(rx_ans, t)
                if not m:
                    return None, 'P6 无法在篇章中定位空位'
                s = m.start() + m.group(0).index(ans, len(left.strip()[-40:]))
                e = s + len(ans)
            spans.append((s, e, q['id']))
        spans.sort()
        if len({s for s, _, _ in spans}) != len(spans):
            return None, 'P6 空位定位重复'
        out, pos = '', 0
        for i, (s, e, qid) in enumerate(spans, 1):
            out += t[pos:s] + '[%d]' % i; pos = e; mp[qid] = i
        out += t[pos:]
        if re.search(r'_{3,}', out):
            return None, 'P6 篇章有多余空位'
        return out, mp
    return None, 'P6 未知题组结构'


# ---------- P7 ----------
TITLE_TX = [
    (r'e-?mail|reply|customer message|correspondence', 'TX.EMAIL'), (r'letter', 'TX.LETTER'), (r'memo', 'TX.MEMO'),
    (r'text message|message chain|message', 'TX.TEXT_MSG'), (r'chat|discussion|thread', 'TX.CHAT'),
    (r'invoice|receipt|bill|order summary|estimate|quote|price list|statement', 'TX.INVOICE'),
    (r'schedule|agenda|itinerary|timetable|trains|calendar|program', 'TX.SCHEDULE'),
    (r'form|survey|application|registration|request', 'TX.APP_FORM'), (r'advertisement|\bad\b|flyer|coupon|offer|studio', 'TX.AD'),
    (r'job|position|opening|vacanc|career', 'TX.JOB_POSTING'), (r'article|news|press|report|update|newsletter|study|research', 'TX.ARTICLE'),
    (r'web ?page|website|product page|online|faq', 'TX.WEB'), (r'review|feedback|comment', 'TX.REVIEW'),
    (r'instruction|guide|procedure|manual|steps|policy|rules|terms|agreement|contract|note|excerpt', 'TX.INSTRUCTIONS'),
    (r'notice|announcement|bulletin|sign|label|alert|pilot', 'TX.NOTICE'),
]
CAT_TX = [('郵件', 'TX.EMAIL'), ('信件', 'TX.LETTER'), ('信', 'TX.LETTER'), ('備忘', 'TX.MEMO'), ('訊息', 'TX.TEXT_MSG'),
          ('廣告', 'TX.AD'), ('職缺', 'TX.JOB_POSTING'), ('徵才', 'TX.JOB_POSTING'), ('新聞', 'TX.ARTICLE'), ('文章', 'TX.ARTICLE'),
          ('報告', 'TX.ARTICLE'), ('網頁', 'TX.WEB'), ('評論', 'TX.REVIEW'), ('表單', 'TX.APP_FORM'), ('時刻', 'TX.SCHEDULE'),
          ('日程', 'TX.SCHEDULE'), ('議程', 'TX.SCHEDULE'), ('帳單', 'TX.INVOICE'), ('估價', 'TX.INVOICE'), ('收據', 'TX.INVOICE'),
          ('訂單確認', 'TX.INVOICE'), ('訂單', 'TX.EMAIL'), ('確認', 'TX.EMAIL'), ('政策', 'TX.INSTRUCTIONS'), ('規則', 'TX.INSTRUCTIONS'), ('流程', 'TX.INSTRUCTIONS'),
          ('規範', 'TX.INSTRUCTIONS'), ('公告', 'TX.NOTICE'), ('通知', 'TX.NOTICE')]
KNOWN_TITLE = re.compile(r'^(document \d.*|(e-?mail|text message|chat message|customer message|form instructions|reply|memo|notice|'
                         r'announcement|article|letter|advertisement|schedule|invoice|receipt|review|web ?page|faq excerpt|project update|'
                         r'catalog production note|staff notice|building notice|message)( \d)?(:.*)?)$', re.I)


def is_title(line):
    l = line.strip()
    if not l or len(l.split()) > 9 or l.endswith(('.', '?', ',')):
        return False
    if KNOWN_TITLE.match(l):
        return True
    letters = re.sub(r'[^A-Za-z]', '', l)
    return len(letters) >= 3 and letters.isupper() and not re.match(r'^(From|To|Subject|Date)\s*:', l)


def tx_of(title, text, cat=''):
    for k, tx in CAT_TX:   # 单篇：原作者的中文类别最可靠（多篇调用时 cat 为空）
        if cat and k in cat:
            return tx
    t = (title or '').lower()
    t = re.sub(r'^document \d\s*[-—:]*\s*', '', t)
    for rx, tx in TITLE_TX:
        if re.search(rx, t):
            return tx
    if re.search(r'\bmemo(randum)?\b', text[:80], re.I):
        return 'TX.MEMO'
    if re.search(r'^\s*(From|To|Subject)\s*:', text, re.M):
        return 'TX.EMAIL'
    if len(re.findall(r'^\s*(\d{1,2}:\d{2}\s*[-—]\s*)?(?!(?:From|To|Subject|Date|Re|Cc|Note|Time|Client|Items|Delivery|Total|Tax)\b)[A-Z][a-z]+( [A-Z][a-z]+)?:\s', text, re.M)) >= 3:
        return 'TX.TEXT_MSG' if re.search(r'^\s*\d{1,2}:\d{2}', text, re.M) else 'TX.CHAT'
    for k, tx in CAT_TX:
        if k in cat:
            return tx
    return 'TX.NOTICE'


def split_docs(passage):
    blocks = re.split(r'\n\s*\n', passage.strip())
    docs = []
    for blk in blocks:
        lines = blk.split('\n')
        l0 = lines[0].strip()
        solo = len(lines) == 1 and 0 < len(l0.split()) <= 5 and not l0.endswith(('.', '?', '!', ',', ':')) and l0[0].isupper() and not re.search(r'\d{1,2}:\d{2}', l0)
        if is_title(lines[0]) or solo or not docs:
            title = l0 if (is_title(lines[0]) or solo) else ''
            rest = '\n'.join(lines[1:]) if title else blk
            docs.append([title, rest.strip()])
        else:
            docs[-1][1] = (docs[-1][1] + '\n\n' + blk).strip()
    # 只有标题没正文的块（例如 "E-mail\n\nTo: ..."）已在上面合并；去掉空文档
    return [d for d in docs if d[1] or d[0]]


def main():
    data = load_source()
    bank, esl = data['bank'], data['esl']
    n5, nr = esl_count(esl)
    eg = esl_ngrams(esl)
    log = {'excluded_esl_module': {'P5': n5, 'P6': nr.get('6'), 'P7': nr.get('7'), 'total': n5 + sum(nr.values())},
           'bank_total': len(bank), 'annotations_applied': data['annot'], 'non_reading': 0, 'esl_text_hits': [], 'dropped_format': [],
           'dropped_dup': [], 'near_dup_report': []}
    reading = [q for q in bank if str(q['part']) in ('5', '6', '7')]
    log['non_reading'] = len(bank) - len(reading)
    log['reading_by_part'] = dict(collections.Counter('P' + str(q['part']) for q in reading))

    # ---- ESL Lounge 文本残留检查（8-gram 覆盖率 ≥ 30% 视为来源可疑）----
    suspicious = set()
    seen_p = set()
    for q in reading:
        for t in (q['prompt'], q.get('passage') if q.get('passage') not in seen_p else ''):
            w = words(re.sub(r'_{3,}', ' ', t or '')); g = [' '.join(w[i:i + 8]) for i in range(len(w) - 7)]
            if len(g) >= 3 and sum(x in eg for x in g) / len(g) >= 0.3:
                suspicious.add(q.get('groupId') or q['id']); log['esl_text_hits'].append(q['id'])
        seen_p.add(q.get('passage'))

    # ---- 格式校验 ----
    def bad(q):
        ch = q.get('choices')
        if not isinstance(ch, list) or len(ch) != 4 or any(not isinstance(c, str) or not c.strip() for c in ch):
            return '选项不是 4 个非空字符串'
        if len({c.strip().lower() for c in ch}) != 4:
            return '选项重复'
        a = q.get('answer')
        if not isinstance(a, int) or not 0 <= a <= 3:
            return '答案缺失/越界'
        if q.get('answerAudit') and str(q['answerAudit']).strip().lower() != ch[a].strip().lower() and q['answerAudit'] not in ch[a]:
            return '答案与 answerAudit 不一致'
        if not (q.get('prompt') or '').strip():
            return '题干为空'
        return None

    items, bundles = [], []
    groups = collections.OrderedDict()
    for q in reading:
        p = int(q['part'])
        key = q.get('groupId') if p in (6, 7) else None
        if p in (6, 7) and not key:
            log['dropped_format'].append({'id': q['id'], 'reason': 'P6/P7 无 groupId'}); continue
        if (key or q['id']) in suspicious:
            continue
        why = bad(q)
        if p in (6, 7) and not (q.get('passage') or '').strip():
            why = why or '缺篇章'
        if why:
            log['dropped_format'].append({'id': q['id'], 'reason': why}); continue
        if p == 5:
            stem = re.sub(r'_{3,}', '-------', q['prompt']).strip()
            if stem.count('-------') != 1:
                log['dropped_format'].append({'id': q['id'], 'reason': 'P5 题干空位数 ≠ 1'}); continue
            items.append(('P5', q, stem))
        else:
            groups.setdefault((p, key), []).append(q)

    # P6 题目质量：答案是篇章里的名词细节（不是填空考点）→ 丢弃
    def p6_odd(q):
        opts = q['choices']
        return all(re.fullmatch(r'[A-Z][a-z]+', o) or o.lower() in q['passage'].lower() for o in opts) and \
            sum(o.lower() in q['passage'].lower() for o in opts) >= 3

    p6_bundles, p7_bundles = [], []
    for (p, gid), qs in groups.items():
        if p == 6:
            keep = []
            for q in qs:
                if p6_odd(q):
                    log['dropped_format'].append({'id': q['id'], 'reason': 'P6 选项是篇章原词（非填空考点，题目设计坏）'})
                else:
                    keep.append(q)
            if not keep:
                continue
            # 篇章若缺被丢题对应空位，仍按剩余题定位
            text, mp = build_p6(keep)
            if text is None:
                log['dropped_format'] += [{'id': q['id'], 'reason': mp} for q in keep]; continue
            if sorted(mp.values()) != list(range(1, len(keep) + 1)) and len(set(mp.values())) != len(keep):
                log['dropped_format'] += [{'id': q['id'], 'reason': 'P6 空号与题数不符'} for q in keep]; continue
            if len(re.findall(r'\[\d\]', text)) != len(keep):
                log['dropped_format'] += [{'id': q['id'], 'reason': 'P6 篇章空位数与题数不符'} for q in keep]; continue
            p6_bundles.append((gid, keep, text, mp))
        else:
            ps = {q['passage'] for q in qs}
            if len(ps) != 1:
                log['dropped_format'] += [{'id': q['id'], 'reason': 'P7 同组篇章不一致'} for q in qs]; continue
            p7_bundles.append((gid, qs, qs[0]['passage']))

    # ---- 去重（pilot + maximcuynat + 自身）----
    refs = []
    for path, tag in (('data/items_pilot_v1.json', 'pilot'), ('data/items_open_maximcuynat.json', 'maximcuynat')):
        d = json.load(open(os.path.join(ROOT, path), encoding='utf-8'))
        for i in d['items']:
            if i['part'] == 5:
                refs.append((tag, i['id'], 'P5', norm(i.get('stem') or '')))
            elif i['part'] == 7:
                refs.append((tag, i['id'], 'Q', norm(i.get('q') or '')))
        for b in d['bundles']:
            refs.append((tag, b['bundle_id'], 'PASSAGE', norm(' '.join(x.get('text', '') for x in b['docs']))))
    ref_sh = [(t, i, k, n, sh3(n)) for t, i, k, n in refs]

    def dup_of(kind, text):
        n = norm(text); s = sh3(text)
        for t, i, k, rn, rs in ref_sh:
            if k != kind:
                continue
            if n == rn:
                return '%s:%s（归一化后完全相同）' % (t, i)
            if kind != 'Q' and len(s) >= 5 and jacc(s, rs) >= 0.8:
                return '%s:%s（3-gram J=%.2f）' % (t, i, jacc(s, rs))
        return None

    seen5 = []
    p5_keep = []
    for _, q, stem in items:
        d = dup_of('P5', stem)
        if not d:
            n = norm(stem); s = sh3(stem)
            for sid, sn, ss, sopts in seen5:
                if n == sn and sopts == sorted(q['choices']):
                    d = 'kdeppaei:%s（自身重复：题干+选项相同）' % sid; break
                if n == sn or jacc(s, ss) >= 0.8:
                    log['near_dup_report'].append({'id': q['id'], 'similar_to': sid, 'J': round(jacc(s, ss), 2), 'action': '保留（选项/考点不同）' if sopts != sorted(q['choices']) else '剔除'})
                    if sopts == sorted(q['choices']):
                        d = 'kdeppaei:%s（自身近似重复 J=%.2f，选项相同）' % (sid, jacc(s, ss)); break
        if d:
            log['dropped_dup'].append({'id': q['id'], 'dup_of': d}); continue
        seen5.append((q['id'], norm(stem), sh3(stem), sorted(q['choices'])))
        p5_keep.append((q, stem))

    seenP = []
    def dedup_bundle(gid, qs, text):
        d = dup_of('PASSAGE', text)
        if not d:
            s = sh3(text)
            for sg, ss in seenP:
                if jacc(s, ss) >= 0.8:
                    d = 'kdeppaei:%s（自身近似重复 J=%.2f）' % (sg, jacc(s, ss)); break
        if d:
            log['dropped_dup'] += [{'id': q['id'], 'dup_of': d} for q in qs]
            return False
        seenP.append((gid, sh3(text)))
        return True
    p6_bundles = [b for b in p6_bundles if dedup_bundle(b[0], b[1], re.sub(r'\[\d\]', ' ', b[2]))]
    p7_bundles = [b for b in p7_bundles if dedup_bundle(b[0], b[1], b[2])]

    # ---- 组装 ----
    def ez(q):
        return t2s((q.get('explanation') or '').strip())

    def extra(q):
        o = {}
        tr = (q.get('translation') or '').strip()
        if tr and not re.match(r'^選出', tr):
            o['translation_zh'] = t2s(tr)
        if q.get('evidence'):
            o['evidence_en'] = q['evidence']
        return o

    def shuf(q):
        """原库正确项绝大多数在 A（P7 91%），app 不洗牌 → 按题 id 定种子确定性洗牌；[1]–[4] 位置题保持原序。
        choiceNotes（逐选项点评）随选项一起移动，错误项点评 → distractor_reasons。"""
        opts = [o.strip() for o in q['choices']]; notes = q.get('choiceNotes') if isinstance(q.get('choiceNotes'), list) and len(q['choiceNotes']) == 4 else None
        perm = [0, 1, 2, 3]
        if not all(re.fullmatch(r'\[\d\]', o) for o in opts):
            random.Random(hashlib.sha1(q['id'].encode()).hexdigest()).shuffle(perm)
        o2 = [opts[i] for i in perm]; a2 = perm.index(q['answer'])
        dr = {}
        if notes:
            for L, i in zip('ABCD', perm):
                if i != q['answer'] and notes[i]:
                    dr[L] = {'why_zh': t2s(notes[i])}
        return o2, a2, dr

    out_items, out_bundles, forms = [], [], []
    # P5：每卷 30 题
    for k, (q, stem) in enumerate(p5_keep):
        form = 'KDP5-%02d' % (k // 30 + 1); qnum = 101 + k % 30
        opts, a, dr = shuf(q)
        prim, ns, t = tag_p5(q, stem, opts[a], opts)
        it = {'id': 'KDP-' + q['id'], 'part': 5, 'form': form, 'qnum': qnum, 'stem': stem, 'options': opts, 'answer': a,
              'answer_letter': 'ABCD'[a], 'node': prim, 'node_ids': cm.uniq([prim] + ns), 'explain_en': '', 'explain_zh': ez(q),
              'src_tags': [t] + [x for x in (q.get('tags') or []) if x != t], 'src_id': q['id'], 'src_category': t2s(q.get('category', '')),
              'difficulty_src': q.get('difficulty'), 'difficulty_est': DIFF.get(str(q.get('difficulty')), 3), 'template_id': None, 'source': SOURCE, 'format_version': 'current'}
        it.update(extra(q))
        if dr:
            it['distractor_reasons'] = dr
        out_items.append(it)
    # P6：每卷 4 篇
    for k, (gid, qs, text, mp) in enumerate(p6_bundles):
        form = 'KDP6-%02d' % (k // 4 + 1); base = 131 + (k % 4) * 4
        hdr, body = cm.split_header(text)
        title = ''
        lines = body.split('\n')
        if not hdr and lines and is_title(lines[0]) or (not hdr and lines and len(lines[0].split()) <= 6 and not lines[0].strip().endswith(('.', ',', ':', '?')) and len(lines) > 1):
            title, body = lines[0].strip(), '\n'.join(lines[1:]).strip()
            if not hdr:   # A2-QC：标题行之后才是 To/From/Subject 信头（G34）
                hdr, body = cm.split_header(body)
        tx = tx_of(title, text, qs[0].get('category', ''))
        if hdr and tx == 'TX.NOTICE' and re.search(r'^Subject:', hdr, re.M):
            tx = 'TX.MEMO' if re.search(r'memo', title, re.I) or not re.search(r'e-?mail', title, re.I) else 'TX.EMAIL'
        bid = 'KDP-' + gid
        order = sorted(qs, key=lambda q: mp[q['id']])
        qn = [base + mp[q['id']] - 1 for q in order]
        doc = {'doc_type': tx, 'title': title or {'TX.EMAIL': 'E-mail', 'TX.MEMO': 'Memo', 'TX.LETTER': 'Letter'}.get(tx, 'Notice')}
        if hdr:
            doc['header'] = hdr
        doc['text'] = body
        bsc = cm.scenes(text)
        out_bundles.append({'bundle_id': bid, 'part': 6, 'form': form, 'kind': 'single', 'text_type': tx, 'docs': [doc], 'qnums': qn,
                            'node_ids': cm.uniq([tx] + bsc), 'refer_to': 'Questions %d-%d refer to the following text.' % (qn[0], qn[-1]),
                            'format_version': 'current', 'source': SOURCE, 'src_group': gid, 'blank_marker': '[n] = 第 n 个空格（显示时替换为 -------）'})
        alltext = re.sub(r'\[(\d)\]', lambda m: '{{%d}}' % (base + int(m.group(1)) - 1), text)
        for q, n in zip(order, qn):
            opts, a, dr = shuf(q)
            stags = p6_srctags(q, opts[a], opts)
            prim, ns = cm.tag_p6({'tags': stags}, alltext, n, opts[a], opts, tx)
            it = {'id': 'KDP-' + q['id'], 'part': 6, 'form': form, 'qnum': n, 'bundle_id': bid, 'options': opts, 'answer': a,
                  'answer_letter': 'ABCD'[a], 'blank_n': mp[q['id']], 'node': prim, 'node_ids': cm.uniq([prim] + ns + bsc[:1]),
                  'explain_en': '', 'explain_zh': ez(q), 'src_tags': stags + (q.get('tags') or []), 'src_id': q['id'],
                  'difficulty_src': q.get('difficulty'), 'difficulty_est': DIFF.get(str(q.get('difficulty')), 3), 'template_id': None, 'source': SOURCE, 'format_version': 'current'}
            it.update(extra(q))
            if dr:
                it['distractor_reasons'] = dr
            out_items.append(it)
    # P7：单篇在前、多篇在后；每卷 ≤ 54 题，bundle 不拆
    p7_rows = []
    for gid, qs, passage in p7_bundles:
        cat = qs[0].get('category', '')
        tg = qs[0].get('tags') or []
        want = 3 if '三篇' in cat or 'triple-passage' in (qs[0].get('tags') or []) else 2 if '雙篇' in cat or 'double-passage' in (qs[0].get('tags') or []) else None
        if want is None and ('單篇' in cat or 'single-passage' in tg):
            want = 1
        if want == 1:
            l0, _, rest = passage.strip().partition('\n')
            solo = rest.startswith('\n') and len(l0.split()) <= 6 and not l0.strip().endswith(('.', '?', '!', ',', ':')) and not re.match(r'^(From|To|Subject|Date)\s*:', l0)
            docs = [[l0.strip(), rest.strip()]] if (is_title(l0) or solo) and rest.strip() else [['', passage.strip()]]
        else:
            docs = split_docs(passage)
        if want and len(docs) != want:
            log.setdefault('p7_split_mismatch', []).append({'group': gid, 'expected': want, 'found': len(docs)})
        n = len(docs)
        kind = {1: 'single', 2: 'double', 3: 'triple'}.get(n)
        if not kind:   # 拆不出 1–3 篇：整段当单篇
            docs = [['', passage.strip()]]; kind = 'single'
        txs = [tx_of(t, x, cat if kind == 'single' else '') for t, x in docs]
        p7_rows.append((0 if kind == 'single' else 1, gid, qs, docs, txs, kind))
    p7_rows.sort(key=lambda r: r[0])
    fno, used = 1, 0
    for _, gid, qs, docs, txs, kind in p7_rows:
        if used + len(qs) > 54:
            fno += 1; used = 0
        form = 'KDP7-%02d' % fno
        qn = list(range(147 + used, 147 + used + len(qs))); used += len(qs)
        btx = txs[0] if kind == 'single' else {'double': 'TX.DOUBLE', 'triple': 'TX.TRIPLE'}[kind]
        bid = 'KDP-' + gid
        odocs = []
        for (title, x), tx in zip(docs, txs):
            hdr, body = cm.split_header(x)
            d = {'doc_type': tx, 'title': re.sub(r'^DOCUMENT \d\s*[-—:]\s*', '', title, flags=re.I).strip() or tx.split('.')[1].title().replace('_', ' ')}
            if hdr:
                d['header'] = hdr
            d['text'] = body
            odocs.append(d)
        alltext = '\n'.join(x for _, x in docs)
        bsc = cm.scenes(alltext)
        out_bundles.append({'bundle_id': bid, 'part': 7, 'form': form, 'kind': kind, 'text_type': btx, 'docs': odocs, 'qnums': qn,
                            'node_ids': cm.uniq(([btx] if kind != 'single' else []) + txs + bsc),
                            'refer_to': 'Questions %d-%d refer to the following %s.' % (qn[0], qn[-1], 'text' if kind == 'single' else 'texts'),
                            'format_version': 'current', 'source': SOURCE, 'src_group': gid})
        for q, n in zip(qs, qn):
            opts, a, dr = shuf(q)
            tags = list(q.get('tags') or [])
            if 'cross-document' in tags and 'cross-reference' not in tags:
                tags.append('cross-reference')
            # 原 tag 常对整组打，单题题型以题干为准
            need = {'inference': r'suggest|impl|infer|likely|probabl', 'sentence-insertion': r'position', 'vocabulary': r'closest in meaning',
                    'purpose': r'purpose|why was .* (sent|written)', 'main-idea': r'main|mainly|primarily', 'not-question': r'\bNOT\b'}
            tags = [t for t in tags if t not in need or re.search(need[t], q['prompt'], re.I if t != 'not-question' else 0)]
            prim, ns, qt = cm.tag_p7(q['prompt'].strip(), tags, btx, txs, kind, opts[a])
            dest = p7_diff(kind, len(words(alltext)), qt, prim.startswith('QT.P7X.CROSS') or prim == 'QT.P7.CROSS_REF', q.get('difficulty'))
            it = {'id': 'KDP-' + q['id'], 'part': 7, 'form': form, 'qnum': n, 'bundle_id': bid, 'q': q['prompt'].strip(), 'options': opts,
                  'answer': a, 'answer_letter': 'ABCD'[a], 'node': prim, 'node_ids': cm.uniq([prim] + ns + bsc[:1]),
                  'explain_en': '', 'explain_zh': ez(q), 'src_tags': q.get('tags') or [], 'src_id': q['id'],
                  'difficulty_src': q.get('difficulty'), 'difficulty_est': dest, 'template_id': None, 'source': SOURCE, 'format_version': 'current'}
            it.update(extra(q))
            if dr:
                it['distractor_reasons'] = dr
            out_items.append(it)

    # ---- 校验 ----
    badn = [(i['id'], n) for i in out_items for n in i['node_ids'] if n not in G] + \
           [(b['bundle_id'], n) for b in out_bundles for n in b['node_ids'] if n not in G]
    if badn:
        print('UNKNOWN NODES', badn[:20]); sys.exit(1)
    assert all(i['node'] in i['node_ids'] for i in out_items)
    assert len({i['id'] for i in out_items}) == len(out_items)
    fc = collections.Counter(i['form'] for i in out_items)
    assert max(fc.values()) < 90, fc
    for b in out_bundles:
        bi = [i for i in out_items if i.get('bundle_id') == b['bundle_id']]
        assert sorted(i['qnum'] for i in bi) == b['qnums'], b['bundle_id']
        if b['part'] == 6:
            tx = ''.join(d['text'] + d.get('header', '') for d in b['docs'])
            assert sorted(int(x) for x in re.findall(r'\[(\d)\]', tx)) == sorted(i['blank_n'] for i in bi), b['bundle_id']
            assert not re.search(r'_{3,}', tx), b['bundle_id']

    cnt = collections.Counter('P%d' % i['part'] for i in out_items)
    meta = {'built': '2026-10-22', 'version': 'open-kdeppaei-v1', 'format_version': 'current', 'source': SOURCE,
            'source_desc': 'github.com/kdeppaei/toeic-question-ocean banks/question-bank*.js（作者原创模拟题；按版本顺序执行得 BUILTIN_BANK）的 P5/P6/P7',
            'license': 'MIT, © 2026 Chun-Hsiung Luo（原仓库 LICENSE；副本 private_data/sources/github/kdeppaei_toeic-question-ocean/LICENSE）',
            'excluded': 'modules/part5-exercise-guides.js + modules/reading-exercise-guides.js 共 336 题（ESL Lounge Student，原站禁止转载）整体未读入；见 data/items_open_kdeppaei_audit.md',
            'compat': '与 items_open_maximcuynat 同 schema；explain_zh=原繁体解析经 %s 转简体，explain_en 留空；另有 translation_zh / evidence_en / src_id / src_category / difficulty_src（原 400/600/800）；difficulty_est 由原难度档映射 400→2、600→3、800→4' % T2S,
            'forms': sorted(fc), 'forms_note': '非整套：P5 每卷 30 题（101–130）、P6 每卷 4 篇（131–146）、P7 每卷 ≤54 题（147 起，单篇在前）；每卷 <90 题，engine 不当模考卷',
            'node_tagging': '规则打标（data/items_open_kdeppaei_convert.py + work/convert_maximcuynat.py 规则函数）+ A2 全量人工复核修正（data/items_open_qc_fixes.json，由 work/qc/apply_qc_fixes.py 应用）',
            'counts': dict(cnt)}
    out = {'meta': meta, 'items': out_items, 'bundles': out_bundles}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log['kept'] = dict(cnt); log['kept_total'] = len(out_items); log['bundles'] = len(out_bundles)
    log['kinds'] = {'%d-%s' % k: v for k, v in collections.Counter((b['part'], b['kind']) for b in out_bundles).items()}
    log['primary_nodes'] = collections.Counter(i['node'] for i in out_items).most_common()
    log['forms'] = dict(fc)
    with open(LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print('bank', len(bank), 'reading', log['reading_by_part'], 'non-reading', log['non_reading'])
    print('ESL module excluded', log['excluded_esl_module'], 'ESL text hits in banks', len(log['esl_text_hits']))
    print('dropped format', len(log['dropped_format']), 'dropped dup', len(log['dropped_dup']), 'near-dup notes', len(log['near_dup_report']))
    print('kept', len(out_items), dict(cnt), 'bundles', len(out_bundles), log['kinds'])
    print('p7 split mismatch', log.get('p7_split_mismatch'))


if __name__ == '__main__':
    main()
