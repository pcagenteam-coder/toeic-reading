#!/usr/bin/env python3
"""TOEIC 阅读题自动审题（现行新制）。
用法：python3 work/item_audit.py [items.json] [--md report.md] [--json report.json]
检查：超纲词（NGSL+TSL lemma，专名/数字/星期月份除外，允许简单屈折）、四选项格式、答案字段、答案分布、
近似重复（与 items_v0、自身、data/external/toeic_items 参考题库）、P6/P7 bundle 建模与题号/题数、长度范围、
节点/模板合法性、意图题/同义词题/插入题的文本一致性。"""
import json, re, sys, os, csv, glob, collections, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 仓库根（原先写死了旧项目路径）
ap = argparse.ArgumentParser()
ap.add_argument("items", nargs="?", default=f"{ROOT}/data/items_pilot_v1.json")
ap.add_argument("--md"); ap.add_argument("--json")
ap.add_argument("--no-external", action="store_true")
ap.add_argument("--imported", action="store_true", help="第三方导入题（无 template_id/错因/难度等编写字段）：只把结构问题记为不通过，编写规范类（超纲词/篇幅/答案分布）记为警告；不给参数时按 template_id 是否全空自动判断")
A = ap.parse_args()

# ---------- 词表 ----------
def load_lemma(path):
    forms = set()
    for line in open(path, encoding="utf-8-sig", errors="ignore"):
        if line.startswith("##") or not line.strip(): continue
        for w in line.strip().split(","):
            w = w.strip().lower()
            if w: forms.add(w)
    return forms
NGSL = load_lemma(f"{ROOT}/data/wordlists/NGSL_12_lemmatized_for_research.csv")
TSL = load_lemma(f"{ROOT}/data/wordlists/TSL_lemma.csv")
_sup = f"{ROOT}/data/external/wordlists/SUP_lemmatized.csv"  # 星期/月份/数词，视同“数字”豁免（可选文件）
SUP = load_lemma(_sup) if os.path.exists(_sup) else {w for w in "monday tuesday wednesday thursday friday saturday sunday january february march april may june july august september october november december one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion first second third fourth fifth sixth seventh eighth ninth tenth".split()}
VOCAB = NGSL | TSL
EXEMPT = {"mr", "ms", "mrs", "dr", "a.m", "p.m", "e-mail", "e-mails", "re", "it", "inc", "co", "web", "vs", "etc", "ok"}
CONTR = {"n't": "", "'re": "", "'ll": "", "'s": "", "'m": "", "'ve": "", "'d": ""}
IRREG = {"won't": "will", "can't": "can", "shan't": "shall"}

def inflect_ok(w):
    if w in VOCAB: return "list"
    cands = []
    for suf, rep in (("ies", "y"), ("ied", "y"), ("ier", "y"), ("iest", "y"), ("es", ""), ("s", ""), ("ed", ""), ("ed", "e"), ("d", ""),
                     ("ing", ""), ("ing", "e"), ("er", ""), ("er", "e"), ("est", ""), ("est", "e"), ("'s", ""), ("s'", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            b = w[: -len(suf)] + rep
            cands.append(b)
            if len(b) >= 3 and b[-1] == b[-2] and suf in ("ed", "ing", "er", "est"): cands.append(b[:-1])
    for b in cands:
        if b in VOCAB: return "inflection"
    return None

DERIV = (("ly", ""), ("ly", "le"), ("ily", "y"), ("ally", ""), ("ation", "e"), ("ation", ""), ("tion", "te"), ("ion", ""), ("ion", "e"), ("ment", ""),
         ("ness", ""), ("iness", "y"), ("ity", ""), ("ity", "e"), ("ive", "e"), ("ive", ""), ("al", ""), ("able", ""), ("able", "e"), ("er", ""), ("or", ""),
         ("ee", ""), ("ee", "e"), ("ance", ""), ("ance", "e"), ("ence", ""), ("ent", ""), ("ant", ""), ("ful", ""), ("less", ""), ("ize", ""))
def deriv_ok(w):
    for suf, rep in DERIV:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            b = w[: -len(suf)] + rep
            if b in VOCAB or inflect_ok(b): return b
    return None

TITLES = {"Mr", "Ms", "Mrs", "Dr", "St", "Ave"}
def tokens(text):
    """返回 [(token, is_capitalized, is_sentence_initial, next_is_cap, alone_on_line, all_caps)]"""
    raw = []
    prev_end = True
    for m in re.finditer(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]*(?:\.[A-Za-z]\.?)?|[\.\!\?\n:—\[\]\|\"]", text):
        t = m.group(0)
        if re.fullmatch(r"[\.\!\?\n:—\[\]\|\"]", t):
            if t == "." and raw and raw[-1][0] in TITLES: continue
            if t in ".!?\n:—|\"": prev_end = True
            continue
        st = m.start()
        if st > 0 and text[st - 1].isdigit(): continue  # 4th, 2nd
        ls = text.rfind("\n", 0, st) + 1; le = text.find("\n", st); le = len(text) if le < 0 else le
        alone = text[ls:le].strip().rstrip(",") == t
        raw.append([t, t[0].isupper(), prev_end, False, alone, len(t) > 1 and t.isupper()]); prev_end = False
    for i in range(len(raw) - 1):
        raw[i][3] = raw[i + 1][1]
    return [tuple(r) for r in raw]

def normalize(t):
    w = t.lower().replace("’", "'").replace("é", "e").strip("'.-")
    if w in IRREG: return [IRREG[w]]
    for c in CONTR:
        if w.endswith(c) and len(w) > len(c): return [w[: -len(c)]]
    return [w]

def check_vocab(text, allow_derived=False, proper_seen=None, exceptions=()):
    """返回 off_list, derived, proper(假定专名)；exceptions=题目声明并说明理由的豁免词"""
    off, der, prop = [], [], []
    for t, cap, init, nxt_cap, alone, allcaps in tokens(text):
        for w in normalize(t):
            if not w or w in EXEMPT or w in SUP or w in exceptions: continue
            if re.search(r"\d", w): continue
            if inflect_ok(w): continue
            if "-" in w and all((p in VOCAB or inflect_ok(p) or p in SUP) for p in w.split("-") if p): continue
            if cap and (not init or nxt_cap or alone or allcaps or (proper_seen and t in proper_seen)):
                prop.append(t); continue
            b = deriv_ok(w)
            if b and allow_derived: der.append(f"{w}←{b}"); continue
            off.append(w + (f"(派生自 {b})" if b else ""))
    return off, der, prop

def capitalized_midsentence(text):
    return {x[0] for x in tokens(text) if x[1] and not x[2]}

# ---------- 近似重复 ----------
def norm_text(s):
    s = re.sub(r"-{3,}|_{3,}|\[\d\]", " ", s.lower())
    return re.findall(r"[a-z']+", s)
def shingles(ws, n=3): return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)} or {" ".join(ws)}
def jacc(a, b): return len(a & b) / max(1, len(a | b))

def load_external():
    out = []
    base = f"{ROOT}/data/external/toeic_items"
    if not os.path.isdir(base):   # 参考题库只用于查重、不进产物；公开仓库没有时退到本地私有副本（若存在）
        base = f"{ROOT}/private_data/sources/toeic_items"
    for p in glob.glob(f"{base}/*.csv"):
        with open(p, encoding="utf-8", errors="ignore") as f:
            r = csv.reader(f); hdr = next(r, None)
            for row in r:
                if row: out.append((os.path.basename(p), row[0]))
    for p in glob.glob(f"{base}/*.json"):
        try: d = json.load(open(p, encoding="utf-8"))
        except Exception:
            d = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]
        def walk(x):
            if isinstance(x, dict):
                for k in ("question", "questions", "stem", "sentence", "text"):
                    if isinstance(x.get(k), str): out.append((os.path.basename(p), x[k]))
                for v in x.values():
                    if isinstance(v, (list, dict)): walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(d)
    return out

def load_v0():
    d = json.load(open(f"{ROOT}/data/items_v0.json"))
    out = [("v0", x["stem"]) for x in d.get("diagnostic_part5", [])]
    out += [("v0", x["body"]) for x in d.get("inbox", [])]
    out += [("v0", " ".join(x["text_parts"])) for x in d.get("drafts", [])]
    out += [("v0", " ".join(x["thread"])) for x in d.get("urgent", [])]
    for x in d.get("inbox", []):
        out += [("v0", q["q"] + " " + " ".join(q["options"])) for q in x["questions"]]
    return out

def load_pilot():
    p = f"{ROOT}/data/items_pilot_v1.json"
    if os.path.abspath(A.items) == os.path.abspath(p): return []
    d = json.load(open(p))
    out = [("pilot", x["stem"]) for x in d["items"] if x["part"] == 5]
    out += [("pilot", " ".join(dd["text"] for dd in b["docs"])) for b in d["bundles"]]
    return out

# ---------- 主流程 ----------
D = json.load(open(A.items))
G = {n["id"]: n for n in json.load(open(f"{ROOT}/data/graph_v1.json"))["nodes"]}
TPL = {t["template_id"]: t for t in json.load(open(f"{ROOT}/data/templates/item_templates.json"))["templates"]}
items, bundles = D["items"], {b["bundle_id"]: b for b in D.get("bundles", [])}
fails = collections.defaultdict(list); warns = collections.defaultdict(list)
vocab_log = []; derived_log = []; proper_log = collections.Counter()
IMPORTED = A.imported or all(not i.get("template_id") for i in items)
def F(iid, msg): fails[iid].append(msg)
def W(iid, msg): warns[iid].append(msg)
def S(iid, msg): (W if IMPORTED else F)(iid, msg)   # 编写规范类：导入题记警告
# 题型判定：编写题看 template_id 前缀，导入题看节点
NODE_KIND = {"T6.INS": "QT.P6.INSERTION", "T7.INSERTION": "QT.P7.INSERTION", "T7.INTENT": "QT.P7.INTENT", "T7.SYNONYM": "QT.P7.SYNONYM", "CROSS_REF": "CROSS_REF"}
def kind_is(it, key):
    if (it.get("template_id") or "").startswith(key) or (key == "CROSS_REF" and "CROSS_REF" in (it.get("template_id") or "")): return True
    if IMPORTED:
        n = NODE_KIND[key]
        return any(n in x for x in it.get("node_ids", [])) if key == "CROSS_REF" else n in it.get("node_ids", [])
    return False
QUOTE = r"[\"“”]"

# 1 题目字段与格式
ids = collections.Counter(i["id"] for i in items)
for k, v in ids.items():
    if v > 1: F(k, f"id 重复 {v} 次")
for it in items:
    iid = it["id"]
    req = ("id", "part", "node", "node_ids", "options", "answer", "format_version", "qnum", "form") if IMPORTED else \
          ("id", "part", "node", "node_ids", "template_id", "options", "answer", "explain_zh", "distractor_reasons", "difficulty_est", "target_time_sec", "format_version", "qnum")
    for f in req:
        if f not in it: F(iid, f"缺字段 {f}")
    if it.get("format_version") != "current": F(iid, "format_version 不是 current")
    opts = it.get("options", [])
    if len(opts) != 4: F(iid, f"选项数 {len(opts)} ≠ 4")
    if len(set(o.strip().lower() for o in opts)) != len(opts): F(iid, "选项有重复")
    if any(not str(o).strip() for o in opts): F(iid, "空选项")
    a = it.get("answer")
    if not isinstance(a, int) or not 0 <= a <= 3: F(iid, f"answer 非法: {a}")
    elif it.get("answer_letter") and it["answer_letter"] != "ABCD"[a]: F(iid, "answer_letter 与 answer 不一致")
    dr = it.get("distractor_reasons", {})
    if isinstance(a, int) and 0 <= a <= 3 and not IMPORTED:
        need = {"ABCD"[i] for i in range(4) if i != a}
        if set(dr) != need: F(iid, f"干扰项错因应覆盖 {sorted(need)}，实际 {sorted(dr)}")
        if "ABCD"[a] in dr: F(iid, "正确选项被写了错因（唯一答案冲突）")
    if IMPORTED:
        if not str(it.get("explain_zh") or it.get("explain_en") or "").strip(): F(iid, "缺解析（explain_zh/explain_en 都空）")
    else:
        if not str(it.get("explain_zh", "")).strip(): F(iid, "缺中文解析")
        if not 1 <= it.get("difficulty_est", 0) <= 5: F(iid, "difficulty_est 不在 1–5")
    for n in it.get("node_ids", []):
        if n not in G: F(iid, f"未知节点 {n}")
    if it.get("node") not in it.get("node_ids", []): F(iid, "node 不在 node_ids 中")
    t = TPL.get(it.get("template_id"))
    if IMPORTED and not it.get("template_id"):
        if it["part"] == 7 and "QT.P7.INSERTION" in it.get("node_ids", []) and opts != ["[1]", "[2]", "[3]", "[4]"]: F(iid, "插入题选项必须为 [1]–[4]")
    elif not t: F(iid, f"未知模板 {it.get('template_id')}")
    else:
        if t["part"] != it["part"]: F(iid, "模板 Part 与题目 Part 不一致")
        if t.get("meta_tag_only"): F(iid, "使用了仅作标签的模板")
        if t.get("fixed_options") and opts != t["fixed_options"]: F(iid, "插入题选项必须为 [1]–[4]")
        for tr in dr.values():
            if tr.get("trap") not in json.load(open(f"{ROOT}/data/templates/item_templates.json"))["trap_types"]:
                F(iid, f"未知干扰套路 {tr.get('trap')}")
    p = it["part"]
    if p == 5:
        if it.get("stem", "").count("-------") != 1: F(iid, "P5 题干必须恰有一个 -------")
        if it.get("bundle_id"): F(iid, "P5 不应有 bundle_id")
        if not 101 <= it["qnum"] <= 130: F(iid, "P5 题号应在 101–130")
    else:
        if not it.get("bundle_id") or it["bundle_id"] not in bundles: F(iid, "P6/P7 必须挂在存在的 bundle_id 上")
        if p == 7 and not it.get("q"): F(iid, "P7 缺题干 q")
    # 选项长度均衡（P7：正确项不得明显最长）
    if p == 7 and len(opts) == 4 and isinstance(a, int) and not (t and t.get("fixed_options")) and opts[0] != "[1]":
        L = [len(o.split()) for o in opts]
        if L[a] == max(L) and L[a] >= 2 * sorted(L)[1] and L[a] - sorted(L)[1] >= 4: W(iid, f"正确项明显最长 {L}")

# 2 词汇
for it in items:
    iid = it["id"]
    tid = it.get("template_id") or ""
    allow = it["part"] in (5, 6) and (any(k in tid for k in ("WORD_FORM", "VERB_FORM", "INDEPENDENT")) or
                                      (IMPORTED and any(k in it["node"] for k in ("WORD_FORM", "VERB_FORM", "INDEPENDENT"))))
    texts = [it.get("stem", ""), it.get("q", "")]
    ctx = ""
    if it.get("bundle_id") in bundles:
        ctx = " ".join(d.get("header", "") + " " + d.get("title", "") + " " + d["text"] for d in bundles[it["bundle_id"]]["docs"])
    seen = capitalized_midsentence(" ".join(texts) + " " + ctx + " " + " ".join(it["options"]))
    for txt in texts:
        off, der, prop = check_vocab(txt, False, seen, set(it.get("vocab_exceptions", {})))
        for w in off: S(iid, f"超纲词（题干）: {w}"); vocab_log.append((iid, "stem", w))
        proper_log.update(prop)
    exc = set(it.get("vocab_exceptions", {}))
    for o in it["options"]:
        off, der, prop = check_vocab(o, allow, seen, exc)
        for w in off: S(iid, f"超纲词（选项）: {w}"); vocab_log.append((iid, "option", w))
        derived_log += [(iid, x) for x in der]; proper_log.update(prop)
for bid, b in bundles.items():
    alltext = " ".join(d.get("header", "") + "\n" + d.get("title", "") + "\n" + d["text"] for d in b["docs"])
    seen = capitalized_midsentence(alltext)
    off, der, prop = check_vocab(alltext, False, seen)
    for w in off: S(bid, f"超纲词（文章）: {w}"); vocab_log.append((bid, "passage", w))
    proper_log.update(prop)

# 3 bundle / 题号 / 题数（现行新制）
by_b = collections.defaultdict(list)
for it in items:
    if it.get("bundle_id"): by_b[it["bundle_id"]].append(it)
for bid, b in bundles.items():
    its = sorted(by_b.get(bid, []), key=lambda x: x["qnum"])
    qn = [x["qnum"] for x in its]
    if qn != b.get("qnums"): F(bid, f"bundle qnums {b.get('qnums')} 与题目题号 {qn} 不一致")
    if qn and qn != list(range(qn[0], qn[0] + len(qn))): F(bid, "bundle 内题号不连续")
    alltext = "\n".join(d["text"] for d in b["docs"])
    words = len(re.findall(r"[A-Za-z0-9$']+", alltext))
    if b["part"] == 6:
        if len(its) != 4: F(bid, f"P6 每篇应 4 题，实际 {len(its)}")
        ins = [x for x in its if kind_is(x, "T6.INS")]
        if len(ins) != 1: F(bid, f"P6 每篇应恰有 1 道句子插入，实际 {len(ins)}")
        for k in range(1, 5):
            if alltext.count(f"[{k}]") != 1: F(bid, f"空格标记 [{k}] 出现 {alltext.count(f'[{k}]')} 次")
        if qn and not (131 <= qn[0] and qn[-1] <= 146 and (qn[0] - 131) % 4 == 0): F(bid, "P6 题号应在 131–146 且每篇从 131/135/139/143 起")
        if len(b["docs"]) != 1: F(bid, "P6 每篇只能 1 个文本")
        lo, hi = 80, 190
        if not lo <= words <= hi: S(bid, f"P6 篇幅 {words} 词，超出 {lo}–{hi}")
        for x in its:
            if x.get("blank_n") is None or f"[{x['blank_n']}]" not in alltext: F(x["id"], "blank_n 在文中找不到")
    if b["part"] == 7:
        kind = b["kind"]
        nd = len(b["docs"])
        if kind == "single":
            if nd != 1: F(bid, "单篇组应 1 个文本")
            if not 2 <= len(its) <= 4: F(bid, f"单篇组应 2–4 题，实际 {len(its)}")
            if qn and not (147 <= qn[0] and qn[-1] <= 175): F(bid, "单篇题号应在 147–175")
        else:
            if nd != {"double": 2, "triple": 3}[kind]: F(bid, f"{kind} 组文本数 {nd} 不对")
            if len(its) != 5: F(bid, f"多篇组应 5 题，实际 {len(its)}")
            if qn and not (176 <= qn[0] and qn[-1] <= 200 and (qn[0] - 176) % 5 == 0): F(bid, "多篇题号应在 176–200 且从 176/181/186/191/196 起")
            if not any(kind_is(x, "CROSS_REF") or any("CROSS_REF" in n for n in x["node_ids"]) for x in its): F(bid, "多篇组至少需 1 道跨篇题")
        lo, hi = {"TX.TEXT_MSG": (35, 150), "TX.CHAT": (70, 230), "TX.DOUBLE": (220, 450), "TX.TRIPLE": (300, 620)}.get(b["text_type"], (30, 330))
        if not lo <= words <= hi: S(bid, f"P7 篇幅 {words} 词，超出 {lo}–{hi}（{b['text_type']}）")
        ins = [x for x in its if kind_is(x, "T7.INSERTION")]
        if ins:
            if kind != "single": F(bid, "P7 插入句题只出现在单篇")
            for k in range(1, 5):
                if alltext.count(f"[{k}]") != 1: F(bid, f"插入位置 [{k}] 出现 {alltext.count(f'[{k}]')} 次")
        for x in its:
            if kind_is(x, "T7.INTENT"):
                m = re.search(QUOTE + r"(.+?)" + QUOTE, x["q"])
                if not m or m.group(1) not in alltext: F(x["id"], "意图题引号原话在文中找不到")
                if b["text_type"] not in ("TX.TEXT_MSG", "TX.CHAT"): F(x["id"], "意图题只用于短信/群聊")
                tm = re.search(r"At (\d+:\d+(?: [AP]\.M\.)?)", x["q"])
                if tm and tm.group(1) not in alltext: F(x["id"], "意图题时间戳在文中找不到")
            if kind_is(x, "T7.SYNONYM"):
                m = re.search(r"word " + QUOTE + r"(\w+)" + QUOTE, x["q"]) or re.search(QUOTE + r"(\w+)" + QUOTE, x["q"])
                if not m or not re.search(rf"\b{m.group(1)}\b", alltext): F(x["id"], "同义词题目标词不在文中")
# P5 题号
for form in {i["form"] for i in items if i["part"] == 5}:
    qs = sorted(i["qnum"] for i in items if i["part"] == 5 and i["form"] == form)
    if len(qs) != len(set(qs)): F(form, "P5 同一卷题号重复")
    if len(qs) > 30: F(form, "P5 一卷超过 30 题")
for form in {i["form"] for i in items if i["part"] in (6, 7)}:
    qs = [i["qnum"] for i in items if i.get("form") == form]
    if len(qs) != len(set(qs)): F(form, "同一卷题号重复")
    p6 = [i for i in items if i.get("form") == form and i["part"] == 6]
    if len(p6) > 16: F(form, "P6 一卷超过 16 题")

# 4 答案分布
dist = {}
for p in (5, 6, 7):
    seq = [i["answer"] for i in sorted([i for i in items if i["part"] == p], key=lambda x: (x["form"], x["qnum"]))]
    if not seq: continue
    c = collections.Counter(seq); n = len(seq)
    dist[p] = {"ABCD"[k]: c.get(k, 0) for k in range(4)}
    for k in range(4):
        share = c.get(k, 0) / n
        if n >= 12 and not 0.15 <= share <= 0.35: S(f"P{p}", f"答案 {'ABCD'[k]} 占比 {share:.0%} 超出 15–35%")
    run = mx = 1
    for x, y in zip(seq, seq[1:]):
        run = run + 1 if x == y else 1; mx = max(mx, run)
    if mx > 3: S(f"P{p}", f"连续相同答案 {mx} 题（>3）")
    dist[p]["max_run"] = mx

# 5 长度（P5）
for it in items:
    if it["part"] == 5:
        n = len(it["stem"].split())
        L = TPL[it["template_id"]]["length"] if it.get("template_id") in TPL else {"min": 8, "max": 35}
        if not L["min"] <= n <= L["max"]: S(it["id"], f"P5 题干 {n} 词，超出 {L['min']}–{L['max']}")

# 6 近似重复
pool = []
for it in items:
    txt = (it.get("stem") or it.get("q") or "")
    if it["part"] == 5: pool.append((it["id"], "stem", txt))
for bid, b in bundles.items():
    pool.append((bid, "passage", " ".join(d["text"] for d in b["docs"])))
refs = load_v0() + load_pilot()
ext = [] if A.no_external else load_external()
dups = []
sh = [(i, k, shingles(norm_text(t)), set(norm_text(t))) for i, k, t in pool]
for x in range(len(sh)):
    for y in range(x + 1, len(sh)):
        if sh[x][1] != sh[y][1]: continue
        j = jacc(sh[x][2], sh[y][2])
        if j >= 0.5: F(sh[x][0], f"与 {sh[y][0]} 近似重复 (3-gram J={j:.2f})"); dups.append((sh[x][0], sh[y][0], j))
for src, label in ((refs, "items_v0"), (ext, "external")):
    idx = collections.defaultdict(list)
    rsh = []
    for k, (f, t) in enumerate(src):
        s = shingles(norm_text(str(t))); rsh.append((f, t, s))
        for g in s: idx[g].append(k)
    for i, kind, s, _ in sh:
        cnt = collections.Counter(k for g in s for k in idx.get(g, []))
        for k, c in cnt.most_common(3):
            j = jacc(s, rsh[k][2])
            if j >= 0.5: F(i, f"与 {label}:{rsh[k][0]} 近似重复 (J={j:.2f}): {str(rsh[k][1])[:80]}"); dups.append((i, label, j))
            elif j >= 0.3: W(i, f"与 {label}:{rsh[k][0]} 部分相似 (J={j:.2f}): {str(rsh[k][1])[:80]}")
# 选项集合完全相同 + 题干相似（自身）
optsets = collections.defaultdict(list)
for it in items: optsets[tuple(sorted(o.lower() for o in it["options"]))].append(it["id"])
for k, v in optsets.items():
    if len(v) > 1 and not k == ("[1]", "[2]", "[3]", "[4]"): W(v[0], f"选项集合与 {v[1:]} 完全相同")

# ---------- 汇总 ----------
units = [i["id"] for i in items] + list(bundles)
failed = [u for u in units if fails.get(u)]
global_fail = {k: v for k, v in fails.items() if k not in units}
node_cov = collections.Counter(n for i in items for n in i["node_ids"])
res = {"file": A.items, "imported_mode": IMPORTED, "n_items": len(items), "n_bundles": len(bundles),
       "items_failed": len([i for i in items if fails.get(i["id"]) or (i.get("bundle_id") and fails.get(i["bundle_id"]))]),
       "units_failed": len(failed), "global_fail": global_fail, "answer_distribution": dist,
       "vocab_offlist": vocab_log, "vocab_exceptions": {i["id"]: i["vocab_exceptions"] for i in items if i.get("vocab_exceptions")}, "derived_allowed": derived_log, "assumed_proper_nouns": sorted(proper_log),
       "fails": {k: v for k, v in fails.items()}, "warns": dict(warns), "external_refs_checked": len(ext), "v0_refs_checked": len(refs),
       "node_coverage": dict(node_cov), "n_nodes_covered": len(node_cov)}
ok = res["items_failed"] == 0 and not global_fail
print(("[导入题模式] " if IMPORTED else "") + f"items {len(items)} bundles {len(bundles)} | 不通过题 {res['items_failed']} | 全局问题 {len(global_fail)} | 警告 {sum(len(v) for v in warns.values())} | 外部比对 {len(ext)} 条")
for k, v in list(fails.items())[:80]: print("FAIL", k, v)
for k, v in list(warns.items())[:30]: print("WARN", k, v)
print("答案分布", dist)
if A.json: json.dump(res, open(A.json, "w"), ensure_ascii=False, indent=1)
sys.exit(0 if ok else 1)
