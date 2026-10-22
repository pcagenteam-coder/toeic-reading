// FSRS-4.5 引擎单元测试（无框架）：node app/test/fsrs.test.js
// 期望值来源：
//   REF  = huieric/toefl-miniapp server/src/services/fsrs.js（MIT，参考实现）实测输出
//   OFFI = open-spaced-repetition/py-fsrs 2.5.1（FSRS-4.5 官方 Python 实现）公式，每步 S/D 四舍五入到 4 位（与本实现/参考实现一致）
// 参考实现 nextRecallStability 有 bug（exp(w8·(11−D)) 应为 e^{w8}·(11−D)），所以含"回忆成功"的序列对拍 OFFI，
// 只含首评 + Again 的序列及各分量公式对拍 REF。若本地有参考源码，另做随机对拍。
'use strict';
const fs = require('fs'), path = require('path'), assert = require('assert');
const F = require('../src/fsrs.js');
let pass = 0, fail = 0;
function t(name, fn) { try { fn(); pass++; console.log('ok  ', name); } catch (e) { fail++; console.log('FAIL', name, '\n     ', e.message); } }
const near = (a, b, tol, msg) => { if (a === b) return; if (a == null || b == null || Math.abs(a - b) > (tol || 1e-9) * Math.max(1, Math.abs(b))) throw new Error((msg || '') + ` got ${a} want ${b}`); };
const T0 = Date.UTC(2026, 9, 1, 2, 0, 0), DAY = 864e5;
function runSeq(seq) { // [[rating, elapsedDays], ...] → 参考实现 review 语义
  let st = null, t = T0; return seq.map(([g, el]) => { t += el * DAY; const r = F.review(st, g, t); st = { stability: r.stability, difficulty: r.difficulty, lastReviewAt: t }; return [r.stability, r.difficulty, r.retrievability, r.interval]; });
}
function cmpSeq(name, seq, want, ivlTol) { // OFFI 的间隔由取整后的 S 算，故 ivl 放宽到 1e-4 相对误差
  const got = runSeq(seq);
  want.forEach((w, i) => w.forEach((v, j) => near(got[i][j], v, j === 3 && ivlTol ? ivlTol : 1e-9, `${name} step ${i} field ${['S', 'D', 'R', 'ivl'][j]}`)));
}

/* ---------- 1. 对拍参考实现（默认参数） ---------- */
const REF = {
  comp: { initS: [0.4872, 1.4003, 3.7145, 13.8206], initD: [7.6214, 6.3916, 5.1618, 3.9320000000000004],
    nextD: [6.7443707999999996, 5.8746933, 5.0050158, 4.1353383, 10, 1],
    forgetS: [1.235311065146688, 4.851248170455642, 0.3037318752034153],
    R: [1, 0.9, 0.470437536140385, 0.9988292197975929],
    ivl: [4.999999999999999, 2.302813821256745, 46.0562764251349, 0.19999999999999996] },
  SEQ: { g_aa: [[3, 0], [1, 5], [1, 2]], e_aaa: [[4, 0], [1, 30], [1, 1], [1, 7]], h_a: [[2, 0], [1, 1]], a_aa: [[1, 0], [1, 3], [1, 0.25]] },
  out: { g_aa: [[3.7145, 5.1618, null, 3.7144999999999992], [1.4835, 6.9012, 0.8718, 1.4834645105445619], [0.7613, 8.5866, 0.8716, 0.7613439311771203]],
    e_aaa: [[13.8206, 3.932, null, 13.820599999999997], [3.5532, 5.7095, 0.814, 3.5531567677071387], [1.2263, 7.4319, 0.9685, 1.2263254281554412], [0.9235, 9.1009, 0.6539, 0.9235272868291233]],
    h_a: [[1.4003, 6.3916, null, 1.4002999999999997], [0.673, 8.0928, 0.9255, 0.6729887837767644]],
    a_aa: [[0.4872, 7.6214, null, 0.4871999999999999], [0.437, 9.2845, 0.6396, 0.4369687906296713], [0.243, 10, 0.939, 0.24296846056719063]] }
};
t('REF 分量：17 个默认权重 / 初始 S·D / 难度更新 / 遗忘稳定度 / R / 间隔', () => {
  assert.strictEqual(F.DEFAULT_PARAMS.w.length, 17);
  assert.deepStrictEqual(Array.from(F.DEFAULT_PARAMS.w), [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031, 1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]);
  const I = F._internals;
  [1, 2, 3, 4].forEach((g, k) => { near(I.initStability(g), REF.comp.initS[k]); near(I.initDifficulty(g), REF.comp.initD[k]); });
  [[5, 1], [5, 2], [5, 3], [5, 4], [9.5, 1], [1.2, 4]].forEach(([d, g], k) => near(I.nextDifficulty(d, g), REF.comp.nextD[k]));
  [[5, 3, 0.9], [8, 20, 0.7], [2, 0.5, 0.95]].forEach((a, k) => near(I.nextForgetStability(...a), REF.comp.forgetS[k]));
  [[0, 5], [5, 5], [30, 2], [1, 100]].forEach((a, k) => near(F.retrievability(...a), REF.comp.R[k]));
  [[0.9, 5], [0.95, 5], [0.95, 100], [0.9, 0.2]].forEach((a, k) => near(F.nextInterval(...a), REF.comp.ivl[k]));
});
Object.keys(REF.SEQ).forEach(k => t('REF 序列 ' + k + '（首评 + Again）', () => cmpSeq(k, REF.SEQ[k], REF.out[k])));

/* ---------- 2. 对拍官方 FSRS-4.5（py-fsrs 2.5.1） ---------- */
const OFFI = {
  SEQ: { allGood: [[3, 0], [3, 4], [3, 12], [3, 35]], lapse: [[3, 0], [3, 3], [1, 10], [3, 1], [3, 3]], hardEasy: [[2, 0], [2, 1], [4, 2], [4, 9], [3, 40]],
    againStart: [[1, 0], [1, 0.5], [2, 1], [3, 2], [4, 6]], overdue: [[4, 0], [3, 60], [1, 200], [2, 2.5]] },
  out: { allGood: [[3.7145, 5.1618, null, 3.7145], [14.8081, 5.1618, 0.8935, 14.8081], [43.1021, 5.1618, 0.9167, 43.1021], [114.4004, 5.1618, 0.9165, 114.4004]],
    lapse: [[3.7145, 5.1618, null, 3.7145], [12.2624, 5.1618, 0.9169, 12.2624], [2.7772, 6.9012, 0.9162, 2.7772], [4.9591, 6.8473, 0.9603, 4.9591], [10.9276, 6.795, 0.9358, 10.9276]],
    hardEasy: [[1.4003, 6.3916, null, 1.4003], [1.9898, 7.2232, 0.9255, 1.9898], [13.3071, 6.2896, 0.8996, 13.3071], [63.9579, 5.385, 0.929, 63.9579], [139.656, 5.3781, 0.9338, 139.656]],
    againStart: [[0.4872, 7.6214, null, 0.4872], [0.2901, 9.2845, 0.8978, 0.2901], [0.5041, 10, 0.7436, 0.5041], [1.4837, 9.85, 0.7197, 1.4837], [9.8229, 8.835, 0.7164, 9.8229]],
    overdue: [[13.8206, 3.932, null, 13.8206], [142.4679, 3.9701, 0.7039, 142.4679], [9.3563, 5.7464, 0.8673, 9.3563], [10.7155, 6.598, 0.9701, 10.7155]] }
};
Object.keys(OFFI.SEQ).forEach(k => t('OFFI 序列 ' + k, () => cmpSeq(k, OFFI.SEQ[k], OFFI.out[k], 1e-4)));

/* 本地有参考源码时：除回忆稳定度外随机对拍 */
const REF_SRC = [path.join(__dirname, '../../../research/toefl-miniapp/server/src/services/fsrs.js'),
  path.join(__dirname, '../../private_data/sources/github/_reference_code/toefl-miniapp/server/src/services/fsrs.js')].find(p => fs.existsSync(p));
if (REF_SRC) t('REF 源码随机对拍 500 组（' + path.basename(path.dirname(path.dirname(path.dirname(path.dirname(REF_SRC))))) + '）', () => {
  const R = require(REF_SRC), I = F._internals; let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 500; i++) {
    const d = 1 + rnd() * 9, s = 0.1 + rnd() * 300, r = rnd(), g = 1 + Math.floor(rnd() * 4), el = rnd() * 400;
    near(I.nextDifficulty(d, g), R._internals.nextDifficulty(d, g)); near(I.nextForgetStability(d, s, r), R._internals.nextForgetStability(d, s, r));
    near(F.retrievability(el, s), R.retrievability(el, s));
    near(F._internals.initStability(g), R._internals.initialStability(g)); near(F._internals.initDifficulty(g), R._internals.initialDifficulty(g));
    near(F.nextInterval(0.9, s), R.nextInterval(0.9, s)); near(F.nextInterval(0.95, s), R.nextInterval(0.95, s));
  }
});

/* ---------- 3. 自动评分 ---------- */
t('grade：错/查词=Again，慢=Hard，正常=Good，明显快=Easy', () => {
  const { AGAIN, HARD, GOOD, EASY } = F;
  assert.strictEqual(F.grade(false, 5000, 20000, false), AGAIN);
  assert.strictEqual(F.grade(true, 5000, 20000, true), AGAIN);
  assert.strictEqual(F.grade(true, 20001, 20000, false), HARD);
  assert.strictEqual(F.grade(true, 20000, 20000, false), GOOD);       // 等于目标 = 正常
  assert.strictEqual(F.grade(true, 12001, 20000, false), GOOD);
  assert.strictEqual(F.grade(true, 12000, 20000, false), EASY);       // ≤ 0.6×目标
  assert.strictEqual(F.grade(true, 12000, 20000, false, 0), GOOD);    // 首见快对不给 Easy
  assert.strictEqual(F.grade(true, 12000, 20000, false, 1), EASY);
  assert.strictEqual(F.grade(true, undefined, 20000, false), GOOD);   // 无用时信息
  assert.strictEqual(F.HARD_RATIO, 1.0); assert.strictEqual(F.EASY_RATIO, 0.6);
});

/* ---------- 4. 考前压缩 ---------- */
t('考前压缩：≤14 天保持率 0.95，间隔不越过考试日', () => {
  const day = 20000, c = { s: 40, d: 5, last: day - 40, due: day, reps: 3, lapses: 0, rv: null };
  assert.strictEqual(F.retentionFor(day, null), 0.9);
  assert.strictEqual(F.retentionFor(day, day + 15), 0.9);
  assert.strictEqual(F.retentionFor(day, day + 14), 0.95);
  assert.strictEqual(F.retentionFor(day, day), 0.95);
  assert.strictEqual(F.retentionFor(day, day - 1), 0.9);              // 考完恢复
  const far = F.scheduleCard(c, F.GOOD, day, null), comp = F.scheduleCard(c, F.GOOD, day, day + 60), near14 = F.scheduleCard(c, F.GOOD, day, day + 14);
  assert.strictEqual(far.due - day, Math.round(far.s));             // 0.9 时间隔 = S
  assert.ok(comp.due <= day + 60);
  const ivl95 = Math.round(F.nextInterval(0.95, near14.s));
  assert.strictEqual(near14.due - day, Math.min(ivl95, 14));
  assert.ok(near14.due <= day + 14);
  assert.ok(ivl95 < Math.round(near14.s), '0.95 间隔应短于 0.9');
  const capped = F.scheduleCard(c, F.EASY, day, day + 3);             // 大间隔被压到考试日
  assert.strictEqual(capped.due, day + 3);
  const after = F.scheduleCard(c, F.GOOD, day, day - 2);              // 考试已过：不压缩
  assert.strictEqual(after.due, far.due);
  // 回放层：exam_date_set 之后的作答都不排到考后
  const tz = 480, base = Date.UTC(2026, 10, 1, 4, 0, 0), ex = '2026-11-10', exDay = F.examDayIndex(ex), ev = [{ e: 'exam_date_set', t: base - 1000, tz, exam_date: ex }];
  for (let i = 0; i < 6; i++) ev.push({ e: 'answer_submit', t: base + i * DAY, tz, item_id: 'X1', mode: 'review', correct: 1, ms: 9000, ms_target: 20000, lookups: 0 });
  ev.splice(1, 0, { e: 'answer_submit', t: base - 500, tz, item_id: 'X1', mode: 'daily5', correct: 0, ms: 9000, ms_target: 20000, lookups: 0 });
  const st = F.replay(ev);
  assert.ok(st.X1 && st.X1.due <= exDay, 'due ' + st.X1.due + ' > exam ' + exDay);
});

/* ---------- 5. 每日上限 + 积压平摊 ---------- */
t('每日上限 20，超出按优先级顺延、填后续空位、不留逾期', () => {
  const today = 30000, cards = {};
  for (let i = 0; i < 50; i++) cards['c' + i] = { s: 5 + i, d: 5, last: today - 30, due: today - (i % 7), reps: 2, lapses: 0, rv: null };
  for (let i = 0; i < 15; i++) cards['n' + i] = { s: 10, d: 5, last: today - 2, due: today + 1, reps: 1, lapses: 0, rv: null }; // 明天本就到期 15 张
  const w = id => (id === 'c49' ? 100 : 1);
  const q = F.dailyQueue(cards, today, { weight: w });
  assert.strictEqual(q.today.length, 20); assert.strictEqual(q.backlog, 30);
  assert.strictEqual(q.today[0], 'c49', '高考频优先');
  // 同权重时遗忘程度大（S 小）的在前
  const rest = q.today.slice(1); assert.deepStrictEqual(rest, rest.slice().sort((a, b) => +a.slice(1) - +b.slice(1)));
  const perDay = {}; Object.keys(q.plan).forEach(id => { assert.ok(q.plan[id] >= today, '无逾期'); perDay[q.plan[id]] = (perDay[q.plan[id]] || 0) + 1; });
  assert.strictEqual(perDay[today + 1], 5);                       // 明天 20 − 原有 15
  assert.strictEqual(perDay[today + 2], 20); assert.strictEqual(perDay[today + 3], 5);
  // 当天已完成的到期复习占额度
  const c2 = JSON.parse(JSON.stringify(cards)); for (let i = 0; i < 8; i++) c2['n' + i] = Object.assign(c2['n' + i], { rv: today });
  assert.strictEqual(F.dailyQueue(c2, today, { weight: w }).today.length, 12);
  assert.strictEqual(F.dailyQueue(cards, today, { cap: 5 }).today.length, 5);
});

/* ---------- 6. 回放 ---------- */
function mkLog() {
  const tz = 480, b = Date.UTC(2026, 9, 1, 1, 0, 0), L = []; let seq = 0;
  const add = (o, dt) => L.push(Object.assign({ eid: 'e' + (++seq), t: b + dt, tz, did: 'd1', seq }, o));
  add({ e: 'profile_create', exam_date: '2026-12-20' }, 0);
  ['A', 'B', 'C', 'D'].forEach((id, k) => add({ e: 'answer_submit', item_id: id, mode: 'daily5', correct: k % 2, ms: 15000 + k * 5000, ms_target: 20000, lookups: k === 2 ? 1 : 0 }, 1000 + k));
  add({ e: 'answer_submit', item_id: 'Q', mode: 'diag', correct: 0, ms: 9000, ms_target: 20000 }, 2000);
  add({ e: 'word_save', lemma: 'Invoice' }, 3000);
  for (let d = 1; d < 30; d += 3) {
    ['A', 'B', 'C'].forEach((id, k) => add({ e: 'answer_submit', item_id: id, mode: 'review', correct: (d + k) % 4 ? 1 : 0, ms: 8000 + ((d * 7 + k * 3) % 20) * 1000, ms_target: 20000, lookups: 0, viewed_hint: false }, d * DAY + k));
    add({ e: 'review_answer', card_type: 'word', card_id: 'invoice', correct: d % 2, ms: 3000 }, d * DAY + 50);
  }
  add({ e: 'exam_date_set', exam_date: '2026-10-25' }, 10 * DAY);
  add({ e: 'answer', id: 'L1', mode: 'free', ok: 0, ms: 30000, lu: 0, ms_target: 22000 }, 11 * DAY); // v2 旧格式
  return L;
}
t('回放：纯函数、幂等、与顺序/重复无关、增量 = 全量', () => {
  const L = mkLog(), snap = JSON.stringify(L);
  const a = F.replay(L), b = F.replay(L);
  assert.deepStrictEqual(a, b); assert.strictEqual(JSON.stringify(L), snap, '不修改输入');
  const shuffled = L.slice().reverse(); assert.deepStrictEqual(F.replay(shuffled), a);
  assert.deepStrictEqual(F.replay(L.concat(L.slice(3, 20))), a, '重复 eid 只算一次');
  const acc = F.newAcc(); F.orderEvents(L).forEach(e => F.applyEvent(acc, e)); assert.deepStrictEqual(acc.cards, a);
  const k = 20, pre = F.replayFull(L.slice(0, k)); L.slice(k).forEach(e => F.applyEvent(pre, e)); assert.deepStrictEqual(pre.cards, a, '前缀回放 + 增量');
  assert.ok(!a.Q, '诊断不建卡'); assert.ok(!a.B || a.B.reps > 1, '新题快对不建卡（B 首次正常对）');
  assert.ok(a.A && a.C && a['w:invoice'] && a.L1, '错题/查词/生词/旧日志建卡');
  assert.ok(a.L1.due <= F.examDayIndex('2026-10-25') || a.L1.last >= F.examDayIndex('2026-10-25'));
  Object.values(a).forEach(c => { assert.ok(c.s > 0 && c.d >= 1 && c.d <= 10 && c.due > c.last, JSON.stringify(c)); });
});
t('回放：B 首次 Good 不建卡，D 首次慢对(Hard)建卡', () => {
  const a = F.replay(mkLog().filter(e => e.e !== 'answer_submit' || e.mode !== 'review'));
  assert.ok(!a.B); assert.ok(a.D && a.D.g === F.HARD); assert.ok(a.A.g === F.AGAIN && a.C.g === F.AGAIN);
});

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
