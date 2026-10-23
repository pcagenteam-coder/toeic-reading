"""语法 60 秒微讲解：lessons_src.txt → data/lessons/grammar_v1.json（幂等）。
覆盖：graph_v1 中 GR.* 叶节点 + QT.P5.* / QT.P6.* 叶节点。
排序：按 strategies_v2 各档最小技巧集；600 档把词性（GR.POS / WORD_FORM）和介词·连词（GR.CONN / PREP / CONJ / CONNECTOR_MIX）排最前。
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, strategies

SRC = os.path.join(os.path.dirname(__file__), 'lessons_src.txt')
OUT = os.path.join(ROOT, 'data/lessons/grammar_v1.json')

g = json.load(open(os.path.join(ROOT, 'data/graph_v1.json')))
nodes = {n['id']: n for n in g['nodes']}
parents = {n.get('parent') for n in g['nodes']}
targets = [n['id'] for n in g['nodes'] if (n['id'].startswith('GR.') or n['id'].startswith(('QT.P5.', 'QT.P6.')))
           and n['id'] not in parents]

lessons, cur = {}, None
for ln in open(SRC, encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.startswith('#'):
        continue
    if ln.startswith('@'):
        cur = ln[1:].strip(); lessons[cur] = {'examples': []}; continue
    k, v = ln[:2], ln[2:].strip()
    if k == 'R:': lessons[cur]['rule'] = v
    elif k == 'E:':
        en, zh = [x.strip() for x in v.split('##', 1)]
        lessons[cur]['examples'].append({'en': en, 'zh': zh})
    elif k == 'T:': lessons[cur]['trap'] = v
    elif k == 'S:': lessons[cur]['signal'] = v
    else: raise SystemExit('bad line: ' + ln)

errs = []
for nid, L in lessons.items():
    if nid not in targets: errs.append('非目标叶节点 ' + nid)
    for f in ('rule', 'trap', 'signal'):
        if not L.get(f): errs.append('%s 缺 %s' % (nid, f))
    if len(L['examples']) != 2: errs.append('%s 例句数 %d' % (nid, len(L['examples'])))
missing = [t for t in targets if t not in lessons]
if missing: errs.append('未覆盖: ' + ','.join(missing))
if errs:
    print('\n'.join(errs)); sys.exit(1)

entries, _ = strategies()
S = json.load(open(os.path.join(ROOT, 'data/strategies/strategies_v2.json')))
bands = S['meta']['bands']
CORE600 = ('GR.POS', 'QT.P5.WORD_FORM', 'QT.P5.IDENTIFY', 'GR.CONN', 'QT.P5.PREP', 'QT.P5.CONJ', 'QT.P5.CONNECTOR_MIX', 'QT.P6.INDEPENDENT', 'QT.P6.CLASSIFY')


def strat_of(nid):
    return [e['id'] for e in entries if nid in e['graph_nodes']]


def band_rank(nid, band):
    ms = S['min_sets'][band]
    idx = [ms.index(s) for s in strat_of(nid) if s in ms]
    return min(idx) if idx else None


out = []
for nid in targets:
    n = nodes[nid]; L = lessons[nid]
    core = any(nid == c or nid.startswith(c + '.') for c in CORE600)
    r600 = band_rank(nid, '600')
    tier = 0 if core else (1 if r600 is not None else 2)
    out.append({'node': nid, 'name_zh': n['name_zh'], 'target_band': n.get('target_band'),
                'strategy_ids': strat_of(nid),
                'in_min_set': [b for b in bands if band_rank(nid, b) is not None],
                'priority_600_tier': tier,
                'rule': L['rule'], 'examples': L['examples'], 'trap': L['trap'], 'signal': L['signal'],
                '_sort': (tier, n.get('target_band') or 999, r600 if r600 is not None else 99, targets.index(nid))})
out.sort(key=lambda x: x['_sort'])
for i, x in enumerate(out, 1):
    x['priority'] = i; x.pop('_sort')
order_by_band = {}
for b in bands:
    lst = [x for x in out if b in x['in_min_set']]
    order_by_band[b] = [x['node'] for x in lst]
meta = {'version': 'grammar_v1', 'n_lessons': len(out),
        'coverage': 'graph_v1 GR.* 叶节点 %d + QT.P5/QT.P6 叶节点 %d' % (
            sum(1 for t in targets if t.startswith('GR.')), sum(1 for t in targets if t.startswith('QT.'))),
        'fields': {'rule': '一句话规则', 'examples': '2 个托业式自编例句 {en, zh}', 'trap': '常见陷阱 1 条',
                   'signal': '识别信号：看到什么就用这招', 'priority': '全局学习顺序（600 档视角）',
                   'priority_600_tier': '0=600 档核心（词性、介词/连词、看选项判题型）；1=在 600 档最小技巧集；2=其余',
                   'in_min_set': '其关联技巧进入了哪些档的最小技巧集'},
        'order_by_band': order_by_band,
        'source': '全部自编；排序依据 data/strategies/strategies_v2.json min_sets', 'builder': 'work/explain/build_lessons.py'}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({'meta': meta, 'lessons': out}, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('lessons', len(out), 'tiers', {t: sum(1 for x in out if x['priority_600_tier'] == t) for t in (0, 1, 2)})
