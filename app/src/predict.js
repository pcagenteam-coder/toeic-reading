/* ===== 托业阅读预测分（C3）：IRT 能力 → 期望正确率 → 原始分 → 量表分（近似） =====
 * 原生 JS、无依赖、纯函数；浏览器里是全局 Predict，Node 里 require('./predict.js')。不改任何状态。
 *
 * 模型（详见 docs/predict_calibration.md）：
 * 1. 能力：3PL（猜测率 c=0.25，区分度 1）分层 MAP。全局 θg ~ N(0,1)；各 Part θp = θg + δp，δp ~ N(0, τ²=0.35²)。
 *    题难度 b = (difficulty_est − 3) × 0.7（与 mastery.js 同尺度）。作答得分 r：错 0 / 查词或看提示 0.5 / 对 1。
 *    旧作答按半衰期 45 天降权（能力在变）。后验方差 = 拉普拉斯近似（Fisher 信息 + 先验精度）。
 *    无作答日志时退回 mastery.js 的全局能力（1PL 尺度，仅作粗先验）。
 * 2. 期望原始分：真题 100 题 = P5 30 + P6 16 + P7 54；各 Part 的难度分布取自传入的整套题（exam），否则用内置分布
 *    （开源整套 MXT01–06 的 difficulty_est 分布）。
 * 3. 用时：各 Part 个人用时比（实际/目标，对数均值，先验 log 1.15、等效 8 题收缩）。75 分钟留 1 分钟涂卡；
 *    按 P5→P6→P7 顺序做，时间不够时末尾的题按猜测率 0.25 计（超时扣减）。
 * 4. 原始分 → 量表分：CONV 表（近似，非官方；见下）。ETS 每套卷经等化，同一原始分的量表分随卷浮动。
 * 5. 不确定度：蒙特卡洛（θg、δp、用时比按后验抽样）→ 期望量表分 T 的分布；加模型误设方差 σ_mis²。
 *    整套模考：每次视作 T 的一次观测（方差 = 抽样误差 + 随时间漂移），按精度加权 → 模考权重最高。
 *    预测区间 = T 的后验 + 一次真实考试的抽样误差（二项）+ 等化误差 σ_eq，再加真实成绩校准偏移。
 * 6. 真实成绩：calibrate() 用“真实 − 当时预测”做贝叶斯偏移估计（先验 N(0,30²)），存为 calib，下次 estimate 传入。
 */
const Predict = (function () {
  'use strict';
  const C = 0.25, TAU = 0.35, PRIOR_SD = 1.0, HALF_LIFE_D = 45, DAY = 864e5;
  const NQ = { 5: 30, 6: 16, 7: 54 }, PARTS = [5, 6, 7];
  const TIME_SEC = 75 * 60 - 60;                       // 75 分钟，留 1 分钟涂卡
  const DEF_T = { 5: 22, 6: 30, 7: 59.6 };             // 每题目标秒（与 build.py DEF_TIME 一致；P7 取整套平均 3220/54）
  const PACE_PRIOR = Math.log(1.15), PACE_N0 = 8, PACE_SD0 = 0.25;
  const SIG_MIS = 15, SIG_EQ = 10, MOCK_DRIFT_WK = 6, CAL_SD0 = 30;
  /* 原始分(0–100) → 阅读量表分。近似：取公开流传的 TOEIC 阅读换算区间（官方题集附表 + 常见培训机构表）的中位数，
   * 未逐表核对，非 ETS 官方固定表；实际每套卷等化后浮动约 ±10–20 分（由 SIG_EQ 计入区间）。 */
  const CONV = [[0, 5], [5, 5], [10, 25], [15, 45], [20, 70], [25, 90], [30, 115], [35, 140], [40, 165], [45, 190], [50, 215],
    [55, 240], [60, 265], [65, 290], [70, 315], [75, 340], [80, 370], [85, 395], [90, 425], [95, 460], [100, 495]];
  /* 内置难度分布（MXT01–06 合计 600 题的 difficulty_est 频数 1:2 2:240 3:282 4:54 5:22），三个 Part 共用 */
  const DEF_DIST = [[-1.4, 2], [-0.7, 240], [0, 282], [0.7, 54], [1.4, 22]];

  const sig = x => 1 / (1 + Math.exp(-x));
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const r5 = x => Math.round(clamp(x, 5, 495) / 5) * 5;
  const diffB = d => ((d || 3) - 3) * 0.7;
  const p3 = (th, b) => C + (1 - C) * sig(th - b);

  function scaledFromRaw(raw) {
    raw = clamp(raw, 0, 100);
    for (let k = 1; k < CONV.length; k++) if (raw <= CONV[k][0]) {
      const [x0, y0] = CONV[k - 1], [x1, y1] = CONV[k]; return y0 + (y1 - y0) * (raw - x0) / (x1 - x0);
    }
    return 495;
  }
  const slopeAt = raw => (scaledFromRaw(Math.min(100, raw + 2.5)) - scaledFromRaw(Math.max(0, raw - 2.5))) / 5;
  function rawFromScaled(s) { let lo = 0, hi = 100; for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (scaledFromRaw(m) < s) lo = m; else hi = m; } return (lo + hi) / 2; }

  /* 可复现随机数（mulberry32）+ 正态 */
  function rng(seed) {
    let a = seed >>> 0;
    const u = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    let spare = null;
    u.n = () => { if (spare != null) { const s = spare; spare = null; return s; } let x, y, r; do { x = 2 * u() - 1; y = 2 * u() - 1; r = x * x + y * y; } while (!r || r >= 1); const f = Math.sqrt(-2 * Math.log(r) / r); spare = y * f; return x * f; };
    return u;
  }

  /* 作答日志 → 观测 [{p, b, r, w, ratio}]。exclMock：已作为整套成绩传入的模考作答不再逐题计入（避免重复计） */
  function observations(log, item, now, exclMock) {
    const out = [];
    (log || []).forEach(ev => {
      if (!ev || (ev.e !== 'answer' && ev.e !== 'answer_submit') || ev.bulk_fill) return;
      const legacy = ev.e === 'answer', id = legacy ? ev.id : ev.item_id, it = id && item(id);
      if (!it || !NQ[it.p]) return;
      const mode = ev.mode;
      if (exclMock && mode === 'mock') return;
      const choice = legacy ? ev.c : ev.choice;
      if (choice == null && mode === 'mock') return;
      const ok = legacy ? !!ev.ok : !!ev.correct;
      const r = !ok ? 0 : ((legacy ? ev.lu : (ev.lookups > 0 || ev.viewed_hint)) ? 0.5 : 1);
      const age = now && ev.t ? Math.max(0, (now - ev.t) / DAY) : 0;
      const tgt = ev.ms_target > 0 ? ev.ms_target : (it.t || DEF_T[it.p]) * 1000;
      const ratio = ev.ms > 0 && tgt > 0 ? clamp(ev.ms / tgt, 0.2, 4) : null;
      out.push({ p: it.p, b: diffB(it.d), r, w: Math.pow(0.5, age / HALF_LIFE_D), ratio, n: it.n });
    });
    return out;
  }

  /* 一维 MAP（Fisher scoring）：obs 的 3PL 似然 + 先验 N(m0, s0²)，θ = base + x */
  function map1(obs, base, m0, s0) {
    let x = m0, I = 0;
    for (let it = 0; it < 30; it++) {
      let g = -(x - m0) / (s0 * s0), h = 1 / (s0 * s0); I = 0;
      for (const o of obs) {
        const s = sig(base + x - o.b), p = C + (1 - C) * s, dp = (1 - C) * s * (1 - s), q = p * (1 - p);
        g += o.w * (o.r - p) * dp / q; const f = o.w * dp * dp / q; h += f; I += f;
      }
      const step = clamp(g / h, -1, 1); x += step;
      if (Math.abs(step) < 1e-5) break;
    }
    return { x: clamp(x, -4, 4), v: 1 / (1 / (s0 * s0) + I), I };
  }

  function fitAbility(obs, macc) {
    if (!obs.length) {
      const g = macc && macc.g ? { mu: macc.g.mu, v: Math.max(macc.g.v, 0.5) } : { mu: 0, v: PRIOR_SD * PRIOR_SD };
      const parts = {}; PARTS.forEach(p => { parts[p] = { d: 0, v: TAU * TAU, n: 0 }; });
      return { g, parts, n: 0, nEff: 0 };
    }
    const G = map1(obs, 0, 0, PRIOR_SD), parts = {};
    PARTS.forEach(p => {
      const o = obs.filter(x => x.p === p), f = map1(o, G.x, 0, TAU);
      parts[p] = { d: f.x, v: f.v, n: o.length };
    });
    return { g: { mu: G.x, v: G.v }, parts, n: obs.length, nEff: obs.reduce((s, o) => s + o.w, 0) };
  }

  function fitPace(obs) {
    const pace = {};
    PARTS.forEach(p => {
      const ls = obs.filter(o => o.p === p && o.ratio).map(o => Math.log(o.ratio)), n = ls.length;
      const mean = n ? ls.reduce((a, b) => a + b, 0) / n : 0;
      const sd = n > 2 ? Math.sqrt(ls.reduce((a, b) => a + (b - mean) * (b - mean), 0) / (n - 1)) : 0.4;
      const mu = (PACE_PRIOR * PACE_N0 + mean * n) / (PACE_N0 + n);
      // 均值的后验 sd：先验 PACE_SD0（人与人差异），数据精度 n/sd²
      const v = 1 / (1 / (PACE_SD0 * PACE_SD0) + n / Math.max(0.04, sd * sd));
      pace[p] = { mu, v, n, ratio: Math.exp(mu) };
    });
    return pace;
  }

  /* 考试结构：各 Part 难度分布 [[b, 权重]] 与各节点每 100 题的期望题数 */
  function examModel(exam) {
    const dist = {}, nodeQ = {};
    if (exam && exam.length) {
      PARTS.forEach(p => {
        const its = exam.filter(i => i.p === p), cnt = {};
        its.forEach(i => { const b = diffB(i.d); cnt[b] = (cnt[b] || 0) + 1; });
        dist[p] = its.length ? Object.keys(cnt).map(b => [+b, cnt[b]]) : DEF_DIST;
        its.forEach(i => { nodeQ[i.n] = (nodeQ[i.n] || 0) + NQ[p] / its.length; });
      });
    } else PARTS.forEach(p => { dist[p] = DEF_DIST; });
    PARTS.forEach(p => { const s = dist[p].reduce((a, x) => a + x[1], 0); dist[p] = dist[p].map(x => [x[0], x[1] / s]); });
    return { dist, nodeQ, tSec: exam && exam.length ? partTime(exam) : DEF_T };
  }
  function partTime(exam) {
    const t = {}; PARTS.forEach(p => { const its = exam.filter(i => i.p === p); t[p] = its.length ? its.reduce((s, i) => s + (i.t || DEF_T[p]), 0) / its.length : DEF_T[p]; }); return t;
  }

  /* 给定能力与用时比 → 各 Part 期望答对数、方差、超时未做题数 */
  function examOutcome(th, ratio, EM) {
    const res = {}; let left = TIME_SEC;
    PARTS.forEach(p => {
      const acc = EM.dist[p].reduce((s, [b, w]) => s + w * p3(th[p], b), 0);
      const per = EM.tSec[p] * ratio[p], need = NQ[p] * per;
      const done = need <= left ? NQ[p] : Math.max(0, left / per);
      left = Math.max(0, left - need);
      const miss = NQ[p] - done;
      res[p] = { acc, done, miss, exp: done * acc + miss * C, varr: done * acc * (1 - acc) + miss * C * (1 - C) };
    });
    return res;
  }

  /* 主入口：见 docs/engine_api.md §5 */
  function estimate(inp) {
    inp = inp || {};
    const now = inp.now || Date.now(), item = inp.item || (() => null);
    const mocks = (inp.mocks || []).filter(m => m && m.n >= 50);   // 至少半套才算整套成绩
    const obs = observations(inp.log, item, now, mocks.length > 0);
    const A = fitAbility(obs, inp.macc), PC = fitPace(obs), EM = examModel(inp.exam);
    const R = rng(inp.seed || 12345), D = inp.draws || 600;
    // 蒙特卡洛：T（期望量表分，无考试抽样误差）
    const Ts = [], parts = {}; PARTS.forEach(p => { parts[p] = { exp: 0, miss: 0, acc: 0 }; });
    let varrSum = 0, rawSum = 0;
    for (let k = 0; k < D; k++) {
      const tg = A.g.mu + Math.sqrt(A.g.v) * R.n(), th = {}, ra = {};
      PARTS.forEach(p => { th[p] = tg + A.parts[p].d + Math.sqrt(A.parts[p].v) * R.n(); ra[p] = Math.exp(PC[p].mu + Math.sqrt(PC[p].v) * R.n()); });
      const o = examOutcome(th, ra, EM); let raw = 0, vr = 0;
      PARTS.forEach(p => { raw += o[p].exp; vr += o[p].varr; parts[p].exp += o[p].exp / D; parts[p].miss += o[p].miss / D; parts[p].acc += o[p].acc / D; });
      Ts.push(scaledFromRaw(raw)); varrSum += vr / D; rawSum += raw / D;
    }
    const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
    const mT = mean(Ts), vT = mean(Ts.map(x => (x - mT) * (x - mT)));
    const slope = slopeAt(rawSum), sSamp = slope * Math.sqrt(varrSum);   // 一次考试的抽样 sd（量表分）
    // 模型 + 整套模考：精度加权
    const hasLog = obs.length > 0, cal = inp.calib && inp.calib.n ? inp.calib : null;
    // 模型误设方差：有真实成绩校准后，由偏移的不确定度取代（偏差已被估计）
    const misV = hasLog ? (cal ? Math.min(SIG_MIS * SIG_MIS, cal.v) : SIG_MIS * SIG_MIS) : 0;
    let prec = 1 / (vT + misV), num = mT * prec, modelW = prec;
    const mockUsed = mocks.map(m => {
      const raw = m.n ? 100 * m.ok / m.n : null, sc = raw != null ? scaledFromRaw(raw) : m.scaled;
      const wk = Math.max(0, (now - (m.ts || now)) / (7 * DAY));
      const sd = Math.sqrt(sSamp * sSamp * (100 / m.n) + SIG_EQ * SIG_EQ + (MOCK_DRIFT_WK * wk) ** 2);
      const pr = 1 / (sd * sd); prec += pr; num += sc * pr; return { ts: m.ts, scaled: r5(sc), w: pr };
    });
    const muT = num / prec, vPost = 1 / prec;
    const center = muT + (cal ? cal.offset : 0);
    const sd = Math.sqrt(vPost + sSamp * sSamp + SIG_EQ * SIG_EQ + (cal && !hasLog ? cal.v : 0));
    const Z80 = 1.2816;
    const score = r5(center), lo = r5(center - Z80 * sd), hi = r5(center + Z80 * sd);
    // 各 Part 贡献（期望答对、量表分折算按比例分摊）
    const partOut = {}, rawTot = PARTS.reduce((s, p) => s + parts[p].exp, 0) || 1;
    PARTS.forEach(p => {
      const x = parts[p], ap = A.parts[p];
      partOut[p] = { q: NQ[p], correct: +x.exp.toFixed(1), acc: +x.acc.toFixed(3), unreached: +x.miss.toFixed(1),
        points: Math.round(score * x.exp / rawTot), n: ap.n, theta: +(A.g.mu + ap.d).toFixed(2), pace: +PC[p].ratio.toFixed(2) };
    });
    const unreached = PARTS.reduce((s, p) => s + parts[p].miss, 0);
    const timeLoss = { q: +unreached.toFixed(1), points: Math.round(slope * unreached * (PARTS.reduce((s, p) => s + parts[p].acc * parts[p].miss, 0) / Math.max(1e-9, unreached) - C) || 0) };
    const w80 = hi - lo, level = w80 <= 70 ? 'high' : w80 <= 130 ? 'mid' : 'low';
    const confidence = { level, width: w80, answers: obs.length, mocks: mockUsed.length, calibrated: !!cal,
      text: `${level === 'high' ? '较准' : level === 'mid' ? '中等' : '粗略'}：基于 ${obs.length} 道练习${mockUsed.length ? `、${mockUsed.length} 次整套模考` : ''}${cal ? '、真实成绩校准' : ''}；80% 可能落在 ${lo}–${hi}。${mockUsed.length ? '' : '做一套整套模考最能收窄区间。'}换算表为近似，非 ETS 官方。` };
    const out = { score, lo, hi, sd: Math.round(sd), approx: true, raw: +rawSum.toFixed(1), parts: partOut, timeLoss, confidence,
      model: { theta: +A.g.mu.toFixed(2), thetaSd: +Math.sqrt(A.g.v).toFixed(2), T: Math.round(muT), modelT: Math.round(mT),
        modelWeight: +(modelW / prec).toFixed(2), mocks: mockUsed, offset: cal ? Math.round(cal.offset) : 0, sSamp: Math.round(sSamp) } };
    // 用于 calibrate：未加校准偏移的预测中心与方差
    out.uncal = { center: muT, v: vPost + sSamp * sSamp + SIG_EQ * SIG_EQ };
    if (inp.target) out.gap = gapAnalysis(inp, out, center, sd, EM, slope);
    return out;
  }

  /* 离目标差多少、主要差在哪些考点 */
  function gapAnalysis(inp, out, center, sd, EM, slope) {
    const target = inp.target, diff = Math.round(target - center);
    const z = (center - target) / sd, prob = 1 / (1 + Math.exp(-1.702 * z));
    const needAcc = clamp(rawFromScaled(target) / 100, 0.3, 0.98);   // 达到目标所需整体正确率
    const nodes = [];
    if (inp.macc && typeof Mastery !== 'undefined' || inp.mastery) {
      const of = inp.mastery || (id => Mastery.of(inp.macc, id, inp.now));
      const NM = {}; (inp.nodes || []).forEach(n => { NM[n.id] = n; });
      Object.keys(EM.nodeQ).forEach(id => {
        const q = EM.nodeQ[id], o = of(id) || {}, m = o.m != null ? o.m : null;
        if (m == null || q < 0.3) return;
        const gainRaw = q * Math.max(0, needAcc - m);
        if (gainRaw <= 0.05) return;
        nodes.push({ id, nm: NM[id] ? NM[id].nm : id, m: +m.toFixed(2), seen: !!o.seen, q: +q.toFixed(1), gain: Math.round(gainRaw * slope) });
      });
      nodes.sort((a, b) => b.gain - a.gain);
    }
    const top = nodes.slice(0, 5);
    const tl = out.timeLoss.points >= 5 ? `；时间不够约丢 ${out.timeLoss.points} 分（${out.timeLoss.q} 题来不及做）` : '';
    const text = diff <= 0 ? `预测已达目标 ${target}（达标概率约 ${Math.round(prob * 100)}%）${tl}` :
      `离目标 ${target} 还差约 ${diff} 分（达标概率约 ${Math.round(prob * 100)}%）${tl}${top.length ? '；主要差在：' + top.slice(0, 3).map(n => `${n.nm}（约 +${n.gain}）`).join('、') : ''}`;
    return { target, diff, prob: +prob.toFixed(2), needAcc: +needAcc.toFixed(2), nodes: top, text };
  }

  /* 真实成绩校准：real = 用户自报阅读分；pred = 当时的 estimate() 结果（或其 uncal）。返回新的 calib，存档后传给 estimate */
  function calibrate(calib, real, pred) {
    const u = pred.uncal || pred, c = calib && calib.n ? calib : { offset: 0, v: CAL_SD0 * CAL_SD0, n: 0 };
    const d = real - u.center, vd = u.v;          // 观测：d ~ N(offset, vd)
    const v = 1 / (1 / c.v + 1 / vd), offset = v * (c.offset / c.v + d / vd);
    return { offset: +offset.toFixed(1), v: +v.toFixed(1), n: c.n + 1, last: { real, pred: Math.round(u.center) } };
  }

  return { estimate, calibrate, scaledFromRaw, rawFromScaled, observations, fitAbility, fitPace, examOutcome, examModel, rng,
    consts: { C, TAU, NQ, TIME_SEC, DEF_T, CONV, SIG_MIS, SIG_EQ, MOCK_DRIFT_WK, HALF_LIFE_D } };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = Predict;
