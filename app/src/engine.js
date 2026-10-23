/* ===== 引擎：数据索引 / 掌握度(mastery.js) / 预测分 / 复习排程(FSRS-4.5，见 fsrs.js) / ROI 排程(planner.js) / 选题 =====
 * 对前端的稳定 API 见 docs/engine_api.md：getTodayPlan / getProgress / recordAnswer / getProfile / setSetting。 */
const D = window.TDATA;
const IT = {}, BU = {}, ND = {}, BY_NODE = {}, FORMS = {}, ALLF = {};
const FULL_MIN = 90;   // 一个 form 题数 ≥90 才算整套（可模考）；pilot 迷你卷不够数，不进模考
D.items.forEach(i => {
  IT[i.id] = i;
  [i.n].concat(i.ns).forEach(n => (BY_NODE[n] = BY_NODE[n] || []).push(i.id));
  (ALLF[i.f] = ALLF[i.f] || []).push(i.id);
});
Object.keys(ALLF).forEach(f => { if (ALLF[f].length >= FULL_MIN) FORMS[f] = ALLF[f]; });   // 整套：open MXT01–06 / 私有 xdf T01–T10 / 以后 ETS 等，按题数通用判定
D.bundles.forEach(b => { BU[b.id] = b; });
D.nodes.forEach(n => { ND[n.id] = n; });
Object.values(FORMS).forEach(a => a.sort((x, y) => IT[x].q - IT[y].q));
/* 掌握度回放上下文：题目 → 节点/难度/用时；节点 → 叶前置（前置弱证据传播） */
const MCTX = { item: id => IT[id], prereqs: n => ((ND[n] && ND[n].pr) || []).filter(p => ND[p] && !ND[p].g) };

const DAY = 864e5;
const today = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
const dayNum = () => Math.floor((Date.now() - new Date().getTimezoneOffset() * 6e4) / DAY);
const sig = x => 1 / (1 + Math.exp(-x));
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const diffB = d => (d - 3) * 0.7;               // difficulty_est(1–5) → logit 难度
const RT = { 600: 300, 700: 350, 800: 400, 900: 450 }; // 总分目标 → 阅读分目标（按一半估）
const RANKS = [[0, '新同事'], [200, '专员'], [275, '资深专员'], [350, '主管'], [420, '经理']];
const rtgOf = s => s.rtg || RT[s.target] || Math.round(s.target * 0.45 / 5) * 5;   // 阅读目标：首日按 总分−听力（无则×0.45）存 st.rtg
const SCALE = [[0, 5], [10, 5], [20, 60], [30, 110], [40, 165], [50, 220], [60, 275], [70, 330], [80, 385], [90, 440], [95, 470], [100, 495]];

function newState(target, exam) {
  return { ver: 2, fv: 'fsrs45', created: Date.now(), target: target || 700, exam: exam || '', diag: false,
    th: 0, N: 0, nd: {}, seen: {}, cards: {}, words: {}, wrong: {}, mocks: [], used: [],
    streak: { d: '', n: 0 }, days: {}, hist: [], cons: {}, hl: {}, run: null,
    log: exam ? [{ t: Date.now(), e: 'exam_date_set', tz: -new Date().getTimezoneOffset(), exam_date: exam }] : [] };
}
/* FSRS 接入：cards[id] / words[w] = {s,d,last,due,reps,lapses,rv}（due/last 为 FSRS.dayIndex，凌晨 4 点换日）。
 * 卡片状态 = FSRS.replay(log) 的结果；作答时对同一条日志事件增量 applyEvent，两者一致。 */
const fxTz = () => -new Date().getTimezoneOffset();
const fxToday = () => FSRS.dayIndex(Date.now(), fxTz());

const E = {
  st: null,
  log(e, o) { const L = this.st.log, x = Object.assign({ t: Date.now(), e }, o || {}); L.push(x); if (L.length > 20000) L.splice(0, L.length - 20000); return x; },
  fxParams() {
    const f = this.st && this.st.fsrsFit, o = { tz: fxTz(), targetMs: id => (IT[id] ? IT[id].t * 1000 : null) };
    if (f && f.use && f.w) o.w = f.w;   // 个人参数（Personal.fsrsFit，≥300 次复习后）
    return FSRS.params(o);
  },
  /* 旧档案（简化排程）或导入数据：从答题日志回放重建卡片状态 */
  fxEnsure() { if (this.st.fv !== 'fsrs45') this.fxReplay(); },
  fxReplay() {
    const s = this.st;
    const ev = (s.exam ? [{ t: 0, e: 'exam_date_set', exam_date: s.exam }] : []).concat(s.log || []);
    const all = FSRS.replay(ev, this.fxParams()), cards = {};
    Object.keys(all).forEach(k => { if (k.indexOf(FSRS.WORD) && k.indexOf(FSRS.PARA)) cards[k] = all[k]; });
    s.cards = cards;
    Object.keys(s.words).forEach(w => { const o = s.words[w], c = all[FSRS.WORD + w]; delete o.ivl; Object.assign(o, c && c.s != null ? c : { s: null, d: null, last: null, reps: 0, lapses: 0, rv: null }); });
    s.fv = 'fsrs45';
  },
  /* 掌握度：mastery.js 回放答题日志（带缓存，日志只追加时增量），未作答节点返回 null */
  macc() {
    const L = this.st.log || [], c = this._mc;
    if (!c || c.log !== L || c.first !== L[0] || c.len > L.length) this._mc = { log: L, first: L[0], len: L.length, acc: Mastery.replay(L, MCTX) };
    else if (c.len < L.length) { for (let k = c.len; k < L.length; k++) Mastery.apply(c.acc, L[k], MCTX); c.len = L.length; }
    return this._mc.acc;
  },
  mastery(n) { const o = Mastery.of(this.macc(), n, Date.now()); return o.seen ? o.m : null; },
  rawFromTheta(th) {
    const bs = [-1.4, -0.7, 0, 0.7, 1.4], ws = [.1, .25, .35, .2, .1];
    return 100 * bs.reduce((s, b, k) => s + ws[k] * sig(th - b), 0);
  },
  scaled(raw) {
    for (let k = 1; k < SCALE.length; k++) if (raw <= SCALE[k][0]) {
      const [x0, y0] = SCALE[k - 1], [x1, y1] = SCALE[k]; return y0 + (y1 - y0) * (raw - x0) / (x1 - x0);
    }
    return 495;
  },
  /* 预测阅读分：点估计 + 区间（答题越多越窄） + 达标概率 */
  predict() {
    const s = this.st, p = this.scaled(this.rawFromTheta(s.th)), hw = Math.max(20, 150 / Math.sqrt(1 + s.N / 8));
    const r5 = x => Math.round(clamp(x, 5, 495) / 5) * 5, tg = rtgOf(s);
    const z = (p - tg) / (hw / 1.645), prob = 1 / (1 + Math.exp(-1.702 * z));
    return { p: r5(p), lo: r5(p - hw), hi: r5(p + hw), tg, prob };
  },
  rank(p) { let r = RANKS[0][1]; RANKS.forEach(([v, nm]) => { if (p >= v) r = nm; }); return r; },
  /* Elo 式更新：主节点全量，其他 node_ids 半量；全局能力 th 用于预测分 */
  update(it, ok) {
    const s = this.st, b = diffB(it.d), r = ok ? 1 : 0;
    const kg = Math.max(0.06, 0.6 / (1 + 0.05 * s.N));
    s.th += kg * (r - sig(s.th - b)); s.N++;
    const up = (n, half) => {
      const v = s.nd[n] || (s.nd[n] = [s.th, 0]);
      const k = Math.max(0.15, 0.8 / (1 + 0.1 * v[1])) * (half ? 0.5 : 1);
      v[0] += k * (r - sig(v[0] - b)); v[1]++;
    };
    up(it.n, false); it.ns.forEach(n => up(n, true));
    s.cons[it.n] = ok ? 0 : (s.cons[it.n] || 0) + 1;
  },
  /* FSRS-4.5：自动评分（错/查词=Again，慢=Hard，正常=Good，快=Easy）；新题快对不建卡；考前压缩。
   * ev = 本次写入日志的 answer 事件，和回放用的是同一个 FSRS.applyEvent。 */
  schedule(ev) {
    this.fxEnsure();
    FSRS.applyEvent({ cards: this.st.cards, exam: FSRS.examDayIndex(this.st.exam) }, ev, this.fxParams());
  },
  scheduleWord(w, grade) { // grade: 2 认识 1 模糊 0 不认识 → Good / Hard / Again
    this.fxEnsure(); const c = this.st.words[w]; if (!c) return;
    Object.assign(c, FSRS.scheduleCard(c, grade === 2 ? FSRS.GOOD : grade === 1 ? FSRS.HARD : FSRS.AGAIN, fxToday(), FSRS.examDayIndex(this.st.exam), this.fxParams()));
  },
  addWord(w, ctx) {
    this.fxEnsure(); w = w.toLowerCase(); const s = this.st, t = fxToday();
    if (!s.words[w]) s.words[w] = { c: ctx.slice(0, 160), ts: Date.now(), s: null, d: null, last: null, due: t + 1, reps: 0, lapses: 0, rv: null };
    else s.words[w].due = Math.min(s.words[w].due, t + 1);
    this.log('word', { w, tz: fxTz() });
  },
  /* 记一次作答（训练/诊断/复习/模考交卷都走这里） */
  record(it, ans, mode) {
    const ok = ans.c === it.a;
    this.update(it, ok);
    const ev = this.log('answer', { tz: fxTz(), id: it.id, mode, c: ans.c, ok: ok ? 1 : 0, ms: ans.ms, lu: ans.lu ? 1 : 0, ms_target: it.t * 1000 });
    if (mode !== 'diag') { this.schedule(ev); if (!ok) this.st.wrong[it.id] = Date.now(); }
    this.maybeRefit();
    const sn = this.st.seen[it.id] || [0, 0]; sn[0]++; sn[1] = ok ? 1 : 0; this.st.seen[it.id] = sn;
    const d = today(); this.st.days[d] = (this.st.days[d] || 0) + 1; this.touchStreak();
    return ok;
  },
  touchStreak() {
    const s = this.st.streak, d = today();
    if (s.d === d) return;
    const y = new Date(Date.now() - DAY); const yd = y.getFullYear() + '-' + String(y.getMonth() + 1).padStart(2, '0') + '-' + String(y.getDate()).padStart(2, '0');
    const gap = s.d ? Math.round((new Date(d) - new Date(s.d)) / DAY) : 0;
    if (gap === 2 && this.freezeOk()) { this.st.fz = { wk: this.wkKey(), d }; s.n += 2; this.log('streak_freeze', {}); }   // ❄ 断签保护：每周自动补 1 天
    else s.n = s.d === yd ? s.n + 1 : 1;
    s.d = d;
  },
  wkKey(t) { const x = new Date(t || Date.now()); x.setHours(0, 0, 0, 0); x.setDate(x.getDate() - (x.getDay() + 6) % 7); return x.getFullYear() + '-' + String(x.getMonth() + 1).padStart(2, '0') + '-' + String(x.getDate()).padStart(2, '0'); },
  freezeOk() { return !(this.st.fz && this.st.fz.wk === this.wkKey()); },
  streakNow() { const s = this.st.streak; if (!s.d) return 0; const gap = Math.round((new Date(today()) - new Date(s.d)) / DAY); return gap <= 1 || (gap === 2 && this.freezeOk()) ? s.n : 0; },
  /* 训练池：去掉模考用过的套；私有题 u==='mock'（留作模考）永不进训练 */
  pool() {
    const k = this.st.used.join(',');
    if (!this._pool || this._pool.k !== k) { const u = new Set(this.st.used); this._pool = { k, a: D.items.filter(i => i.u !== 'mock' && !(FORMS[i.f] && u.has(i.f))) }; }
    return this._pool.a;
  },
  /* 每个节点在训练池里的可练题数：n=作主节点，any=主节点或其他标注节点 */
  practice() {
    const P = this.pool();
    if (this._prac && this._prac.a === P) return this._prac.m;
    const m = {}; P.forEach(i => { const add = (x, prim) => { const o = m[x] || (m[x] = { n: 0, any: 0 }); o.any++; if (prim) o.n++; }; add(i.n, true); i.ns.forEach(x => { if (x !== i.n) add(x, false); }); });
    this._prac = { a: P, m }; return m;
  },
  /* 薄弱节点：考频 × (1 − 掌握度)；未测节点用全局能力并稍加探索分 */
  weakList() {
    const g = sig(this.st.th), bd = this.band();
    return D.nodes.filter(n => !n.g && BY_NODE[n.id] && n.w > 0 && (!n.mb || n.mb.includes(bd))).map(n => {   // C2：只列目标档 must 集合
      const m = this.mastery(n.id), mm = m == null ? g : m;
      return { n, m, sc: n.w * (1 - mm) * (m == null ? 0.9 : 1) };
    }).sort((a, b) => b.sc - a.sc);
  },
  /* 今天该复习：每日上限 20，超出按"考频×遗忘程度"顺延到后几天（不出现逾期） */
  /* 今天该复习（C2）：题卡 + 生词合并每日上限 20；积压平摊 5–7 天；考前 3 天只留高考频（Planner.reviewQueue） */
  cardWeight(id) {
    const it = IT[id]; if (!it) return 0.5; const n = ND[it.n]; if (!n) return 0.5;
    let w = n.w > 0 ? n.w : 0.05; if (/^QT\.P7X\./.test(n.id) && ND[n.pa]) w = Math.max(w, ND[n.pa].w || 0);   // 设问×文本组合按其设问类型算考频
    return w;
  },
  reviewQueue() {
    this.fxEnsure();
    const day = fxToday(), ex = FSRS.examDayIndex(this.st.exam), left = ex != null ? ex - day : null;
    return Planner.reviewQueue(this.st.cards, this.st.words, day, { params: this.fxParams(), filter: id => !!IT[id],
      weight: id => this.cardWeight(id), highOnly: left != null && left >= 0 && left <= 3 });
  },
  dueItems() { return this.reviewQueue().items; },
  dueWords() { return this.reviewQueue().words; },
  /* 选题：节点集合内、未做过、难度贴近能力 */
  pickSingles(nodes, k, used, fill) {
    const ns = new Set(nodes), th = this.st.th;
    let c = this.pool().filter(i => i.p === 5 && !used.has(i.id) && (ns.size === 0 || ns.has(i.n) || i.ns.some(x => ns.has(x))));
    // fill：薄弱节点里 P5 不够 k 道时（前几名薄弱点常是 TX/ST 等非 P5 节点），用其余 P5 补足（日常训练按设计"补到 8"）
    if (fill && c.length < k) { const have = new Set(c.map(i => i.id)); c = c.concat(this.pool().filter(i => i.p === 5 && !used.has(i.id) && !have.has(i.id)).sort(() => Math.random() - 0.5).slice(0, k - c.length)); }
    c.sort((a, b) => ((this.st.seen[a.id] ? 5 : 0) + Math.abs(diffB(a.d) - th) + Math.random()) - ((this.st.seen[b.id] ? 5 : 0) + Math.abs(diffB(b.d) - th) + Math.random()));
    const out = c.slice(0, k); out.forEach(i => used.add(i.id)); return out.map(i => ({ ids: [i.id] }));
  },
  pickBundle(part, nodes, used, kind, must) {
    const ns = new Set(nodes), u = new Set(this.st.used);
    const c = D.bundles.filter(b => b.p === part && b.qs.length && !(FORMS[b.f] && u.has(b.f)) && !b.qs.some(q => !IT[q] || IT[q].u === 'mock') && !b.qs.some(q => used.has(q)) && (!kind || kind.includes(b.k)) && (!must || b.qs.some(q => ns.has(IT[q].n) || IT[q].ns.some(x => ns.has(x)))));
    const score = b => b.qs.reduce((s, q) => { const i = IT[q]; return s + (ns.has(i.n) || i.ns.some(x => ns.has(x)) ? 1 : 0) - (this.st.seen[q] ? 2 : 0); }, 0) + Math.random();
    c.sort((a, b) => score(b) - score(a));
    const b = c[0]; if (!b) return null; b.qs.forEach(q => used.add(q)); return { b: b.id, ids: b.qs.slice() };
  },
  /* 复习单元：P5 单题；P6/P7 只出到期那题，但带原文 */
  reviewUnits(cap) {
    return this.dueItems().slice(0, cap).map(id => IT[id].b ? { b: IT[id].b, ids: [id] } : { ids: [id] });
  },
  /* 每日任务（C2）：由 ROI 排程决定，见 getTodayPlan */
  plan(min) { return this.getTodayPlan(this.st, min || 5).units; },
  weakPlan(nodeId) { // 攻克：该节点的 P5 单题 ×6 + 含该节点的 P6/P7 各 1 组（按题库实际分布）
    const used = new Set(), out = this.pickSingles([nodeId], 6, used), has = new Set((BY_NODE[nodeId] || []).map(q => IT[q].p));
    [6, 7].forEach(p => { if (has.has(p)) { const b = this.pickBundle(p, [nodeId], used, null, true); if (b) out.unshift(b); } });
    return out;
  },
  diagPlan(min) {
    const P = D.items.filter(i => i.src === 'pilot' && i.p === 5), used = new Set(), out = [];
    [2, 2, 3, 3, 4, 4].forEach(d => { const c = P.filter(i => i.d === d && !used.has(i.id)); const i = c[Math.floor(Math.random() * c.length)] || P.find(i => !used.has(i.id)); used.add(i.id); out.push({ ids: [i.id] }); });
    const pb = D.bundles.filter(b => b.qs[0] && b.qs[0].startsWith('PL'));
    const b6 = pb.find(b => b.p === 6), b7 = pb.filter(b => b.p === 7 && b.k === 'single' && b.qs.length <= 3)[0];
    if (b6) out.push({ b: b6.id, ids: b6.qs.slice() }); if (b7) out.push({ b: b7.id, ids: b7.qs.slice() });
    return out;
  },
  /* 模考：选未用过、做过题最少的整套（题数 ≥ FULL_MIN 的任意 form） */
  nextForm() {
    const u = new Set(this.st.used);
    return Object.keys(FORMS).filter(f => !u.has(f)).sort((a, b) => FORMS[a].filter(q => this.st.seen[q]).length - FORMS[b].filter(q => this.st.seen[q]).length)[0] || null;
  },
  mockPlan(form) {
    const out = [], done = new Set();
    FORMS[form].forEach(id => {
      if (done.has(id)) return; const i = IT[id];
      if (i.b) { const b = BU[i.b]; b.qs.forEach(q => done.add(q)); out.push({ b: b.id, ids: b.qs.slice() }); }
      else { done.add(id); out.push({ ids: [id] }); }
    });
    return out;
  },
  rules(nodeId) {
    const n = ND[nodeId], keys = new Set([nodeId, n && n.pa].filter(Boolean));
    return D.strats.filter(s => s.pm && s.ns.some(x => keys.has(x))).sort((a, b) => b.w - a.w).slice(0, 2);
  },
  /* ================= C2：ROI 排程 + 个性化（对前端的 API，见 docs/engine_api.md） ================= */
  band() { const r = this.st.rtg; return r ? (r <= 225 ? '≤500' : r <= 300 ? '600' : r <= 370 ? '730' : '860+') : Planner.band(this.st.target); },
  rtg() { return rtgOf(this.st); },
  pctx(minutesPerDay) {
    return { nodes: ND, practice: this.practice(), acc: this.macc(), now: Date.now(), band: this.band(), day: fxToday(),
      examDay: FSRS.examDayIndex(this.st.exam), minutesPerDay: minutesPerDay || (this.st.settings && this.st.settings.daily_min) || 5 };
  },
  paceProfile() { return Personal.pace(this.macc()); },
  estSec(id, pc) { const it = IT[id]; return it.t * ((pc || this.paceProfile())[it.p] || { ratio: 1 }).ratio + 10; },  // 作答 + 看反馈约 10 秒
  /* 为节点挑一个练习单元：优先 P5 单题（主节点优先、未做过、难度贴近该节点能力），否则含该节点的 P6/P7 篇章（按档位终点线限制篇型） */
  pickFor(node, used, maxSec, pc) {
    const mu = (this.macc().nd[node] || {}).mu || 0, seen = this.st.seen;
    const bd = this.band(), inBand = n => !ND[n] || !ND[n].mb || ND[n].mb.includes(bd);   // 题目主考点也须在目标档内（不借道练档外考点）
    const P = this.pool().filter(i => i.p === 5 && !used.has(i.id) && (i.n === node || i.ns.includes(node)) && inBand(i.n));
    if (P.length) {
      P.sort((a, b) => ((seen[a.id] ? 5 : 0) + (a.n === node ? 0 : 0.5) + Math.abs(diffB(a.d) - mu)) - ((seen[b.id] ? 5 : 0) + (b.n === node ? 0 : 0.5) + Math.abs(diffB(b.d) - mu)));
      const i = P[0]; return this.estSec(i.id, pc) <= maxSec ? { ids: [i.id], node, est: Math.round(this.estSec(i.id, pc)) } : null;
    }
    const kinds = bd === '≤500' || bd === '600' ? ['single'] : bd === '730' ? ['single', 'double'] : null, u = new Set(this.st.used);
    const c = D.bundles.filter(b => b.qs.length && (b.p === 6 || b.p === 7) && (b.p === 6 || !kinds || kinds.includes(b.k)) && !(FORMS[b.f] && u.has(b.f)) &&
      !b.qs.some(q => !IT[q] || IT[q].u === 'mock' || used.has(q)) && b.qs.some(q => IT[q].n === node || IT[q].ns.includes(node)) && b.qs.filter(q => inBand(IT[q].n)).length * 2 >= b.qs.length)
      .map(b => ({ b, est: b.qs.reduce((s, q) => s + this.estSec(q, pc), 0), sc: b.qs.reduce((s, q) => s + (IT[q].n === node || IT[q].ns.includes(node) ? 1 : 0) - (seen[q] ? 2 : 0), 0) }))
      .filter(x => x.est <= maxSec).sort((x, y) => y.sc - x.sc || x.est - y.est || (x.b.id < y.b.id ? -1 : 1));
    return c[0] ? { b: c[0].b.id, ids: c[0].b.qs.slice(), node, est: Math.round(c[0].est) } : null;
  },
  /* 今日任务：复习（合并上限 20）+ 按 ROI 的新学 / 维持；按个人用时估时间装满 minutes */
  getTodayPlan(state, minutes) {
    if (state && state !== this.st) { const k = this.st; this.st = state; try { return this.getTodayPlan(state, minutes); } finally { this.st = k; } }
    minutes = minutes || (this.st.settings && this.st.settings.daily_min) || 5;
    const T = Planner.today(this.pctx(), minutes), pc = this.paceProfile(), rq = this.reviewQueue(), used = new Set(), units = [];
    rq.items.forEach(id => used.add(id));
    Object.keys(this.st.cards).forEach(id => { const c = this.st.cards[id]; if (c.due <= fxToday()) used.add(id); });   // 到期但排到以后的卡不拿来当新题（保证复习 ≤20/天）
    let rsec = 0; const words = [];
    for (const id of rq.items) {
      const it = IT[id], e = this.estSec(id, pc) + (it.b ? 30 : 0);
      if (rsec + e > T.reviewSec && (units.length || T.mode !== 'review_only')) break;
      units.push(it.b ? { b: it.b, ids: [id], kind: 'review', node: it.n, est: Math.round(e) } : { ids: [id], kind: 'review', node: it.n, est: Math.round(e) }); rsec += e;
    }
    for (const w of rq.words) { if (rsec + 6 > T.reviewSec) break; words.push(w); rsec += 6; }
    let left = T.totalSec - rsec;
    const kind = T.mode === 'learn' ? 'learn' : 'maintain';
    let pool = T.mode === 'review_only' ? T.analysis.goal.filter(x => x.seen && x.w >= Planner.HIGH_W && !x.dropped).sort((a, b) => a.margin - b.margin).map(x => x.id) : T.ranked.map(x => x.id);
    const K = minutes <= 5 ? 2 : minutes <= 20 ? 3 : 4, act = pool.slice(0, K); let nx = K;
    while (left >= 25 && act.length) {
      let any = false;
      for (let k = 0; k < act.length && left >= 25; k++) {
        const u = this.pickFor(act[k], used, left + (units.length ? 0 : 60), pc);
        if (!u) { act.splice(k, 1); k--; if (nx < pool.length) act.push(pool[nx++]); continue; }
        u.kind = kind; units.push(u); u.ids.forEach(q => used.add(q)); left -= u.est; any = true;
      }
      if (!any) break;
    }
    const A = T.analysis, nodes = T.nodes.map(id => { const g = A.goal.find(x => x.id === id); return { id, nm: ND[id] && ND[id].nm, m: g ? Math.round(g.m * 100) / 100 : null, stuck: g ? g.stuck : false }; });
    return { mode: T.mode, phase: T.phase, daysLeft: T.daysLeft, minutes, band: A.band, units, words,
      reviewCount: units.filter(u => u.kind === 'review').length + words.length, backlog: rq.backlog,
      estSec: Math.round(T.totalSec - left), nodes, progress: Planner.progressText(A), tip: this.getProfile().circadian.tip };
  },
  /* 进度：离目标还差 N 个考点、约 X 小时；维持模式；倒排放弃；作战卡 */
  getProgress(state) {
    if (state && state !== this.st) { const k = this.st; this.st = state; try { return this.getProgress(state); } finally { this.st = k; } }
    const A = Planner.analyze(this.pctx()), nm = id => (ND[id] ? ND[id].nm : id);
    const next = A.goal.filter(x => !x.achieved && !x.dropped && x.unlocked).sort((a, b) => b.roi - a.roi).slice(0, 3);
    return { band: A.band, target: this.st.target, targetMastery: A.target, mode: A.allAchieved ? 'maintain' : 'learn', phase: A.phase, daysLeft: A.daysLeft,
      remainingNodes: A.remainingNodes, remainingHours: Math.round(A.remainingMin / 6) / 10, achievedNodes: A.achievedNodes, totalNodes: A.totalNodes,
      text: Planner.progressText(A), next: next.map(x => ({ id: x.id, nm: nm(x.id), m: Math.round(x.m * 100) / 100, roi: x.roi })),
      stuck: A.goal.filter(x => x.stuck).map(x => x.id), dropped: A.dropped.map(id => ({ id, nm: nm(id) })),
      ruleNodes: A.untrainable.length, nodes: A.goal.map(x => ({ id: x.id, m: Math.round(x.m * 1000) / 1000, achieved: x.achieved, stuck: x.stuck, dropped: !!x.dropped, unlocked: x.unlocked, remainMin: Math.round(x.remainMin) })),
      battle: Personal.battleCard(A.band, this.paceProfile()) };
  },
  /* 记一次作答。event：{item_id, choice, ms, lookups?, viewed_hint?, mode?}（UX §15 answer_submit 字段；也接受 v2 的 {id, c, lu}） */
  recordAnswer(event) {
    const id = event.item_id || event.id, it = IT[id]; if (!it) return null;
    const c = event.choice != null ? event.choice : event.c;
    const ok = this.record(it, { c, ms: event.ms, lu: event.lookups > 0 || !!event.viewed_hint || !!event.lu }, event.mode || 'train');
    return { correct: ok, node: it.n, mastery: this.mastery(it.n) };
  },
  /* 个人画像：各 Part 用时比、作战卡（终点线/跳题预算）、作息建议、FSRS 参数来源 */
  getProfile(state) {
    if (state && state !== this.st) { const k = this.st; this.st = state; try { return this.getProfile(state); } finally { this.st = k; } }
    const acc = this.macc(), pc = Personal.pace(acc), set = this.st.settings || {};
    const f = this.st.fsrsFit;
    return { pace: pc, battle: Personal.battleCard(this.band(), pc), circadian: Personal.circadian(acc, set.circadian !== false),
      fsrs: f ? { personal: !!f.use, reviews: f.n, before: f.before, after: f.after } : { personal: false, reviews: null } };
  },
  /* 设置（追加 setting_change 事件）：circadian=false 关闭作息建议；daily_min 默认每日分钟 */
  setSetting(key, value) { (this.st.settings = this.st.settings || {})[key] = value; this.log('setting_change', { key, value }); },
  /* FSRS 个人参数：每多 100 次作答检查一次；够 300 次复习且拟合更好才采用，并按新参数重放卡片 */
  maybeRefit(force) {
    const s = this.st, n = s.log.filter(e => e.e === 'answer' || e.e === 'answer_submit').length, f = s.fsrsFit;
    if (!force && f && n - f.at < 100) return f;
    if (!force && !f && n < Personal.MIN_REVIEWS) return null;
    const r = Personal.fsrsFit((s.exam ? [{ t: 0, e: 'exam_date_set', exam_date: s.exam }] : []).concat(s.log), { tz: fxTz() });
    const changed = JSON.stringify((f && f.use && f.w) || null) !== JSON.stringify(r.use ? r.w : null);
    s.fsrsFit = { at: n, use: r.use, w: r.w, n: r.n, before: r.before, after: r.after };
    if (changed) this.fxReplay();
    return s.fsrsFit;
  },
  weekStats(st) {
    const t0 = Date.now() - 7 * DAY, a = st.log.filter(x => x.e === 'answer' && x.t >= t0);
    return { n: a.length, acc: a.length ? a.filter(x => x.ok).length / a.length : 0 };
  }
};
if (typeof globalThis !== 'undefined') globalThis.ToeicEngine = E;   // 前端/测试入口（B2 用 ToeicEngine.getTodayPlan 等）
