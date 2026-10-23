// C3 预测分测试（无框架）：node app/test/predict.test.js [--full] [dist 路径]
// 单测 + 模拟校准（模拟不同真实能力的用户 → 一次“真实考试”成绩 → 比较点估计误差与 80% 区间覆盖率）。
// 默认跑快速版（约 300 名模拟用户）；--full 跑 docs/predict_calibration.md 用的完整版并打印表格。
'use strict';
const fs = require('fs'), path = require('path'), assert = require('assert');
const args = process.argv.slice(2), FULL = args.includes('--full');
const DIST = args.find(a => !a.startsWith('--')) || path.join(__dirname, '../dist/index.html');
const P = require('../src/predict.js'), Mastery = require('../src/mastery.js');
const html = fs.readFileSync(DIST, 'utf8');
const dataJs = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).find(s => s.includes('window.TDATA='));
const window = {}; new Function('window', dataJs)(window);
const D = window.TDATA, IT = {}; D.items.forEach(i => { IT[i.id] = i; });
const item = id => IT[id];
const forms = {}; D.items.forEach(i => { (forms[i.f] = forms[i.f] || []).push(i); });
const FULLF = Object.keys(forms).filter(f => forms[f].length >= 90).sort();
const EXAM = FULLF.flatMap(f => forms[f]);
const POOL = D.items.filter(i => i.u !== 'mock' && !FULLF.includes(i.f) && [5, 6, 7].includes(i.p));
let pass = 0, fail = 0;
function t(name, fn) { try { fn(); pass++; console.log('ok  ', name); } catch (e) { fail++; console.log('FAIL', name, '\n     ', e.stack.split('\n').slice(0, 3).join('\n      ')); } }
const sig = x => 1 / (1 + Math.exp(-x)), DAY = 864e5, NOW = Date.UTC(2026, 10, 1, 12);
const R = P.rng(20261024);

/* ---------- 模拟用户 ---------- */
function mkUser(theta) {
  return { th: theta, d: { 5: 0.3 * R.n(), 6: 0.3 * R.n(), 7: 0.3 * R.n() }, pace: Math.exp(0.1 + 0.25 * R.n()), bias: 0 };
}
const pCorrect = (u, p, b, shift) => 0.25 + 0.75 * sig(u.th + u.d[p] + (shift || 0) - b);
function practiceLog(u, n) {
  const log = [];
  for (let k = 0; k < n; k++) {
    const it = POOL[Math.floor(R() * POOL.length)], ok = R() < pCorrect(u, it.p, Mastery.diffB(it.d));
    log.push({ e: 'answer', t: NOW - Math.floor(R() * 30 * DAY), id: it.id, mode: 'train', c: ok ? it.a : (it.a + 1) % 4, ok: ok ? 1 : 0,
      lu: ok && R() < 0.05 ? 1 : 0, ms: Math.round(it.t * 1000 * u.pace * Math.exp(0.35 * R.n())), ms_target: it.t * 1000 });
  }
  return log.sort((a, b) => a.t - b.t);
}
/* 一次计时整套考试（真实考试 / 模考）：考试当天状态波动 shift ~ N(bias, 0.15)，用时比当天波动 */
function sitExam(u, form) {
  const its = forms[form].slice().sort((a, b) => a.q - b.q), shift = u.bias + 0.15 * R.n(), pace = u.pace * Math.exp(0.08 * R.n());
  let left = P.consts.TIME_SEC, ok = 0;
  for (const it of its) {
    const need = it.t * pace;
    if (left >= need) { left -= need; if (R() < pCorrect(u, it.p, Mastery.diffB(it.d), shift)) ok++; }
    else if (R() < 0.25) ok++;
  }
  // 真实换算随卷等化浮动、且与本模块近似表不完全一致：量表分加 N(0,10) 换算误差
  return { ok, n: its.length, scaled: Math.round(Math.max(5, Math.min(495, P.scaledFromRaw(100 * ok / its.length) + 10 * R.n())) / 5) * 5 };
}

/* ================= 单测 ================= */
t('换算表单调、端点 5/495、步长 5', () => {
  let prev = -1; for (let r = 0; r <= 100; r++) { const s = P.scaledFromRaw(r); assert(s >= prev); prev = s; }
  assert.strictEqual(P.scaledFromRaw(0), 5); assert.strictEqual(P.scaledFromRaw(100), 495);
  assert(Math.abs(P.rawFromScaled(315) - 70) < 0.1);
});
t('无数据：返回合法宽区间、置信度低', () => {
  const o = P.estimate({ now: NOW });
  assert(o.score >= 5 && o.score <= 495 && o.score % 5 === 0 && o.lo % 5 === 0 && o.hi % 5 === 0);
  assert(o.lo < o.score && o.hi > o.score); assert.strictEqual(o.confidence.level, 'low'); assert(o.approx);
});
const U = mkUser(0.8); U.d = { 5: 0, 6: 0, 7: 0 }; U.pace = 1;
const LOG400 = practiceLog(U, 400);
t('作答越多区间越窄', () => {
  const w = [20, 80, 400].map(n => { const o = P.estimate({ log: LOG400.slice(0, n), item, exam: EXAM, now: NOW }); return o.hi - o.lo; });
  assert(w[0] > w[1] && w[1] > w[2], w.join(' '));
});
t('能力高 → 分高；各 Part 贡献加总≈总分', () => {
  const lo = P.estimate({ log: practiceLog(Object.assign(mkUser(-1), { d: { 5: 0, 6: 0, 7: 0 }, pace: 1 }), 200), item, exam: EXAM, now: NOW });
  const hi = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW });
  assert(hi.score > lo.score + 80, lo.score + ' ' + hi.score);
  const s = [5, 6, 7].reduce((a, p) => a + hi.parts[p].points, 0); assert(Math.abs(s - hi.score) <= 3);
  assert.deepStrictEqual(Object.keys(hi.parts), ['5', '6', '7']); assert(hi.parts[7].q === 54);
});
t('用时慢 → 超时扣减（P7 来不及做的题）', () => {
  const slow = LOG400.map(e => Object.assign({}, e, { ms: e.ms * 1.6 }));
  const a = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW }), b = P.estimate({ log: slow, item, exam: EXAM, now: NOW });
  assert(b.timeLoss.q > 10 && b.parts[7].unreached > 10 && b.score < a.score - 15, JSON.stringify([a.score, b.score, b.timeLoss]));
});
t('整套模考权重最高：模考分把预测拉向模考', () => {
  const L = LOG400.slice(-100), base = P.estimate({ log: L, item, exam: EXAM, now: NOW });
  const mk = P.estimate({ log: L, item, exam: EXAM, now: NOW, mocks: [{ ts: NOW - DAY, ok: 50, n: 100 }] });
  assert(mk.model.modelWeight < 0.5, mk.model.modelWeight);
  assert(Math.abs(mk.score - 215) < Math.abs(base.score - 215) - 40, base.score + ' → ' + mk.score);
  const old = P.estimate({ log: L, item, exam: EXAM, now: NOW, mocks: [{ ts: NOW - 120 * DAY, ok: 50, n: 100 }] });
  assert(old.model.modelWeight > mk.model.modelWeight, '旧模考权重应更低');
});
t('真实成绩校准：存偏移并修正后续预测', () => {
  const o = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW });
  const cal = P.calibrate(null, o.score - 60, o);
  assert(cal.n === 1 && cal.offset < -20 && cal.offset > -60, JSON.stringify(cal));
  const o2 = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW, calib: cal });
  assert(o2.score < o.score - 15 && o2.model.offset === Math.round(cal.offset));
  const cal2 = P.calibrate(cal, o.score - 60, o); assert(cal2.offset < cal.offset && cal2.v < cal.v);
});
t('离目标差多少 / 主要差在哪些考点', () => {
  const acc = Mastery.replay(LOG400, { item: id => IT[id], prereqs: () => [] });
  const o = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW, target: 450, macc: acc, nodes: D.nodes, mastery: id => Mastery.of(acc, id, NOW) });
  assert(o.gap && o.gap.target === 450 && o.gap.diff > 0 && o.gap.prob < 0.5 && /还差/.test(o.gap.text), JSON.stringify(o.gap));
  assert(o.gap.nodes.length > 0 && o.gap.nodes[0].gain >= o.gap.nodes[o.gap.nodes.length - 1].gain && o.gap.nodes[0].nm);
  const e = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW, target: 100 }); assert(e.gap.diff < 0 && /已达/.test(e.gap.text));
});
t('日志兼容 answer_submit；bulk_fill/未作答模考不计', () => {
  const it = POOL[0], ev = [{ e: 'answer_submit', item_id: it.id, choice: it.a, correct: true, ms: 20000, t: NOW }, { e: 'answer', id: it.id, c: null, mode: 'mock', ok: 0, t: NOW }, { e: 'answer', id: it.id, c: 1, ok: 0, bulk_fill: 1, t: NOW }];
  assert.strictEqual(P.observations(ev, item, NOW).length, 1);
});
t('纯函数：同输入同输出', () => {
  const a = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW }), b = P.estimate({ log: LOG400, item, exam: EXAM, now: NOW });
  assert.deepStrictEqual(a, b);
});

/* ================= 模拟校准 ================= */
function simulate(nUsers, ns, withMock) {
  const rows = {};
  for (const n of ns) rows[n] = { err: [], cov: 0, w: [], cnt: 0 };
  for (let k = 0; k < nUsers; k++) {
    const u = mkUser(-0.3 + 1.2 * R.n());         // 真实能力：覆盖 ~100–495 分
    const full = practiceLog(u, Math.max(...ns));
    const fs2 = FULLF.slice().sort(() => R() - 0.5), real = sitExam(u, fs2[0]);
    const mocks = withMock ? [{ ts: NOW - 3 * DAY, ...sitExam(u, fs2[1]) }] : [];
    for (const n of ns) {
      const o = P.estimate({ log: full.slice(-n), item, exam: EXAM, now: NOW, mocks, draws: 300, seed: k + 1 });
      const r = rows[n]; r.cnt++; r.err.push(o.score - real.scaled); r.w.push(o.hi - o.lo);
      if (real.scaled >= o.lo && real.scaled <= o.hi) r.cov++;
    }
  }
  return ns.map(n => { const r = rows[n], mae = r.err.reduce((s, x) => s + Math.abs(x), 0) / r.cnt, bias = r.err.reduce((s, x) => s + x, 0) / r.cnt;
    return { n, mae: +mae.toFixed(1), bias: +bias.toFixed(1), cov: +(r.cov / r.cnt).toFixed(3), width: Math.round(r.w.reduce((s, x) => s + x, 0) / r.cnt), users: r.cnt }; });
}
function simCalib(nUsers) {   // 系统偏差用户（考场能力比练习低 0.4）：报一次真实成绩后，下一次考试的误差
  let e0 = 0, e1 = 0, c1 = 0;
  for (let k = 0; k < nUsers; k++) {
    const u = mkUser(-0.3 + 1.0 * R.n()); u.bias = -0.4;
    const log = practiceLog(u, 200), f = FULLF.slice().sort(() => R() - 0.5);
    const o = P.estimate({ log, item, exam: EXAM, now: NOW, draws: 300, seed: k + 7 }), r1 = sitExam(u, f[0]), r2 = sitExam(u, f[1]);
    const cal = P.calibrate(null, r1.scaled, o), o2 = P.estimate({ log, item, exam: EXAM, now: NOW, draws: 300, seed: k + 7, calib: cal });
    e0 += Math.abs(o.score - r2.scaled); e1 += Math.abs(o2.score - r2.scaled); if (r2.scaled >= o2.lo && r2.scaled <= o2.hi) c1++;
  }
  return { mae_before: +(e0 / nUsers).toFixed(1), mae_after: +(e1 / nUsers).toFixed(1), cov_after: +(c1 / nUsers).toFixed(3), users: nUsers };
}

const NS = [10, 30, 100, 300];
const sim = simulate(FULL ? 1000 : 250, NS, false);
const simM = simulate(FULL ? 600 : 120, [30, 300], true);
const simC = simCalib(FULL ? 400 : 100);
console.log('sim (no mock):', JSON.stringify(sim));
console.log('sim (+1 mock):', JSON.stringify(simM));
console.log('sim (calib):  ', JSON.stringify(simC));
t('模拟：80% 区间覆盖率在 0.72–0.88（快速版放宽 ±3pt）', () => {
  [...sim, ...simM].forEach(r => assert(r.cov >= 0.72 && r.cov <= 0.88, JSON.stringify(r)));
});
t('模拟：作答越多 MAE 越小、区间越窄', () => {
  assert(sim[0].mae > sim[3].mae && sim[0].width > sim[3].width, JSON.stringify(sim));
});
t('模拟：整套模考降低误差', () => { assert(simM[0].mae < sim[1].mae, JSON.stringify([simM[0], sim[1]])); });
t('模拟：真实成绩校准降低系统偏差用户的误差', () => { assert(simC.mae_after < simC.mae_before, JSON.stringify(simC)); });
if (FULL) fs.writeFileSync(path.join(__dirname, '../../work/c3/sim_full.json'), JSON.stringify({ sim, simM, simC }, null, 1));

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
