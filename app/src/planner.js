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
    const K = minutes <= 5 ? 2 : minutes <= 20 ? 3 : 4;
    return { mode, phase: A.phase, daysLeft: A.daysLeft, reviewSec: Math.round(sec * share), newSec: Math.round(sec * (1 - share)), totalSec: sec,
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

  function progressText(A) {
    if (A.allAchieved) return '目标考点已全部达标，进入维持模式';
    return `离目标还差 ${A.remainingNodes} 个考点、约 ${Math.max(0.1, Math.round(A.remainingMin / 6) / 10)} 小时`;
  }

  return { BANDS, TARGET, MIN_ITEMS, MIN_EVID, REVIEW_CAP, HIGH_W, SHARE, band, phaseOf, analyze, today, reviewQueue, progressText };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = Planner;
