"""A3 中文解析：共用工具（公开/私有题通用）。

工作流（可断点续做）：
  1. python3 work/explain/dump.py --pool open --n 40        # 打印下一批未完成题（P6/P7 按 bundle 带原文）
  2. 人工（agent）按下面的“行格式”写解析到 authored_<pool>/batch_XXX.txt
  3. python3 work/explain/merge.py --pool open             # 解析+校验所有 authored 文件 → 输出 JSON + flags + 进度
  已完成 id 记在 state_<pool>.json（由 merge 重算，幂等）。

行格式（一题一行，字段用 | 分隔；# 开头为注释）：
  ID | 答案字母 | 依据 | 为什么 | 错项 | 记一招 | 同义替换
  - 答案字母：作者独立判断的答案；与 item.answer_letter 不一致 → 进 flags，不写解析。
  - 依据：英文原句片段（≤12 词；可用 … 连两段），必须能在题干/原文中找到（___ 代表空格）。
           可在片段后加“ —— 中文注”。
  - 错项：A:理由;B:理由  可合并 BD:理由。必须覆盖且只覆盖 3 个错误选项。
  - 记一招：≤20 字；留空=不写；写 - =用该题考点的默认招（strategies_v2 默认表）；
           可在末尾加 @S2-XX-NN 指定技巧 id。
  - 同义替换（P7）：原文短语=>选项短语;原文2=>选项2 （原文短语须在原文中出现）
  - FLAG 行：ID | FLAG | 原因   （答案有问题/题目有缺陷，不硬写）
"""
import json, os, re, hashlib, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))

POOLS = {
    'open': {
        'items': ['data/items_pilot_v1.json', 'data/items_open_maximcuynat.json', 'data/items_open_kdeppaei.json'],
        'authored': os.path.join(HERE, 'authored_open'),
        'state': os.path.join(HERE, 'state_open.json'),
        'out': 'data/explanations/zh_open_v1.json',
        'flags': 'data/explanations/zh_open_v1_flags.json',
    },
    'private': {
        'items': ['private_data/items/items_private_v1.json'],
        'authored': os.path.join(ROOT, 'private_data', 'work_private', 'explain', 'authored'),
        'state': os.path.join(ROOT, 'private_data', 'work_private', 'explain', 'state_private.json'),
        'out': 'private_data/explanations/zh_private_v1.json',
        'flags': 'private_data/explanations/zh_private_v1_flags.json',
    },
}
LET = 'ABCD'


def load_pool(pool):
    items, bundles = [], {}
    for f in POOLS[pool]['items']:
        d = json.load(open(os.path.join(ROOT, f)))
        for it in d['items']:
            it['_file'] = f
            items.append(it)
        for b in d.get('bundles', []):
            bundles[b['bundle_id']] = b
    return items, bundles


def item_hash(it, bundles):
    b = bundles.get(it.get('bundle_id'))
    blob = json.dumps([it.get('stem'), it.get('q'), it['options'], it['answer'],
                       [x['text'] for x in b['docs']] if b else None], ensure_ascii=False)
    return hashlib.sha1(blob.encode()).hexdigest()[:12]


def norm(s):
    s = s.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2013', '-').replace('\u2014', '-')
    s = re.sub(r'-{3,}|_{2,}|\[\d\]|\(\d\)', ' ___ ', s)
    s = re.sub(r'[^a-z0-9_$%]+', ' ', s.lower())
    return ' '.join(s.split())


def source_text(it, bundles):
    parts = [it.get('stem') or '', it.get('q') or ''] + list(it['options'])
    b = bundles.get(it.get('bundle_id'))
    if b:
        for x in b['docs']:
            parts += [x.get('header') or '', x.get('title') or '', x.get('text') or '']
    return norm(' \n '.join(parts))


def passage_text(it, bundles):
    b = bundles.get(it.get('bundle_id'))
    parts = [it.get('stem') or '']
    if b:
        for x in b['docs']:
            parts += [x.get('header') or '', x.get('text') or '']
    return norm(' '.join(parts))


# ---------- 技巧映射 ----------
_STRAT = None

def strategies():
    global _STRAT
    if _STRAT is None:
        s = json.load(open(os.path.join(ROOT, 'data/strategies/strategies_v2.json')))
        order = {sid: i for i, sid in enumerate(s['min_sets']['600'])}
        _STRAT = (s['entries'], order)
    return _STRAT


def strategy_for(node_ids):
    entries, order = strategies()
    for n in node_ids:
        if n.startswith(('VO.', 'TX.', 'FD.')):
            continue
        cands = [e for e in entries if n in e['graph_nodes']]
        if cands:
            cands.sort(key=lambda e: (order.get(e['id'], 99), e['roi'], -e['weight']))
            return cands[0]['id']
    return None


# 每条技巧的默认“记一招”（≤20 字，自写）
DEFAULT_TIPS = {
    'S2-P5-01': '先看选项，再决定读多少',
    'S2-P5-02': '词尾不同→只看空格前后',
    'S2-P5-03': '先练词性和介连词',
    'S2-P5-04': '-tion名 -ive形 -ly副',
    'S2-P5-05': '读三遍没思路就涂',
    'S2-P5-06': '没搭配线索就涂走人',
    'S2-P5-07': '词汇题先找搭配',
    'S2-P5-08': '跟名词用介词，跟句子用连词',
    'S2-P5-09': '去掉枝叶看主干',
    'S2-P5-10': '缺谓语才填动词',
    'S2-P5-11': '谓语→主被动→时态→单复数',
    'S2-P5-12': '介词先想固定搭配',
    'S2-P5-13': '代词先看位置定形式',
    'S2-P5-14': '名词再分人/物、单/复',
    'S2-P5-15': '熟词先想商务义',
    'S2-P5-18': '关系词：看先行词和缺啥',
    'S2-P5-19': 'than比较级，the最高级',
    'S2-P5-20': '自己做-ing，被做-ed',
    'S2-P5-21': '先看动词后面跟什么',
    'S2-P5-22': '先看数量词再定单复数',
    'S2-P5-23': '副词按作用选',
    'S2-P5-24': '看到both/either找另一半',
    'S2-P5-25': 'suggest that 后用原形',
    'S2-P6-01': '本句能做的按P5秒做',
    'S2-P6-02': '600档插入句直接涂',
    'S2-P6-03': 'P6顺着读全文',
    'S2-P6-04': '插入句放最后做',
    'S2-P6-05': '时态看信件日期和时间线',
    'S2-P6-06': '先判转折/因果/补充',
    'S2-P6-07': '词汇看整篇在讲啥',
    'S2-P6-08': '盯住this/they/also接谁',
    'S2-P6-09': '代词往前找指谁',
    'S2-P6-10': '按空的位置猜句型',
    'S2-P7-01': '先看题，再进文章找',
    'S2-P7-02': '拿人名数字当路标',
    'S2-P7-03': '目的题看第一段',
    'S2-P7-06': '答案常换个说法',
    'S2-P7-07': 'NOT题放最后做',
    'S2-P7-08': '推断也要原文撑腰',
    'S2-P7-09': '同义词代回原句读',
    'S2-P7-10': '先认文体再找位置',
    'S2-P7-13': '题序≈文序',
    'S2-P7-14': 'NOT题逐项核对',
    'S2-P7-15': '绝对词选项先怀疑',
    'S2-P7-16': '先认准问的是谁',
    'S2-P7-17': '细节读两句，推断读一段',
    'S2-P7-18': '意图题看上一条消息',
    'S2-P7-19': '条件一篇、数据一篇',
    'S2-P7-20': '先看每题问哪一篇',
    'S2-P7-23': '先读待插句猜前文',
    'S2-P7-24': '邮件留意附件和职位',
    'S2-P7-25': 'although后面常是考点',
}


def tip_len(t):
    # 中文字符算 1，英文单词算 1（粗略）
    zh = len(re.findall(r'[\u4e00-\u9fff，。、；：？！“”（）→]', t))
    en = len(re.findall(r'[A-Za-z0-9]+', t))
    return zh + en


def parse_line(line):
    parts = [p.strip() for p in line.split('|')]
    return parts


def parse_distractors(s, answer_letter):
    out, errs = {}, []
    for seg in [x.strip() for x in re.split(r'[;；]\s*(?=[A-D]{1,3}\s*[:：])', s) if x.strip()]:
        m = re.match(r'^([A-D]{1,3})\s*[:：]\s*(.+)$', seg, re.S)
        if not m:
            errs.append('错项格式: ' + seg[:30]); continue
        for L in m.group(1):
            if L in out:
                errs.append('错项重复 ' + L)
            out[L] = m.group(2).strip().rstrip(';；')
    need = set(LET) - {answer_letter}
    if set(out) != need:
        errs.append('错项字母 %s ≠ 应为 %s' % (''.join(sorted(out)), ''.join(sorted(need))))
    return out, errs


def check_quote(q, src):
    """英文片段每段都能在 src 中找到；返回 (ok, n_words)。"""
    segs = [s for s in re.split(r'…|\.\.\.', q) if s.strip()]
    nw = 0
    for s in segs:
        ns = norm(s)
        nw += len([w for w in s.split() if not re.fullmatch(r'_+|-{3,}|\[\d\]', w) and re.search(r'\w', w)])
        if ns and ns not in src:
            return False, nw
    return True, nw
