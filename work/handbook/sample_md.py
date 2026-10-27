"""抽 1 章生成人工可读版 docs/review/handbook_sample.md。用法: python3 sample_md.py [章号，默认 8]"""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '../..')
n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
hb = json.load(open(f'{R}/data/lessons/handbook_v1.json')); c = [x for x in hb['chapters'] if x['chapter'] == n][0]
o = [f"# 《新人工作手册》样章：第 {c['chapter']} 章 {c['title']}", '',
     f"> 自动导出自 `data/lessons/handbook_v1.json`（{hb['meta']['model']} 生成，独立作答核对；全部原创）。Part {c['part']} · 章目：{c['topic']} · 带教：{c['mentor']}", '',
     '## 一招', *[f'> {x}  ' for x in c['trick']], '', '## 适用信号', *[f'- {x}' for x in c['signals']], '']
def item(it, title):
    global o
    o.append(f"### {title}（{it['id']} · {it['band']} · 参考 {it['ref_seconds']} 秒）"); o.append('')
    for d in it.get('passage') or []:
        o.append(f"**[{d.get('type')}] {d.get('title', '')}**"); o.append(''); o += ['> ' + ln for ln in d['text'].split('\n')]; o.append('')
    o.append(f"**{it['question']}**"); o.append('')
    o += [f"- ({k}) {v}" for k, v in it['options'].items()]; o.append('')
    if it.get('steps'): o.append('**三步拆解**'); o += [f'{i+1}. {s}' for i, s in enumerate(it['steps'])]; o.append('')
    o.append(f"<details><summary>答案与解析</summary>\n\n**答案 {it['answer']}**　{it['explain_zh']}\n")
    o += [f"- 排除 {k}：{v}" for k, v in it['distractors'].items()]; o += ['', '</details>', '']
o.append('## 示范题'); item(c['example'], '示范')
o.append('## 练习（由易到难）')
for i, it in enumerate(c['practice'], 1): item(it, f'练习 {i}')
open(f'{R}/docs/review/handbook_sample.md', 'w').write('\n'.join(o)); print('ok', len('\n'.join(o)))
