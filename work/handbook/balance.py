"""答案位置均衡：模型生成的答案偏 A/B（A27 B26 C15 D4）。确定性重排选项使每章答案字母分布均匀，
并同步替换 explain_zh / steps / distractors 中的字母引用。随后 reverify.py 用独立作答复核。"""
import json, re, random, os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/lessons/handbook_v1.json')
hb = json.load(open(F)); rnd = random.Random(20261027); L = 'ABCD'
LET = re.compile(r'(?<![A-Za-z])([A-D])(?![A-Za-z])')
n = sum(1 + len(c['practice']) for c in hb['chapters']); seq = (list(L) * (n // 4 + 1))[:n]; rnd.shuffle(seq); pos = 0
for c in hb['chapters']:
    items = [c['example']] + c['practice']
    targets = seq[pos:pos + len(items)]; pos += len(items)
    for it, t in zip(items, targets):
        old = it['answer']; others = [x for x in L if x != old]; rnd.shuffle(others)
        new_slots = [x for x in L if x != t]
        mp = {old: t, **dict(zip(others, new_slots))}            # old letter -> new letter
        it['options'] = {mp[k]: v for k, v in it['options'].items()}; it['options'] = {k: it['options'][k] for k in L}
        sub = lambda s: LET.sub(lambda m: mp[m.group(1)], s)
        it['explain_zh'] = sub(it['explain_zh'])
        if 'steps' in it: it['steps'] = [sub(x) for x in it['steps']]
        it['distractors'] = {mp[k[:1]]: sub(v) for k, v in it['distractors'].items() if k[:1] in mp}
        it['distractors'] = {k: it['distractors'][k] for k in L if k in it['distractors']}
        it['answer'] = t
hb['meta']['answer_balanced'] = 'options reshuffled (seed 20261027), letters in explanations remapped, re-verified'
json.dump(hb, open(F, 'w'), ensure_ascii=False, indent=1)
import collections; print(collections.Counter(it['answer'] for c in hb['chapters'] for it in [c['example']] + c['practice']))
