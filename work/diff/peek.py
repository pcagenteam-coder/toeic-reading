#!/usr/bin/env python3
"""抽查评分结果（不打印题目文本）。用法: python3 work/diff/peek.py open|private [N]"""
import json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rate
st = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 25
idx = {}
for f in rate.SETS[st]:
    for q in json.load(open(os.path.join(ROOT, f)))['items']:
        idx[q['id']] = q
rows = []; toks = []; eps = collections.Counter()
for ln in open(os.path.join(ROOT, rate.OUTS[st])):
    r = json.loads(ln); toks.append(r['usage'].get('completion_tokens', 0)); eps[r['usage'].get('ep')] += 1
    for it in r['items']:
        rows.append((it['id'], idx[it['id']], it['f']))
print('units', len(toks), 'items', len(rows), 'avg completion tok', sum(toks) // max(1, len(toks)), 'eps', dict(eps))
for i, q, f in rows[:N]:
    print(i, q['node'][3:28], 'old', q.get('difficulty_est'), q.get('difficulty_src', ''), '|', f.get('score'), f.get('band'), f.get('cefr'),
          'D%s' % f.get('distractor'), f.get('locate'), f.get('reasoning'), 'S%s' % f.get('syntax'), '%ss' % f.get('time_sec'),
          'ch', f.get('handbook_chapter'), f.get('technique_zh'))
bad = [i for i, q, f in rows if not isinstance(f.get('score'), (int, float))]
print('non-numeric score', len(bad))
print('bands', collections.Counter(f.get('band') for _, _, f in rows))
