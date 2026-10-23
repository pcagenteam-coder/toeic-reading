/* ===== 掌握度模型（C2）：带不确定度的 Elo / 1PL-IRT（Glicko 式近似贝叶斯更新） =====
 * 原生 JS、无依赖；浏览器里是全局 Mastery，Node 里 require('./mastery.js')。
 *
 * 每个节点一个能力 θ~N(mu, v)（logit 尺度）。题目难度 b = (difficulty_est − 3) × 0.7（与 engine 原 Elo 同尺度）。
 * 一次作答的“得分” r ∈ [0,1]：
 *   错 → 0；对但查词/看提示 → 0.5；对但用时 > 1.5×目标 → 0.8；对且正常 → 1。
 * 更新（单步拉普拉斯近似，Glickman 1999 的 logistic 版本）：
 *   p = σ(mu − b)，I = p(1−p)，v' = 1/(1/v + ω·I)，mu' = mu + v'·ω·(r − p)
 *   ω = 证据权重：题目主节点 1、其他标注节点 0.5、主节点的前置节点 0.15（前置弱证据传播）。
 * 不确定度随时间增长（每天 +DRIFT，封顶 V0）→ 久不练的节点“掌握度”向 0.5 回落，自然产生维持需求。
 * 掌握度 m = E[σ(θ − 0)] ≈ σ(mu / √(1 + π·v/8))：对一道中等难度（d=3）题的预期答对率，已计入不确定度。
 * 未作答节点：用全局能力（所有作答共同更新的一个 θ）+ 先验方差 V0 作先验。
 *
 * 纯函数回放：replay(events, ctx) 只依赖事件日志与题目索引；apply(acc, ev, ctx) 增量，与回放结果一致。
 * 同一遍回放顺带统计个人画像原始量（各 Part 用时比、各时段的“超预期”残差），供 personal.js 使用。
 */
const Mastery = (function () {
  'use strict';
  const V0 = 1.0, V_MIN = 0.06, G_V_MIN = 0.02, DRIFT = 0.01, MU_LIM = 4;
  const W_PRIMARY = 1, W_SECONDARY = 0.5, W_PREREQ = 0.15;
  const SLOW_RATIO = 1.5, HIST = 12, DAY = 864e5;
  const sig = x => 1 / (1 + Math.exp(-x));
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const diffB = d => ((d || 3) - 3) * 0.7;
  /* 时段（本地时间）：作息画像用 */
  const SLOTS = [[5, 9, 'early', '早上'], [9, 12, 'morning', '上午'], [12, 14, 'noon', '中午'], [14, 18, 'afternoon', '下午'], [18, 22, 'evening', '晚上']];
  const slotOf = (t, tz) => {
    const h = new Date(t + (tz != null ? tz : 480) * 6e4).getUTCHours();
    const s = SLOTS.find(x => h >= x[0] && h < x[1]); return s ? s[2] : 'late';
  };
  const SLOT_NAMES = { early: '早上 5–9 点', morning: '上午 9–12 点', noon: '中午 12–14 点', afternoon: '下午 14–18 点', evening: '晚上 18–22 点', late: '深夜 22–5 点' };

  function create() {
    return { g: { mu: 0, v: V0, n: 0 }, nd: {}, n: 0, last: 0, pace: {}, slot: {}, ver: 1 };
  }
  const expP = (mu, v) => sig(mu / Math.sqrt(1 + Math.PI * v / 8));

  function nodeState(acc, id, t) {
    let s = acc.nd[id];
    if (!s) s = acc.nd[id] = { mu: acc.g.mu, v: V0, n: 0, att: 0, last: t, h: [] };
    else if (t > s.last) { s.v = Math.min(V0, s.v + DRIFT * (t - s.last) / DAY); s.last = t; }
    return s;
  }
  function upd(s, b, r, w, vmin) {
    const p = sig(s.mu - b), I = p * (1 - p);
    s.v = Math.max(vmin, 1 / (1 / s.v + w * I));
    s.mu = clamp(s.mu + s.v * w * (r - p), -MU_LIM, MU_LIM);
    return p;
  }

  /* 作答得分 r（见文件头）。返回 null = 不计入（统一涂卡 / 未作答） */
  function scoreOf(ev) {
    const legacy = ev.e === 'answer';
    if (ev.bulk_fill) return null;
    const choice = legacy ? ev.c : ev.choice;
    if (choice == null && ev.mode === 'mock') return null;
    const ok = legacy ? !!ev.ok : !!ev.correct;
    if (!ok) return 0;
    if (legacy ? ev.lu : (ev.lookups > 0 || ev.viewed_hint)) return 0.5;
    if (ev.ms > 0 && ev.ms_target > 0 && ev.ms > SLOW_RATIO * ev.ms_target) return 0.8;
    return 1;
  }

  /* ctx = { item(id) → {n, ns[], d, p, t}，prereqs(nodeId) → [nodeId] } */
  function apply(acc, ev, ctx) {
    if (!ev || (ev.e !== 'answer' && ev.e !== 'answer_submit')) return acc;
    const id = ev.e === 'answer' ? ev.id : ev.item_id, it = id && ctx.item(id);
    if (!it) return acc;
    const r = scoreOf(ev); if (r == null) return acc;
    const t = ev.t || 0, b = diffB(it.d);
    acc.n++; acc.last = Math.max(acc.last, t);
    const pg = upd(acc.g, b, r, 1, G_V_MIN); acc.g.n++;
    // 主节点
    const s = nodeState(acc, it.n, t);
    upd(s, b, r, W_PRIMARY, V_MIN); s.n += W_PRIMARY; s.att++;
    s.h.push(Math.round(expP(s.mu, s.v) * 1000) / 1000); if (s.h.length > HIST) s.h.shift();
    // 其他标注节点
    (it.ns || []).forEach(x => { if (x === it.n) return; const q = nodeState(acc, x, t); upd(q, b, r, W_SECONDARY, V_MIN); q.n += W_SECONDARY; q.att2 = (q.att2 || 0) + 1; });
    // 前置弱证据
    const pre = ctx.prereqs ? ctx.prereqs(it.n) || [] : [];
    pre.forEach(x => { const q = nodeState(acc, x, t); upd(q, b, r, W_PREREQ, V_MIN); q.n += W_PREREQ; });
    // 画像：用时比（各 Part）
    const tgt = ev.ms_target > 0 ? ev.ms_target : (it.t ? it.t * 1000 : 0);
    if (ev.ms > 0 && tgt > 0 && !ev.bulk_fill) {
      const pc = acc.pace[it.p] || (acc.pace[it.p] = { n: 0, sum: 0 });
      pc.n++; pc.sum += clamp(ev.ms / tgt, 0.2, 4);
    }
    // 画像：时段残差（实际 − 作答前全局模型预期），控制了题目难度与能力变化
    const k = slotOf(t, ev.tz), sl = acc.slot[k] || (acc.slot[k] = { n: 0, ok: 0, res: 0 });
    sl.n++; sl.ok += r >= 0.8 ? 1 : 0; sl.res += (r >= 0.8 ? 1 : 0) - pg;
    return acc;
  }

  function order(events) {
    return (typeof FSRS !== 'undefined' && FSRS.orderEvents) ? FSRS.orderEvents(events) :
      (events || []).slice().sort((a, b) => (a.t || 0) - (b.t || 0));
  }
  function replay(events, ctx) { return order(events).reduce((a, e) => apply(a, e, ctx), create()); }

  /* 读一个节点：m=掌握度，n=加权证据量，att=主节点作答次数，seen=是否有过直接证据。now 用于计入遗忘漂移 */
  function of(acc, id, now) {
    const s = acc.nd[id];
    if (!s) return { m: expP(acc.g.mu, V0 + acc.g.v), n: 0, att: 0, seen: false, h: [] };
    const v = now && now > s.last ? Math.min(V0, s.v + DRIFT * (now - s.last) / DAY) : s.v;
    return { m: expP(s.mu, v), mu: s.mu, v, n: s.n, att: s.att, att2: s.att2 || 0, seen: s.att + (s.att2 || 0) > 0, h: s.h };
  }
  /* 学不动：主节点作答 ≥10 次，最近 8 次掌握度涨幅 < 0.03，且仍低于目标 */
  function stuck(acc, id, target) {
    const s = acc.nd[id]; if (!s || s.att < 10 || s.h.length < 9) return false;
    const h = s.h, now = h[h.length - 1];
    return now < target && now - h[h.length - 9] < 0.03;
  }
  function globalM(acc) { return expP(acc.g.mu, acc.g.v); }

  return { create, apply, replay, of, stuck, globalM, scoreOf, slotOf, SLOT_NAMES, diffB,
    consts: { V0, V_MIN, DRIFT, W_PRIMARY, W_SECONDARY, W_PREREQ, SLOW_RATIO } };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = Mastery;
