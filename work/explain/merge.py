"""解析 authored 文件 → 校验 → 写输出 JSON / flags / 进度（幂等，可重复跑）。
用法：python3 work/explain/merge.py --pool open|private [--strict]
校验项：
  - 作者答案字母 == item.answer_letter（不一致→flags，原因 answer_conflict）
  - 错项恰好覆盖 3 个错误选项
  - 依据英文片段 ≤12 词、能在题干/原文找到
  - 为什么非空；记一招 ≤20 字
  - 同义替换：原文短语在原文中出现（P7）
  - 题目内容变了（hash 不同）→ 该条作废、回到待做
"""
import argparse, json, os, sys, re, glob
sys.path.insert(0, os.path.dirname(__file__))
from common import *


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pool', default='open')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    P = POOLS[a.pool]
    items, bundles = load_pool(a.pool)
    byid = {it['id']: it for it in items}
    out, flags, errors = {}, {}, []
    files = sorted(glob.glob(os.path.join(P['authored'], '*.txt')))
    for f in files:
        for ln, raw in enumerate(open(f, encoding='utf-8'), 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = parse_line(line)
            iid = parts[0]
            where = '%s:%d %s' % (os.path.basename(f), ln, iid)
            it = byid.get(iid)
            if not it:
                errors.append(where + ' 未知 id'); continue
            if len(parts) >= 2 and parts[1] == 'FLAG':
                flags[iid] = {'reason': 'author_flag', 'note': '|'.join(parts[2:]).strip(),
                              'answer_letter': it['answer_letter'], 'hash': item_hash(it, bundles)}
                out.pop(iid, None)
                continue
            if len(parts) < 7:
                parts += [''] * (7 - len(parts))
            if len(parts) > 7:
                errors.append(where + ' 字段数 %d>7（文本里有 | ？）' % len(parts)); continue
            _, al, basis, why, dis, tip, para = parts
            al = al.upper()
            if al != it['answer_letter']:
                flags[iid] = {'reason': 'answer_conflict', 'author_answer': al,
                              'answer_letter': it['answer_letter'], 'note': why,
                              'hash': item_hash(it, bundles)}
                out.pop(iid, None)
                continue
            errs = []
            src = source_text(it, bundles)
            q_en = basis.split('——')[0].strip()
            ok, nw = check_quote(q_en, src)
            if not q_en:
                errs.append('依据为空')
            elif not ok:
                errs.append('依据片段在原文中找不到: ' + q_en[:50])
            elif nw > 12:
                errs.append('依据超过 12 词 (%d)' % nw)
            if not why:
                errs.append('为什么为空')
            dmap, derr = parse_distractors(dis, al)
            errs += derr
            tip_sid = None
            m = re.search(r'@(S2-[A-Z0-9]+-\d+)\s*$', tip)
            if m:
                tip_sid = m.group(1); tip = tip[:m.start()].strip()
            node_sid = strategy_for(it['node_ids'])
            if tip == '-':
                tip_sid = tip_sid or node_sid
                tip = DEFAULT_TIPS.get(tip_sid, '')
            elif tip and not tip_sid:
                tip_sid = node_sid
            if tip and tip_len(tip) > 20:
                errs.append('记一招超 20 字 (%d): %s' % (tip_len(tip), tip))
            if tip_sid and tip_sid not in {e['id'] for e in strategies()[0]}:
                errs.append('技巧 id 不存在 ' + tip_sid)
            pairs = []
            if para:
                ptxt = passage_text(it, bundles)
                for seg in [x for x in re.split(r'[;；]', para) if x.strip()]:
                    if '=>' not in seg:
                        errs.append('同义替换格式: ' + seg); continue
                    t, o = [x.strip() for x in seg.split('=>', 1)]
                    if not check_quote(t, ptxt)[0]:
                        errs.append('同义替换原文短语找不到: ' + t)
                    pairs.append({'text': t, 'option': o})
            if errs:
                errors.append(where + ' ' + '；'.join(errs)); continue
            rec = {'answer_letter': al, 'basis': basis, 'why': why,
                   'distractors': {k: dmap[k] for k in sorted(dmap)},
                   'tip': tip or None, 'tip_strategy_id': tip_sid if tip else None,
                   'paraphrase': pairs if it['part'] == 7 else (pairs or None),
                   'node': it['node'], 'hash': item_hash(it, bundles)}
            if it['part'] != 7 and not pairs:
                rec.pop('paraphrase')
            out[iid] = rec
            flags.pop(iid, None)
    # 有效性：hash 变化
    for d in (out, flags):
        for iid in list(d):
            if d[iid]['hash'] != item_hash(byid[iid], bundles):
                errors.append('%s 题目已变，需重写' % iid); d.pop(iid)
    order = {it['id']: i for i, it in enumerate(items)}
    out = dict(sorted(out.items(), key=lambda kv: order[kv[0]]))
    flags = dict(sorted(flags.items(), key=lambda kv: order[kv[0]]))
    n_all = len(items)
    meta = {'version': 'zh_%s_v1' % a.pool, 'format': {
        'basis': '依据：英文原句/题干片段（≤12 词，___=空格），可带“—— 中文注”',
        'why': '为什么：一两句大白话', 'distractors': '你选错在哪：{错误选项字母: 一句}（合并的组文本相同）',
        'tip': '记一招（≤20 字，可空）', 'tip_strategy_id': 'strategies_v2 条目 id',
        'paraphrase': 'P7 同义替换对 [{text 原文短语, option 选项短语}]'},
        'n_items_pool': n_all, 'n_explained': len(out), 'n_flagged': len(flags),
        'generator': 'work/explain/merge.py（文本由 agent 逐题自写，不含第三方解析原文）'}
    os.makedirs(os.path.dirname(os.path.join(ROOT, P['out'])), exist_ok=True)
    json.dump({'meta': meta, 'items': out}, open(os.path.join(ROOT, P['out']), 'w'), ensure_ascii=False, indent=1)
    json.dump({'meta': {'n_flagged': len(flags), 'reasons': {
        'answer_conflict': '作者独立判断与 item.answer 不一致', 'author_flag': '题目/选项有缺陷或答案不唯一'}},
        'items': flags}, open(os.path.join(ROOT, P['flags']), 'w'), ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(P['state']), exist_ok=True)
    json.dump({'done': {k: v['hash'] for k, v in out.items()}, 'flagged': {k: v['hash'] for k, v in flags.items()}},
              open(P['state'], 'w'), ensure_ascii=False)
    print('pool=%s items=%d explained=%d flagged=%d remaining=%d errors=%d' % (
        a.pool, n_all, len(out), len(flags), n_all - len(out) - len(flags), len(errors)))
    for e in errors[:80]:
        print('  ERR ' + e)


if __name__ == '__main__':
    main()
