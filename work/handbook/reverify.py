"""对 handbook_v1.json 全部题再独立作答一次（Kunyou/igrok 互备），报告不一致。"""
import json, os, sys, concurrent.futures as cf
H = os.path.dirname(os.path.abspath(__file__)); sys.argv = sys.argv[:1]
import importlib.util; spec = importlib.util.spec_from_file_location('g', os.path.join(H, 'gen.py')); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
hb = json.load(open(os.path.join(H, '../../data/lessons/handbook_v1.json')))
jobs = [(c['part'], it) for c in hb['chapters'] for it in [c['example']] + c['practice']]
def go(j):
    try: s = g.solve(j[1], j[0]); return j[1]['id'], j[1]['answer'], str(s.get('answer', ''))[:1].upper(), s.get('unique')
    except Exception as e: return j[1]['id'], j[1]['answer'], 'ERR', repr(e)[:80]
with cf.ThreadPoolExecutor(15) as ex: res = list(ex.map(go, jobs))
bad = [r for r in res if r[1] != r[2] or r[3] is False]
json.dump(res, open(os.path.join(H, 'reverify.json'), 'w'))
print('checked', len(res), 'mismatch', bad, flush=True)
