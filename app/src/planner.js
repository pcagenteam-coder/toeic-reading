/* ===== 最小努力 ROI 排程（C2） =====
 * 原生 JS；浏览器全局 Planner，Node 里 require('./planner.js')（需全局 Mastery / FSRS 或同目录可 require）。
 * 纯函数：输入 = 图谱节点（含 learn_cost_min / must_for_band / prereqs）+ 掌握度回放结果 + 题库可练量 + 日期，
 *         输出 = 目标集合的状态、今日新学/复习时间配比、复习队列（合并上限 20、积压平摊 5–7 天）。
 * 组题（挑具体题目）在 engine.js 里做，这里只决定“练哪些考点、各给多少时间”。
 *
 * ROI(节点) = 考频权重 w × 预计提分空间 (1 − m) / 剩余学习成本（分钟）
 *   剩余成本 = learn_cost_min × max(0.1, 缺口比例) × (学不动 ? 3 : 1)，缺口比例 = (目标 − m)/(目标 − 0.25)
 * 只在目标档 must 集合内、且训练池里作主节点 ≥3 道题的节点（“考点”）里排；前置考点没过 0.5（且练得不够 6 次）不排。
 * 距考试天数倒排：剩余成本 > 考前可用的新学时间 → 按 ROI 只保留排得下的，其余列为“来不及，按放弃规则处理”。
 * 全部（未放弃的）考点达标 → 维持模式：复习为主，余下时间练“离目标最近”的已达标考点。
 */
const Planner = (function () {
  'use strict';
  const M = () => (typeof Mastery !== 'undefined' ? Mastery : require('./mastery.js'));
  const F = () => (typeof FSRS !== 'undefined' ? FSRS : require('./fsrs.js'));
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

  const BANDS = ['≤500', '600', '730', '860+'];
  const TARGET = { '≤500': 0.6, '600': 0.7, '730': 0.8, '860+': 0.88 };   // 达标掌握度（中等难度题预期答对率）
  const MIN_ITEMS = 3, MIN_EVID = 3, HYST = 0.05, UNLOCK_M = 0.5, UNLOCK_ATT = 6, STUCK_MULT = 3;
  const REVIEW_CAP = 20, HIGH_W = 0.12, WORD_W = 0.15;
  const NOVICE_DAYS = 7, NOVICE_M = 0.45, P7_EVERY = 3;   // 新手期：开始后前 7 天，或已练考点平均掌握度 < 0.45 → P5 为主；任意连续 3 天至少 1 篇 P7
  const SHARE = { base: 0.5, strengthen: 0.5, sprint: 0.6, final3: 1, examday: 1, none: 0.5, maintain: 0.7 };

  /* 目标总分 → 档位（graph_v1_cost.json band_from_total） */
  function band(total) {
    total = +total || 600;
    if (total <= 550) return '≤500';
    if (total <= 665) return '600';
    if (total <= 795) return '730';
    return '860+';
  }
  function phaseOf(daysLeft) {
    if (daysLeft == null || daysLeft < 0) return 'none';
    if (daysLeft === 0) return 'examday';
    if (daysLeft <= 3) return 'final3';
    if (daysLeft <= 14) return 'sprint';
    if (daysLeft <= 56) return 'strengthen';
    return 'base';
  }

  /* ctx: { nodes:{id:{id,w,lc,mb[],pr[],g}}, practice:{id:{n,any}}, acc, now, band, day, examDay, minutesPerDay } */
  function analyze(ctx) {
    const Ms = M(), b = ctx.band, tgt = TARGET[b], acc = ctx.acc, now = ctx.now;
    const must = Object.values(ctx.nodes).filter(n => (n.mb || []).includes(b));
    const trainable = n => ctx.practice[n.id] && ctx.practice[n.id].n >= MIN_ITEMS;   // 考点 = 训练池里作主节点 ≥3 题的节点（只作副标签的节点靠证据传播，不单独排）
    const goal = must.filter(trainable).map(n => {
      const o = Ms.of(acc, n.id, now);
      // 达标（带回差）：m ≥ 目标；或曾经达标、现在只回落不到 HYST（避免维持模式因遗忘漂移来回切换）
      const achieved = o.n >= MIN_EVID && (o.m >= tgt || (o.m >= tgt - HYST && (o.h || []).some(v => v >= tgt)));
      const stuck = !achieved && Ms.stuck(acc, n.id, tgt);
      const gap = clamp((tgt - o.m) / (tgt - 0.25), 0, 1);
      const remainMin = achieved ? 0 : (n.lc || 20) * Math.max(0.1, gap) * (stuck ? STUCK_MULT : 1);
      const w = Math.max(0.01, n.w || 0);
      return { id: n.id, nm: n.nm, w, lc: n.lc || 20, m: o.m, n: o.n, att: o.att, seen: o.seen, achieved, stuck, remainMin,
        roi: w * (1 - o.m) / Math.max(1, remainMin), margin: o.m - tgt };
    });
    const G = {}; goal.forEach(x => { G[x.id] = x; });
    goal.forEach(x => {
      const pre = (ctx.nodes[x.id].pr || []).filter(p => G[p]);
      x.blockedBy = pre.filter(p => !(G[p].achieved || G[p].m >= UNLOCK_M || G[p].att >= UNLOCK_ATT));
      x.unlocked = x.blockedBy.length === 0;
    });
    // 倒排
    const daysLeft = ctx.examDay != null ? ctx.examDay - ctx.day : null, phase = phaseOf(daysLeft);
    const mpd = ctx.minutesPerDay || 5;
    let dropped = [];
    const open = goal.filter(x => !x.achieved).sort((a, c) => c.roi - a.roi);
    if (daysLeft != null && daysLeft >= 0) {
      let budget = 0;   // 考前还能用于新学的分钟数（按阶段的新学占比逐日累加）
      for (let k = 0; k < daysLeft; k++) budget += mpd * (1 - SHARE[phaseOf(daysLeft - k)]);
      let cum = 0;
      open.forEach(x => { if (cum + x.remainMin <= budget) cum += x.remainMin; else { x.dropped = true; dropped.push(x.id); } });
    }
    const active = goal.filter(x => !x.dropped);
    const remaining = active.filter(x => !x.achieved);
    const untrainable = must.filter(n => !n.g && !trainable(n)).map(n => n.id);
    return {
      band: b, target: tgt, phase, daysLeft, goal, dropped, untrainable,
      allAchieved: active.length > 0 && remaining.length === 0,
      remainingNodes: remaining.length, remainingMin: Math.round(remaining.reduce((s, x) => s + x.remainMin, 0)),
      achievedNodes: active.filter(x => x.achieved).length, totalNodes: active.length
    };
  }

  /* 新手期与 P7 节奏（纯函数）。ctx.startDay = 开始训练那天的日序号，ctx.lastP7Day = 最近一次练 P7 的日序号（无则 null）
   * novice：开始后 < 7 天，或有证据的目标考点平均掌握度 < 0.45 → 新学以 P5 单题为主（篇章只留必需的那 1 篇 P7）
   * needP7：从未练过 P7 且已到第 3 天（首日计划自带 1 篇），或距上次 P7 已 ≥3 天 → 今天必须排 1 篇 P7 */
  function rhythm(ctx, A) {
    const day = ctx.day, sd = ctx.startDay != null ? ctx.startDay : day;
    const ev = (A.goal || []).filter(x => x.n > 0), avgM = ev.length ? ev.reduce((s, x) => s + x.m, 0) / ev.length : null;
    const novice = day - sd < NOVICE_DAYS || (avgM != null && avgM < NOVICE_M);
    const lp = ctx.lastP7Day;
    const needP7 = lp == null ? day - sd >= P7_EVERY - 1 : day - lp >= P7_EVERY;
    return { novice, needP7, sinceStart: day - sd, avgM };
  }

  /* 今日配比与考点顺序（不挑题） */
  function today(ctx, minutes) {
    const A = analyze(ctx), sec = (minutes || ctx.minutesPerDay || 5) * 60;
    let mode = 'learn';
    if (A.phase === 'final3' || A.phase === 'examday') mode = 'review_only';
    else if (A.allAchieved) mode = 'maintain';
    const share = mode === 'learn' ? SHARE[A.phase] : SHARE[mode === 'maintain' ? 'maintain' : 'final3'];
    let learn = [];
    if (mode === 'learn') learn = A.goal.filter(x => !x.achieved && !x.dropped && x.unlocked).sort((a, b) => b.roi - a.roi);
    else if (mode === 'maintain') learn = A.goal.filter(x => !x.dropped && (A.phase !== 'sprint' || x.w >= HIGH_W)).sort((a, b) => a.margin - b.margin || b.w - a.w);
    const K = minutes <= 5 ? 2 : minutes <= 20 ? 3 : 4, R = rhythm(ctx, A);
    return { mode, phase: A.phase, novice: R.novice, needP7: mode !== 'review_only' && R.needP7, maxBundles: R.novice ? 1 : null, daysLeft: A.daysLeft, reviewSec: Math.round(sec * share), newSec: Math.round(sec * (1 - share)), totalSec: sec,
      nodes: learn.slice(0, K).map(x => x.id), ranked: learn.map(x => ({ id: x.id, roi: x.roi, m: x.m, stuck: x.stuck })), analysis: A };
  }

  /* 合并复习队列：题卡 + 生词卡共用每日上限 20；积压（到期日早于今天）平摊 5–7 天；考前 3 天只留高考频。
   * cards / words：FSRS 卡片表（words 的 key 是单词本身）。weight(cardId) → 考频权重。
   * 返回 { today:[{k, id, type:'item'|'word'}], items:[id], words:[w], backlog, spreadDays, share, plan:{k:day} } */
  function reviewQueue(cards, words, day, opts) {
    opts = opts || {};
    const Fs = F(), p = Fs.params(opts.params), cap = opts.cap != null ? opts.cap : REVIEW_CAP;
    const weight = opts.weight || (() => 1), keep = opts.filter || (() => true), high = !!opts.highOnly;
    const all = [];
    Object.keys(cards || {}).forEach(id => { if (keep(id)) all.push({ k: id, id, type: 'item', c: cards[id], w: weight(id) }); });
    Object.keys(words || {}).forEach(w => { const c = words[w]; if (c && c.due != null) all.push({ k: Fs.WORD + w, id: w, type: 'word', c, w: WORD_W }); });
    const done = all.filter(x => x.c.rv === day).length, left = Math.max(0, cap - done);
    const pr = x => { const c = x.c, R = c.s == null ? 0 : Fs.retrievability(Math.max(0, day - c.last), c.s, p); return x.w * (1 - R); };
    let due = all.filter(x => x.c.due <= day && x.c.rv !== day);
    if (high) due = due.filter(x => x.w >= HIGH_W);
    due.forEach(x => { x.pr = pr(x); });
    const by = (a, b) => b.pr - a.pr || a.c.due - b.c.due || (a.k < b.k ? -1 : a.k > b.k ? 1 : 0);
    const backlog = due.filter(x => x.c.due < day).sort(by), native = due.filter(x => x.c.due >= day).sort(by);
    const spreadDays = backlog.length ? clamp(Math.ceil(backlog.length / (cap / 2)), 5, 7) : 0;
    const share = backlog.length ? Math.ceil(backlog.length / spreadDays) : 0;
    const takeB = backlog.slice(0, Math.min(share, left));
    const takeN = native.slice(0, Math.max(0, left - takeB.length));
    const todayL = takeB.concat(takeN).sort(by);
    const plan = {}; todayL.forEach(x => { plan[x.k] = day; });
    backlog.slice(takeB.length).forEach((x, i) => { plan[x.k] = day + 1 + Math.floor(i / Math.max(1, share)); });
    native.slice(takeN.length).forEach(x => { plan[x.k] = day + 1; });
    return { today: todayL.map(x => ({ k: x.k, id: x.id, type: x.type })), items: todayL.filter(x => x.type === 'item').map(x => x.id),
      words: todayL.filter(x => x.type === 'word').map(x => x.id), backlog: backlog.length - takeB.length, spreadDays, share, done, cap, plan };
  }

  /* 够达标的最少考点数（UX §11.2）：按 ROI 从高到低累加未稳考点，直到它们全部达稳后预测中值 ≥ 目标。
   * pred = {score, lo, target}（预测分点估计/下沿/阅读目标）。每个考点稳下来的提分按 w × (稳阈值 − m) 比例分摊：
   * 假定目标档全部考点达稳 ≈ 目标 + MARGIN 分（档位 must 集合即“够这一档”的定义），且全部从 0 学到稳 ≈ NEED_SPAN 分，K 取两者大者。
   * 预测中值已 ≥ 目标：reached=true；下沿 < 目标 − 10 时仍给“再稳 X 个留余量”（按下沿补齐）；否则 safe=true（只需维持）。 */
  const NEED_MARGIN = 30, NEED_SPAN = 300;
  function need(A, pred) {
    const open = (A.goal || []).filter(x => !x.achieved && !x.dropped).sort((a, b) => b.roi - a.roi);
    const raw = x => (x.w || 1) * Math.max(0.05, (A.target || 0.8) - (x.m || 0));
    const tot = open.reduce((s, x) => s + raw(x), 0);
    const out = { nodes: 0, min: 0, ids: [], reached: false, safe: false, diff: null };
    if (!pred || pred.score == null || !pred.target) { out.nodes = open.length; out.min = Math.round(open.reduce((s, x) => s + x.remainMin, 0)); out.ids = open.map(x => x.id); return out; }
    const tg = pred.target, lo = pred.lo != null ? pred.lo : pred.score;
    out.reached = pred.score >= tg; out.diff = tg - pred.score;
    const gapPts = out.reached ? (tg - 10) - lo : tg - pred.score;   // 已达标：补齐下沿余量；未达标：补到中值
    if (gapPts <= 0 || !open.length) { out.safe = out.reached; return out; }
    // 两个口径取大：①目标档全部考点从 0 学到稳 ≈ NEED_SPAN 分；②当前未稳的全部稳下来 ≈ 目标 + MARGIN
    const all = (A.goal || []).filter(x => !x.dropped).reduce((s, x) => s + (x.w || 1) * (A.target || 0.8), 0);
    const K = Math.max(NEED_SPAN / Math.max(1e-9, all), (tg + NEED_MARGIN - pred.score) / Math.max(1e-9, tot));
    let cum = 0;
    for (const x of open) { if (cum >= gapPts) break; cum += K * raw(x); out.ids.push(x.id); out.min += x.remainMin; }
    out.nodes = out.ids.length; out.min = Math.round(out.min);
    return out;
  }

  /* 小时给区间（P1-1）：0.75×–1.5× 预计分钟，取 0.5 小时步长；< 1 小时写“不到 1 小时” */
  function hoursText(min) {
    if (!min) return '';
    const h = min / 60, r = x => Math.max(0.5, Math.round(x * 2) / 2), lo = r(h * 0.75), hi = r(h * 1.5);
    if (hi <= 1) return '不到 1 小时';
    return lo === hi ? `约 ${lo} 小时` : `约 ${lo}–${hi} 小时`;
  }

  function progressText(A, nd) {
    if (nd && nd.reached) return nd.nodes ? `已够线，再稳 ${nd.nodes} 个考点留出余量` : '已经够到目标了 ✓ 现在只需每天复习保持';
    if (nd) return nd.nodes ? `离目标还差 ${nd.nodes} 个考点（${hoursText(nd.min)}）` : '目标考点已全部达标，进入维持模式';
    if (A.allAchieved) return '目标考点已全部达标，进入维持模式';
    return `离目标还差 ${A.remainingNodes} 个考点（${hoursText(A.remainingMin)}）`;
  }

  return { BANDS, TARGET, NOVICE_DAYS, NOVICE_M, P7_EVERY, MIN_ITEMS, MIN_EVID, REVIEW_CAP, HIGH_W, SHARE, band, phaseOf, analyze, rhythm, today, reviewQueue, progressText, need, hoursText, NEED_MARGIN };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = Planner;
