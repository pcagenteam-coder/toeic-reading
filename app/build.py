#!/usr/bin/env python3
"""托业阅读提分 v2 构建脚本。
读 data/ 下题库/技巧库/图谱 → 统一 schema、精简字段 → 内嵌进 src/index.html → dist/index.html（单文件，离线可用）。
用法：python3 app/build.py --public  → dist/index.html（只含公开题：pilot 自编 + open 开源 MIT 题）
      python3 app/build.py           → private_data/ 存在时 dist/index.private.html（另含 xdf 私有题，禁止公开）
"""
import json, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
SRC = os.path.join(APP, 'src')
JS_FILES = ['store.js', 'fsrs.js', 'engine.js', 'app.js']   # 按顺序拼接
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
            if src in ('pilot', 'open'):
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


def conv_strat(e):
    ns = e['qtype_nodes'] + e['texttype_nodes'] + e['strategy_nodes'] + e['skill_nodes']
    if 'plain_zh' in e:   # v2
        return {'id': e['id'], 'ti': e['title_zh'], 'wr': e['plain_zh'], 'r': e['detail_zh'], 'ns': ns, 'p': e['parts'],
                'w': e['weight'], 'pm': 1 if e['practice_mode'] else 0, 'roi': e['roi'], 'bd': e['bands'], 'ms': e['min_set_bands']}
    return {'id': e['id'], 'ti': e['title_zh'], 'wr': e['work_rule'], 'r': e['rule_zh'],   # v1
            'ns': ns, 'p': e['parts'], 'w': e['weight'], 'pm': 1 if e['practice_mode'] else 0}


def main():
    # 私有题库（无授权，只自用）：private_data/ 存在就一起打包，否则只用公开题。
    # 公开构建：python3 app/build.py --public   （强制不打私有题，可发布到 GitHub Pages）
    P = load('data/items_pilot_v1.json')
    xp = os.path.join(ROOT, 'private_data', 'items', 'items_xdf1000.json')
    use_private = os.path.exists(xp) and '--public' not in sys.argv
    X = load(xp) if use_private else {'items': [], 'bundles': []}
    print('build mode:', 'PRIVATE (含无授权题，禁止公开)' if use_private else 'PUBLIC (仅公开题)')
    G = load('data/graph_v1.json'); S = load_strats()
    OPEN = {'items': [], 'bundles': []}
    for path, tag in OPEN_SETS:
        if os.path.exists(os.path.join(ROOT, path)):
            o = load(path); OPEN['items'] += o['items']; OPEN['bundles'] += o['bundles']
    items, bundles, skipped = [], [], 0
    for src, d in (('pilot', P), ('open', OPEN), ('xdf', X)):
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
    nodes = [{'id': n['id'], 'nm': n['name_zh'], 'l': n['layer'], 'pa': n['parent'],
              'w': n['exam_weight'], 'bd': n['target_band'], 'g': 1 if n['is_group'] else 0}
             for n in G['nodes']]
    strats = [conv_strat(e) for e in S['entries']]
    data = {'v': 'v2-' + G.get('built', ''), 'items': items, 'bundles': bundles, 'nodes': nodes, 'strats': strats}
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

    html = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
    css = open(os.path.join(SRC, 'style.css'), encoding='utf-8').read()
    code = '\n'.join(open(os.path.join(SRC, f), encoding='utf-8').read() for f in JS_FILES)
    assert '</script' not in code.lower()
    out = html.replace('/*CSS*/', css).replace('/*JS*/', code).replace('/*DATA*/', 'window.TDATA=' + js + ';')
    os.makedirs(os.path.join(APP, 'dist'), exist_ok=True)
    dst = os.path.join(APP, 'dist', 'index.html' if not use_private else 'index.private.html')
    open(dst, 'w', encoding='utf-8').write(out)
    from collections import Counter
    allf = Counter(i['f'] for i in items)
    full = {f: n for f, n in sorted(allf.items()) if n >= 90}   # 整套（模考可用），与 engine.js FULL_MIN 一致
    print('items', len(items), 'skipped', skipped, 'bundles', len(bundles), 'nodes', len(nodes), 'strats', len(strats))
    print('by src', dict(Counter(i['src'] for i in items)), 'by part', dict(Counter(i['p'] for i in items)))
    print('mock forms (>=90 题)', full)
    if not use_private:
        assert not any(i['src'] == 'xdf' for i in items), '公开构建混入了私有题'
    print('code KB', round(len(code.encode()) / 1024, 1), 'css KB', round(len(css.encode()) / 1024, 1),
          'dist KB', round(os.path.getsize(dst) / 1024, 1))


if __name__ == '__main__':
    main()
