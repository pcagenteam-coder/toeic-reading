/* ===== 个性化（C2）：用时画像 → 跳题预算 / P7 终点线；作息画像；FSRS 个人参数重拟合 =====
 * 原生 JS；浏览器全局 Personal，Node 里 require('./personal.js')（需先有全局 FSRS 或传入）。
 * 所有结果都由答题事件日志（经 Mastery 回放的画像原始量）重算，可随时丢弃。
 */
const Personal = (function () {
  'use strict';
  const F = () => (typeof FSRS !== 'undefined' ? FSRS : require('./fsrs.js'));
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const BANDS = ['≤500', '600', '730', '860+'];

  /* ---------- 用时画像 ---------- */
  const PACE_PRIOR = 10;   // 先验：10 题、用时比 1.0（数据少时不乱改建议）
  function pace(acc) {
    const out = {};
    [5, 6, 7].forEach(p => {
      const c = (acc && acc.pace[p]) || { n: 0, sum: 0 };
      out[p] = { n: c.n, ratio: Math.round((c.sum + PACE_PRIOR) / (c.n + PACE_PRIOR) * 100) / 100 };
    });
    return out;
  }

  /* 作战卡：终点线 / 跳题预算 / 单题放弃线。基准遵循 strategies_v2（S2-ALL-01/02/03/04、C1/C2/C5）：
   *   终点线 ≤500/600 → Q175，730 → Q185，860+ → 不设（Q200）
   *   P5+P6 计划用时 ≤500/600 约 27 分钟（25–30），730 约 20，860+ 约 17
   *   P7 每题放弃线 ≤600 约 90 秒，730+ 约 60 秒
   * 个人化：按个人用时比算 P5+P6 实际要多久、P7 每题多久，推算 75 分钟（留 1 分钟涂卡）能做到第几题。
   * 个人终点线 = min(档位终点线, 能做到的题号)；只会提前，不会越过档位线（多出来的时间按 S2-ALL-15 捡分）。 */
  const LINE = { '≤500': 175, '600': 175, '730': 185, '860+': 200 };
  const P56_MIN = { '≤500': 27, '600': 27, '730': 20, '860+': 17 };
  const SKIP_BASE = { '≤500': [30, 35], '600': [20, 30], '730': [10, 15], '860+': [0, 5] };
  const P7_CUT = { '≤500': 90, '600': 90, '730': 60, '860+': 60 };
  const P5_CUT = { '≤500': 30, '600': 30, '730': 20, '860+': 15 };
  const T = { 5: 22, 6: 30, 7: 55, 7.5: 65 };   // 目标秒（与 build.py DEF_TIME 一致）
  function battleCard(band, pc) {
    pc = pc || pace(null);
    const r5 = pc[5].ratio, r6 = pc[6].ratio, r7 = pc[7].ratio;
    const natural56 = (30 * T[5] * r5 + 16 * T[6] * r6) / 60;
    const p56 = Math.max(P56_MIN[band], Math.round(natural56));
    let left = (75 - 1 - p56) * 60, q = 146;
    while (q < 200) {
      const s = (q + 1 <= 175 ? T[7] : T[7.5]) * r7;
      if (left < s) break; left -= s; q++;
    }
    const base = LINE[band], personal = Math.min(base, q);
    const spare = q > base ? Math.round(((q - base) * T[7.5] * r7 + left) / 60) : 0;
    const extra = band === '≤500' ? 8 : band === '600' ? 4 : 0;   // ≤500 另涂插入句 4 + 长篇报道约 4；600 另涂插入句 4（S2-P6-02 / S2-P7-05）
    return {
      band, finishLine: { base, personal, reachable: q, spareMin: spare,
        tip: personal < base ? `按你现在的速度，做到第 ${personal} 题就停，后面统一涂` :
          spare >= 5 ? `做到第 ${base} 题后还剩约 ${spare} 分钟：多篇只捡词义题和单篇细节题（S2-ALL-15）` : `做到第 ${base} 题就停，后面统一涂` },
      skipBudget: { base: SKIP_BASE[band], personal: 200 - personal + extra },
      p56Min: p56, p5CutSec: Math.round(P5_CUT[band] * clamp(r5, 0.8, 1.3)), p7CutSec: P7_CUT[band],
      pace: pc
    };
  }

  /* ---------- 作息画像：按时段的“超预期”正确率（实际 − 模型预期），收缩估计 ---------- */
  const SLOT_PRIOR = 20, SLOT_MIN_N = 15, TOTAL_MIN_N = 60, SLOT_GAIN = 0.04;
  function circadian(acc, enabled) {
    if (enabled === false) return { enabled: false, best: null, slots: {} };
    const sl = (acc && acc.slot) || {}, keys = Object.keys(sl), slots = {};
    const tot = keys.reduce((s, k) => s + sl[k].n, 0);
    keys.forEach(k => { const x = sl[k]; slots[k] = { n: x.n, acc: Math.round(x.ok / x.n * 100) / 100, lift: Math.round(x.res / (x.n + SLOT_PRIOR) * 1000) / 1000 }; });
    const ok = keys.filter(k => sl[k].n >= SLOT_MIN_N);
    let best = null;
    if (tot >= TOTAL_MIN_N && ok.length >= 2) {
      const sorted = ok.sort((a, b) => slots[b].lift - slots[a].lift), worst = sorted[sorted.length - 1];
      if (slots[sorted[0]].lift - slots[worst].lift >= SLOT_GAIN && slots[sorted[0]].lift > 0) best = sorted[0];
    }
    const name = (typeof Mastery !== 'undefined' ? Mastery.SLOT_NAMES : {})[best] || best;
    return { enabled: true, best, name, n: tot, slots, tip: best ? `你在${name}做题比平时更准，有空就挑这个时段练` : null };
  }

  /* ---------- FSRS 个人参数 ----------
   * 从事件日志抽出每张卡的复习序列（天、评分），损失 = 每次“隔天以上的复习”上
   * −[y·log R + (1−y)·log(1−R)]，R 为按参数 w 回放得到的复习前可提取度，y = 评分 ≠ Again。
   * 拟合：坐标搜索（每个权重 ×(1±步长)，步长 0.3→0.15→0.07，每步长最多 3 轮），
   *       加 L2 先验（向官方默认收缩，λ=0.002·Σ ln²(w/w0)）防过拟合；参数夹在 [0.01, 60]。
   * 门槛：可计损失的复习 ≥300 次才拟合；拟合后损失比默认至少低 0.002 才采用，否则用默认参数。 */
  const MIN_REVIEWS = 300, LAMBDA = 0.002, IMPROVE = 0.002;
  function sequences(events, opts) {
    const Fs = F(), p = Fs.params(opts || {}), seq = {}, reps = {};
    Fs.orderEvents(events).forEach(ev => {
      let id, g, day;
      const tz = ev.tz != null ? ev.tz : p.tz; day = Fs.dayIndex(ev.t || 0, tz);
      if (ev.e === 'answer' || ev.e === 'answer_submit') {
        if (ev.mode === 'diag' || ev.bulk_fill) return;
        const legacy = ev.e === 'answer';
        id = ev.card_id || (legacy ? ev.id : ev.item_id); if (!id) return;
        const correct = legacy ? !!ev.ok : !!ev.correct, looked = legacy ? !!ev.lu : (ev.lookups > 0 || !!ev.viewed_hint);
        let target = ev.ms_target; if (!(target > 0)) target = (p.targetMs && p.targetMs(id)) || p.defaultTargetMs;
        g = Fs.grade(correct, ev.ms, target, looked, reps[id] || 0);
        if (!seq[id] && g >= Fs.GOOD) return;   // 与 applyEvent 一致：新题快对不建卡
      } else if (ev.e === 'review_answer') {
        id = (ev.card_type === 'paraphrase' ? Fs.PARA : Fs.WORD) + String(ev.card_id || '').toLowerCase();
        g = Fs.grade(!!ev.correct, ev.ms, Fs.WORD_TARGET_MS, false, reps[id] || 0);
      } else if (ev.e === 'wordrev') {
        id = Fs.WORD + String(ev.w || '').toLowerCase(); g = ev.g === 2 ? Fs.GOOD : ev.g === 1 ? Fs.HARD : Fs.AGAIN;
      } else return;
      (seq[id] = seq[id] || []).push([day, g]); reps[id] = (reps[id] || 0) + 1;
    });
    return seq;
  }
  function countReviews(seq) { let n = 0; Object.values(seq).forEach(s => { for (let k = 1; k < s.length; k++) if (s[k][0] > s[k - 1][0]) n++; }); return n; }
  function logLoss(seq, w, ids) {
    const Fs = F(), p = Fs.params({ w }); let L = 0, n = 0;
    (ids || Object.keys(seq)).forEach(id => {
      const s = seq[id]; let st = null, last = null;
      for (let k = 0; k < s.length; k++) {
        const [day, g] = s[k];
        if (st && day > last) {
          const R = clamp(Fs.retrievability(day - last, st.s, p), 1e-3, 1 - 1e-3), y = g !== Fs.AGAIN ? 1 : 0;
          L -= y ? Math.log(R) : Math.log(1 - R); n++;
        }
        const o = Fs.step(st, g, st ? day - last : 0, p); st = { s: o.sRaw, d: o.d }; last = day;
      }
    });
    return n ? L / n : null;
  }
  function fitW(seq, opts) {
    opts = opts || {};
    const Fs = F(), w0 = Array.from(Fs.DEFAULT_PARAMS.w), ids = opts.ids || Object.keys(seq);
    const pen = w => LAMBDA * w.reduce((s, x, k) => s + Math.pow(Math.log(x / w0[k]), 2), 0);
    const obj = w => logLoss(seq, w, ids) + pen(w);
    let w = w0.slice(), best = obj(w); const before = logLoss(seq, w0, ids);
    [0.3, 0.15, 0.07].forEach(step => {
      for (let pass = 0; pass < 3; pass++) {
        let moved = false;
        for (let k = 0; k < w.length; k++) {
          for (const f of [1 + step, 1 / (1 + step)]) {
            const c = w.slice(); c[k] = clamp(c[k] * f, 0.01, 60);
            if (k === 7) c[k] = clamp(c[k], 0.001, 0.5);   // 难度均值回归率
            const v = obj(c); if (v < best - 1e-9) { best = v; w = c; moved = true; }
          }
        }
        if (!moved) break;
      }
    });
    const after = logLoss(seq, w, ids);
    return { w: w.map(x => Math.round(x * 10000) / 10000), before, after };
  }
  /* 对事件日志：够数就拟合，返回 {use, n, w|null, before, after} */
  function fsrsFit(events, opts) {
    const seq = sequences(events, opts), n = countReviews(seq);
    if (n < MIN_REVIEWS) return { use: false, n, w: null, reason: `复习 ${n} 次 < ${MIN_REVIEWS}，用默认参数` };
    const r = fitW(seq);
    const use = r.after != null && r.before - r.after >= IMPROVE;
    return { use, n, w: use ? r.w : null, before: r.before, after: r.after, reason: use ? '个人参数' : '拟合改善不足，用默认参数' };
  }

  return { pace, battleCard, circadian, sequences, countReviews, logLoss, fitW, fsrsFit,
    LINE, SKIP_BASE, MIN_REVIEWS, BANDS };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = Personal;
