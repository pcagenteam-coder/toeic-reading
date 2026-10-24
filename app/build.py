#!/usr/bin/env python3
"""托业阅读提分 v2 构建脚本。
读 data/ 下题库/技巧库/图谱 → 统一 schema、精简字段 → 内嵌进 src/index.html → dist/index.html（单文件，离线可用）。
用法：python3 app/build.py --public  → dist/index.html（只含公开题：pilot 自编 + open 开源 MIT 题）
      python3 app/build.py           → private_data/ 存在时 dist/index.private.html（另含 xdf 私有题，禁止公开）
"""
import json, re, os, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
SRC = os.path.join(APP, 'src')
JS_FILES = ['store.js', 'fsrs.js', 'mastery.js', 'predict.js', 'personal.js', 'planner.js', 'engine.js', 'api.js', 'app.js']   # 按顺序拼接
# C2：图谱排程字段（learn_cost_min / must_for_band + 2 个遗留节点），由 data/graph_v1_cost_build.py 生成；不存在则不合并
GRAPH_COST = 'data/graph_v1_cost.json'
# 开源题库（可公开发布）：(相对路径, src 标记)。题目字段与 items_pilot_v1 兼容
OPEN_SETS = [('data/items_open_maximcuynat.json', 'open'), ('data/items_open_kdeppaei.json', 'open')]
# EdNet 先验 + 新制节奏：xdf/open 题没有 target_time_sec / difficulty_est 时用这里的默认值
DEF_TIME = {5: 22, 6: 30, 7: 55}
DEF_DIFF = {5: 3, 6: 3, 7: 3}


def load(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return json.load(f)


def blank_re_xdf(text):
    # "(131) -------" / "(131)" → {{131}}
    return re.sub(r'\((1[3-4]\d)\)\s*-*', r'{{\1}}', text)


def conv_bundle(b, items_of_bundle, src):
    """统一 bundle：docs → [{t:文本类型, h:标题/信头, x:正文}]，P6 空位统一成 {{题号}}"""
    docs = []
    for d in b['docs']:
        h = (d.get('header') or d.get('title') or '').strip()   # 信头优先（open 题同时有 title=文本类型名 和 header=To/From）
        x = d.get('text') or ''
        if b['part'] == 6:
            if src in ('pilot', 'open', 'priv'):
                # pilot 用 [n]（n=blank_n，第 n 个空），换成对应题号
                m = {str(i.get('blank_n')): i['qnum'] for i in items_of_bundle if i.get('blank_n')}
                x = re.sub(r'\[(\d)\]', lambda g: '{{%s}}' % m.get(g.group(1), g.group(1)), x)
                h = re.sub(r'\[(\d)\]', lambda g: '{{%s}}' % m.get(g.group(1), g.group(1)), h)
            else:
                x = blank_re_xdf(x); h = blank_re_xdf(h)
        docs.append({'t': d.get('doc_type', ''), 'h': h, 'x': x})
    return {'id': b['bundle_id'], 'p': b['part'], 'f': b['form'], 'k': b['kind'],
            'tt': b.get('text_type', ''), 'docs': docs, 'qs': [i['id'] for i in items_of_bundle]}


def conv_item(i, src, kind=None):
    p = i['part']
    ns = [n for n in (i.get('node_ids') or []) if n != i['node']]
    dr = {}
    for L, v in (i.get('distractor_reasons') or {}).items():
        w = v.get('why_zh') if isinstance(v, dict) else v
        if w:
            dr['ABCD'.index(L)] = w
    t = i.get('target_time_sec') or (65 if (p == 7 and kind in ('double', 'triple')) else DEF_TIME[p])
    o = {'id': i['id'], 'p': p, 'f': i['form'], 'q': i['qnum'], 'n': i['node'], 'ns': ns,
         's': i.get('stem') or i.get('q') or '', 'o': i['options'], 'a': i['answer'],
         'e': i.get('explain_zh') or i.get('explain_en') or '', 'd': i.get('difficulty_est') or DEF_DIFF[p], 't': t,
         'src': src}
    if i.get('bundle_id'):
        o['b'] = i['bundle_id']
    if dr:
        o['dr'] = {str(k): v for k, v in dr.items()}
    if p == 6:
        o['s'] = ''   # P6 题干就是原文里的空，不重复存
    return o



# 技巧库：优先读 v2（data/strategies/strategies_v2.json），不存在则回退 v1；两种格式都转成同一前端结构
STRATS_V2 = 'data/strategies/strategies_v2.json'
STRATS_V1 = 'data/strategies/strategy_library_v1.json'


def load_strats():
    p = STRATS_V2 if os.path.exists(os.path.join(ROOT, STRATS_V2)) else STRATS_V1
    print('strategies:', p)
    return load(p)


EXTRA_IDS = set()   # graph_v1_cost.json 补的遗留节点；strategies_v2 用 suggested_new_node 指向它们


def conv_strat(e):
    ns = e['qtype_nodes'] + e['texttype_nodes'] + e['strategy_nodes'] + e['skill_nodes']
    sn = (e.get('suggested_new_node') or '').split('（')[0]
    if sn in EXTRA_IDS and sn not in ns:
        ns = ns + [sn]
    if 'plain_zh' in e:   # v2
        return {'id': e['id'], 'ti': e['title_zh'], 'wr': e['plain_zh'], 'r': e['detail_zh'], 'ns': ns, 'p': e['parts'],
                'w': e['weight'], 'pm': 1 if e['practice_mode'] else 0, 'roi': e['roi'], 'bd': e['bands'], 'ms': e['min_set_bands']}
    return {'id': e['id'], 'ti': e['title_zh'], 'wr': e['work_rule'], 'r': e['rule_zh'],   # v1
            'ns': ns, 'p': e['parts'], 'w': e['weight'], 'pm': 1 if e['practice_mode'] else 0}


# B2：可选内联（缺失则跳过）——中文解析、语法 60 秒微讲解、词典（只收题库出现过的词）、词汇摸底池
EXPL = 'data/explanations/zh_open_v1.json'
GRAM = 'data/lessons/grammar_v1.json'
LEX = 'data/wordlists/lexicon_v1.json'
LEX_SA = 'data/wordlists/lexicon_v1_sa.json'
VPOOL = 'data/wordlists/vocab_test_pool.json'
TOK = re.compile(r"[a-z]+(?:[-'][a-z]+)*")


def exists(p):
    return os.path.exists(os.path.join(ROOT, p))


def extras(items, bundles):
    out, ids = {}, {i['id'] for i in items}
    if exists(EXPL):
        ex = {}
        for k, v in load(EXPL)['items'].items():
            if k not in ids:
                continue
            o = {'b': v.get('basis', ''), 'w': v.get('why', '')}
            if v.get('distractors'):
                o['d'] = v['distractors']
            if v.get('tip'):
                o['t'] = v['tip']
            if v.get('paraphrase'):
                o['pp'] = [[x.get('text', ''), x.get('option', '')] for x in v['paraphrase']][:2]
            ex[k] = o
        out['exp'] = ex
    if exists(GRAM):
        out['gr'] = {L['node']: {'nm': L['name_zh'], 'r': L['rule'], 'ex': [[e['en'], e['zh']] for e in L.get('examples', [])][:2],
                                 'tr': L.get('trap', ''), 'sg': L.get('signal', '')} for L in load(GRAM)['lessons']}
    if exists(LEX):
        toks = set()
        for i in items:
            for t in [i['s']] + i['o']:
                toks.update(TOK.findall(t.lower()))
        for b in bundles:
            for d in b['docs']:
                toks.update(TOK.findall((d['h'] + ' ' + d['x']).lower()))
        dic, forms = {}, {}
        for e in load(LEX)['entries']:
            if e.get('kind') != 'word':
                continue
            h = e['headword'].lower(); fs = [f.lower() for f in (e.get('forms') or [])]
            hit = [f for f in fs if f in toks and f != h]
            if h in toks or hit:
                dic[h] = [e['zh'][:40], ' '.join(e.get('pos') or [])[:12], 1 if e.get('tier') else 0]
                for f in hit:
                    forms.setdefault(f, h)
        if exists(LEX_SA):
            for e in load(LEX_SA)['entries']:
                h = e['headword'].lower()
                if h in toks and h not in dic:
                    dic[h] = [e['zh'][:40], '', 0]
        out['dict'] = dic; out['forms'] = forms
    if exists(VPOOL):
        out['voc'] = [[v['word'], 1 if v.get('real') else 0, v.get('tier') or '', v.get('zh', '')[:24]] for v in load(VPOOL)['items']]
    return out


def main():
    # 私有题库（无授权，只自用）：private_data/ 存在就一起打包，否则只用公开题。
    # 公开构建：python3 app/build.py --public   （强制不打私有题，可发布到 GitHub Pages）
    P = load('data/items_pilot_v1.json')
    # 私有题库优先读统一版 items_private_v1.json（xdf+GrittingLeo+ETS+其他，P6 空位 [n]，带 use=mock|train），没有则回退 items_xdf1000.json
    xp1 = os.path.join(ROOT, 'private_data', 'items', 'items_private_v1.json')
    xp = xp1 if os.path.exists(xp1) else os.path.join(ROOT, 'private_data', 'items', 'items_xdf1000.json')
    psrc = 'priv' if xp == xp1 else 'xdf'
    use_private = os.path.exists(xp) and '--public' not in sys.argv
    X = load(xp) if use_private else {'items': [], 'bundles': []}
    if use_private:
        print('private items:', os.path.relpath(xp, ROOT))
    print('build mode:', 'PRIVATE (含无授权题，禁止公开)' if use_private else 'PUBLIC (仅公开题)')
    G = load('data/graph_v1.json'); S = load_strats()
    GC = load(GRAPH_COST) if os.path.exists(os.path.join(ROOT, GRAPH_COST)) else None
    if GC:
        G['nodes'] = G['nodes'] + GC['extra_nodes']; EXTRA_IDS.update(n['id'] for n in GC['extra_nodes'])
        print('graph cost:', GRAPH_COST, '+%d extra nodes' % len(GC['extra_nodes']))
    OPEN = {'items': [], 'bundles': []}
    for path, tag in OPEN_SETS:
        if os.path.exists(os.path.join(ROOT, path)):
            o = load(path); OPEN['items'] += o['items']; OPEN['bundles'] += o['bundles']
    items, bundles, skipped = [], [], 0
    for src, d in (('pilot', P), ('open', OPEN), (psrc, X)):
        by_b = {}
        for i in d['items']:
            if i.get('bundle_id'):
                by_b.setdefault(i['bundle_id'], []).append(i)
        bad = {b['bundle_id'] for b in d['bundles'] if b.get('text_missing')}
        kinds = {}
        for b in d['bundles']:
            if b['bundle_id'] in bad:
                continue
            its = sorted(by_b.get(b['bundle_id'], []), key=lambda x: x['qnum'])
            bundles.append(conv_bundle(b, its, src)); kinds[b['bundle_id']] = b['kind']
        for i in d['items']:
            if 'passage_missing' in (i.get('flags') or []) or i.get('bundle_id') in bad:
                skipped += 1; continue
            if len(i.get('options') or []) != 4 or not isinstance(i.get('answer'), int):
                skipped += 1; continue
            items.append(conv_item(i, src, kinds.get(i.get('bundle_id'))))
            if src == 'priv' and i.get('use'):
                items[-1]['u'] = i['use']   # 私有题用途：mock 只做模考 / train 训练
    nodes = [{'id': n['id'], 'nm': n['name_zh'], 'l': n['layer'], 'pa': n['parent'],
              'w': n['exam_weight'], 'bd': n['target_band'], 'g': 1 if n['is_group'] else 0, 'pr': n.get('prereqs') or []}
             for n in G['nodes']]
    if GC:   # lc 学会估计分钟，mb 必须掌握的目标档
        for n in nodes:
            c = GC['nodes'].get(n['id'])
            if c:
                n['lc'] = c['learn_cost_min']; n['mb'] = c['must_for_band']
    strats = [conv_strat(e) for e in S['entries']]
    data = {'v': 'v2-' + G.get('built', ''), 'items': items, 'bundles': bundles, 'nodes': nodes, 'strats': strats}
    X2 = extras(items, bundles); data.update(X2)
    print('extras', {k: len(v) for k, v in X2.items()}, 'KB', {k: round(len(json.dumps(v, ensure_ascii=False, separators=(',', ':')).encode()) / 1024) for k, v in X2.items()})
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

    html = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
    css = open(os.path.join(SRC, 'style.css'), encoding='utf-8').read()
    code = '\n'.join(open(os.path.join(SRC, f), encoding='utf-8').read() for f in JS_FILES)
    assert '</script' not in code.lower()
    out = html.replace('/*CSS*/', css).replace('/*JS*/', code).replace('/*DATA*/', 'window.TDATA=' + js + ';')
    os.makedirs(os.path.join(APP, 'dist'), exist_ok=True)
    dst = os.path.join(APP, 'dist', 'index.html' if not use_private else 'index.private.html')
    open(dst, 'w', encoding='utf-8').write(out)
    shutil.copyfile(os.path.join(SRC, 'sw.js'), os.path.join(APP, 'dist', 'sw.js'))   # P0-4：本地通知用的最小 SW（需与 index.html 同目录、https 部署）
    from collections import Counter
    allf = Counter(i['f'] for i in items)
    full = {f: n for f, n in sorted(allf.items()) if n >= 90}   # 整套（模考可用），与 engine.js FULL_MIN 一致
    print('items', len(items), 'skipped', skipped, 'bundles', len(bundles), 'nodes', len(nodes), 'strats', len(strats))
    print('by src', dict(Counter(i['src'] for i in items)), 'by part', dict(Counter(i['p'] for i in items)))
    print('mock forms (>=90 题)', full)
    if not use_private:
        assert not any(i['src'] in ('xdf', 'priv') for i in items), '公开构建混入了私有题'
    print('code KB', round(len(code.encode()) / 1024, 1), 'css KB', round(len(css.encode()) / 1024, 1),
          'dist KB', round(os.path.getsize(dst) / 1024, 1))


if __name__ == '__main__':
    main()
