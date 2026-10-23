'use strict';
/* ===== B2 前端 API 层：只调引擎公开 API（docs/engine_api.md），引擎缺新 API 时回退 v2 旧接口 ===== */
const API = {
  plan(min) {
    try { if (E.getTodayPlan) return E.getTodayPlan(E.st, min); } catch (e) { console.warn('getTodayPlan', e); }
    const units = E.plan(min); return { mode: 'learn', units, words: [], reviewCount: 0, estSec: min * 60, progress: '', tip: null };
  },
  /* 预测分（C3 Predict.estimate，docs/engine_api.md §5）；按日志长度/模考/校准/目标缓存；缺 Predict 时回退旧 E.predict()。
   * 返回 {p, lo, hi, tg, prob, level:'low'|'mid'|'high', need:约还要几题, gap, timeLoss, approx, est}（p/lo/hi/tg/prob 兼容旧字段） */
  predict() {
    const s = E.st, L = s.log || [], tg = E.rtg(), mk = (s.mocks || []).filter(m => !m.part);
    const key = [L.length, mk.length, s.predCalib ? s.predCalib.n + ':' + s.predCalib.offset : 0, tg].join('|');
    if (API._pk === key && API._ps === s && API._pv) return API._pv;
    let r = null;
    try {
      if (typeof Predict !== 'undefined') {
        const o = Predict.estimate({ log: L, item: id => IT[id], mocks: mk, calib: s.predCalib, target: tg, macc: E.macc(), nodes: Object.values(ND), seed: 7, draws: 400 });
        const lv = o.confidence.level;
        r = { p: o.score, lo: o.lo, hi: o.hi, tg, prob: o.gap ? o.gap.prob : null, level: lv, answers: o.confidence.answers,
          need: lv === 'low' ? Math.max(5, Math.ceil((40 - o.confidence.answers) / 5) * 5) : 0, gap: o.gap || null, timeLoss: o.timeLoss, approx: true, est: o };
      }
    } catch (e) { console.warn('Predict.estimate', e); }
    if (!r) { const o = E.predict(), w = o.hi - o.lo, lv = (s.N || 0) < 20 || w > 130 ? 'low' : w > 70 ? 'mid' : 'high';
      r = Object.assign({}, o, { level: lv, need: lv === 'low' ? Math.max(5, Math.ceil((30 - (s.N || 0)) / 5) * 5) : 0, gap: null, timeLoss: null, approx: true, est: null }); }
    API._pk = key; API._ps = s; API._pv = r; return r;
  },
  /* 自报真实阅读分 → Predict.calibrate，结果存 st.predCalib（并记 setting_change 事件） */
  calibrate(real) {
    if (typeof Predict === 'undefined') return null;
    const pr = API.predict(), est = pr.est; if (!est) return null;
    const c = Predict.calibrate(E.st.predCalib, real, est);
    E.st.predCalib = c; E.log('setting_change', { key: 'predCalib', value: c }); API._pk = null;
    return c;
  },
  progress() {
    try { if (E.getProgress) { const pr = API.predict(); return E.getProgress(E.st, { pred: { score: pr.p, lo: pr.lo, hi: pr.hi, target: pr.tg } }); } } catch (e) { console.warn('getProgress', e); }
    return { text: '', remainingNodes: null, remainingHours: null, next: [], battle: null };
  },
  profile() {
    try { if (E.getProfile) return E.getProfile(E.st); } catch (e) { console.warn('getProfile', e); }
    return { pace: {}, battle: null, circadian: { enabled: false }, fsrs: {} };
  },
  record(ev) {   // ev: {item_id, choice, ms, lookups, viewed_hint, mode}
    if (E.recordAnswer) { const r = E.recordAnswer(ev); if (r) return r; }
    const it = IT[ev.item_id], ok = E.record(it, { c: ev.choice, ms: ev.ms, lu: ev.lookups > 0 }, ev.mode || 'train');
    return { correct: ok, node: it.n, mastery: E.mastery(it.n) };
  },
  /* 解析：zh_open_v1 优先，否则回退题目自带 explain_zh / 干扰项原因 */
  explain(id) {
    const it = IT[id], x = (D.exp || {})[id];
    if (x) return { basis: x.b, why: x.w, dis: x.d || {}, tip: x.t || '', pp: x.pp || [] };
    const dis = {}; Object.keys(it.dr || {}).forEach(k => { dis['ABCD'[k]] = it.dr[k]; });
    return { basis: '', why: it.e || '', dis, tip: '', pp: [] };
  },
  lesson(node) {
    const G = D.gr || {}; if (G[node]) return Object.assign({ node }, G[node]);
    const n = ND[node]; return n && n.pa && G[n.pa] ? Object.assign({ node: n.pa }, G[n.pa]) : null;
  },
  lookup(w) {
    w = String(w || '').toLowerCase().replace(/[’']s$/, '').replace(/^[^a-z]+|[^a-z]+$/g, '');
    const Dc = D.dict || {}, F = D.forms || {};
    const tryW = x => (Dc[x] ? [x, Dc[x]] : F[x] && Dc[F[x]] ? [F[x], Dc[F[x]]] : null);
    let h = tryW(w);
    if (!h) for (const [suf, rep] of [['ies', 'y'], ['es', ''], ['s', ''], ['ed', ''], ['ed', 'e'], ['ing', ''], ['ing', 'e'], ['ly', '']])
      if (w.endsWith(suf) && (h = tryW(w.slice(0, -suf.length) + rep))) break;
    return h ? { w: h[0], zh: h[1][0], pos: h[1][1], hi: !!h[1][2], form: w } : { w, zh: '', pos: '', hi: false, form: w };
  }
};
