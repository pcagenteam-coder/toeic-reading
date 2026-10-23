// 无浏览器冒烟测试：最小 DOM 桩 + 跑完整流程
// 用法：node app/test/smoke.js [dist 路径]   默认 app/dist/index.html（公开构建）；私有构建：node app/test/smoke.js app/dist/index.private.html
const fs = require('fs'), vm = require('vm'), path = require('path');
const DIST = process.argv[2] ? path.resolve(process.argv[2]) : path.join(__dirname, '../dist/index.html');
console.log('dist', path.relative(process.cwd(), DIST));
const html = fs.readFileSync(DIST, 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const els = {};
const mk = id => els[id] || (els[id] = { id, innerHTML: '', textContent: '', value: '', dataset: {}, style: {}, firstChild: { style: {} },
  classList: { toggle() { }, add() { }, remove() { } }, select() { }, focus() { } });
const ls = {};
const ctx = { window: {}, console, alert: m => console.log('[alert]', m), confirm: () => true, scrollTo() { }, setInterval: () => 1, clearInterval() { }, setTimeout: () => 1, requestAnimationFrame: () => 1,
  btoa: s => Buffer.from(s, 'binary').toString('base64'), atob: s => Buffer.from(s, 'base64').toString('binary'), escape, unescape, encodeURIComponent, decodeURIComponent,
  navigator: { clipboard: { writeText: () => Promise.resolve() } }, URL: { createObjectURL: () => 'blob:' }, Blob: function () { },
  document: { querySelector: s => mk(s.replace('#', '')), querySelectorAll: () => [], addEventListener() { }, createElement: () => ({ click() { }, remove() { } }), body: { appendChild() { } }, execCommand() { } } };
ctx.window.localStorage = { getItem: k => (k in ls ? ls[k] : null), setItem: (k, v) => { ls[k] = String(v); }, removeItem: k => { delete ls[k]; } };
ctx.window.addEventListener = () => { }; ctx.addEventListener = () => { };
vm.createContext(ctx);
vm.runInContext(scripts[0], ctx);
const test = `
const el = (o) => ({ dataset: o || {} });
$('#sName').value = 'A'; $('#sDate').value = '2026-12-20';
A.setupGo(el({ d: '1' }));
if (E.st.rtg !== 270 || E.st.ob.step !== 'vocab') throw new Error('S1 goal: rtg ' + E.st.rtg);
render(); if (!/词汇摸底/.test($('#main').innerHTML)) throw new Error('vocab intro');
A.vstart(); let vk = 0; while (E.st.ob.step === 'vtest') { const vt = E.st.ob.vt; render(); if (vt.chk) A.vchk(el({ i: String(vt.chk.a) })); else A.vk(el({ y: vt.q[vt.i][1] ? '1' : '0' })); vk++; if (vk === 10) { A.vpause(); A.vresume(); } }
console.log('vocab', JSON.stringify(E.st.ob.voc), 'steps', vk); if (!(E.st.ob.voc.n > 1000)) throw new Error('vocab estimate');
render(); A.diag();
let n = 0; while (S && S.mode === 'diag') { vQuiz(); if (n === 3) { A.pause(); render(); A.diag(); } answer(Math.floor(Math.random() * 4)); n++; }
if (!E.st.diag || E.st.ob.step !== 'result' || R) throw new Error('diag not done');
render(); const rh = $('#main').innerHTML, bl = (rh.match(/<li>/g) || []).length;
console.log('diag answered', n, 'pred', E.predict().p, 'result battle lines', bl, 'weak', E.st.ob.res.weak.length);
if (!/作战卡/.test(rh) || bl < 1 || bl > 8 || !/第 1 天/.test(rh)) throw new Error('S6 result');
if (/正确率/.test(rh)) throw new Error('S6 shows accuracy');
A.obDone(); if (E.st.doneDay !== today()) throw new Error('day 1 not counted');
if (E.st.ob.step !== 'remind') throw new Error('S7 remind step missing'); render(); if (!/每天几点提醒你/.test($('#main').innerHTML) || !/跳过/.test($('#main').innerHTML)) throw new Error('S7 remind view');
$('#obRm').value = '21:30'; A.rmSave(); if (E.st.settings.remind !== '21:30' || E.st.ob.step !== 'done') throw new Error('remind save ' + E.st.settings.remind);
{ const fp = API.plan(5), b = fp.units.filter(u => u.b); if (!fp.first || fp.units.length - b.length !== 2 || b.length !== 1 || IT[b[0].ids[0]].p !== 7 || b[0].ids.length > 3) throw new Error('first-day plan ' + JSON.stringify(fp.units)); console.log('first-day plan', fp.units.map(u => u.b || u.ids[0]).join(' '), fp.estSec + 's'); }
{ const dd = E.st.doneDay; E.st.doneDay = ''; E.st.settings.remind = '00:00'; tab = 'today'; render(); if (!/rmtip/.test($('#main').innerHTML)) throw new Error('remind tip'); A.rmX(); if (/rmtip/.test($('#main').innerHTML)) throw new Error('remind tip dismiss'); E.st.doneDay = dd; }
for (const m of [5, 15]) { A.start(el({ m })); let k = 0, saw = 0;
  while (S) { const h = vQuiz(); if (!h.includes('class="opt')) throw new Error('no options'); if (bundle()) saw++;
    if (k === 2) { A.pause(); if (!E.st.run || $('#main').innerHTML.indexOf('继续') < 0) throw new Error('pause lost'); A.start(el({ m })); }
    answer(k % 4); if (S && S.fb) { vQuiz(); next(); } k++; }
  const res = vResult(); if (/正确率|\\d+\\s*\\/\\s*\\d+ 题/.test(res)) throw new Error('result shows counts');
  console.log('plan', m, 'answered', R.n, 'bundleViews', saw, 'pred', R.p0.p, '->', R.p1.p); A.closeR(); }
const b7 = D.bundles.find(b => b.p === 7 && b.docs.length > 1 && b.qs.every(q => IT[q]));
startSession('train', [{ b: b7.id, ids: b7.qs.slice() }]); let h = vQuiz(); console.log('multi P7', b7.id, b7.docs.map(d => d.t).join('+'), 'tabs', (h.match(/data-act="doc"/g) || []).length);
answer(0); vQuiz(); next(); while (S) { answer(1); if (S && S.fb) next(); } A.closeR();
const lk = API.lookup('invoices'); console.log('lookup', lk.w, lk.zh.slice(0, 10), 'dict', Object.keys(D.dict || {}).length, 'exp', Object.keys(D.exp || {}).length, 'gr', Object.keys(D.gr || {}).length);
const x = API.explain(D.items[0].id); if (!x.why && !x.basis) throw new Error('no explain');
E.st.cards[Object.keys(E.st.cards)[0]].due = 0; A.rev(); while (S) { answer(0); if (S && S.fb) next(); } A.closeR();
A.mock(); console.log('mock form', S.form); if (!S || S.mode !== 'mock') throw new Error('mock not started');
const mf = S.form; for (let i = 0; i < 40; i++) { vQuiz(); answer(i % 4); } finish(); console.log('mock scaled', R.scaled); A.closeR();
if (!E.st.used.includes(mf) || E.pool().some(i => i.f === mf)) throw new Error('used mock form still in pool');
for (const f of Object.keys(FORMS)) { const pl = E.mockPlan(f), n = pl.reduce((s, u) => s + u.ids.length, 0); if (n !== FORMS[f].length || n < FULL_MIN) throw new Error('mockPlan ' + f + ' ' + n); }
for (const t of ['today', 'review', 'progress', 'me']) { tab = t; render(); const h = $('#main').innerHTML; console.log('tab', t, h.length); if (/出了点问题/.test(h)) throw new Error('render error ' + t + ' ' + A._err); }
tab = 'progress'; render(); { const h = $('#main').innerHTML; if (/正确率|做了 \\d+ 题|\\d+\\s*\\/\\s*\\d+ 题/.test(h) || !/职级/.test(h) || !/绩效评估/.test(h)) throw new Error('progress page'); }
['apple', 'invoice', 'deadline', 'budget'].forEach(w => { E.addWord(w, 'x'); E.st.words[w].due = 0; }); Object.keys(E.st.cards).slice(0, 30).forEach(k => E.st.cards[k].due = 0);
{ const a = revAlloc(); console.log('review alloc items', a.ni, 'words', a.nw); if (a.ni + a.nw > 20) throw new Error('review > 20');
  A.rev(); let k = 0; while (WQ) { render(); A.wqA(el({ i: String(k % 2 ? WQ.q.a : -1) })); if (WQ && WQ.ans != null) A.wqN(); k++; } while (S) { answer(0); if (S && S.fb) next(); } A.closeR(); }
tab = 'me'; render(); if (!/mRm/.test($('#main').innerHTML)) throw new Error('me remind'); $('#mRm').value = '07:45'; A.rmSet(); if (E.st.settings.remind !== '07:45') throw new Error('me remind set'); A.rmOff(); if (E.st.settings.remind !== false) throw new Error('me remind off'); A.fz(el({ v: '1.25' })); A.tgl(el({ k: 'nostory' })); A.circ(); if ((E.st.settings || {}).circadian !== false) throw new Error('circadian off');
A._mtg = 800; $('#mLs').value = '420'; $('#mDate').value = '2027-01-10'; A.saveGoal(); if (E.st.rtg !== 380 || E.st.exam !== '2027-01-10' || E.band() !== '860+') throw new Error('saveGoal ' + E.st.rtg + ' ' + E.band());
$('#mLs').value = ''; $('#mDate').value = '2027-01-10'; A._mtg = 600; A.saveGoal(); A.dl();
E.addWord('Invoice', 'Please send the invoice.'); A.wg(el({ w: 'invoice', g: '2' })); A.unword(el({ w: 'invoice' })); if (E.st.words.invoice) throw new Error('unword');
A.newp(); $('#sName').value = 'B'; A.setupGo(el({ d: '0' })); E.st.diag = true; A.start(el({ m: 5 })); while (S) { answer(2); if (S && S.fb) next(); } A.closeR();
const code = Code.enc({ app: 'toeic-r-v2', name: 'B', st: E.st }); $('#codeBox').value = code; A.imp(); console.log('profiles', Profiles.list().length, 'code KB', (code.length/1024).toFixed(1));
tab = 'me'; A.clr1(); if (!/确定清空/.test($('#main').innerHTML)) throw new Error('clear confirm'); A.clr0(); A.clr1(); const nP = Profiles.list().length; A.clr2(); if (Profiles.list().length !== nP - 1) throw new Error('clear'); console.log('after clear', Profiles.list().length, 'log', E.st ? E.st.log.length : 0, 'storage', Store.kind);
console.log('SMOKE OK');
`;
vm.runInContext(scripts[1].replace(/boot\(\);\s*$/, 'boot();') + '\n' + test, Object.assign(ctx, { mk }));
