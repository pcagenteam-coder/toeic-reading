#!/usr/bin/env python3
"""C2：给 graph_v1 补排程字段 → data/graph_v1_cost.json（build.py 合并，不改 graph_v1.json 本体）。

产出字段（每个节点，含分组节点）：
  learn_cost_min   学会估计分钟（从 0 练到本档目标掌握度，含练习+复习；规则见 COST_RULES 与 graph_v1_cost.md）
  cost_basis       该成本用的哪条规则
  must_for_band    哪些目标档必须掌握：子集 of ["≤500","600","730","860+"]
  must_note        覆盖规则说明（为什么某档被移出/提入）
另补 2 个遗留节点（strategies_v2 suggested_new_node）：ST.ORDER.TEXT_TYPE_TRIAGE、ST.REVIEW.PARAPHRASE_LOG。

用法：python3 data/graph_v1_cost_build.py   （幂等，纯规则，无随机）
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = json.load(open(os.path.join(ROOT, 'data/graph_v1.json'), encoding='utf-8'))
S = json.load(open(os.path.join(ROOT, 'data/strategies/strategies_v2.json'), encoding='utf-8'))

BANDS = ['≤500', '600', '730', '860+']
BASE_IDX = {400: 0, 600: 1, 700: 2, 800: 3, 900: None}   # 900 段（满分冲刺）任何档都不列为必须

# ---------- 遗留节点 ----------
EXTRA_NODES = [
    {'id': 'ST.ORDER.TEXT_TYPE_TRIAGE', 'name_zh': '按文体决定做不做（跳篇不跳序）', 'layer': 'strategy', 'parent': 'ST.ORDER',
     'prereqs': ['ST.GIVEUP.NO_BLANK', 'FD.READ.SKIM'], 'target_band': 400, 'is_group': False, 'parts': [7],
     'exam_weight': 0.3,
     'exam_weight_source': {'type': 'impact_estimate', 'type_zh': '影响面估计（无直接题数的能力/技巧节点）', 'est_items_per_test': None,
                            'note': '低分档跳过长篇报道（P7 article 约 9 题/卷）换时间给短篇；按影响面估计'},
     'description_zh': '低中分档按文体决定做不做：短信/群聊、通知、表格、广告认真做；长篇报道（article）整篇涂掉往下走，不回头挑（S2-P7-05 / SL11-11）。',
     'example_pattern': 'Questions 165-168 refer to the following article. → 600 档整篇涂 B，继续 169 题',
     'mapped_from_v0': [], 'delivery': 'user', 'added_by': 'C2 (graph_v1_cost.json)'},
    {'id': 'ST.REVIEW.PARAPHRASE_LOG', 'name_zh': '记“改写对”（原文↔选项同义替换本）', 'layer': 'strategy', 'parent': 'ST.REVIEW',
     'prereqs': ['ST.REVIEW.VOCAB_FROM_ITEMS', 'VO.PARA.WORD_SYNONYM'], 'target_band': 400, 'is_group': False, 'parts': [7],
     'exam_weight': 0.3,
     'exam_weight_source': {'type': 'impact_estimate', 'type_zh': '影响面估计（无直接题数的能力/技巧节点）', 'est_items_per_test': None,
                            'note': '正确选项约 70% 为原文改写；由 App 自动生成改写对卡片（delivery=engine）'},
     'description_zh': '做错/做慢的 P7 题，把原文说法和正确选项说法记成一对（purchase ↔ buy），用 FSRS 复习（S2-P7-12 / SL11-15）。',
     'example_pattern': 'complimentary breakfast ↔ free morning meal',
     'mapped_from_v0': [], 'delivery': 'engine', 'added_by': 'C2 (graph_v1_cost.json)'},
]
nodes = G['nodes'] + EXTRA_NODES
ND = {n['id']: n for n in nodes}

# ---------- 学会成本（分钟） ----------
BAND_MULT_GR = {400: 1.0, 600: 1.3, 700: 1.6, 800: 2.0, 900: 2.4}   # 语法：段位越高越绕
BAND_MULT_QT = {400: 1.0, 600: 1.15, 700: 1.3, 800: 1.5, 900: 1.7}  # 题型/文本：方法相近，量变为主
EXPLICIT = {   # 个别节点（能力型/长期型）直接给值
    'FD.SENT.CORE': (40, '句型识别：约 4 次 10 分钟练习'), 'FD.SENT.CLAUSE_COUNT': (30, '规则少'), 'FD.SENT.MODIFIER_STRIP': (30, '规则少'),
    'FD.SENT.LONG': (90, '长难句需大量精读'),
    'FD.READ.CHUNK': (60, '意群顺读需反复练'), 'FD.READ.SPEED_150': (600, '阅读提速是长期量变（约 10 小时有效阅读）'),
    'FD.READ.SPEED_200': (900, '长期量变'), 'FD.READ.SCAN': (30, '技巧型'), 'FD.READ.SKIM': (30, '技巧型'),
    'FD.READ.UNKNOWN_WORD': (20, '习惯型'), 'FD.READ.REFERENCE': (40, '指代追踪'), 'FD.READ.DISCOURSE': (40, '逻辑信号词'),
    'FD.VOC.NGSL_CORE': (1500, '约 2,800 词 × 约 0.5 分钟（含复习）'), 'FD.VOC.AFFIX': (60, '常用词缀约 40 个'),
    'VO.BAND.B600': (900, '600 段词表（约 1,500 词）'), 'VO.BAND.B730': (1200, '730 段词表'), 'VO.BAND.B860': (1500, '860 段词表'),
    'VO.BAND.B990': (1800, '990 段词表'), 'VO.TITLES_DEPTS': (30, '约 60 个职位/部门名'),
    'QT.P5.IDENTIFY': (10, '看选项判题型：一条规则'), 'QT.P5.VOCAB': (40, '词汇题：靠词量，单独练只学“找搭配/一眼不会就涂”'),
    'QT.P6.CLASSIFY': (10, '两类分流：一条规则'), 'QT.P6.INSERTION': (45, '插入句：最难题，需篇章理解'),
    'TX.DOUBLE': (40, '双篇：结构+对照'), 'TX.TRIPLE': (60, '三篇：结构+对照+图表'), 'TX.MULTI': (40, '多篇总述'),
    'QT.P7X.CROSS_REF.DOUBLE': (40, '跨篇对照（双）'), 'QT.P7X.CROSS_REF.TRIPLE': (60, '跨篇对照（三）'), 'QT.P7.CROSS_REF': (45, '跨篇对照'),
    'ST.TIME.TOTAL_PLAN': (30, '配速：需 1–2 次限时练'), 'ST.REVIEW.TIMED_MOCK': (90, '一次整卷 75 分钟 + 复盘'),
    'ST.REVIEW.SPEED_REPEAT': (60, '复读提速'), 'ST.REVIEW.AUDIO_SHADOW': (60, '跟读'), 'ST.REVIEW.ERROR_CAUSE_LOG': (20, '错因分类'),
}


def cost_of(n):
    i, L, b = n['id'], n['layer'], n['target_band']
    if i in EXPLICIT:
        return EXPLICIT[i]
    if L == 'grammar':
        return round(25 * BAND_MULT_GR[b]), f'语法考点 25 分钟 × 段位系数 {BAND_MULT_GR[b]}'
    if L == 'vocab':
        if i.startswith('VO.SCENE.'):
            return round(45 * BAND_MULT_QT[b]), f'场景词包约 40–60 词 × 段位系数 {BAND_MULT_QT[b]}'
        if i.startswith('VO.LEX.'):
            return 30, '同词性词汇题：找搭配法 + 高频词'
        if i.startswith('VO.PARA.'):
            return round(15 * BAND_MULT_QT[b]), f'改写类型 15 分钟 × 段位系数 {BAND_MULT_QT[b]}'
        return round(25 * BAND_MULT_QT[b]), f'搭配/易混 25 分钟 × 段位系数 {BAND_MULT_QT[b]}'
    if L == 'qtype':
        m = BAND_MULT_QT[b]
        if i.startswith('QT.P5.'):
            return round(15 * m), f'P5 题型 15 分钟 × {m}'
        if i.startswith('QT.P6.'):
            return round((15 if i.startswith('QT.P6.INS_') else 20) * m), f'P6 题型 {15 if i.startswith("QT.P6.INS_") else 20} 分钟 × {m}'
        if i.startswith('QT.P7X.'):
            base = 30 if re.search(r'\.(TRIPLE|MULTI)$', i) else 20 if i.endswith('.DOUBLE') else 12
            return round(base * m), f'P7 设问×文本组合（父题型已学，只学增量）{base} 分钟 × {m}'
        return round(30 * m), f'P7 设问类型 30 分钟 × {m}'
    if L == 'texttype':
        base = 12 if n.get('parent') == 'TX.FORM' else 15
        return round(base * BAND_MULT_QT[b]), f'文本类型熟悉 {base} 分钟 × {BAND_MULT_QT[b]}'
    if L == 'strategy':
        return 10, '工作规则卡：读懂 + 2–3 次练习中用上'
    if L == 'foundation':
        return 40, '基础能力默认'
    return 20, '默认'


# ---------- must_for_band：基础 = 节点段位起累积；再按 strategies_v2 冲突裁决覆盖 ----------
LOW = ['≤500', '600']
GR_LOW_ALLOWED = {'GR.CONN.PREP_TIME', 'GR.CONN.PREP_PLACE', 'GR.CONN.PREP_MEANING', 'GR.CONN.PREP_VS_CONJ',
                  'GR.CONN.CONJ_ADVERBIAL', 'GR.CONN.CONJ_COORD', 'GR.CONN.CONJ_ADVERB'}
QT_LOW_OFF = {'QT.P5.VERB_FORM', 'QT.P5.PRONOUN', 'QT.P5.RELATIVE', 'QT.P5.COMPARATIVE', 'QT.P5.PAIR_GRAMMAR',
              'QT.P6.CTX_TENSE', 'QT.P6.CTX_PRONOUN'}


def off_rules(n):
    """返回 {band: 原因}：该档明确不必学（放弃/后移规则，优先于任何提入）"""
    i, L, off = n['id'], n['layer'], {}
    def put(bands, why):
        for b in bands:
            off.setdefault(b, why)
    if L == 'grammar' and not n['is_group'] and not (i.startswith('GR.POS.') or i in GR_LOW_ALLOWED):
        put(LOW, 'C8/S2-P5-03：600 及以下语法只练词性位置 + 介词/连词，其余语法移到 730+')
    if i in QT_LOW_OFF:
        put(LOW, 'C8/S2-P5-03：该题型依赖动词形态/代词/关系词/比较等，600 及以下按限时规则猜')
    if i.startswith('QT.P6.INS') or i == 'QT.P7.INSERTION' or i.startswith('QT.P7X.INSERTION.'):
        put(LOW, 'C3/S2-P6-02：600 及以下插入句直接涂')
    multi = i in ('TX.MULTI', 'TX.DOUBLE', 'TX.TRIPLE', 'QT.P7.CROSS_REF') or bool(re.search(r'^QT\.P7X\..*\.(DOUBLE|TRIPLE|MULTI)$', i))
    if multi:
        put(LOW, 'C2/S2-ALL-02：600 及以下 P7 终点线 Q175（单篇做完），多篇统一涂')
    if i == 'TX.TRIPLE' or i.endswith('.TRIPLE'):
        put(['730'], 'C2/S2-ALL-02：730 档终点线 Q185（双篇做完），三篇统一涂')
    if i == 'TX.ARTICLE' or re.search(r'^QT\.P7X\..*\.ARTICLE$', i):
        put(LOW, 'S2-P7-05：600 及以下遇长篇报道整篇涂掉（跳篇不跳序）')
    if n['target_band'] == 900:
        put(BANDS, '900 段（满分冲刺）考点：考频极低，任何档都不列为必须')
    return off


# 最小技巧集里的用户条目：其 qtype/strategy/skill 节点若只高一档，提入该档（与 strategies_v2 min_sets 一致）
E = {e['id']: e for e in S['entries']}
for e in S['entries']:   # 遗留节点绑定
    sn = (e.get('suggested_new_node') or '').split('（')[0]
    if sn in ND:
        e.setdefault('_extra_nodes', []).append(sn)
PROMOTE = {b: {} for b in BANDS}
for b in BANDS:
    for sid in S['min_sets'][b]:
        e = E[sid]
        if e.get('delivery') != 'user':
            continue
        for x in e['qtype_nodes'] + e['strategy_nodes'] + e['skill_nodes'] + e.get('_extra_nodes', []):
            PROMOTE[b].setdefault(x, sid)

out, notes = {}, {}
for n in nodes:
    i = n['id']; off = off_rules(n); bi = BASE_IDX[n['target_band']]
    must, nt = [], []
    for k, b in enumerate(BANDS):
        if b in off:
            continue
        if bi is not None and bi <= k:
            must.append(b)
        elif i in PROMOTE[b] and bi is not None and bi == k + 1 and not any(b in off_rules(ND[p]) for p in n['prereqs']):
            must.append(b); nt.append(f'{b}：由最小技巧集 {PROMOTE[b][i]} 提入')
    for b, why in off.items():
        if bi is not None and bi <= BANDS.index(b):
            nt.append(f'{b}：移出（{why}）')
    out[i] = must; notes[i] = nt

# 前置闭包：必须节点的叶前置若未被放弃规则移出，也列为必须；被移出的前置记为“豁免”
changed = True
while changed:
    changed = False
    for n in nodes:
        for b in out[n['id']]:
            for p in n['prereqs']:
                pn = ND[p]
                if pn['is_group'] or b in out[p]:
                    continue
                if b in off_rules(pn) or cost_of(pn)[0] >= 300:
                    w = f'{b}：前置 {p} ' + ('已按放弃规则移出' if b in off_rules(pn) else '是长期能力（≥300 分钟，靠日常练习自然提升）') + '，豁免'
                    if w not in notes[n['id']]:
                        notes[n['id']].append(w)
                    continue
                out[p] = sorted(set(out[p]) | {b}, key=BANDS.index); changed = True
                notes[p].append(f'{b}：作为 {n["id"]} 的前置补入')

# 分组节点：任一子节点必须 → 该档必须
children = {}
for n in nodes:
    if n.get('parent'):
        children.setdefault(n['parent'], []).append(n['id'])
def grp(i):
    if not ND[i]['is_group']:
        return set(out[i])
    s = set()
    for c in children.get(i, []):
        s |= grp(c)
    return s
for n in nodes:
    if n['is_group']:
        out[n['id']] = sorted(grp(n['id']), key=BANDS.index)

res = {'version': 'graph_v1_cost 1.0', 'built_by': 'data/graph_v1_cost_build.py', 'graph': 'data/graph_v1.json ' + G.get('built', ''),
       'bands': BANDS,
       'band_from_total': {'≤500': '目标总分 ≤550', '600': '551–665', '730': '666–795', '860+': '≥796'},
       'mastery_target': {'≤500': 0.6, '600': 0.7, '730': 0.8, '860+': 0.88},
       'cost_note': 'learn_cost_min = 从 0 练到本档目标掌握度的估计分钟（含练习与复习），按层/类型规则 × 段位系数；分组节点的值是“作为练习目标时自身的成本”，不含子节点。计划器用 剩余成本 = learn_cost_min × 缺口比例。',
       'extra_nodes': EXTRA_NODES,
       'nodes': {}}
for n in nodes:
    c, basis = cost_of(n)
    res['nodes'][n['id']] = {'learn_cost_min': c, 'cost_basis': basis, 'must_for_band': out[n['id']], 'must_note': notes[n['id']]}
json.dump(res, open(os.path.join(ROOT, 'data/graph_v1_cost.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 摘要
leaf = [n for n in nodes if not n['is_group']]
print('nodes', len(nodes), 'leaves', len(leaf))
for b in BANDS:
    m = [n for n in leaf if b in out[n['id']]]
    print(b, 'must leaves', len(m), 'cost h', round(sum(cost_of(n)[0] for n in m) / 60, 1))
