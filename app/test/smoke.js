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
const ctx = { window: {}, console, alert: m => console.log('[alert]', m), confirm: () => true, scrollTo() { }, setInterval: () => 1, clearInterval() { },
  btoa: s => Buffer.from(s, 'binary').toString('base64'), atob: s => Buffer.from(s, 'base64').toString('binary'), escape, unescape, encodeURIComponent, decodeURIComponent,
  navigator: { clipboard: { writeText: () => Promise.resolve() } }, URL: { createObjectURL: () => 'blob:' }, Blob: function () { },
  document: { querySelector: s => mk(s.replace('#', '')), querySelectorAll: () => [], addEventListener() { }, createElement: () => ({ click() { }, remove() { } }), body: { appendChild() { } }, execCommand() { } } };
ctx.window.localStorage = { getItem: k => (k in ls ? ls[k] : null), setItem: (k, v) => { ls[k] = String(v); }, removeItem: k => { delete ls[k]; } };
ctx.window.addEventListener = () => { }; ctx.addEventListener = () => { };
vm.createContext(ctx);
vm.runInContext(scripts[0], ctx);
const test = `
const el = (o) => ({ dataset: o || {} });
mk = null;
$('#sName').value = 'A'; $('#sDate').value = '2026-12-20';
A.setupGo(el({ d: '1' }));
let n = 0; while (S && S.mode === 'diag') { answer(Math.floor(Math.random() * 4)); n++; }
console.log('diag answered', n, 'result', R && R.p1.p, R && R.p1.lo, R && R.p1.hi, E.rank(R.p1.p));
vResult(); A.closeR();
for (const m of [5, 20]) { A.plan(el({ m })); let k = 0; while (S) { A.tool(el({t:'w'})); answer(k % 3); if (S && S.fb) { vQuiz(); next(); } k++; } console.log('plan', m, 'n', R.n, 'ok', R.ok, 'pred', R.p0.p, '->', R.p1.p); vResult(); A.closeR(); }
const wl = E.weakList(); console.log('weak top', wl.slice(0, 3).map(x => x.n.id + ':' + x.sc.toFixed(2)).join(' '));
A.weak(el({ n: wl[0].n.id })); while (S) { answer(1); if (S && S.fb) next(); } console.log('weak n', R.n); A.closeR();
E.st.cards[Object.keys(E.st.cards)[0]].due = 0; A.rev(); while (S) { answer(0); if (S && S.fb) next(); } A.closeR();
A.mock(); console.log('mock form', S.form, S.flat.length); if (!S || S.mode !== 'mock' || S.flat.length < FULL_MIN) throw new Error('mock not started / form too small');
const mf = S.form; for (let i = 0; i < 40; i++) { vQuiz(); answer(i % 4); } A.go(el({k:'90'})); vQuiz(); submitMock(); console.log('mock scaled', R.scaled, JSON.stringify(R.parts)); A.closeR();
if (!E.st.used.includes(mf) || E.pool().some(i => i.f === mf)) throw new Error('used mock form still in pool');
console.log('mock forms', Object.keys(FORMS).join(','), 'next', E.nextForm());
for (const f of Object.keys(FORMS)) { const pl = E.mockPlan(f), n = pl.reduce((s, u) => s + u.ids.length, 0); if (n !== FORMS[f].length || n < FULL_MIN) throw new Error('mockPlan ' + f + ' ' + n); }
for (const t of ['home', 'weak', 'review', 'graph', 'me']) { tab = t; render(); console.log('tab', t, $('#main').innerHTML.length); }
E.addWord('Invoice', 'Please send the invoice.'); E.st.words.invoice.due = 0; A.flash(); A.fg(el({ g: '2' }));
A.newp(); $('#sName').value = 'B'; A.setupGo(el({ d: '0' })); A.plan(el({ m: 5 })); while (S) { answer(2); if (S && S.fb) next(); } A.closeR();
tab = 'me'; render(); console.log('PK has rows', (vPK(Profiles.list()).match(/class="li"/g) || []).length);
const code = Code.enc({ app: 'toeic-r-v2', name: 'B', st: E.st }); $('#codeBox').value = code; A.imp(); console.log('profiles', Profiles.list().length, 'code KB', (code.length/1024).toFixed(1));
A.delp(el({ id: Profiles.cur() })); console.log('after delete', Profiles.list().length, 'log', E.st.log.length, 'storage', Store.kind);
console.log('SMOKE OK');
`;
vm.runInContext(scripts[1].replace(/boot\(\);\s*$/, 'boot();') + '\n' + test.replace('mk = null;', ''), Object.assign(ctx, { mk }));
