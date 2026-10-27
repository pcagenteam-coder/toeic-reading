#!/usr/bin/env python3
"""合并 LLM 难度评分 → difficulty_v2_open.json / difficulty_v2_private.json + docs/review/difficulty_v2_report.md
档位由 score 固定映射（与 rubric 一致）：<35 基础(<500) / 35–54 进阶(500–650) / 55–74 熟练(650–800) / ≥75 真考+(800+)
diff1_5（供 engine diffB=(d-3)*0.7）：<25→1, 25–39→2, 40–54→3, 55–69→4, ≥70→5
用法: python3 work/diff/merge.py   （私有输出仅当 private_data/ 存在）"""
import json, os, sys, collections, math, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rate

BANDS = ['基础', '进阶', '熟练', '真考+']
BAND_LBL = {'基础': '基础 <500', '进阶': '进阶 500–650', '熟练': '熟练 650–800', '真考+': '真考+ 800+'}
FEATS = ['cefr', 'hard_words', 'distractor', 'locate', 'reasoning', 'paraphrase', 'syntax', 'sent_len', 'time_sec']


def band_of(s):
    return '基础' if s < 35 else '进阶' if s < 55 else '熟练' if s < 75 else '真考+'


def d15(s):
    return 1 if s < 25 else 2 if s < 40 else 3 if s < 55 else 4 if s < 70 else 5


def num(x, d=None):
    try:
        return float(x)
    except Exception:
        m = re.search(r'-?\d+(\.\d+)?', str(x or ''))
        return float(m.group()) if m else d


def chapters(x):
    if isinstance(x, (int, float, str)):
        x = [x]
    out = []
    for c in x or []:
        n = num(c)
        if n is not None and 1 <= int(n) <= 12 and int(n) not in out:
            out.append(int(n))
    return out[:3]


def qtype(node):
    p = (node or '').split('.')
    if len(p) >= 3 and p[1] == 'P7X':
        return 'P7.' + p[2]
    return '.'.join(p[1:3]) if len(p) >= 3 else node


def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    if n < 3:
        return float('nan')
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else float('nan')


def spearman(a, b):
    return pearson(rank(a), rank(b))


def load_set(st):
    items = []
    for f in rate.SETS[st]:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            return None, None
        d = json.load(open(p))
        for q in d['items']:
            q['_file'] = os.path.basename(f); items.append(q)
    res = {}; stat = collections.Counter()
    op = os.path.join(ROOT, rate.OUTS[st])
    if os.path.exists(op):
        for ln in open(op):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            for it in r['items']:
                f = it['f']; s = num(f.get('score'))
                if s is None:
                    stat['bad_score'] += 1; continue
                s = int(round(max(0, min(100, s))))
                b = band_of(s)
                if f.get('band') != b:
                    stat['llm_band_mismatch'] += 1
                feats = {k: f.get(k) for k in FEATS}
                feats['llm_band'] = f.get('band')
                res[it['id']] = {'score': s, 'band': b, 'diff1_5': d15(s), 'features': feats,
                                 'chapter': chapters(f.get('handbook_chapter')),
                                 'technique_zh': str(f.get('technique_zh') or '')[:60]}
    return items, (res, stat)


def src_label(q):
    return {'items_pilot_v1.json': 'pilot', 'items_open_maximcuynat.json': 'maximcuynat', 'items_open_kdeppaei.json': 'kdeppaei'}.get(q['_file'], q.get('source', '?'))


def red(n, thr=20):
    return f'<span style="color:red">**{n}**</span>' if n < thr else str(n)


def report(sets):
    L = ['# 难度重评 v2 报告（UX_SPEC_v2 §6）', '',
         '- 方法：LLM（deepseek-v4.1-flash，Kunyou + igrok 双端点）按固定 rubric + 7 条锚定示例，P5 每 5 题一次、P6/P7 每篇一次调用；输出 ETS 风格特征（CEFR 最难词、干扰项强度 0–3、定位距离、认知类型、同义替换、句法复杂度、句长、用时）+ 0–100 难度分。',
         '- 档位由分数固定映射：<35 基础(<500) / 35–54 进阶(500–650) / 55–74 熟练(650–800) / ≥75 真考+(800+)；新 difficulty_est(1–5)：<25→1, 25–39→2, 40–54→3, 55–69→4, ≥70→5。',
         '- 文件：公开 `data/difficulty/difficulty_v2_open.json`；私有 `private_data/difficulty/difficulty_v2_private.json`（id→{score,band,diff1_5,features,chapter,technique_zh}）。',
         '- 局限：① LLM 分数偏向中段，800+ 档仅 2–3%（与题源自带难度 ρ≈0.42–0.45，P5 最好、P6 最弱），上线后须用作答数据 IRT 校准；② igrok 端点本次返回 Invalid token，全部由 Kunyou 完成；③ 公开池前约 110 个调用单位用默认推理强度，其后改 reasoning_effort=low（rubric 不变）；④ 题型 = 主考点 node 去掉文体后缀（P7X.DETAIL.EMAIL → P7.DETAIL）。', '']
    for st, (items, res, stat) in sets.items():
        name = '公开池' if st == 'open' else '私有池'
        got = [q for q in items if q['id'] in res]
        L += [f'## {name}', '', f'- 题数 {len(items)}，已评 {len(got)}，未评 {len(items) - len(got)}；LLM 自报档与分数映射不一致 {stat.get("llm_band_mismatch", 0)}（以分数为准）。', '']
        # 1 分布 source×Part×band
        L += ['### 分布：题源 × Part × 档', '', '| 题源 | Part | ' + ' | '.join(BAND_LBL[b] for b in BANDS) + ' | 合计 | 均分 |', '|---|---|' + '---|' * (len(BANDS) + 2)]
        grp = collections.defaultdict(list)
        for q in got:
            grp[(src_label(q), int(q['part']))].append(res[q['id']]['score'])
        for (s, p), v in sorted(grp.items()):
            c = collections.Counter(band_of(x) for x in v)
            L.append(f'| {s} | P{p} | ' + ' | '.join(str(c[b]) for b in BANDS) + f' | {len(v)} | {sum(v) / len(v):.1f} |')
        c = collections.Counter(res[q['id']]['band'] for q in got)
        L.append('| **合计** | | ' + ' | '.join(f'**{c[b]}** ({100 * c[b] / max(1, len(got)):.0f}%)' for b in BANDS) + f' | **{len(got)}** | |')
        L.append('')
        # 2 旧 difficulty_est 对比
        L += ['### 与旧 difficulty_est 对比', '', '| 旧 est | n | ' + ' | '.join(BANDS) + ' | 新均分 | 新 est 均值 |', '|---|---|' + '---|' * (len(BANDS) + 2)]
        by_old = collections.defaultdict(list)
        for q in got:
            by_old[q.get('difficulty_est')].append(res[q['id']])
        for o in sorted(by_old, key=lambda x: (x is None, x)):
            v = by_old[o]; c = collections.Counter(r['band'] for r in v)
            L.append(f'| {o} | {len(v)} | ' + ' | '.join(str(c[b]) for b in BANDS) + f' | {sum(r["score"] for r in v) / len(v):.1f} | {sum(r["diff1_5"] for r in v) / len(v):.2f} |')
        pairs = [(q['difficulty_est'], res[q['id']]['score']) for q in got if isinstance(q.get('difficulty_est'), (int, float))]
        ch = sum(1 for q in got if isinstance(q.get('difficulty_est'), (int, float)) and q['difficulty_est'] != res[q['id']]['diff1_5'])
        L += ['', f'- 旧 est vs 新分 Spearman ρ = {spearman([a for a, _ in pairs], [b for _, b in pairs]):.3f}（n={len(pairs)}）；est 值变动 {ch} 题。']
        # 锚定：题源自带难度
        if st == 'open':
            an = [(int(q['difficulty_src']), res[q['id']]['score'], int(q['part'])) for q in got if str(q.get('difficulty_src')) in ('400', '600', '800')]
            if an:
                L.append(f'- **锚定（kdeppaei 题源自带 400/600/800 级）**：与 LLM 分 Spearman ρ = {spearman([a for a, _, _ in an], [b for _, b, _ in an]):.3f}（n={len(an)}）；分 Part：' +
                         '，'.join(f'P{p} ρ={spearman([a for a, _, pp in an if pp == p], [b for _, b, pp in an if pp == p]):.2f}' for p in (5, 6, 7)))
                lv = collections.defaultdict(list)
                for a, b, _ in an:
                    lv[a].append(b)
                L.append('  - 各级 LLM 均分：' + '，'.join(f'{k}级 {sum(v) / len(v):.1f}（n={len(v)}）' for k, v in sorted(lv.items())))
        else:
            an = [(q['difficulty_est'], res[q['id']]['score'], src_label(q)) for q in got if q.get('difficulty_src') == 'source' and isinstance(q.get('difficulty_est'), (int, float))]
            if an:
                L.append(f'- **锚定（私有 {len(an)} 道题源自带 difficulty）**：与 LLM 分 Spearman ρ = {spearman([a for a, _, _ in an], [b for _, b, _ in an]):.3f}，Pearson r = {pearson([a for a, _, _ in an], [b for _, b, _ in an]):.3f}；分题源：' +
                         '，'.join(f'{s} ρ={spearman([a for a, _, ss in an if ss == s], [b for _, b, ss in an if ss == s]):.2f}(n={sum(1 for x in an if x[2] == s)})' for s in sorted({x[2] for x in an})))
        # 特征均值
        L += ['', '### 特征 × 档（均值）', '', '| 档 | 干扰项 0–3 | 句法 1–3 | 用时 s | 跨句/跨段/跨篇占比 | 推断/NOT/插入占比 | C1+ 词占比 |', '|---|---|---|---|---|---|---|']
        for b in BANDS:
            v = [res[q['id']]['features'] for q in got if res[q['id']]['band'] == b]
            if not v:
                continue
            m = lambda k: sum(num(f.get(k), 0) for f in v) / len(v)
            L.append(f'| {b} | {m("distractor"):.2f} | {m("syntax"):.2f} | {m("time_sec"):.0f} | '
                     f'{100 * sum(f.get("locate") in ("cross_sentence", "cross_paragraph", "cross_doc") for f in v) / len(v):.0f}% | '
                     f'{100 * sum(f.get("reasoning") in ("inference", "not_true", "insertion", "cross_ref") for f in v) / len(v):.0f}% | '
                     f'{100 * sum(str(f.get("cefr", "")).upper().startswith("C") for f in v) / len(v):.0f}% |')
        # 缺口
        L += ['', f'### 缺口：题型 × 档（{name}；<20 标红；规格目标公开池每档每题型 ≥30）', '',
              '| 题型 | ' + ' | '.join(BANDS) + ' | 合计 | 缺口（补到 20 / 补到 30） |', '|---|' + '---|' * (len(BANDS) + 2)]
        tg = collections.defaultdict(collections.Counter)
        for q in got:
            tg[qtype(q['node'])][res[q['id']]['band']] += 1
        need20 = need30 = 0
        for t in sorted(tg, key=lambda t: (t[:2], -sum(tg[t].values()))):
            c = tg[t]; g20 = sum(max(0, 20 - c[b]) for b in BANDS); g30 = sum(max(0, 30 - c[b]) for b in BANDS)
            need20 += g20; need30 += g30
            L.append(f'| {t} | ' + ' | '.join(red(c[b]) for b in BANDS) + f' | {sum(c.values())} | {g20} / {g30} |')
        L += ['', f'- 合计需补：到每格 20 题 {need20} 题；到每格 30 题 {need30} 题。', '']
        if st == 'open':
            L += ['### 原创难题补充需求（公开池，按缺口排序前 20 格）', '', '| 题型 | 档 | 现有 | 补到 30 |', '|---|---|---|---|']
            cells = sorted(((30 - tg[t][b], t, b) for t in tg for b in BANDS if tg[t][b] < 30), reverse=True)[:20]
            for g, t, b in cells:
                L.append(f'| {t} | {b} | {tg[t][b]} | {g} |')
            L.append('')
        # 章节分布
        cc = collections.Counter(res[q['id']]['chapter'][0] for q in got if res[q['id']]['chapter'])
        L += ['### 手册主章分布', '', ' / '.join(f'第{k}章 {v}' for k, v in sorted(cc.items())), '']
    return '\n'.join(L) + '\n'


def main():
    sets = {}
    for st in ('open', 'private'):
        items, rs = load_set(st)
        if items is None:
            continue
        res, stat = rs
        ids = {q['id'] for q in items}
        res = {k: v for k, v in res.items() if k in ids}
        sets[st] = (items, res, stat)
        outp = os.path.join(ROOT, 'data/difficulty/difficulty_v2_open.json' if st == 'open' else 'private_data/difficulty/difficulty_v2_private.json')
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        meta = {'version': 'v2', 'spec': 'docs/ux/UX_SPEC_v2.md §6', 'model': 'deepseek-v4.1-flash',
                'bands': {'基础': '<500 (score<35)', '进阶': '500-650 (35-54)', '熟练': '650-800 (55-74)', '真考+': '800+ (>=75)'},
                'diff1_5': '<25:1, 25-39:2, 40-54:3, 55-69:4, >=70:5', 'n_items': len(items), 'n_rated': len(res)}
        json.dump({'meta': meta, 'items': res}, open(outp, 'w'), ensure_ascii=False, separators=(',', ':'))
        print(st, 'items', len(items), 'rated', len(res), dict(stat), collections.Counter(v['band'] for v in res.values()))
    rp = os.path.join(ROOT, 'docs/review/difficulty_v2_report.md')
    open(rp, 'w').write(report(sets))
    print('report', rp)


if __name__ == '__main__':
    main()
