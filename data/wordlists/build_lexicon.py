#!/usr/bin/env python3
"""A6 词表清洗：生成 lexicon_v1.json / lexicon_v1_sa.json / vocab_test_pool.json / lexicon_v1_report.md

复跑：python3 data/wordlists/build_lexicon.py   （在仓库根目录或任意目录均可）
依赖：pip install opencc-python-reimplemented
ECDICT：优先用完整版（环境变量 ECDICT_FULL，默认 /tmp/ecdict.csv）；没有时用仓库内
  data/open_items/skywind3000_ECDICT/ecdict_toeic_subset.csv + data/wordlists/ecdict_items_supplement.csv
  （后者由本脚本在有完整版时写出：题库词/词形里子集缺的行，MIT）。

许可策略：
  lexicon_v1.json     只含 CC BY 4.0（LEE-WHITE）+ MIT（EnglishCoach、ECDICT）内容 → 整体按 CC BY 4.0 署名发布
  lexicon_v1_sa.json  kknono668（CC BY-SA 4.0）的托业语境释义，只对主文件释义来自 ECDICT 兜底的词做覆盖层；独立文件、独立许可
  NGSL/TSL/BSL（CC BY-SA 4.0）只用“词名单 + 排名”做分档与词元归并，不复制其释义/统计值进主文件
"""
import csv, json, os, re, random, gzip, sys, collections, math
from pathlib import Path

import opencc

ROOT = Path(globals().get("__file__", "data/wordlists/x.py")).resolve().parents[2]
WL = ROOT / "data" / "wordlists"
OI = ROOT / "data" / "open_items"
ECDICT_FULL = Path(os.environ.get("ECDICT_FULL", "/tmp/ecdict.csv"))
SEED = 20261022
T2S = opencc.OpenCC("tw2sp")
csv.field_size_limit(10**9)

LIC = {
    "LW": {"name": "LEE-WHITE/toeic-vocab-tw v110.5", "url": "https://huggingface.co/datasets/LEE-WHITE/toeic-vocab-tw", "license": "CC-BY-4.0"},
    "EC": {"name": "chunchiech/EnglishCoach toeic_3600.csv", "url": "https://github.com/chunchiech/EnglishCoach", "license": "MIT"},
    "ED": {"name": "skywind3000/ECDICT", "url": "https://github.com/skywind3000/ECDICT", "license": "MIT"},
    "HK": {"name": "toeic-reading 项目自编补充", "url": "", "license": "CC-BY-4.0"},
    "KK": {"name": "kknono668/toeic-vocab-tw v112.0", "url": "https://huggingface.co/datasets/kknono668/toeic-vocab-tw", "license": "CC-BY-SA-4.0"},
}
# 自编补充（ECDICT 未收的现代常用词；本项目自撰，CC BY 4.0）
MANUAL = {"app": ("n.", "应用程序；手机软件"), "apps": None, "webinar": ("n.", "网络研讨会；线上讲座"),
          "e-mail": ("n.", "电子邮件"), "email": ("n.", "电子邮件"), "online": ("adj.", "在线的；网上的"),
          "smartphone": ("n.", "智能手机"), "livestream": ("n.", "直播"), "rideshare": ("n.", "拼车；网约车"),
          "coworker": ("n.", "同事"), "coworking": ("n.", "共享办公"),
          "ms": ("n.", "女士"), "mr": ("n.", "先生"), "mrs": ("n.", "夫人；太太"), "dr": ("n.", "博士；医生"),
          "cybersecurity": ("n.", "网络安全"), "chatbot": ("n.", "聊天机器人"), "shortlist": ("v.", "列入候选名单"),
          "barista": ("n.", "咖啡师"), "preapproval": ("n.", "预先批准"), "preapprove": ("v.", "预先批准"),
          "homeware": ("n.", "家居用品"), "wayfinding": ("n.", "导视；指路标识"), "nonurgent": ("adj.", "不紧急的")}
MANUAL_FORMS = {"app": ["apps"], "webinar": ["webinars"], "chatbot": ["chatbots"], "shortlist": ["shortlisted", "shortlisting", "shortlists"],
                "barista": ["baristas"], "preapprove": ["preapproved", "preapproves"], "homeware": ["homewares"]}
# 已知错释（人工改正，来源仍记原库）
OVERRIDES = {"ever": "曾经；永远；究竟"}
GLOSS_NAME = re.compile(r"人名|男子名|女子名|男性名字|女性名字|的名字|姓氏|地名|城市名|[州省].{0,8}城市|省会|^.{1,8}[，,]\\s*(中国|加拿大|美国|英国|日本|澳大利亚|法国|德国)")
FUNC_POS = {"prep.", "conj.", "pron.", "art.", "det.", "int."}

# ---------------------------------------------------------------- helpers
def norm_head(w):
    w = w.replace("’", "'").replace("‘", "'").strip()
    w = re.sub(r"\s*\([^)]*\)\s*", " ", w).strip()
    w = re.sub(r"\s+", " ", w)
    return w

def is_placeholder(w):
    # "A be followed by B" / "sb" / "sth" / "one's" 式句型
    return bool(re.search(r"(^|\s)[A-Z](\s|$)", w)) or bool(re.search(r"\b(sb|sth|somebody|something)\b", w)) and " " in w

def clean_gloss(s, maxlen=20):
    """繁→简，去括注，按义项累加到 ≤maxlen 字"""
    if not s:
        return ""
    s = T2S.convert(s).replace("\\r", "").replace("\r", "")
    s = re.sub(r"\s*,\s*", "，", s)
    s = re.sub(r"（[^）]*）|\([^)]*\)|【[^】]*】|\[[^\]]*\]|<[^>]*>", "", s)
    s = s.replace("…", "").replace("...", "")
    parts = [re.sub(r"[，,]\s*(通常|一般|常常|常用|常|指|一个|一种|是|用于|多用|主要|特别|尤其|表示|意指|也|如|例如).*$", "", p) for p in re.split(r"[；;／/]|\\n|\n", s)]
    parts = [p.strip(" ，,.。、：:") for p in parts]
    parts = [p for p in parts if p]
    out = ""
    for p in parts:
        cand = p if not out else out + "；" + p
        if len(cand) <= maxlen:
            out = cand
        elif not out:
            # 首义项过长：在逗号处截断，否则硬截
            sub = re.split(r"[，,、]", p)
            acc = ""
            for q in sub:
                c2 = q if not acc else acc + "，" + q
                if len(c2) <= maxlen:
                    acc = c2
                else:
                    break
            out = acc or p[:maxlen]
            break
    return out

POSMAP = {"noun": "n.", "verb": "v.", "adjective": "adj.", "adverb": "adv.", "preposition": "prep.",
          "conjunction": "conj.", "pronoun": "pron.", "interjection": "int.", "modal verb": "v.",
          "determiner": "det.", "abbreviation": "abbr.", "gerund": "n.", "verb (passive)": "v.",
          "n": "n.", "v": "v.", "adj": "adj.", "adv": "adv.", "prep": "prep.", "conj": "conj.", "pron": "pron."}

def map_pos(p):
    p = p.strip().lower().rstrip(".")
    if "phrase" in p or p == "idiom":
        return "phr."
    return POSMAP.get(p)

ECD_POS_RE = re.compile(r"^(n|v|vt|vi|adj|a|adv|ad|prep|conj|pron|art|num|int|interj|abbr|aux|pl|det|suf|pref)\.\s*")
ECD_POS_NORM = {"vt": "v.", "vi": "v.", "v": "v.", "n": "n.", "adj": "adj.", "a": "adj.", "adv": "adv.", "ad": "adv.",
                "prep": "prep.", "conj": "conj.", "pron": "pron.", "art": "art.", "num": "num.", "int": "int.",
                "interj": "int.", "abbr": "abbr.", "aux": "v.", "pl": "n.", "det": "det.", "suf": "suf.", "pref": "pref."}
NAME_SENSE = re.compile(r"人名|地名|姓氏|男子名|女子名|男名|女名|\[人名\]|\[地名\]|（[^）]*(名|河|湖|州|郡|市|城|国|岛|山)[^）]*）|河$|州$|市$|首都")
NAME_RE = re.compile(r"人名|地名|姓氏|男子名|女子名|国名|州名|城市|首都|河名|山名|岛名|美国.{0,4}州|英国.{0,4}郡")

def parse_ecdict_translation(tr):
    """→ (gloss≤20, [pos], is_name_only, web_only)"""
    lines = [l.strip() for l in tr.replace("\\n", "\n").split("\n") if l.strip()]
    good, web, names, pos = [], [], 0, []
    for l in lines:
        if l.startswith("[网络]"):
            web.append(l[4:].strip())
            continue
        body = ECD_POS_RE.sub("", l)
        senses = [x for x in re.split(r"[；;,，]", body) if x.strip()]
        if senses and (all(NAME_SENSE.search(x) for x in senses) or any(re.match(r"^\s*\[?(人名|地名|姓氏)\]?\s*$", x) for x in senses)):
            names += 1
            continue
        m = ECD_POS_RE.match(l)
        if m:
            p = ECD_POS_NORM.get(m.group(1))
            if p and p not in pos:
                pos.append(p)
            l = l[m.end():]
        good.append(l)
    # 带领域标签（[计][医]…）的行放到最后
    good.sort(key=lambda l: bool(re.search(r"\[[^\]网]{1,4}\]", l)))
    name_only = names > 0 and not good
    web_only = not good and bool(web)
    src = good if good else web
    if not src:
        return "", pos, name_only, web_only
    # 每行取首义项，凑满 20 字
    first = [re.split(r"[；;]", re.sub(r"\[[^\]]*\]|\([^)]*\)|（[^）]*）", "", l))[0].strip(" ,，") for l in src]
    gloss = clean_gloss(src[0])
    for f in first[1:]:
        f = clean_gloss(f)
        if f and f not in gloss and len(gloss) + 1 + len(f) <= 20:
            gloss += "；" + f
    return gloss, pos, name_only, web_only

# ---------------------------------------------------------------- load lists
def read_lemma_csv(path):
    heads, fmap = [], {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("##"):
                continue
            cells = [c.strip().lower() for c in line.strip().split(",") if c.strip()]
            if not cells or not cells[0].isascii():
                continue
            heads.append(cells[0])
            for c in cells:
                fmap.setdefault(c, cells[0])
    return heads, fmap

def read_rank(path, col_word, col_rank):
    r = {}
    with open(path, encoding="utf-8-sig", errors="ignore") as f:
        for row in csv.DictReader(f):
            w = (row.get(col_word) or "").strip().lower()
            try:
                r.setdefault(w, int(float(row[col_rank])))
            except Exception:
                pass
    return r

ngsl_heads, ngsl_map = read_lemma_csv(WL / "NGSL_12_lemmatized_for_research.csv")
tsl_heads, tsl_map = read_lemma_csv(WL / "TSL_lemma.csv")
bsl_heads, bsl_map = read_lemma_csv(WL / "BSL_120_lemmatized_for_research.csv")
ngsl_rank = read_rank(WL / "NGSL_12_stats.csv", "Lemma", "SFI Rank")
tsl_rank = read_rank(WL / "TSL_12_stats.csv", "Word", "TSL Rank")
bsl_rank = read_rank(WL / "BSL_120_stats.csv", "Word", "BSL Rank")
for h in ngsl_heads:
    ngsl_rank.setdefault(h, 2810)
for h in tsl_heads:
    tsl_rank.setdefault(h, 1251)
for h in bsl_heads:
    bsl_rank.setdefault(h, 1745)
LIST_HEADS = set(ngsl_heads) | set(tsl_heads) | set(bsl_heads)
list_map = {}
for m in (ngsl_map, tsl_map, bsl_map):
    for k, v in m.items():
        list_map.setdefault(k, v)

# ---------------------------------------------------------------- ECDICT
def load_ecdict():
    rows = {}
    if ECDICT_FULL.exists():
        src = [ECDICT_FULL]
        mode = "full"
    else:
        src = [OI / "skywind3000_ECDICT" / "ecdict_toeic_subset.csv", WL / "ecdict_items_supplement.csv"]
        mode = "subset"
    for p in src:
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                w = row["word"]
                rows.setdefault(w, row)
    return rows, mode

ecd, ecd_mode = load_ecdict()
ecd_lower = collections.defaultdict(list)
for w in ecd:
    ecd_lower[w.lower()].append(w)

def ecd_get(w):
    """小写优先；只有大写条目（专名）时返回 (row, True)"""
    if w in ecd and w == w.lower():
        return ecd[w], False
    for v in ecd_lower.get(w.lower(), []):
        if v == v.lower():
            return ecd[v], False
    vs = ecd_lower.get(w.lower(), [])
    if vs:
        return ecd[vs[0]], True
    return None, False

def ecd_lemma(w):
    row, cap = ecd_get(w)
    if not row or cap:
        return None, None
    ex = row.get("exchange") or ""
    d = dict(x.split(":", 1) for x in ex.split("/") if ":" in x)
    if "0" in d and d["0"] and d["0"] != w:
        return d["0"].lower(), d.get("1", "")
    return None, None

def ecd_forms(w):
    row, cap = ecd_get(w)
    if not row or cap:
        return []
    ex = row.get("exchange") or ""
    out = []
    for x in ex.split("/"):
        if ":" in x:
            k, v = x.split(":", 1)
            if k in "pdi3sre" and v and v != w and k != "0":
                out.append(v.lower())
    return out

# ---------------------------------------------------------------- items text
EN_KEYS = {"stem", "q", "question", "options", "text", "header", "thread", "title"}
def collect_en(obj, out, key=None):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in EN_KEYS:
                collect_en(v, out, k)
            elif isinstance(v, (dict, list)):
                collect_en(v, out, None)
    elif isinstance(obj, list):
        for v in obj:
            collect_en(v, out, key)
    elif isinstance(obj, str) and key in EN_KEYS:
        out.append(obj)

item_files = sorted((ROOT / "data").glob("items_*.json"))
item_files = [p for p in item_files if not p.name.endswith("_log.json")]
texts = []
per_file_tokens = {}
TOK_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*(?:-[^\W\d_]+)*")
for p in item_files:
    d = json.load(open(p, encoding="utf-8"))
    t = []
    collect_en(d, t)
    texts.extend(t)
    per_file_tokens[p.name] = sum(len(TOK_RE.findall(s)) for s in t)

URL_RE = re.compile(r"\S+@\S+|https?://\S+|www\.\S+|\b[\w-]+\.(?:com|org|net|co|io|biz|info)\b\S*")
texts = [URL_RE.sub(" ", s) for s in texts]
raw_tokens = []
for s in texts:
    raw_tokens.extend(TOK_RE.findall(s.replace("’", "'")))
lower_seen = set(t.lower() for t in raw_tokens if t[0].islower())

# ---------------------------------------------------------------- TOEIC lists
def lw_entries():
    d = json.load(open(OI / "LEE-WHITE_toeic-vocab-tw" / "toeic_vocabulary.json", encoding="utf-8"))
    for grp in d["vocabulary_by_importance"].values():
        for e in grp:
            forms = []
            def walk(x):
                if isinstance(x, str):
                    forms.append(x)
                elif isinstance(x, dict):
                    for v in x.values(): walk(v)
                elif isinstance(x, list):
                    for v in x: walk(v)
            walk(e.get("word_forms") or {})
            yield {"w": e["english_word"], "zh": e.get("chinese_definition", ""), "pos": e.get("parts_of_speech", []),
                   "forms": forms, "star": e.get("star_rating")}

def ec_entries():
    with open(OI / "chunchiech_EnglishCoach" / "toeic_3600.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            yield {"w": r["word"], "zh": r["translation"], "pos": re.split(r"[/,&\s]+", r.get("part_of_speech") or ""),
                   "forms": [], "level": r.get("level")}

def kk_entries():
    with gzip.open(OI / "kknono668_toeic-vocab-tw" / "toeic_vocabulary.json.gz", "rt", encoding="utf-8") as f:
        d = json.load(f)
    for e in d:
        forms = [x for wf in e.get("word_forms") or [] for x in wf.get("forms", [])]
        yield {"w": e["english_word"], "zh": e.get("chinese_definition", ""), "pos": e.get("parts_of_speech", []),
               "forms": forms, "range": e.get("toeic_score_range")}

stats = collections.Counter()
dropped = collections.defaultdict(list)

def name_check(w):
    """True=人名/地名（应删）"""
    if " " in w:
        return False
    if w in LIST_HEADS or w in list_map:
        return False
    row, cap = ecd_get(w)
    if row is None:
        return False
    g, p, name_only, _ = parse_ecdict_translation(row.get("translation") or "")
    if cap:
        # 只有大写条目：星期/月份/国名/语言等保留（无专名标记），人名地名删
        return name_only or not g or bool(NAME_SENSE.search(g))
    return name_only

def lemma_of(w):
    """单词 → (lemma, how)；w 自身是词元时返回 (w, None)"""
    if " " in w:
        return w, None
    if w in LIST_HEADS:
        return w, None
    # -ings 先还原到 -ing 名词（findings→finding），再看 ECDICT，最后才用研究版词形表
    if w.endswith("ings") and w[:-1] in LEX:
        return w[:-1], "ings"
    l, t = ecd_lemma(w)
    if l:
        return l, "ecdict:" + (t or "")
    if w in list_map and list_map[w] != w:
        return list_map[w], "list"
    return w, None

# raw entries per source
LEX = {}  # headword -> entry
def get(w):
    if w not in LEX:
        LEX[w] = {"headword": w, "pos": [], "zh": "", "source": None, "forms": set(), "kind": "phrase" if " " in w else "word",
                  "_lw_star": None, "_cand": {}}
    return LEX[w]

for src, gen in (("LW", lw_entries), ("EC", ec_entries)):
    for e in gen():
        stats[src + "_raw"] += 1
        w0 = norm_head(e["w"])
        if not w0 or is_placeholder(w0) or not re.fullmatch(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ' .\-]*", w0) or w0.endswith((".", "?", "!")):
            dropped["bad_headword"].append(f"{src}:{e['w']}"); continue
        w = w0 if (w0.isupper() and len(w0) <= 5) else w0.lower()
        zh = clean_gloss(e["zh"])
        if not zh:
            dropped["empty_gloss"].append(f"{src}:{w}"); continue
        if " " not in w and not w.isascii() and w not in ("résumé",):
            dropped["not_in_dict"].append(f"{src}:{w}"); continue
        if " " not in w and w.lower() not in ecd_lower and w not in list_map and w not in MANUAL:
            dropped["not_in_dict"].append(f"{src}:{w}"); continue
        if name_check(w) or (w not in LIST_HEADS and GLOSS_NAME.search(T2S.convert(e["zh"]))):
            dropped["name"].append(f"{src}:{w}"); continue
        ent = get(w)
        ent["_cand"].setdefault(src, {"zh": zh, "pos": [p for p in (map_pos(x) for x in e["pos"] if x) if p]})
        if src == "LW":
            ent["_lw_star"] = e.get("star")
        for f in e["forms"]:
            f = norm_head(f).lower()
            if f and f != w and re.fullmatch(r"[a-z'\-]+", f):
                ent["forms"].add(f)

# 纯变形词并入词元
merged = 0
for w in sorted(LEX, key=lambda x: x.endswith("ings")):
    ent = LEX[w]
    if ent["kind"] != "word":
        continue
    lem, how = lemma_of(w)
    if not how or lem == w:
        continue
    keep = False
    lwpos = ent["_cand"].get("LW", {}).get("pos", [])
    # -ed/-ing 形容词、介词等有独立义 → 保留为独立词条（如 following / qualified）
    if re.search(r"(ed|ing)$", w) and any(p in ("adj.", "prep.", "conj.", "adv.") for p in lwpos):
        keep = True
    if w.endswith("ing") and "n." in lwpos:   # booking / funding / training 作名词
        keep = True
    if keep:
        continue
    tgt = get(lem)
    for s, c in ent["_cand"].items():
        tgt["_cand"].setdefault(s, c)
    tgt["forms"].add(w)
    tgt["forms"] |= ent["forms"]
    if tgt["_lw_star"] is None:
        tgt["_lw_star"] = ent["_lw_star"]
    del LEX[w]
    merged += 1
    dropped["merged_form"].append(f"{w}->{lem}")

# ---------------------------------------------------------------- item lemmas → add ECDICT entries
def resolve_token(tok):
    """题内 token → 词典 headword 或 None"""
    t = tok.replace("’", "'")
    cands = []
    if t.isupper() and len(t) <= 5:
        cands.append(t)
    low = t.lower()
    cands.append(low)
    if low.endswith("'s"):
        cands.append(low[:-2])
    if "'" in low:
        base = low.split("'")[0]
        cands.append({"won": "will", "ca": "can", "sha": "shall"}.get(base, base))
    import unicodedata
    for c in list(cands):
        a = "".join(ch for ch in unicodedata.normalize("NFD", c) if unicodedata.category(ch) != "Mn")
        if a != c:
            cands.append(a)
    for c in cands:
        if c in LEX:
            return c
        if c in FORM2HEAD:
            return FORM2HEAD[c]
    return None

def ensure_ecd(word):
    """尝试用 ECDICT 把 word（或其词元）加入词典，返回 headword 或 None"""
    w = word.lower()
    lem, how = lemma_of(w)
    for cand in ([lem, w] if lem != w else [w]):
        if cand in LEX:
            if cand != w:
                LEX[cand]["forms"].add(w)
            return cand
        row, cap = ecd_get(cand)
        if row is None:
            continue
        g, pos, name_only, web_only = parse_ecdict_translation(row.get("translation") or "")
        if name_only or not g or (cap and (NAME_SENSE.search(g) or web_only)):
            continue
        ent = get(cand)
        ent["_cand"]["ED"] = {"zh": g, "pos": pos, "web": web_only}
        if cand != w:
            ent["forms"].add(w)
        return cand
    return None

for mw, mv in MANUAL.items():
    if mv and mw not in LEX:
        if True:
            ent = get(mw); ent["_cand"]["HK"] = {"zh": mv[1], "pos": [mv[0]]}
    if mw in LEX:
        LEX[mw]["forms"] |= set(MANUAL_FORMS.get(mw, []))
# list heads always get an entry (NGSL/TSL/BSL)
for h in sorted(LIST_HEADS):
    if h not in LEX:
        ensure_ecd(h)
    for f, l in list_map.items():
        pass

FORM2HEAD = {}
def rebuild_form_index():
    FORM2HEAD.clear()
    for w, e in LEX.items():
        for f in e["forms"]:
            FORM2HEAD.setdefault(f, w)
    for f, l in list_map.items():
        if l in LEX and f not in LEX:
            FORM2HEAD.setdefault(f, l)
rebuild_form_index()

for tok in sorted(set(raw_tokens)):
    if len(tok) == 1 and tok.lower() not in ("a", "i"):
        continue
    if resolve_token(tok):
        continue
    parts = [tok] + (tok.split("-") if "-" in tok else [])
    for p in parts:
        if not p or resolve_token(p):
            continue
        if p[0].isupper() and p.lower() not in lower_seen:
            # 专名候选：只有在 ECDICT 有非专名小写义项时才加
            row, cap = ecd_get(p.lower())
            if row is None or cap:
                continue
            rk = [int(x) for x in (row.get("bnc") or "0", row.get("frq") or "0") if str(x).isdigit() and int(x) > 0]
            if p.lower() not in list_map and (not rk or min(rk) > 30000):
                continue
        ensure_ecd(p)
rebuild_form_index()

# ECDICT 兜底释义也给 LW/EC 词条准备（备用）+ 词形补全（只收真实词或题内出现的形）
for w, e in LEX.items():
    if e["kind"] == "word":
        for f in ecd_forms(w):
            e["forms"].add(f)
        for f, l in list_map.items():
            pass
for f, l in list_map.items():
    if l in LEX and f != l and f not in LEX:
        row, cap = ecd_get(f)
        if (row is not None and not cap) or f in lower_seen:
            LEX[l]["forms"].add(f)
for mw, fs in MANUAL_FORMS.items():
    if mw in LEX:
        LEX[mw]["forms"] |= set(fs)
for w, e in LEX.items():
    # 去掉不是真实词形的噪声（LLM 列的 'A be followed by B' 等）
    e["forms"] = {f for f in e["forms"] if f != w and f not in LEX and re.fullmatch(r"[a-z][a-z'\-]*", f)
                  and (f in ecd_lower or f in lower_seen or f in MANUAL_FORMS.get(w, []))
                  and not (f.endswith("ings") and f[:-1] in LEX and f[:-1] != w)}
rebuild_form_index()

# ---------------------------------------------------------------- choose gloss
for w, e in LEX.items():
    c = e["_cand"]
    if w in OVERRIDES:
        src = "EC" if "EC" in c and "LW" not in c else ("LW" if "LW" in c else "ED")
        e["zh"], e["source"] = OVERRIDES[w], src
        e["pos"] = (c.get(src) or {}).get("pos", [])
    for s in ("LW", "EC", "HK", "ED"):
        if e["source"]:
            break
        if s in c and c[s]["zh"]:
            e["zh"], e["source"], e["pos"] = c[s]["zh"], s, c[s]["pos"]
    if not e["pos"]:
        for s in ("LW", "EC", "ED"):
            if s in c and c[s]["pos"]:
                e["pos"] = c[s]["pos"]; break
    if not e["pos"] and e["kind"] == "word":
        row, cap = ecd_get(w)
        if row and not cap:
            e["pos"] = parse_ecdict_translation(row.get("translation") or "")[1]
for w in [w for w, e in LEX.items() if not e["zh"]]:
    dropped["empty_gloss"].append(f"final:{w}")
    del LEX[w]
rebuild_form_index()

# ---------------------------------------------------------------- frequency in items
lemma_freq = collections.Counter()
lemma_items = collections.defaultdict(int)
tok_stats = collections.Counter()
missing = collections.Counter()
proper = collections.Counter()
for s in texts:
    seen_here = set()
    for tok in TOK_RE.findall(s.replace("’", "'")):
        if len(tok) == 1 and tok.lower() not in ("a", "i"):
            tok_stats["skip_letter"] += 1; continue
        h = resolve_token(tok)
        if h is None and "-" in tok:
            ps = [p for p in tok.split("-") if p]
            hs = [resolve_token(p) for p in ps]
            if all(hs):
                tok_stats["covered"] += 1
                for x in hs:
                    lemma_freq[x] += 1; seen_here.add(x)
                continue
        if h:
            tok_stats["covered"] += 1
            lemma_freq[h] += 1; seen_here.add(h)
        elif tok[0].isupper() and tok.lower() not in lower_seen:
            tok_stats["proper"] += 1; proper[tok] += 1
        else:
            tok_stats["missing"] += 1; missing[tok.lower()] += 1
    for x in seen_here:
        lemma_items[x] += 1

# ---------------------------------------------------------------- tiers
def tier_of(w, e):
    f = lemma_freq.get(w, 0)
    nr, tr, br = ngsl_rank.get(w), tsl_rank.get(w), bsl_rank.get(w)
    if e["kind"] != "word":
        return None
    if nr and nr <= 1000:
        return "core"
    if (nr and nr <= 2000) or (tr and (tr <= 400 or f >= 3)):
        return "600"
    if (nr and f >= 1) or tr or (br and (br <= 600 or f >= 3)) or (f >= 5 and not nr):
        return "730"
    if (nr) or (br and (f >= 1 or br <= 1200)) or f >= 2 or (e["_lw_star"] and e["_lw_star"] >= 4 and f >= 1):
        return "860"
    return None

for w, e in LEX.items():
    e["tier"] = tier_of(w, e)
tier_counts = collections.Counter(e["tier"] or "ref" for e in LEX.values())

# ---------------------------------------------------------------- write lexicon_v1.json
entries = []
for w in sorted(LEX, key=lambda x: (x.lower(), x)):
    e = LEX[w]
    out = {"headword": w, "pos": e["pos"], "zh": e["zh"], "forms": sorted(e["forms"]), "tier": e["tier"],
           "source": e["source"], "license": LIC[e["source"]]["license"], "kind": e["kind"]}
    if lemma_freq.get(w):
        out["item_freq"] = lemma_freq[w]
    lists = [n for n, r in (("NGSL", ngsl_rank), ("TSL", tsl_rank), ("BSL", bsl_rank)) if w in r]
    if lists:
        out["lists"] = lists
    entries.append(out)

lex_meta = {
    "name": "toeic-reading lexicon v1",
    "built_by": "data/wordlists/build_lexicon.py",
    "license": "CC BY 4.0（整体）；含 MIT 许可内容（ECDICT、EnglishCoach），使用时须保留下列署名",
    "attribution": [
        "LEE-WHITE, toeic-vocab-tw (CC BY 4.0) https://huggingface.co/datasets/LEE-WHITE/toeic-vocab-tw — 释义经 OpenCC 繁→简、截短",
        "chunchiech, EnglishCoach (MIT) https://github.com/chunchiech/EnglishCoach — 释义经 OpenCC 繁→简、截短",
        "skywind3000, ECDICT (MIT, © 2017 Linwei) https://github.com/skywind3000/ECDICT — 兜底释义、词形",
        "少量自编释义（source=HK，app/webinar 等 ECDICT 未收词），CC BY 4.0",
        "分档参考 NGSL 1.2 / TSL 1.2 / BSL 1.20 (Browne, Culligan & Phillips, CC BY-SA 4.0) 的词名单与排名；本文件未复制其释义或统计值",
    ],
    "sources": {k: v for k, v in LIC.items() if k != "KK"},
    "lookup_order": "token → 小写/去所有格 → headword 或 forms 反查 → 显示 zh（source=LW/EC 为托业语境释义，ED 为通用兜底）；可选叠加 lexicon_v1_sa.json",
    "tiers": {"core": "NGSL 前 1000", "600": "NGSL 1001–2000 + TSL 前 400 或题内≥3 次", "730": "其余 TSL / 题内出现的 NGSL / BSL 前 600 或题内≥3 / 非名单题内≥5",
              "860": "其余 NGSL、BSL（题内出现或前 1200）、题内≥2 次的词、LEE-WHITE 4★+ 且题内出现", "null": "只供查词，不主动教"},
    "counts": {"entries": len(entries), **{f"tier_{k}": v for k, v in sorted(tier_counts.items())},
               "by_source": dict(collections.Counter(e["source"] for e in entries))},
}
json.dump({"meta": lex_meta, "entries": entries}, open(WL / "lexicon_v1.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- SA overlay
sa = []
for e in kk_entries():
    w0 = norm_head(e["w"])
    if not w0 or is_placeholder(w0):
        continue
    w = w0.lower()
    h = w if w in LEX else FORM2HEAD.get(w)
    if not h or LEX[h]["source"] != "ED":
        continue
    zh = clean_gloss(e["zh"])
    if not zh or "人名" in zh:
        continue
    if any(x["headword"] == h for x in sa[-3:]):
        continue
    sa.append({"headword": h, "zh": zh, "toeic_score_range": e.get("range")})
seen = set(); sa2 = []
for x in sa:
    if x["headword"] not in seen:
        seen.add(x["headword"]); sa2.append(x)
json.dump({"meta": {"name": "toeic-reading lexicon v1 — ShareAlike overlay", "license": "CC BY-SA 4.0",
                    "attribution": "kknono668, toeic-vocab-tw v112.0 (CC BY-SA 4.0) https://huggingface.co/datasets/kknono668/toeic-vocab-tw — 释义经 OpenCC 繁→简、截短；本文件为其改编作品，须以 CC BY-SA 4.0 再发布",
                    "usage": "可选覆盖层：仅收录主文件中释义来自 ECDICT 兜底（source=ED）的词，提供托业语境释义；不加载也不影响主文件",
                    "count": len(sa2)}, "entries": sa2},
          open(WL / "lexicon_v1_sa.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- ECDICT supplement (for reruns without full ECDICT)
if ecd_mode == "full":
    sub = set()
    with open(OI / "skywind3000_ECDICT" / "ecdict_toeic_subset.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sub.add(r["word"])
    need = set()
    for w, e in LEX.items():
        for x in [w] + sorted(e["forms"]):
            for v in ecd_lower.get(x.lower(), []):
                if v not in sub:
                    need.add(v)
    with open(WL / "ecdict_items_supplement.csv", "w", encoding="utf-8", newline="") as f:
        cols = ["word", "phonetic", "translation", "pos", "collins", "oxford", "tag", "bnc", "frq", "exchange"]
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        for v in sorted(need):
            wr.writerow(ecd[v])
    stats["ecdict_supplement_rows"] = len(need)

# ---------------------------------------------------------------- vocab test pool
rng = random.Random(SEED)
PER_TIER = 100
real = []
for t in ("core", "600", "730", "860"):
    pool = [e for e in entries if e["tier"] == t and e["kind"] == "word" and re.fullmatch(r"[a-z]{3,14}", e["headword"])
            and not (set(e["pos"]) & FUNC_POS) and not (t == "core" and ngsl_rank.get(e["headword"], 9999) <= 150)]
    pool.sort(key=lambda e: (-(e.get("item_freq") or 0), e["headword"]))
    # 按题内频次分 5 层均匀抽
    k = min(PER_TIER, len(pool)); strata = 5; pick = []
    for i in range(strata):
        seg = pool[i * len(pool) // strata:(i + 1) * len(pool) // strata]
        pick += rng.sample(seg, min(len(seg), k // strata))
    for e in pick:
        real.append({"word": e["headword"], "real": True, "tier": t, "zh": e["zh"], "pos": e["pos"]})

# 假词：在名单词元上训练字母三元组模型，过滤掉 ECDICT/词形里存在的串及与真词编辑距离 1 的串
train = [w for w in LIST_HEADS if re.fullmatch(r"[a-z]{4,10}", w)]
trans = collections.defaultdict(collections.Counter)
for w in train:
    s = "^^" + w + "$"
    for i in range(len(s) - 2):
        trans[s[i:i + 2]][s[i + 2]] += 1
allwords = set(ecd_lower) | set(list_map) | set(FORM2HEAD) | set(LEX)
tiered = {e["headword"] for e in entries if e["tier"]}
BAD = re.compile(r"(fuck|shit|cunt|dick|cock|nig|fag|slut|whor|rape|porn|sex|kill|nazi|piss|tit|ass)")
ALPHA = "abcdefghijklmnopqrstuvwxyz"
def near_real(c):
    for i in range(len(c) + 1):
        for a in ALPHA:
            if c[:i] + a + c[i:] in tiered: return True
    for i in range(len(c)):
        if c[:i] + c[i + 1:] in tiered: return True
        for a in ALPHA:
            if c[:i] + a + c[i + 1:] in tiered: return True
    return False
def gen():
    s = "^^"
    while len(s) < 16:
        nxt = trans[s[-2:]]
        if not nxt: return None
        ch = rng.choices(list(nxt), weights=list(nxt.values()))[0]
        if ch == "$": break
        s += ch
    return s[2:]
n_fake = round(len(real) * 0.15 / 0.85)
fakes = set(); tries = 0
while len(fakes) < n_fake and tries < 200000:
    tries += 1
    c = gen()
    if not c or not (5 <= len(c) <= 10) or c in allwords or c in fakes or BAD.search(c):
        continue
    if not re.search(r"[aeiouy]", c) or re.search(r"(.)\1\1", c) or near_real(c):
        continue
    fakes.add(c)
fake_items = [{"word": w, "real": False, "tier": None} for w in sorted(fakes)]
items = real + fake_items
rng.shuffle(items)
for i, x in enumerate(items):
    x["id"] = f"VT{i + 1:04d}"
json.dump({"meta": {"built_by": "data/wordlists/build_lexicon.py", "seed": SEED,
                    "design": "认识/不认识自评；每档按题内频次分 5 层均匀抽 100 个真词（排除虚词与 NGSL 前 150），另加约 15% 合法拼写假词（字母三元组生成，已排除 ECDICT 77 万词条/词形与真词编辑距离 1 的串）；选中假词=过度自评，用于校正",
                    "scoring_hint": "估计词汇档 = 各档 (真词认识率 − 假词误认率) 校正后过 0.8 的最高档",
                    "license": "真词释义同 lexicon_v1.json（CC BY 4.0/MIT）",
                    "counts": {"real": len(real), "fake": len(fake_items), **{f"real_{t}": sum(1 for x in real if x['tier'] == t) for t in ('core', '600', '730', '860')}}},
           "items": items}, open(WL / "vocab_test_pool.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# ---------------------------------------------------------------- report
total_counted = tok_stats["covered"] + tok_stats["missing"]
cov = tok_stats["covered"] / total_counted if total_counted else 0
cov_raw = tok_stats["covered"] / (total_counted + tok_stats["proper"]) if total_counted else 0
types_cov = len(set(lemma_freq))
src_counts = collections.Counter(e["source"] for e in entries)
tiered_items_tok = sum(f for w, f in lemma_freq.items() if LEX[w]["tier"])
def tier_tok(t):
    return sum(f for w, f in lemma_freq.items() if LEX[w]["tier"] == t)
cum = 0; tier_cov_lines = []
for t in ("core", "600", "730", "860"):
    cum += tier_tok(t)
    tier_cov_lines.append(f"| {t} | {tier_counts[t]} | {tier_tok(t)} | {cum / total_counted:.1%} |")
src_tok = collections.Counter()
for w, f in lemma_freq.items():
    src_tok[LEX[w]["source"]] += f

rep = f"""# lexicon_v1 报告（A6 词表清洗）

生成：`python3 data/wordlists/build_lexicon.py`（ECDICT 模式：{ecd_mode}；随机种子 {SEED}）

## 产出
| 文件 | 内容 | 许可 |
|---|---|---|
| `data/wordlists/lexicon_v1.json` | {len(entries)} 词条（单词 {sum(1 for e in entries if e['kind']=='word')}，短语 {sum(1 for e in entries if e['kind']=='phrase')}）；字段 headword/pos/zh(≤20 字简体)/forms/tier/source/license/kind/item_freq/lists | CC BY 4.0 整体署名（含 MIT 内容） |
| `data/wordlists/lexicon_v1_sa.json` | {len(sa2)} 条 kknono668 托业语境释义覆盖层（只对主文件 source=ED 的词） | CC BY-SA 4.0（独立文件） |
| `data/wordlists/vocab_test_pool.json` | 真词 {len(real)}（每档 {PER_TIER}）+ 假词 {len(fake_items)}（{len(fake_items)/len(items):.1%}） | 同主文件 |
| `data/wordlists/ecdict_items_supplement.csv` | ECDICT 子集外、本词典用到的行（无完整 ECDICT 时复跑用） | MIT |
| `data/wordlists/BSL_120_*.csv`、`NGSL_12_stats.csv` | 从 handoff 副本拷入（原 newgeneralservicelist.com），只用名单/排名 | CC BY-SA 4.0（原样） |

## 释义来源（按词条）
- LEE-WHITE（CC BY，托业语境）：{src_counts['LW']}
- EnglishCoach（MIT，托业语境）：{src_counts['EC']}
- ECDICT（MIT，通用兜底）：{src_counts['ED']}
- 项目自编补充（CC BY，ECDICT 未收的 app/webinar 等）：{src_counts['HK']}
- 按题内 token 计：LW {src_tok['LW']/max(1,sum(src_tok.values())):.1%} / EC {src_tok['EC']/max(1,sum(src_tok.values())):.1%} / ED {src_tok['ED']/max(1,sum(src_tok.values())):.1%}

## 清洗
- 繁→简：OpenCC `tw2sp`（含台湾用语转换，如 軟體→软件）；去括注，按义项累加截到 ≤20 字。
- 读入原始条目：LEE-WHITE {stats['LW_raw']}，EnglishCoach {stats['EC_raw']}。
- 删除：人名/地名 {len(dropped['name'])}（例：{', '.join(dropped['name'][:8])}）；句型/占位符/非法词头 {len(dropped['bad_headword'])}（例：{', '.join(dropped['bad_headword'][:5])}）；空释义 {len(dropped['empty_gloss'])}。
- 纯变形词并入词元：{merged}（例：{', '.join(dropped['merged_form'][:10])}）；-ed/-ing 且原库标为形容词/介词等的保留为独立词条（following、qualified 类）。词元判定：NGSL/TSL/BSL 词形表 → ECDICT exchange。
- 词典里查无此词（LLM 拼错/混入西里尔字母等）：{len(dropped['not_in_dict'])}（例：{', '.join(dropped['not_in_dict'][:8])}）。
- 人工改正：{', '.join(f'{k}→{v}' for k, v in OVERRIDES.items())}（EnglishCoach 错释“从未”）。
- 题库里出现、但三份托业词表没有的词，用 ECDICT 补词条（去掉只有人名/地名义项、只有大写专名条目的）。

## 分档（自建，NGSL/TSL/BSL 名单 + 公开题库词频）
题库文本：{', '.join(f'{k}（{v} token）' for k, v in per_file_tokens.items())}；只取 stem/q/options/text/header/thread/title 英文字段。

| 档 | 词数 | 题内 token | 累计 token 覆盖 |
|---|---|---|---|
{chr(10).join(tier_cov_lines)}
| 未分档（只供查词） | {tier_counts['ref']} | {sum(f for w,f in lemma_freq.items() if not LEX[w]['tier'])} | — |

规则：core=NGSL 前 1000；600=NGSL 1001–2000 + TSL 前 400 或题内≥3；730=其余 TSL + 题内出现的 NGSL 2001+ + BSL 前 600 或题内≥3 + 非名单词题内≥5；860=其余 NGSL + BSL（题内出现或前 1200）+ 题内≥2 + LEE-WHITE 4★+ 且题内出现。短语不分档。kknono668 分数段没有参与（避免 SA 与 LLM 标签）。

## 覆盖率（全部公开题 {len(item_files)} 个文件）
- 计入 token {total_counted}（另有专名 {tok_stats['proper']}、单字母 {tok_stats['skip_letter']} 不计）
- **离线释义 token 覆盖率 {cov:.2%}**（含专名为分母时 {cov_raw:.2%}）；覆盖到的不同词元 {types_cov}
- 未覆盖 {tok_stats['missing']} token / {len(missing)} 种，前 40：{', '.join(f'{w}({c})' for w, c in missing.most_common(40))}
- 专名示例（判定：首字母大写且全文从未小写出现、词典无普通义）：{', '.join(f'{w}' for w, c in proper.most_common(25))}

## 词汇量测试题池
- 每档 {PER_TIER} 真词（按题内频次 5 层均匀抽，排除虚词、NGSL 前 150）+ {len(fake_items)} 假词。
- 假词例：{', '.join(sorted(fakes)[:15])}

## 遗留 / 注意
- 释义来自 LLM 生成词表（LEE-WHITE/EnglishCoach），只抽查过；ECDICT 兜底释义是通用义，托业语境不一定贴切（可加载 SA 覆盖层改善 {len(sa2)} 词）。
- 词元归并依赖词形表，同形异义（found/left/rose）会并到高频词元；-ed/-ing 形容词只按原库词性保留，可能有漏。
- 分档阈值是推断设计（题库仅约 1,500 题，频次稀疏），需要后续用真实答题数据校准。
- 专名识别是启发式：句首大写的生僻真词若词典没有，会被算专名而不计入分母。
- 无完整 ECDICT 时复跑，假词过滤只能用子集+补充表，结果会略有不同（释义不变）。
"""
open(WL / "lexicon_v1_report.md", "w", encoding="utf-8").write(rep)
print(json.dumps({"entries": len(entries), "tiers": dict(tier_counts), "coverage": round(cov, 4), "coverage_raw": round(cov_raw, 4),
                  "sa": len(sa2), "pool_real": len(real), "pool_fake": len(fake_items), "merged": merged,
                  "dropped": {k: len(v) for k, v in dropped.items()}, "src": dict(src_counts), "missing_top": missing.most_common(30)}, ensure_ascii=False, indent=1))
