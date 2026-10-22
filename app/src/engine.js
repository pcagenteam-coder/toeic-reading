/* ===== 引擎：数据索引 / 掌握度(Elo) / 预测分 / 简化 FSRS / 选题 ===== */
const D = window.TDATA;
const IT = {}, BU = {}, ND = {}, BY_NODE = {}, FORMS = {};
D.items.forEach(i => {
  IT[i.id] = i;
  [i.n].concat(i.ns).forEach(n => (BY_NODE[n] = BY_NODE[n] || []).push(i.id));
  if (i.src === 'xdf') (FORMS[i.f] = FORMS[i.f] || []).push(i.id);
});
D.bundles.forEach(b => { BU[b.id] = b; });
D.nodes.forEach(n => { ND[n.id] = n; });
Object.values(FORMS).forEach(a => a.sort((x, y) => IT[x].q - IT[y].q));

const DAY = 864e5;
const today = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
const dayNum = () => Math.floor((Date.now() - new Date().getTimezoneOffset() * 6e4) / DAY);
const sig = x => 1 / (1 + Math.exp(-x));
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const diffB = d => (d - 3) * 0.7;               // difficulty_est(1–5) → logit 难度
const RT = { 600: 300, 700: 350, 800: 400, 900: 450 }; // 总分目标 → 阅读分目标（按一半估）
const RANKS = [[0, '实习生'], [200, '专员'], [300, '主管'], [375, '经理'], [430, '总监']];
const SCALE = [[0, 5], [10, 5], [20, 60], [30, 110], [40, 165], [50, 220], [60, 275], [70, 330], [80, 385], [90, 440], [95, 470], [100, 495]];

function newState(target, exam) {
  return { ver: 2, created: Date.now(), target: target || 700, exam: exam || '', diag: false,
    th: 0, N: 0, nd: {}, seen: {}, cards: {}, words: {}, wrong: {}, mocks: [], used: [],
    streak: { d: '', n: 0 }, days: {}, log: [], hist: [], cons: {}, hl: {}, run: null };
}

const E = {
  st: null,
  log(e, o) { const L = this.st.log; L.push(Object.assign({ t: Date.now(), e }, o || {})); if (L.length > 20000) L.splice(0, L.length - 20000); },
  mastery(n) { const v = this.st.nd[n]; return v ? sig(v[0]) : null; },
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
    const r5 = x => Math.round(clamp(x, 5, 495) / 5) * 5, tg = RT[s.target] || s.target / 2;
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
  /* 简化 FSRS：快对×2.5、慢对×1.3、错/查词→1 天。新题快对不建卡（已会）。 */
  schedule(id, ok, fast, lookedUp) {
    const s = this.st, c = s.cards[id];
    if (!c && ok && fast && !lookedUp) return;
    const iv = c ? c.ivl : 1;
    const ni = (!ok || lookedUp) ? 1 : (fast ? Math.max(1, iv) * 2.5 : Math.max(1, iv) * 1.3);
    s.cards[id] = { ivl: ni, due: dayNum() + Math.round(ni) };
    if (!ok) s.wrong[id] = Date.now();
  },
  scheduleWord(w, grade) { // grade: 2 认识 1 模糊 0 不认识
    const c = this.st.words[w]; if (!c) return;
    c.ivl = grade === 2 ? Math.max(1, c.ivl) * 2.5 : grade === 1 ? Math.max(1, c.ivl) * 1.3 : 1;
    c.due = dayNum() + Math.round(c.ivl);
  },
  addWord(w, ctx) {
    w = w.toLowerCase(); const s = this.st;
    if (!s.words[w]) s.words[w] = { c: ctx.slice(0, 160), ivl: 1, due: dayNum() + 1, ts: Date.now() };
    else s.words[w].due = dayNum() + 1;
    this.log('word', { w });
  },
  /* 记一次作答（训练/诊断/复习/模考交卷都走这里） */
  record(it, ans, mode) {
    const ok = ans.c === it.a, fast = ans.ms / 1000 <= it.t;
    this.update(it, ok);
    if (mode !== 'diag') this.schedule(it.id, ok, fast, !!ans.lu);
    const sn = this.st.seen[it.id] || [0, 0]; sn[0]++; sn[1] = ok ? 1 : 0; this.st.seen[it.id] = sn;
    const d = today(); this.st.days[d] = (this.st.days[d] || 0) + 1; this.touchStreak();
    this.log('answer', { id: it.id, mode, c: ans.c, ok: ok ? 1 : 0, ms: ans.ms, lu: ans.lu ? 1 : 0 });
    return ok;
  },
  touchStreak() {
    const s = this.st.streak, d = today();
    if (s.d === d) return;
    const y = new Date(Date.now() - DAY); const yd = y.getFullYear() + '-' + String(y.getMonth() + 1).padStart(2, '0') + '-' + String(y.getDate()).padStart(2, '0');
    s.n = s.d === yd ? s.n + 1 : 1; s.d = d;
  },
  streakNow() { const s = this.st.streak; if (!s.d) return 0; const gap = (new Date(today()) - new Date(s.d)) / DAY; return gap <= 1 ? s.n : 0; },
  /* 训练池：去掉模考用过的套 */
  pool() { const u = new Set(this.st.used); return D.items.filter(i => !(i.src === 'xdf' && u.has(i.f))); },
  /* 薄弱节点：考频 × (1 − 掌握度)；未测节点用全局能力并稍加探索分 */
  weakList() {
    const g = sig(this.st.th);
    return D.nodes.filter(n => !n.g && BY_NODE[n.id] && n.w > 0).map(n => {
      const m = this.mastery(n.id), mm = m == null ? g : m;
      return { n, m, sc: n.w * (1 - mm) * (m == null ? 0.9 : 1) };
    }).sort((a, b) => b.sc - a.sc);
  },
  dueItems() { const t = dayNum(); return Object.keys(this.st.cards).filter(id => IT[id] && this.st.cards[id].due <= t).sort((a, b) => this.st.cards[a].due - this.st.cards[b].due); },
  dueWords() { const t = dayNum(); return Object.keys(this.st.words).filter(w => this.st.words[w].due <= t); },
  /* 选题：节点集合内、未做过、难度贴近能力 */
  pickSingles(nodes, k, used) {
    const ns = new Set(nodes), th = this.st.th;
    const c = this.pool().filter(i => i.p === 5 && !used.has(i.id) && (ns.size === 0 || ns.has(i.n) || i.ns.some(x => ns.has(x))));
    c.sort((a, b) => ((this.st.seen[a.id] ? 5 : 0) + Math.abs(diffB(a.d) - th) + Math.random()) - ((this.st.seen[b.id] ? 5 : 0) + Math.abs(diffB(b.d) - th) + Math.random()));
    const out = c.slice(0, k); out.forEach(i => used.add(i.id)); return out.map(i => ({ ids: [i.id] }));
  },
  pickBundle(part, nodes, used, kind, must) {
    const ns = new Set(nodes), u = new Set(this.st.used);
    const c = D.bundles.filter(b => b.p === part && b.qs.length && !(b.qs[0].startsWith('XDF') && u.has(b.f)) && !b.qs.some(q => used.has(q)) && (!kind || kind.includes(b.k)) && (!must || b.qs.some(q => ns.has(IT[q].n) || IT[q].ns.some(x => ns.has(x)))));
    const score = b => b.qs.reduce((s, q) => { const i = IT[q]; return s + (ns.has(i.n) || i.ns.some(x => ns.has(x)) ? 1 : 0) - (this.st.seen[q] ? 2 : 0); }, 0) + Math.random();
    c.sort((a, b) => score(b) - score(a));
    const b = c[0]; if (!b) return null; b.qs.forEach(q => used.add(q)); return { b: b.id, ids: b.qs.slice() };
  },
  /* 复习单元：P5 单题；P6/P7 只出到期那题，但带原文 */
  reviewUnits(cap) {
    return this.dueItems().slice(0, cap).map(id => IT[id].b ? { b: IT[id].b, ids: [id] } : { ids: [id] });
  },
  plan(min) {
    const used = new Set(), top = this.weakList().slice(0, 6).map(x => x.n.id);
    if (min === 5) { const r = this.reviewUnits(4).filter(u => !u.b); r.forEach(u => used.add(u.ids[0])); return r.concat(this.pickSingles(top, 8 - r.length, used)); }
    if (min === 20) {
      const r = this.reviewUnits(10); r.forEach(u => u.ids.forEach(q => used.add(q)));
      const out = r.concat(this.pickSingles(top, 8, used));
      const b6 = this.pickBundle(6, top, used); if (b6) out.push(b6);
      const b7 = this.pickBundle(7, top, used, ['single']); if (b7) out.push(b7);
      return out;
    }
    return null;
  },
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
  /* 模考：选做过题最少、未用过的 xdf 套 */
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
  weekStats(st) {
    const t0 = Date.now() - 7 * DAY, a = st.log.filter(x => x.e === 'answer' && x.t >= t0);
    return { n: a.length, acc: a.length ? a.filter(x => x.ok).length / a.length : 0 };
  }
};
