"""原创性检查：手册英文文本与公开/私有题库的 8-gram 重合（只输出计数与 id，不输出私有文本）。"""
import json, re, glob, os
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '../..')
def toks(s): return re.findall(r"[a-z0-9']+", s.lower())
def grams(s, n=8):
    t = toks(s); return {' '.join(t[i:i+n]) for i in range(len(t)-n+1)}
def walk(o):
    if isinstance(o, str): yield o
    elif isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
bank = set()
for f in glob.glob(f'{R}/data/items_*.json') + [f'{R}/private_data/items/items_private_v1.json', f'{R}/private_data/items/items_xdf1000.json']:
    try: d = json.load(open(f))
    except Exception: continue
    for s in walk(d):
        if len(s) > 40 and re.search('[a-zA-Z]{3}', s): bank |= grams(s)
hb = json.load(open(f'{R}/data/lessons/handbook_v1.json'))
hits = {}
for c in hb['chapters']:
    for it in [c['example']] + c['practice']:
        txt = ' '.join([it.get('question', '')] + list(it.get('options', {}).values()) + [d.get('text', '') for d in (it.get('passage') or [])])
        g = grams(txt); h = g & bank
        if h: hits[it['id']] = len(h)
print('bank grams', len(bank), 'items with 8-gram overlap', hits)
