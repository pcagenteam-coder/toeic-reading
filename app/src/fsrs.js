/* ===== FSRS-4.5 引擎（C1）：自动评分 / 考前压缩 / 积压平摊 / 事件日志回放 =====
 * 原生 JS、无依赖；浏览器里作为全局 FSRS（build.py 拼接），Node 里 require('./fsrs.js')。
 *
 * 算法核心移植自 huieric/toefl-miniapp server/src/services/fsrs.js（MIT License）
 *   https://github.com/huieric/toefl-miniapp
 *   参考：https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm
 * MIT License — Copyright (c) huieric / toefl-miniapp contributors.
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software
 * and associated documentation files (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify, merge, publish, distribute,
 * sublicense, and/or sell copies of the Software, subject to the condition that the above copyright
 * notice and this permission notice shall be included in all copies or substantial portions of the
 * Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
 *
 * 修正：参考实现 nextRecallStability 把 e^{w8}·(11−D) 误写为 exp(w8·(11−D))，此处按官方公式
 *   （与 open-spaced-repetition/py-fsrs 2.5.1 = FSRS-4.5 一致）。
 * 改造（本项目）：参数可配置（目标保持率等）；评分由作答自动推断；距考试 ≤14 天提高保持率且
 * 间隔不越过考试日；每日复习上限 + 按"考频×遗忘程度"顺延（无"逾期"）；所有卡片状态由
 * 答题事件日志纯函数回放得到（UX_SPEC_v1 §6.2 / §9.3 / §11 / §15）。
 *
 * 状态 S=稳定度(天) D=难度(1–10)；评分 1=Again 2=Hard 3=Good 4=Easy。
 * 排程按"天"计：一天从本地凌晨 4 点开始（UX §9.1），dayIndex = 本地日期的 UTC 天序号。
 */
const FSRS = (function () {
  'use strict';
  const AGAIN = 1, HARD = 2, GOOD = 3, EASY = 4;
  const GRADE_NAMES = { 1: 'again', 2: 'hard', 3: 'good', 4: 'easy' };

  /* —— 自动评分阈值（UX §6.2） —— */
  const HARD_RATIO = 1.0;      // 用时 > 目标×1.0 → Hard
  const EASY_RATIO = 0.6;      // 用时 ≤ 目标×0.6 → Easy
  const EASY_MIN_REPS = 1;     // Easy 需本卡已复习过 ≥1 次（首见快对只算 Good）
  const WORD_TARGET_MS = 4000; // 生词四选一：≤4 秒 = Good

  /* —— 考前压缩 / 积压 —— */
  const COMPRESS_DAYS = 14;    // 距考试 ≤14 天进入冲刺期
  const EXAM_RETENTION = 0.95; // 冲刺期目标保持率
  const DAILY_CAP = 20;        // 每日复习上限
  const DAY_START_H = 4;       // 一天的界限：本地凌晨 4 点
  const DAY = 864e5;

  const DEFAULT_PARAMS = Object.freeze({
    requestRetention: 0.9,
    examRetention: EXAM_RETENTION,
    compressDays: COMPRESS_DAYS,
    maximumInterval: 36500,
    dailyCap: DAILY_CAP,
    // FSRS-4.5 官方默认参数（17 个权重）
    w: Object.freeze([0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031,
      1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]),
    decay: -0.5,
    factor: 19 / 81,
    tz: 480,              // 事件缺 tz 时的本地时区偏移（分钟）
    defaultTargetMs: 22000 // 事件缺 ms_target 且查不到题目目标时
  });

  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const round4 = n => Math.round(n * 10000) / 10000;
  const P_ = p => (p && p.__full) ? p : Object.assign({ __full: true }, DEFAULT_PARAMS, p || {});

  /* ===== 核心公式（与参考实现一致；唯一差异：回忆稳定度按官方公式修正，见 nextRecallStability） ===== */
  function retrievability(elapsedDays, stability, p) {
    p = P_(p);
    if (!(stability > 0)) return 0;
    return Math.pow(1 + p.factor * (elapsedDays / stability), p.decay);
  }
  function nextInterval(retention, stability, p) {
    p = P_(p);
    if (!(stability > 0)) return 1;
    const ivl = (stability / p.factor) * (Math.pow(retention, 1 / p.decay) - 1);
    return clamp(ivl, 0.1, p.maximumInterval);
  }
  const initStability = (g, p) => P_(p).w[g - 1];
  const initDifficulty = (g, p) => { const w = P_(p).w; return clamp(w[4] - (g - 3) * w[5], 1, 10); };
  function nextDifficulty(d, g, p) {
    const w = P_(p).w;
    return clamp(w[7] * w[4] + (1 - w[7]) * (d - w[6] * (g - 3)), 1, 10);
  }
  function nextRecallStability(d, s, r, g, p) {
    const w = P_(p).w;
    const hard = g === HARD ? w[15] : 1, easy = g === EASY ? w[16] : 1;
    // 官方 FSRS-4.5：e^{w8}·(11−D)。参考实现写成 exp(w8·(11−D))（S 一次涨上千倍，是 bug），此处按官方公式修正。
    return s * (Math.exp(w[8]) * (11 - d) * Math.pow(s, -w[9]) * (Math.exp(w[10] * (1 - r)) - 1) * hard * easy + 1);
  }
  function nextForgetStability(d, s, r, p) {
    const w = P_(p).w;
    return w[11] * Math.pow(d, -w[12]) * (Math.pow(s + 1, w[13]) - 1) * Math.exp(w[14] * (1 - r));
  }

  /* 一步记忆更新：state={s,d} 或 null（新卡），elapsedDays 为距上次复习天数 */
  function step(state, g, elapsedDays, p) {
    p = P_(p);
    let s, d, r = null;
    if (!state || state.s == null) { s = initStability(g, p); d = initDifficulty(g, p); }
    else {
      d = state.d != null ? state.d : initDifficulty(g, p);
      r = retrievability(Math.max(0, elapsedDays), state.s, p);
      s = g === AGAIN ? nextForgetStability(d, state.s, r, p) : nextRecallStability(d, state.s, r, g, p);
      d = nextDifficulty(d, g, p);
    }
    return { s: round4(s), d: round4(d), r: r == null ? null : round4(r), sRaw: s };
  }

  /* 与参考实现 review(state, rating, now) 同语义（毫秒时间、小数天、目标保持率），用于对拍 */
  function review(state, g, nowMs, p) {
    p = P_(p);
    const st = state && state.stability != null ? { s: state.stability, d: state.difficulty } : null;
    const last = state && state.lastReviewAt != null ? +new Date(state.lastReviewAt) : nowMs;
    const o = step(st, g, Math.max(0, (nowMs - last) / DAY), p);
    const interval = nextInterval(p.requestRetention, o.sRaw, p); // 参考实现：间隔用未取整的 S
    return { rating: g, stability: o.s, difficulty: o.d, retrievability: o.r, interval, due: nowMs + interval * DAY };
  }

  /* ===== 自动评分（UX §6.2）=====
   * 错 / 查词 / 看了提示再答 → Again；对但慢于目标 → Hard；对且 ≤0.6×目标（且复习过）→ Easy；其余 Good。
   * timeMs/targetMs 缺失时视为正常用时（Good）。 */
  function grade(correct, timeMs, targetMs, lookedUp, reps) {
    if (!correct || lookedUp) return AGAIN;
    if (!(timeMs >= 0) || !(targetMs > 0)) return GOOD;
    if (timeMs > targetMs * HARD_RATIO) return HARD;
    if (timeMs <= targetMs * EASY_RATIO && (reps == null || reps >= EASY_MIN_REPS)) return EASY;
    return GOOD;
  }

  /* ===== 日期 ===== */
  const dayIndex = (t, tzMin) => Math.floor((t + (tzMin || 0) * 6e4 - DAY_START_H * 36e5) / DAY);
  function examDayIndex(dateStr) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(dateStr || '');
    return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) / DAY : null;
  }
  /* 当天的目标保持率：距考试 0..compressDays 天 → examRetention */
  function retentionFor(day, examDay, p) {
    p = P_(p);
    if (examDay == null) return p.requestRetention;
    const left = examDay - day;
    return left >= 0 && left <= p.compressDays ? Math.max(p.examRetention, p.requestRetention) : p.requestRetention;
  }

  /* 排程一张卡：返回新卡状态（不修改入参）。c={s,d,last,due,reps,lapses,rv}；day 为今天的 dayIndex */
  function scheduleCard(c, g, day, examDay, p) {
    p = P_(p);
    const fresh = !c || c.s == null;
    const o = step(fresh ? null : c, g, fresh ? 0 : day - c.last, p);
    let days = clamp(Math.round(nextInterval(retentionFor(day, examDay, p), o.s, p)), 1, p.maximumInterval);
    if (examDay != null && examDay > day) days = Math.min(days, examDay - day); // 不排到考后
    const wasDue = !!c && c.due != null && c.due <= day;   // 本次是"到期复习"→ 计入当天上限
    return {
      s: o.s, d: o.d, last: day, due: day + days,
      reps: (c && c.reps || 0) + 1, lapses: (c && c.lapses || 0) + (g === AGAIN && !fresh ? 1 : 0),
      rv: wasDue ? day : (c && c.rv != null ? c.rv : null),
      g
    };
  }

  /* ===== 事件 → 卡片状态（UX §15；同时兼容 v2 旧日志 answer/word/wordrev/profile） ===== */
  const WORD = 'w:', PARA = 'p:';
  function newAcc() { return { cards: {}, exam: null }; }
  function applyEvent(acc, ev, p) {
    p = P_(p);
    if (!ev || !ev.e) return acc;
    const tz = ev.tz != null ? ev.tz : p.tz, day = dayIndex(ev.t || 0, tz), C = acc.cards;
    switch (ev.e) {
      case 'profile_create': case 'exam_date_set':
        acc.exam = examDayIndex(ev.exam_date); break;
      case 'profile': acc.exam = examDayIndex(ev.ex); break;                 // v2 旧
      case 'setting_change': if (ev.key === 'exam_date') acc.exam = examDayIndex(ev.value); break;
      case 'state_snapshot':
        if (ev.state && ev.state.cards) { acc.cards = JSON.parse(JSON.stringify(ev.state.cards)); if ('exam' in ev.state) acc.exam = ev.state.exam; }
        break;
      case 'answer_submit': case 'answer': {
        const legacy = ev.e === 'answer';
        const mode = ev.mode;
        if (mode === 'diag') break;                                            // 诊断不建卡（沿用 v2）
        const id = ev.card_id || (legacy ? ev.id : ev.item_id); if (!id) break;
        const correct = legacy ? !!ev.ok : !!ev.correct;
        const looked = legacy ? !!ev.lu : (ev.lookups > 0 || !!ev.viewed_hint);
        let target = ev.ms_target;
        if (!(target > 0)) target = (p.targetMs && p.targetMs(id)) || p.defaultTargetMs;
        const c = C[id];
        const g = grade(correct, ev.ms, target, looked, c ? c.reps : 0);
        if (!c && g >= GOOD) break;                                            // 新题快对且未查词：不建卡
        C[id] = scheduleCard(c, g, day, acc.exam, p);
        break;
      }
      case 'word_save': case 'word': {                                          // 生词入本：明天首考
        const id = WORD + String(ev.lemma || ev.w || '').toLowerCase(); if (id === WORD) break;
        if (!C[id]) C[id] = { s: null, d: null, last: null, due: day + 1, reps: 0, lapses: 0, rv: null };
        else C[id] = Object.assign({}, C[id], { due: Math.min(C[id].due, day + 1) });   // 再次查到：最迟明天见
        break;
      }
      case 'word_remove': delete C[WORD + String(ev.lemma || '').toLowerCase()]; break;
      case 'review_answer': {
        const id = (ev.card_type === 'paraphrase' ? PARA : WORD) + String(ev.card_id || '').toLowerCase();
        const c = C[id];
        C[id] = scheduleCard(c, grade(!!ev.correct, ev.ms, WORD_TARGET_MS, false, c ? c.reps : 0), day, acc.exam, p);
        break;
      }
      case 'wordrev': {                                                         // v2 旧：自评 2/1/0
        const id = WORD + String(ev.w || '').toLowerCase();
        C[id] = scheduleCard(C[id], ev.g === 2 ? GOOD : ev.g === 1 ? HARD : AGAIN, day, acc.exam, p);
        break;
      }
    }
    return acc;
  }

  /* 确定顺序：t → did → seq → eid；有 eid 的重复事件只算一次（多端合并） */
  function orderEvents(events) {
    const seen = new Set(), out = [];
    (events || []).forEach((e, i) => {
      if (!e) return;
      if (e.eid != null) { if (seen.has(e.eid)) return; seen.add(e.eid); }
      out.push([e, i]);
    });
    out.sort((A, B) => {
      const a = A[0], b = B[0];
      return (a.t || 0) - (b.t || 0) || String(a.did || '').localeCompare(String(b.did || '')) ||
        (a.seq || 0) - (b.seq || 0) || String(a.eid || '').localeCompare(String(b.eid || '')) || A[1] - B[1];
    });
    return out.map(x => x[0]);
  }

  /* 纯函数回放：replay(events, params) → { [cardId]: cardState }；不修改 events */
  function replay(events, params) {
    const p = P_(params);
    const acc = orderEvents(events).reduce((a, e) => applyEvent(a, e, p), newAcc());
    return acc.cards;
  }
  function replayFull(events, params) { // 同上，另返回回放末尾的考试日
    const p = P_(params);
    return orderEvents(events).reduce((a, e) => applyEvent(a, e, p), newAcc());
  }

  /* ===== 每日队列 / 积压平摊（UX §6.2、§9.3）=====
   * 返回 { today: [id…] ≤ 剩余额度, plan: {id: 安排日}, backlog: 顺延张数 }
   * 优先级 = weight(id) × (1 − R)；R 按今天算。顺延的卡填进后续日子的空余额度，不标"逾期"。 */
  function dailyQueue(cards, today, opts) {
    opts = opts || {};
    const p = P_(opts.params), cap = opts.cap != null ? opts.cap : p.dailyCap;
    const weight = opts.weight || (() => 1), keep = opts.filter || (() => true);
    const ids = Object.keys(cards).filter(keep);
    const done = ids.filter(id => cards[id].rv === today).length;
    const left = Math.max(0, cap - done);
    const pr = id => { const c = cards[id]; const R = c.s == null ? 0 : retrievability(Math.max(0, today - c.last), c.s, p); return weight(id) * (1 - R); };
    const due = ids.filter(id => cards[id].due <= today)
      .map(id => [id, pr(id)])
      .sort((a, b) => b[1] - a[1] || cards[a[0]].due - cards[b[0]].due || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0))
      .map(x => x[0]);
    const todayList = due.slice(0, left), rest = due.slice(left), plan = {};
    todayList.forEach(id => { plan[id] = today; });
    const native = {};
    ids.forEach(id => { const d = cards[id].due; if (d > today) native[d] = (native[d] || 0) + 1; });
    let k = 1, used = 0;
    rest.forEach(id => {
      while ((native[today + k] || 0) + used >= cap) { k++; used = 0; }
      plan[id] = today + k; used++;
    });
    return { today: todayList, plan, backlog: rest.length };
  }

  return {
    AGAIN, HARD, GOOD, EASY, GRADE_NAMES, HARD_RATIO, EASY_RATIO, EASY_MIN_REPS, WORD_TARGET_MS,
    COMPRESS_DAYS, EXAM_RETENTION, DAILY_CAP, DAY_START_H, DEFAULT_PARAMS, WORD, PARA,
    retrievability, nextInterval, step, review, grade, dayIndex, examDayIndex, retentionFor,
    scheduleCard, applyEvent, newAcc, orderEvents, replay, replayFull, dailyQueue,
    params: P_,
    _internals: { initStability, initDifficulty, nextDifficulty, nextRecallStability, nextForgetStability }
  };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = FSRS;
