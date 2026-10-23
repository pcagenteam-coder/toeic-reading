'use strict';
/* ===== B2 前端 API 层：只调引擎公开 API（docs/engine_api.md），引擎缺新 API 时回退 v2 旧接口 ===== */
const API = {
  plan(min) {
    try { if (E.getTodayPlan) return E.getTodayPlan(E.st, min); } catch (e) { console.warn('getTodayPlan', e); }
    const units = E.plan(min); return { mode: 'learn', units, words: [], reviewCount: 0, estSec: min * 60, progress: '', tip: null };
  },
  progress() {
    try { if (E.getProgress) return E.getProgress(E.st); } catch (e) { console.warn('getProgress', e); }
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
