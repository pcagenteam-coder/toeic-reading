// C2 排程引擎测试（无框架）：node app/test/planner.test.js [dist 路径]
// 数据：取公开构建 app/dist/index.html 里的 window.TDATA（先跑 python3 app/build.py --public）；
// 代码：直接加载 app/src/{fsrs,mastery,personal,planner,engine}.js（不加载 UI）。
// 时间：用可控的假 Date（模拟 30 天）。另注入 8 道 u:'mock' 的私有式题目，验证不进训练。
'use strict';
const fs = require('fs'), vm = require('vm'), path = require('path'), assert = require('assert');
const DIST = process.argv[2] ? path.resolve(process.argv[2]) : path.join(__dirname, '../dist/index.html');
const SRC = path.join(__dirname, '../src');
const html = fs.readFileSync(DIST, 'utf8');
const dataJs = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).find(s => s.includes('window.TDATA='));
let pass = 0, fail = 0;
function t(name, fn) { try { fn(); pass++; console.log('ok  ', name); } catch (e) { fail++; console.log('FAIL', name, '\n     ', e.stack.split('\n').slice(0, 3).join('\n      ')); } }

/* ---------- 沙箱：假时钟 + 数据 + 引擎 ---------- */
function makeEngine(opts) {
  opts = opts || {};
  const ctx = { console, window: {}, require, module: undefined };
  vm.createContext(ctx);
  vm.runInContext(`
    const RealDate = Date; globalThis.__NOW = ${opts.now || Date.UTC(2026, 10, 1, 12)};
    class FakeDate extends RealDate { constructor(...a) { if (a.length === 0) super(globalThis.__NOW); else super(...a); } static now() { return globalThis.__NOW; } }
    globalThis.Date = FakeDate;`, ctx);
  vm.runInContext(dataJs, ctx);
  ctx.window.TDATA = ctx.window.TDATA;
  // 注入私有式模考题：主节点 QT.P5.WORD_FORM（600 档 must、P5），u:'mock'
  const D = ctx.window.TDATA, src = D.items.filter(i => i.p === 5 && i.n === 'QT.P5.WORD_FORM').slice(0, 8);
  src.forEach((i, k) => D.items.push(Object.assign({}, i, { id: 'MOCKX-' + k, f: 'MOCKF', q: 101 + k, src: 'priv', u: 'mock', d: 3 })));
  const code = ['fsrs.js', 'mastery.js', 'personal.js', 'planner.js', 'engine.js'].map(f => fs.readFileSync(path.join(SRC, f), 'utf8')).join('\n');
  vm.runInContext(code + '\nglobalThis.__X = { E, IT, ND, FORMS, newState, FSRS, Mastery, Personal, Planner, fxToday };', ctx);
  const X = ctx.__X; X.ctx = ctx; X.setNow = ms => { ctx.__NOW = ms; }; X.now = () => ctx.__NOW;
  return X;
}
const DAY = 864e5, sig = x => 1 / (1 + Math.exp(-x));
const rng = (seed => () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; })(20261023);

/* ================= 1. 模拟 600 档用户 30 天 ================= */
const X = makeEngine();
const { E, IT, ND } = X;
const MUST = new Set(Object.values(ND).filter(n => (n.mb || []).includes('600')).map(n => n.id));
E.st = X.newState(600, '2027-03-15');           // 考试远（>8 周，基础期）
const theta = {};                                // 模拟用户的“真实”能力：练一次涨一点
const th = n => (theta[n] != null ? theta[n] : (theta[n] = -0.4));
const days = [];
for (let d = 0; d < 30; d++) {
  const t0 = Date.UTC(2026, 10, 1 + d, 12);       // 每天北京时间 20:00
  X.setNow(t0);
  if (d < 8) ['allocate', 'invoice', 'itinerary'].forEach(w => E.addWord(w + d, 'ctx'));
  const plan = E.getTodayPlan(E.st, 30);
  const info = { d, mode: plan.mode, units: plan.units, words: plan.words, reviewCount: plan.reviewCount, progress: plan.progress };
  plan.words.forEach(w => E.scheduleWord(w, 2));
  plan.units.forEach(u => u.ids.forEach(id => {
    const it = IT[id], b = (it.d - 3) * 0.7;
    const eff = 0.7 * th(it.n) + 0.3 * (it.ns.length ? it.ns.reduce((s, n) => s + th(n), 0) / it.ns.length : th(it.n)), ok = rng() < sig(eff + 0.4 - b);
    const ms = Math.round(it.t * 1000 * 0.9);
    X.setNow(X.now() + ms);
    E.recordAnswer({ item_id: id, choice: ok ? it.a : (it.a + 1) % 4, ms, mode: 'train' });
    theta[it.n] = Math.min(2.8, th(it.n) + 0.25); it.ns.forEach(n => { theta[n] = Math.min(2.8, th(n) + 0.1); });
  }));
  const today = X.fxToday();
  info.rvDone = Object.values(E.st.cards).filter(c => c.rv === today).length + Object.values(E.st.words).filter(c => c.rv === today).length;
  info.prog = E.getProgress();
  days.push(info);
}
console.log('sim modes', days.map(x => x.mode[0]).join(''), '| day1', days[0].progress, '| day30', days[29].progress);
console.log('sim reviews/day', days.map(x => x.rvDone).join(','));

t('600 档：新学/维持单元只练 must 集合（P5 单题的主考点也在 must 内）', () => {
  let n = 0;
  days.forEach(x => x.units.filter(u => u.kind !== 'review').forEach(u => {
    assert(MUST.has(u.node), 'day ' + x.d + ' 单元考点不在 600 must：' + u.node);
    if (!u.b) assert(MUST.has(IT[u.ids[0]].n), 'P5 主考点不在 must：' + IT[u.ids[0]].n);
    n++;
  }));
  assert(n > 100, '新学单元太少 ' + n);
  ['QT.P5.VERB_FORM', 'QT.P5.RELATIVE', 'QT.P7X.CROSS_REF.TRIPLE', 'QT.P6.INSERTION'].forEach(x => assert(!MUST.has(x), x + ' 不应在 600 must'));
});
t('600 档：所有 must 考点达标后进入维持模式，进度显示 0 个考点', () => {
  const k = days.findIndex(x => x.mode === 'maintain');
  assert(k > 0 && k < 29, '30 天内未进入维持模式');
  assert(days.slice(-3).every(x => x.mode === 'maintain'), '最后 3 天应为维持模式');
  const p = days[29].prog; assert.strictEqual(p.remainingNodes, 0); assert.strictEqual(p.mode, 'maintain');
  assert(/离目标还差 \d+ 个考点、约 [\d.]+ 小时/.test(days[0].progress), days[0].progress);
  assert(days[k].units.length > 0 && days[k].units.every(u => u.kind !== 'learn'), '维持模式不应再有 learn 单元');
});
t('每日复习（题卡+生词合并）≤ 20', () => {
  days.forEach(x => { assert(x.reviewCount <= 20, 'plan ' + x.reviewCount); assert(x.rvDone <= 20, 'day ' + x.d + ' done ' + x.rvDone); });
  assert(days.some(x => x.reviewCount > 0), '应有复习');
});
t('mock 题不进训练池 / 不出现在任何任务里', () => {
  assert(!E.pool().some(i => i.u === 'mock'));
  days.forEach(x => x.units.forEach(u => u.ids.forEach(id => assert(!/^MOCKX/.test(id), id))));
  assert(!E.weakPlan('QT.P5.WORD_FORM').some(u => u.ids.some(id => /^MOCKX/.test(id))));
});
t('掌握度可纯回放：增量缓存 = 从日志重算', () => {
  const a = JSON.stringify(E.macc()), b = JSON.stringify(X.Mastery.replay(E.st.log, { item: id => IT[id], prereqs: n => (ND[n].pr || []).filter(p => ND[p] && !ND[p].g) }));
  assert.strictEqual(a, b);
});

/* ================= 2. 复习：积压平摊 5–7 天、考前 3 天只留高考频 ================= */
t('积压 60 张：今天只排 ~1/6（平摊 6 天），且 ≤20；生词与题卡共用 20', () => {
  const P = X.Planner, cards = {}, words = {}, day = 20000;
  for (let i = 0; i < 60; i++) cards['c' + i] = { s: 3, d: 5, last: day - 15, due: day - 10, reps: 2, lapses: 0, rv: null };
  let q = P.reviewQueue(cards, {}, day, {});
  assert.strictEqual(q.spreadDays, 6); assert.strictEqual(q.items.length, 10); assert(q.backlog === 50);
  const c2 = {}; for (let i = 0; i < 15; i++) c2['n' + i] = { s: 3, d: 5, last: day - 3, due: day, reps: 1, lapses: 0, rv: null };
  for (let i = 0; i < 10; i++) words['w' + i] = { s: 2, d: 5, last: day - 2, due: day, reps: 1, lapses: 0, rv: null };
  q = P.reviewQueue(c2, words, day, {});
  assert.strictEqual(q.today.length, 20); assert(q.words.length > 0 && q.items.length > 0);
  const c3 = {}; for (let i = 0; i < 300; i++) c3['b' + i] = { s: 3, d: 5, last: day - 30, due: day - 20, reps: 2, lapses: 0, rv: null };
  q = P.reviewQueue(c3, {}, day, {}); assert.strictEqual(q.today.length, 20); assert.strictEqual(q.spreadDays, 7);
});
t('考前 3 天：只复习高考频、不出新考点（review_only）', () => {
  const Y = makeEngine({ now: Date.UTC(2026, 11, 1, 12) }), E2 = Y.E, day = Y.fxToday();
  E2.st = Y.newState(600, '2026-12-03');
  const hi = Object.values(Y.IT).find(i => i.p === 5 && i.n === 'QT.P5.VOCAB'), lo = Object.values(Y.IT).find(i => i.p === 5 && Y.ND[i.n].w < 0.05 && !/^QT\.P7X/.test(i.n));
  [hi, lo].forEach(i => { E2.st.cards[i.id] = { s: 2, d: 5, last: day - 3, due: day, reps: 1, lapses: 0, rv: null }; });
  const due = E2.dueItems(); assert(due.includes(hi.id) && !due.includes(lo.id), JSON.stringify(due));
  const pl = E2.getTodayPlan(E2.st, 5); assert.strictEqual(pl.mode, 'review_only'); assert(pl.units.every(u => u.kind !== 'learn'));
});
t('距考试 10 天、每天 5 分钟：排不下的考点按 ROI 放弃（倒排）', () => {
  const Y = makeEngine({ now: Date.UTC(2026, 11, 1, 12) }); Y.E.st = Y.newState(600, '2026-12-11');
  const p = Y.E.getProgress(); assert(p.phase === 'sprint' && p.dropped.length > 0, JSON.stringify(p.dropped.length));
  const kept = p.nodes.filter(n => !n.dropped && !n.achieved).reduce((s, n) => s + n.remainMin, 0);
  assert(kept <= 10 * 5 * 0.4 + 1, 'kept ' + kept);
  const Z = makeEngine(); Z.E.st = Z.newState(600, ''); assert.strictEqual(Z.E.getProgress().dropped.length, 0);
});

/* ================= 3. 学不动降优先级 ================= */
t('多次练习掌握度不涨 → 标记学不动，ROI 降低（剩余成本 ×3）', () => {
  const Y = makeEngine(), E2 = Y.E; E2.st = Y.newState(600, '');
  const node = 'QT.P5.PREP', its = Object.values(Y.IT).filter(i => i.p === 5 && i.n === node);
  const before = Y.Planner.analyze(E2.pctx()).goal.find(x => x.id === node);
  for (let k = 0; k < 16; k++) { Y.setNow(Y.now() + 60000); E2.recordAnswer({ item_id: its[k % its.length].id, choice: (its[k % its.length].a + 1) % 4, ms: 20000 }); }
  const g = Y.Planner.analyze(E2.pctx()).goal.find(x => x.id === node);
  assert(g.stuck, 'should be stuck'); assert(g.remainMin > before.remainMin * 2, g.remainMin + ' vs ' + before.remainMin);
  assert(E2.getProgress().stuck.includes(node));
});

/* ================= 4. 个性化 ================= */
function answerMany(Y, filter, n, ratio, okRate, hourUTC) {
  const its = Object.values(Y.IT).filter(filter); let k = 0;
  for (let i = 0; i < n; i++) {
    const it = its[i % its.length], ok = (i % 10) < okRate * 10;
    if (hourUTC != null) Y.setNow(Date.UTC(2026, 10, 1 + Math.floor(i / 10), hourUTC, i % 10));
    else Y.setNow(Y.now() + 60000);
    Y.E.recordAnswer({ item_id: it.id, choice: ok ? it.a : (it.a + 1) % 4, ms: Math.round(it.t * 1000 * ratio) });
  }
}
t('用时画像：P7 慢 → 个人终点线提前到 175 之前；正常速度 → 175 且提示余量捡分', () => {
  const S = makeEngine(); S.E.st = S.newState(600, ''); answerMany(S, i => i.p === 7, 60, 2.2, 0.7);
  const F = makeEngine(); F.E.st = F.newState(600, ''); answerMany(F, i => i.p === 7, 60, 0.9, 0.7);
  const bs = S.E.getProfile().battle, bf = F.E.getProfile().battle;
  assert(bs.pace[7].ratio > 1.8 && bs.finishLine.personal < 175, JSON.stringify(bs.finishLine));
  assert.strictEqual(bf.finishLine.personal, 175); assert(bf.finishLine.spareMin >= 5);
  assert(bs.skipBudget.personal > bf.skipBudget.personal);
  const T = makeEngine(); T.E.st = T.newState(730, ''); assert.strictEqual(T.E.getProfile().battle.finishLine.base, 185);
});
t('用时画像：P5 慢的用户 5 分钟排的题更少（题量随速度自适应）', () => {
  const S = makeEngine(); S.E.st = S.newState(600, ''); answerMany(S, i => i.p === 5 && i.n === 'QT.P5.VERB_FORM', 40, 2.5, 0.6);
  const F = makeEngine(); F.E.st = F.newState(600, ''); answerMany(F, i => i.p === 5 && i.n === 'QT.P5.VERB_FORM', 40, 0.8, 0.6);
  const ns = S.E.getTodayPlan(S.E.st, 5).units.reduce((s, u) => s + u.ids.length, 0), nf = F.E.getTodayPlan(F.E.st, 5).units.reduce((s, u) => s + u.ids.length, 0);
  assert(ns < nf, ns + ' vs ' + nf);
});
t('作息画像：上午明显更准 → 建议上午；关闭后不再建议', () => {
  const Y = makeEngine(); Y.E.st = Y.newState(600, '');
  const P5 = i => i.p === 5 && i.d === 3;
  const off = Math.round(-new Date().getTimezoneOffset() / 60);   // 引擎按本机时区记 tz；换算成本地 10 点 / 20 点
  answerMany(Y, P5, 40, 1, 0.9, (10 - off + 24) % 24);   // 本地上午 10 点：90% 对
  answerMany(Y, P5, 40, 1, 0.4, (20 - off + 24) % 24);   // 本地晚上 8 点：40% 对
  const c = Y.E.getProfile().circadian; assert.strictEqual(c.best, 'morning', JSON.stringify(c)); assert(c.tip);
  Y.E.setSetting('circadian', false);
  const c2 = Y.E.getProfile().circadian; assert(c2.enabled === false && c2.best === null);
  assert(Y.E.st.log.some(e => e.e === 'setting_change' && e.key === 'circadian'));
});

/* FSRS 个人参数：按“真实”参数（遗忘更快）生成复习日志，拟合后在留出卡片上 log loss 更低 */
function simReviews(Fs, nCards, wTrue, seed) {
  let s = seed; const r = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const pT = Fs.params({ w: wTrue }), pD = Fs.params({}), ev = [], T0 = Date.UTC(2026, 0, 1, 12);
  for (let c = 0; c < nCards; c++) {
    let day = Math.floor(r() * 30), st = null, card = null;
    for (let k = 0; k < 7; k++) {
      let ok;
      if (!st) ok = false;                                           // 首次答错才建卡（新题快对不建卡）
      else ok = r() < Fs.retrievability(day - st.last, st.s, pT);
      const g = ok ? Fs.GOOD : Fs.AGAIN;
      ev.push({ e: 'answer', t: T0 + day * DAY + c * 1000 + k, tz: 0, id: 'C' + c, mode: 'review', ok: ok ? 1 : 0, c: 0, ms: 8000, ms_target: 10000, lu: 0 });
      const o = Fs.step(st ? { s: st.s, d: st.d } : null, g, st ? day - st.last : 0, pT); st = { s: o.sRaw, d: o.d, last: day };
      card = Fs.scheduleCard(card, g, day, null, pD);                // App 用默认参数排下次（真实流程）
      day = card.due + (r() < 0.3 ? Math.floor(r() * 4) : 0);       // 偶尔晚几天才复习
    }
  }
  return ev;
}
t('FSRS 个人参数：≥300 次复习后重拟合 w，留出数据 log loss 下降；不足 300 用默认', () => {
  const Fs = X.FSRS, P = X.Personal, w0 = Array.from(Fs.DEFAULT_PARAMS.w);
  const wTrue = w0.slice(); [0, 1, 2, 3].forEach(k => { wTrue[k] *= 0.4; }); wTrue[8] -= 0.5; wTrue[11] *= 0.6;
  const ev = simReviews(Fs, 160, wTrue, 7), seq = P.sequences(ev, { tz: 0 }), ids = Object.keys(seq);
  const train = ids.filter((_, i) => i % 4), hold = ids.filter((_, i) => !(i % 4));
  const fit = P.fitW(seq, { ids: train });
  const l0 = P.logLoss(seq, w0, hold), l1 = P.logLoss(seq, fit.w, hold);
  console.log('      fsrs fit: train', fit.before.toFixed(4), '→', fit.after.toFixed(4), '| holdout', l0.toFixed(4), '→', l1.toFixed(4), '| reviews', P.countReviews(seq));
  assert(fit.after < fit.before && l1 < l0 - 0.005, 'holdout ' + l0 + ' → ' + l1);
  const r = P.fsrsFit(ev, { tz: 0 }); assert(r.use && r.n >= 300);
  const small = P.fsrsFit(simReviews(Fs, 20, wTrue, 9), { tz: 0 }); assert(!small.use && small.n < 300);
  // 接入引擎：日志里够数 → maybeRefit 采用个人参数，fxParams().w 随之改变
  const Y = makeEngine(); Y.E.st = Y.newState(600, '');
  const known = Object.keys(Y.IT).slice(0, 160); Y.E.st.log = ev.map(e => Object.assign({}, e, { id: known[+e.id.slice(1)] }));
  const f = Y.E.maybeRefit(true); assert(f.use, JSON.stringify(f));
  assert.notDeepStrictEqual(Array.from(Y.E.fxParams().w), w0); assert(Y.E.getProfile().fsrs.personal);
  const Z = makeEngine(); Z.E.st = Z.newState(600, ''); assert.deepStrictEqual(Array.from(Z.E.fxParams().w), w0);
});

/* ================= 5. API 形状 ================= */
t('API：getTodayPlan / getProgress / recordAnswer / getProfile 字段齐全；默认 5 分钟', () => {
  const Y = makeEngine(); Y.E.st = Y.newState(600, '');
  const p = Y.E.getTodayPlan(Y.E.st); assert.strictEqual(p.minutes, 5);
  ['mode', 'phase', 'units', 'words', 'reviewCount', 'estSec', 'nodes', 'progress', 'band'].forEach(k => assert(k in p, k));
  assert(p.estSec <= 5 * 60 + 60 && p.units.reduce((s, u) => s + u.ids.length, 0) >= 3, JSON.stringify(p));
  const g = Y.E.getProgress(); ['remainingNodes', 'remainingHours', 'text', 'battle', 'next', 'mode'].forEach(k => assert(k in g, k));
  assert(g.remainingNodes > 0 && g.remainingHours > 0 && g.band === '600');
  const r = Y.E.recordAnswer({ item_id: p.units[0].ids[0], choice: 0, ms: 15000 }); assert(r && 'correct' in r && r.mastery != null);
  assert.strictEqual(Y.Planner.band(450), '≤500'); assert.strictEqual(Y.Planner.band(700), '730'); assert.strictEqual(Y.Planner.band(900), '860+');
});

/* ================= B2 遗留：新手期 / P7 节奏 / 首日计划 / 诊断起始难度 ================= */
const isP7 = u => u.b && IT[u.ids[0]].p === 7;
t('每 3 天至少 1 篇 P7（30 天模拟，任意连续 3 天）', () => {
  for (let d = 0; d + 2 < 30; d++) assert(days.slice(d, d + 3).some(x => x.units.some(isP7)), 'day ' + d + '–' + (d + 2) + ' 没有 P7');
});
t('新手期（前 7 天）P5 为主：P5 单题占新学多数；有 P5 可练时篇章 ≤1', () => {
  let s5 = 0, sb = 0;
  days.slice(0, 7).forEach(x => {
    const nu = x.units.filter(u => u.kind !== 'review'), nb = nu.filter(u => u.b).length; s5 += nu.length - nb; sb += nb;
    if (x.d < 3) assert(nb <= 1, 'day ' + x.d + ' 篇章 ' + nb);
    const i = nu.findIndex(u => u.b && !u.p7), j = nu.map(u => !u.b).lastIndexOf(true);
    if (nb > 1) assert(i > j || j < 0, 'day ' + x.d + ' 篇章排在 P5 前');
  });
  assert(s5 > 3 * sb, 'P5 ' + s5 + ' vs 篇章 ' + sb);
  const Y = makeEngine(); Y.E.st = Y.newState(600, ''); const pl = Y.E.getTodayPlan(Y.E.st, 15);
  assert(pl.novice && pl.units.filter(u => u.b).length <= 1, '新用户 15 分钟篇章 ' + pl.units.filter(u => u.b).length);
});
t('Planner.rhythm：新手期按天数/掌握度判定；needP7 按距上次 P7 天数', () => {
  const P = X.Planner, g = m => ({ goal: [{ n: 3, m }, { n: 2, m }] });
  assert(P.rhythm({ day: 103, startDay: 100 }, g(0.7)).novice);                  // 第 4 天
  assert(!P.rhythm({ day: 110, startDay: 100 }, g(0.7)).novice);                 // 第 11 天、掌握度高
  assert(P.rhythm({ day: 110, startDay: 100 }, g(0.3)).novice);                  // 掌握度低仍算新手
  assert(!P.rhythm({ day: 101, startDay: 100, lastP7Day: null }, g(0.6)).needP7);
  assert(P.rhythm({ day: 102, startDay: 100, lastP7Day: null }, g(0.6)).needP7);
  assert(!P.rhythm({ day: 112, startDay: 100, lastP7Day: 110 }, g(0.6)).needP7);
  assert(P.rhythm({ day: 113, startDay: 100, lastP7Day: 110 }, g(0.6)).needP7);
});
t('首日计划：入职测试最薄弱的前 2 个考点 P5 + 1 篇短 P7（单篇 ≤3 题）', () => {
  const Y = makeEngine(), { E: E1, IT: I1 } = Y; E1.st = Y.newState(600, '');
  E1.diagPlan().forEach((u, k) => u.ids.forEach((id, j) => E1.recordAnswer({ item_id: id, choice: (k + j) % 3 ? I1[id].a : (I1[id].a + 1) % 4, ms: 30000, mode: 'diag' })));
  E1.st.diag = true;
  const pl = E1.getTodayPlan(E1.st, 5), p5 = pl.units.filter(u => !u.b), b = pl.units.filter(u => u.b);
  assert(pl.first === true, 'first'); assert.strictEqual(p5.length, 2); assert.strictEqual(b.length, 1);
  const bu = Y.ctx.window.TDATA.bundles.find(x => x.id === b[0].b); assert(bu.p === 7 && bu.k === 'single' && bu.qs.length <= 3, JSON.stringify([bu.p, bu.k, bu.qs.length]));
  const A = E1.getProgress(), G = {}; A.nodes.forEach(x => { G[x.id] = x.m; });
  const dn = [...new Set(E1.st.log.filter(x => x.e === 'answer' && x.mode === 'diag').map(x => I1[x.id].n))].filter(n => G[n] != null).sort((a, c) => G[a] - G[c]);
  assert(p5.every(u => G[u.node] <= G[dn[Math.min(2, dn.length - 1)]] + 1e-9), JSON.stringify(p5.map(u => [u.node, G[u.node]])) + ' vs ' + JSON.stringify(dn.slice(0, 3).map(n => G[n])));
  E1.recordAnswer({ item_id: p5[0].ids[0], choice: 0, ms: 20000, mode: 'train' });
  assert(E1.getTodayPlan(E1.st, 5).first === false, '做过训练后不再是首日计划');
});
t('入职测试起始难度随词汇量：低词汇从 1 级起步，高词汇更难', () => {
  const Y = makeEngine(), E1 = Y.E; E1.st = Y.newState(600, '');
  const d0 = v => Y.IT[E1.diagPlan(5, v)[0].ids[0]].d;
  assert.strictEqual(JSON.stringify(E1.diagLevels(1500).slice(0, 2)), '[1,1]'); assert.strictEqual(d0(1500), 1);
  assert(d0(3000) === 2 && d0(6000) >= 2); assert(E1.diagLevels(6000).reduce((a, b) => a + b) > E1.diagLevels(3000).reduce((a, b) => a + b));
  E1.st.vocab = 1200; assert.strictEqual(Y.IT[E1.diagPlan()[0].ids[0]].d, 1);
});

t('P0-1 need：预测已达标不再报“还差全部考点”；未达标按 ROI 只计最少考点；小时给区间', () => {
  const P = require(path.join(SRC, 'planner.js'));
  const goal = Array.from({ length: 28 }, (_, i) => ({ id: 'n' + i, w: 1 + (i % 3), m: 0.5, achieved: false, dropped: false, remainMin: 2, roi: 28 - i }));
  const A = { goal, target: 0.8 };
  const r1 = P.need(A, { score: 370, lo: 330, target: 300 });
  assert(r1.reached && r1.safe && r1.nodes === 0, 'lo ≥ 目标−10 → 维持'); assert(/够到目标/.test(P.progressText(A, r1)));
  const r2 = P.need(A, { score: 320, lo: 260, target: 300 });
  assert(r2.reached && r2.nodes > 0 && r2.nodes < 28, '已达标但下沿低 → 再稳几个留余量: ' + r2.nodes); assert(/已够线/.test(P.progressText(A, r2)));
  const r3 = P.need(A, { score: 290, lo: 250, target: 300 }), r4 = P.need(A, { score: 200, lo: 160, target: 300 });
  assert(r3.nodes >= 1 && r3.nodes < r4.nodes && r4.nodes <= 28, `差 10 分少于差 100 分: ${r3.nodes} vs ${r4.nodes}`);
  assert.deepStrictEqual(r3.ids, goal.slice(0, r3.nodes).map(x => x.id), '按 ROI 顺序');
  assert.strictEqual(P.hoursText(20), '不到 1 小时'); assert.strictEqual(P.hoursText(120), '约 1.5–3 小时');
});

console.log(`\n${pass} passed, ${fail} failed`);
if (fail) process.exit(1);
