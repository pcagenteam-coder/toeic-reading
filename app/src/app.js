/* ===== 界面层 B2：4 入口 + 做题页（P5 审稿 / P6 改稿 / P7 收件箱）+ 10 秒结算 ===== */
const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s) || []);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const pick = a => a[Math.floor(Math.random() * a.length)];
const L4 = 'ABCD';
const wide = () => (typeof window !== 'undefined' && window.innerWidth >= 768);
const TXN = { 'TX.EMAIL': '邮件', 'TX.NOTICE': '通知', 'TX.ARTICLE': '报道', 'TX.MEMO': '备忘录', 'TX.TEXT_MSG': '短信', 'TX.WEB': '网页', 'TX.INVOICE': '单据',
  'TX.AD': '广告', 'TX.SCHEDULE': '日程', 'TX.LETTER': '信件', 'TX.INSTRUCTIONS': '说明', 'TX.CHAT': '群聊', 'TX.JOB_POSTING': '招聘', 'TX.REVIEW': '评价', 'TX.APP_FORM': '表格' };
const TXK = { 'TX.EMAIL': /e-?mail/i, 'TX.LETTER': /letter/i, 'TX.MEMO': /memo/i, 'TX.TEXT_MSG': /text/i, 'TX.CHAT': /chat|discussion/i, 'TX.NOTICE': /notice|announcement/i,
  'TX.ARTICLE': /article/i, 'TX.WEB': /web ?page|website/i, 'TX.INVOICE': /invoice|receipt|order/i, 'TX.AD': /advertisement/i, 'TX.SCHEDULE': /schedule|itinerary|agenda/i,
  'TX.REVIEW': /review/i, 'TX.APP_FORM': /form/i, 'TX.JOB_POSTING': /job|posting/i, 'TX.INSTRUCTIONS': /instructions/i };
const KIND = t => /EMAIL|LETTER|MEMO/.test(t) ? 'mail' : /TEXT_MSG|CHAT/.test(t) ? 'chat' : /NOTICE|AD|JOB_POSTING/.test(t) ? 'notice' : /ARTICLE|WEB|REVIEW/.test(t) ? 'article' : 'plain';
const SCENE = { 5: ['Ken 在群里 @你：帮我看下这几句～', 'Ken：这份稿子还差几句，麻烦了'], 6: ['Mia：这份草稿麻烦顺一下', 'Mia：帮我把空着的地方补上'], 7: ['Leo 转来一封客户邮件', 'Leo：收件箱里有几封要处理'] };
const SAY = ['Ken：“改得很干净，省了我不少事。”', 'Dana：“辛苦了，明天见。”', 'Mia：“这版可以发了。”', 'Leo：“客户那边回得很快，谢谢。”'];

let tab = 'today', S = null, R = null, setupNew = false, popW = null;
const ui = () => (E.st.ui = E.st.ui || {});
const save = () => { if (E.st) { E.st.run = S && !S.done ? S : null; Profiles.save(E.st); } };

function banner() {
  if (Store.kind !== 'memory') return;
  const b = $('#banner'); b.textContent = '当前环境不能自动保存，离开前请到「我的」复制进度码。'; b.classList.remove('hide');
}
Store.onFallback = banner;

function boot() {
  banner();
  if (!Profiles.cur()) { setupNew = true; return render(); }
  E.st = Profiles.load() || newState();
  S = E.st.run || null;
  if (S && S.day !== fxToday()) S = null;            // 任务保留到次日 4 点
  if (S) { S.paused = false; S.qt0 = Date.now(); }   // 断点续做：打开即回到原位置
  render();
}

/* ---------- 外壳 ---------- */
function render() {
  const inRun = !!(S && !S.done && !S.paused), m = $('#main');
  keepScroll();
  $('#app').classList.toggle('quiz', inRun);
  $$('#nav button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
  if (E.st) { const n = E.dueItems().length + E.dueWords().length; $('#revN').textContent = n ? String(n) : ''; }
  if (setupNew) m.innerHTML = wrap(vSetup());
  else if (inRun) m.innerHTML = vQuiz();
  else m.innerHTML = wrap(({ today: vToday, review: vReview, progress: vProgress, me: vMe })[tab]());
  modal(R ? vResult() : '');
  hidePop();
  restoreScroll();
}
const wrap = h => `<div class="wrap">${h}</div>`;
function modal(h) { $('#sheet').innerHTML = h; $('#modal').classList.toggle('hide', !h); }

/* ---------- 首日（简版，第 2 段做完整 S1–S6） ---------- */
function vSetup() {
  const t = (E.st && E.st.target) || 700;
  return `<div class="card"><h2>入职登记 · Halvorsen</h2><p class="mut">选目标和考试日期，做一次约 5 分钟的入职测试，系统按你的情况排每天的活。</p>
  <h3>怎么称呼你</h3><input id="sName" placeholder="例如：我" value="${esc(Profiles.list().length ? '' : '我')}">
  <h3>目标总分</h3><div class="row wrapr">${[600, 700, 800, 900].map(v => `<button class="chip ${v === t ? 'on' : ''}" data-act="tg" data-v="${v}">${v}</button>`).join('')}</div>
  <h3>考试日期（可不填）</h3><input id="sDate" type="date">
  <p></p><button class="btn full lg" data-act="setupGo" data-d="1">开始入职测试</button>
  ${Profiles.list().length ? '<p></p><button class="btn ghost full" data-act="setupCancel">取消</button>' : ''}</div>`;
}

/* ---------- 今天 ---------- */
function dayName() { const h = new Date().getHours(); return h < 12 ? '上午' : h < 18 ? '下午' : '傍晚'; }
function weekDays() { const d0 = Date.now() - 6 * 864e5; return Object.keys(E.st.days || {}).filter(d => new Date(d).getTime() >= d0 - 864e5).length; }
function planSummary(p) {
  const c = { 5: 0, 6: 0, 7: 0, r: 0 };
  p.units.forEach(u => { if (u.kind === 'review') c.r += u.ids.length; else if (u.b) c[IT[u.ids[0]].p]++; else c[5] += u.ids.length; });
  c.r += (p.words || []).length;
  return [c[7] && `${c[7]} 封邮件`, c[5] && `${c[5]} 句审稿`, c[6] && `${c[6]} 段改稿`, c.r && `复习 ${c.r} 个`].filter(Boolean).join(' · ') || '今天的活已经排好';
}
function vToday() {
  const d = new Date(), wd = '日一二三四五六'[d.getDay()], pr = E.predict();
  const top = `<div class="hd"><h1>今天 · ${d.getMonth() + 1}月${d.getDate()}日 周${wd}</h1><span class="mut sm">本周 ${weekDays()} 天</span></div>
  <p class="scene">«${dayName()} · Halvorsen 运营部»</p>`;
  if (!E.st.diag) return top + `<div class="card task"><h2>入职第一天</h2><p class="sum">先做一次入职测试（约 5 分钟），之后每天的活由系统来排。</p>
    <button class="btn full lg" data-act="diag">开始</button></div>`;
  const done = E.st.doneDay === today();
  const min = (E.st.settings && E.st.settings.daily_min) || 5;
  let main;
  if (S && S.paused) main = `<div class="card task"><h2>做到一半的活</h2><p class="sum">进度都在，接着上次的位置继续。</p><button class="btn full lg" data-act="start">继续</button></div>`;
  else if (done) main = `<div class="card task"><h2>今天的活干完了 ✓</h2><p class="sum">Dana：辛苦了，明天见。</p><button class="link" data-act="start" data-m="5">想再做 5 分钟</button></div>`;
  else {
    const p = API.plan(min);
    main = `<div class="card task"><h2>今天的活 · 约 ${Math.max(1, Math.round((p.estSec || min * 60) / 60))} 分钟</h2><p class="sum">${esc(planSummary(p))}</p>
      <button class="btn full lg" data-act="start" data-m="${min}">${S ? '继续' : '开始'}</button>
      <details><summary>今天时间多？ ˅</summary><div class="row wrapr"><button class="chip" data-act="start" data-m="15">多做 15 分钟</button>
      <button class="chip" data-act="mock">紧急项目（全真模考）</button></div></details></div>`;
  }
  const g = API.progress();
  const side = `<div class="card"><div class="mut sm">预测阅读分</div><div class="big">${pr.p}</div><div class="mut sm">（${pr.lo}–${pr.hi}）· 目标 ${pr.tg}</div>
    ${g.text ? `<p class="sm">${esc(g.text)}</p>` : ''}</div>`;
  return top + `<div class="grid2">${main}${side}</div>`;
}

/* ---------- 复习 / 进度 / 我的（简版占位，第 2 段完善） ---------- */
function vReview() {
  const it = E.dueItems(), ws = E.dueWords();
  const wl = ws.slice(0, 20).map(w => { const x = API.lookup(w); return `<div class="li"><span><b>${esc(w)}</b> <span class="mut sm">${esc(x.zh)}</span></span>
    <span class="row"><button class="chip" data-act="wg" data-w="${esc(w)}" data-g="2">认识</button><button class="chip" data-act="wg" data-w="${esc(w)}" data-g="0">不认识</button></span></div>`; }).join('');
  return `<div class="hd"><h1>复习</h1></div><div class="card"><h2>题目</h2><p class="mut">${it.length ? `今天有 ${it.length} 道题该回头看看。` : '今天没有要复习的题。'}</p>
    ${it.length ? '<button class="btn full" data-act="rev">开始复习</button>' : ''}</div>
    <div class="card"><h2>生词</h2>${wl || '<p class="mut">做题时点生词，会自动加进来。</p>'}</div>`;
}
function vProgress() {
  const g = API.progress(), pr = E.predict();
  const nx = (g.next || []).map(n => `<div class="li"><span>${esc(n.nm)}</span><span class="mut sm">接下来练</span></div>`).join('');
  return `<div class="hd"><h1>进度</h1></div><div class="card"><div class="mut sm">离目标</div>
    <div class="big">${g.remainingNodes != null ? `还差 ${g.remainingNodes} 个考点` : '—'}</div>
    <p class="mut">${g.remainingHours != null ? `约 ${g.remainingHours} 小时 · ` : ''}预测阅读分 ${pr.p}（${pr.lo}–${pr.hi}）</p></div>
    ${nx ? `<div class="card"><h2>接下来</h2>${nx}</div>` : ''}`;
}
function vMe() {
  const u = ui(), L = Profiles.list();
  return `<div class="hd"><h1>我的</h1><span class="mut sm">${esc(Profiles.name())} · 目标 ${E.st.target}</span></div>
  <div class="card"><h2>做题</h2>
    <div class="li"><span>用时环</span><button class="chip ${u.hideRing ? '' : 'on'}" data-act="set" data-k="hideRing">${u.hideRing ? '已隐藏' : '显示'}</button></div>
    <div class="li"><span>简洁外壳（不显示同事和剧情）</span><button class="chip ${u.plain ? 'on' : ''}" data-act="set" data-k="plain">${u.plain ? '已开' : '关'}</button></div>
    <div class="li"><span>每天时长</span><span class="row">${[5, 10, 15].map(m => `<button class="chip ${((E.st.settings || {}).daily_min || 5) === m ? 'on' : ''}" data-act="dm" data-m="${m}">${m} 分钟</button>`).join('')}</span></div></div>
  <div class="card"><h2>档案与进度码</h2>${L.map(p => `<div class="li"><span>${esc(p.name)}${p.id === Profiles.cur() ? ' ✓' : ''}</span>
    <span class="row">${p.id === Profiles.cur() ? '' : `<button class="chip" data-act="usep" data-id="${p.id}">切换</button>`}<button class="chip" data-act="delp" data-id="${p.id}">删除</button></span></div>`).join('')}
    <p></p><div class="row wrapr"><button class="btn ghost" data-act="newp">新档案</button><button class="btn ghost" data-act="exp">复制进度码</button></div>
    <p></p><input id="codeBox" placeholder="粘贴进度码导入"><p></p><button class="btn ghost full" data-act="imp">导入</button></div>`;
}

/* ---------- 会话 ---------- */
function startSession(mode, units, extra) {
  if (!units || !units.length) { alert('没有可用的题目了'); return; }
  const nd0 = {}; units.forEach(u => u.ids.forEach(id => { const i = IT[id]; nd0[i.n] = E.mastery(i.n); }));
  const g = API.progress();
  S = Object.assign({ mode, units, ui: 0, qi: 0, ans: {}, lu: {}, mt: {}, t0: Date.now(), qt0: Date.now(), day: fxToday(), pred0: E.predict(), nd0,
    rem0: g.remainingNodes, fb: null, v: 'q', doc: 0, sc: {}, ppn: 0, tipN: 0 }, extra || {});
  if (mode === 'mock') { S.end = Date.now() + 75 * 6e4; S.v = 'a'; }
  E.log('start', { mode, n: units.reduce((s, u) => s + u.ids.length, 0), form: S.form });
  save(); render();
}
const unit = () => S.units[S.ui];
const curId = () => unit().ids[S.qi];
const bundle = () => unit().b ? BU[unit().b] : null;
function spent(id) { return (S.mt[id] || 0) + (S.ans[id] ? 0 : Date.now() - S.qt0); }
function leaveQ() { const id = curId(); if (!S.ans[id]) S.mt[id] = (S.mt[id] || 0) + (Date.now() - S.qt0); S.qt0 = Date.now(); }
function goQ(i) { if (i < 0 || i >= unit().ids.length || i === S.qi) return; leaveQ(); S.qi = i; S.fb = S.ans[curId()] ? 'old' : null; save(); render(); }

function answer(c) {
  const id = curId(), it = IT[id];
  if (S.ans[id]) return;
  const ms = spent(id), a = { c, ms, lu: S.lu[id] ? 1 : 0 }; S.ans[id] = a; S.mt[id] = ms;
  const r = API.record({ item_id: id, choice: c, ms, lookups: S.lu[id] || 0, mode: S.mode === 'diag' ? 'diag' : S.mode });
  a.ok = r ? !!r.correct : c === it.a;
  if (S.mode === 'mock' || S.mode === 'diag') { S.fb = null; return next(); }
  S.fb = a.ok && ms <= it.t * 1000 ? 'fast' : 'full';
  save(); render();
  if (S.fb === 'fast') { const k = id; setTimeout(() => { if (S && S.fb === 'fast' && curId() === k) next(); }, 800); }
}
function next() {
  if (!S) return;
  leaveQ(); S.fb = null;
  const ids = unit().ids, n = ids.length;
  for (let k = 1; k <= n; k++) { const j = (S.qi + k) % n; if (!S.ans[ids[j]]) { S.qi = j; S.qt0 = Date.now(); save(); return render(); } }
  S.ui++; S.qi = 0; S.doc = 0; S.sc = {}; S.v = S.mode === 'mock' ? 'a' : 'q';
  if (S.ui >= S.units.length) return finish();
  S.qt0 = Date.now(); save(); render();
}
function finish() {
  if (S.mode === 'mock') {   // 没答的按未作答记
    S.units.forEach(u => u.ids.forEach(id => { if (!S.ans[id]) { S.ans[id] = { c: -1, ms: 0 }; API.record({ item_id: id, choice: -1, ms: 0, mode: 'mock' }); } }));
    if (S.form && !E.st.used.includes(S.form)) E.st.used.push(S.form);
  }
  const ids = Object.keys(S.ans), ok = ids.filter(id => S.ans[id].c === IT[id].a).length;
  const ms = Date.now() - S.t0, p1 = E.predict(), g = API.progress();
  const nodes = Object.keys(S.nd0).map(n => ({ n, a: S.nd0[n], b: E.mastery(n) })).filter(x => x.b != null).map(x => Object.assign(x, { d: x.b - (x.a == null ? 0.5 : x.a) }));
  const p5 = ids.filter(id => IT[id].p === 5 && S.ans[id].ms), p5s = p5.reduce((s, id) => s + S.ans[id].ms, 0) / Math.max(1, p5.length) / 1000, p5t = p5.reduce((s, id) => s + IT[id].t, 0) / Math.max(1, p5.length);
  R = { mode: S.mode, n: ids.length, ok, ms, p0: S.pred0, p1, nodes, rem0: S.rem0, rem1: g.remainingNodes, hrs: g.remainingHours, p5: p5.length ? [Math.round(p5s), Math.round(p5t)] : null, form: S.form };
  if (S.mode === 'mock') { R.scaled = Math.round(E.scaled(ok / Math.max(1, ids.length) * 100) / 5) * 5; E.st.mocks.push({ ts: Date.now(), form: S.form, ok, n: ids.length, scaled: R.scaled, ms }); }
  if (S.mode === 'diag') E.st.diag = true;
  if (S.mode === 'train' || S.mode === 'diag') E.st.doneDay = today();
  E.st.hist.push([Date.now(), p1.p]);
  E.log('end', { mode: S.mode, n: ids.length, ok, ms });
  S.done = true; S = null; tab = 'today'; save(); render();
}
/* 10 秒结算：写 2–3 条具体进步，不显示题数和正确率 */
function vResult() {
  const r = R, ls = [];
  if (r.mode === 'mock') ls.push(`紧急项目交付：预估阅读 ${r.scaled} 分`);
  r.nodes.filter(x => x.d > 0.02).sort((a, b) => b.d - a.d).slice(0, 2).forEach(x => ls.push(`${esc((ND[x.n] || {}).nm || x.n)}：又稳了一点`));
  if (r.p5 && r.p5[0] <= r.p5[1]) ls.push(`审稿 ${r.p5[0]} 秒/句（目标 ${r.p5[1]}）`);
  if (r.rem1 != null) ls.push(`离目标还差 ${r.rem1} 个考点${r.rem0 != null && r.rem0 > r.rem1 ? `（−${r.rem0 - r.rem1}）` : ''}${r.hrs != null ? ` · 约 ${r.hrs} 小时` : ''}`);
  if (ls.length < 2 && !r.nodes.some(x => x.d > 0.02)) ls.unshift('碰到几个新考点，已经记下，明天换更顺手的题。');
  const t = Math.round(r.ms / 1000), title = r.mode === 'diag' ? '入职测试做完了 ✓' : `${dayName()}的活干完了 ✓`;
  return `<div class="res"><div class="hd"><h1>${title}</h1><span class="mut sm">用时 ${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}</span></div>
  <ul>${ls.slice(0, 3).map(x => `<li>${x}</li>`).join('')}</ul>
  <p>预测阅读分 <b>${r.p1.p}</b> <span class="mut">（${r.p1.lo}–${r.p1.hi}）</span></p>
  ${ui().plain ? '' : `<p class="say">${pick(SAY)}</p>`}
  <button class="btn full lg" data-act="closeR">完成</button><p></p><button class="link" data-act="more">再来 5 分钟</button></div>`;
}

/* ---------- 文本渲染 ---------- */
const MK = ['\u0001', '\u0002', '\u0003'];
function markIn(x, phrase, k) {   // 在原文里给短语加哨兵（大小写/弯引号不敏感），找不到返回 null
  if (!phrase) return null;
  const norm = s => s.replace(/[’‘]/g, "'").replace(/[“”]/g, '"').toLowerCase();
  const i = norm(x).indexOf(norm(phrase)); if (i < 0) return null;
  return x.slice(0, i) + MK[0] + k + MK[1] + x.slice(i, i + phrase.length) + MK[2] + x.slice(i + phrase.length);
}
function rich(t, o) {   // 转义 → 词可点 → 哨兵/空位/插入点
  o = o || {};
  let h = esc(t).replace(/[A-Za-z][A-Za-z'’-]*/g, w => `<span class="w">${w}</span>`);
  h = h.replace(/\u0001(\d)\u0002/g, (m, k) => o.mk ? o.mk(k) : '').replace(/\u0003/g, o.mkEnd || '</mark>');
  if (o.blank) h = h.replace(/\{\{(\d+)\}\}/g, (m, q) => o.blank(+q));
  if (o.ins) h = h.replace(/\[([1-4])\]/g, (m, n) => `<span class="ins" id="ins${n}">[${n}]</span>`);
  return h;
}
function paras(x) { return x.split(/\n\s*\n/).map(p => p.replace(/^\n+|\n+$/g, '')).filter(p => p.trim()); }
const GENERIC = /^(article|e-?mail|notice|memo|letter|web ?page|advertisement|text[- ]message chain|online chat discussion|schedule|invoice|review|form|instructions|job posting)$/i;
const CHAT_RE = /^(.{1,48}?)\s*[\[(](\d{1,2}[:.]\d{2}\s*(?:[AaPp]\.?\s?[Mm]\.?)?)[\])]\s*:?\s*(.*)$/;
function docHTML(d, di, o) {
  const k = KIND(d.t), hdr = d.h || '', x = o.x != null ? o.x : d.x;
  let head = '';
  if (/^(To|From|Date|Subject|Re|Sent|Cc)\s*:/im.test(hdr)) {
    head = `<div class="mh">${hdr.split('\n').filter(l => l.trim()).map(l => { const m = l.match(/^([A-Za-z]+)\s*:\s*(.*)$/); return m ? `<b>${esc(m[1])}</b><span>${rich(m[2], o)}</span>` : `<b></b><span>${rich(l, o)}</span>`; }).join('')}</div>`;
  } else if (GENERIC.test(hdr.trim())) head = `<div class="mut sm" style="margin:0 0 8px">${esc(hdr.trim())}</div>`;
  else if (hdr.trim()) head = `<div class="ttl">${rich(hdr, o)}</div>`;
  let body = '', pn = 0;
  if (k === 'chat') {
    let who0 = null, cur = null; const out = [];
    x.split('\n').forEach(l => {
      const m = l.match(CHAT_RE);
      if (m && /[A-Za-z]/.test(m[1])) { who0 = who0 || m[1]; cur = { who: m[1], t: m[2], x: [m[3]].filter(Boolean) }; out.push(cur); }
      else if (l.trim()) { if (cur) cur.x.push(l); else out.push({ who: '', t: '', x: [l] }); }
    });
    body = out.map(m => m.who ? `<div class="msg ${m.who === who0 ? '' : 'me'}"><div class="who">${esc(m.who)} · ${esc(m.t)}</div><div class="bb">${rich(m.x.join('\n'), o).replace(/\n/g, '<br>')}</div></div>`
      : `<p>${rich(m.x.join(' '), o)}</p>`).join('');
  } else {
    body = paras(x).map(p => {
      const ls = p.split('\n');
      if (ls.filter(l => l.includes('|')).length >= 2) return `<table class="tb">${ls.map((l, i) => `<tr>${l.split('|').map(c => i ? `<td>${rich(c.trim(), o)}</td>` : `<th>${rich(c.trim(), o)}</th>`).join('')}</tr>`).join('')}</table>`;
      pn++; return `<p class="p" id="p${di}-${pn}">${rich(p, o).replace(/\n/g, '<br>')}</p>`;
    }).join('');
  }
  return `<div class="doc ${k}">${head}${body}</div>`;
}
/* 题干里的引用：引号短语 / 第 N 段 / 插入句 [1]–[4] / 点名的文本类型 */
function refsOf(it, b) {
  const s = it.s || '', r = {};
  const q = s.match(/["“]([^"”]{2,90})["”]/); if (q) r.q = q[1].replace(/[,.]$/, '');
  const p = s.match(/paragraph (\d+)/i); if (p) r.para = +p[1];
  if (/\[1\]/.test(s)) r.ins = 1;
  if (b) {
    let di = -1;
    if (r.q) di = b.docs.findIndex(d => markIn(d.x, r.q, 0));
    if (di < 0) { const ord = /second|2nd/i.test(s) ? 1 : /third/i.test(s) ? 2 : /first/i.test(s) ? 0 : -1; const hits = b.docs.map((d, i) => TXK[d.t] && TXK[d.t].test(s) ? i : -1).filter(i => i >= 0); if (hits.length) di = ord >= 0 && hits.length > 1 ? hits[Math.min(ord, hits.length - 1)] : hits[0]; }
    r.doc = di;
  }
  return r;
}
function basisPhrase(id) {
  const x = API.explain(id); let b = (x.basis || '').split('——')[0].replace(/^["“]|["”]$/g, '').trim();
  return b && !/___/.test(b) && b.length > 6 ? b : '';
}

/* ---------- 做题页 ---------- */
function ringSvg(id) {
  if (ui().hideRing && S.mode !== 'mock') return '';
  return `<svg class="ring" viewBox="0 0 36 36"><circle class="bg" cx="18" cy="18" r="15"/><circle id="ringFg" class="fg" cx="18" cy="18" r="15" stroke-dasharray="94.25" stroke-dashoffset="94.25" transform="rotate(-90 18 18)"/></svg>`;
}
function vQuiz() {
  const u = unit(), id = curId(), it = IT[id], b = bundle(), part = it.p;
  const lab = S.mode === 'mock' ? '紧急项目' : S.mode === 'diag' ? '入职测试' : part === 5 ? '审稿' : part === 6 ? '改稿' : '收件箱';
  const sub = part === 7 && b ? (b.docs.length > 1 ? `Part 7 ${b.docs.length === 2 ? '双篇' : '三篇'}` : 'Part 7 单篇') : 'Part ' + part;
  const tot = S.units.length, dots = tot <= 12 ? `<div class="dots">${S.units.map((x, i) => `<i class="${i < S.ui ? 'd' : i === S.ui ? 'c' : ''}"></i>`).join('')}</div>` : `<span class="mut sm">${S.ui + 1}/${tot}</span>`;
  const sc = SCENE[part], story = !ui().plain && S.mode !== 'mock' && !S.noStory ? `<div class="story"><span>«${esc(sc[S.ui % 2])}»</span><button data-act="nostory" aria-label="关闭">✕</button></div>` : '';
  const head = `<div class="qh"><button class="x" data-act="pause" aria-label="暂停">✕</button><div class="tt">${lab}<small>${sub}</small></div>${dots}${ringSvg(id)}<button class="mm" data-act="menu" aria-label="更多">⋯</button></div>${story}`;
  if (!b) return `<div class="qz">${head}<div class="qb pane" id="pq">${vP5(it, id)}</div></div>`;
  const multi = b.docs.length > 1, refs = refsOf(it, b), di = S.docPinned != null ? S.doc : (refs.doc >= 0 && !S.ans[id] ? refs.doc : S.doc);
  S.doc = Math.min(di, b.docs.length - 1);
  const seg = `<div class="seg"><button class="${S.v === 'a' ? 'on' : ''}" data-act="view" data-v="a">文章</button><button class="${S.v === 'q' ? 'on' : ''}" data-act="view" data-v="q">题目 ${S.qi + 1}/${u.ids.length}</button></div>`;
  return `<div class="qz">${head}${seg}<div class="qb"><div class="split" id="split" data-v="${S.v}" style="--sp:${ui().split || 55}%">
    <div class="pane pa" id="pa">${vPassage(b, it, id, refs, multi)}</div><div class="dv" id="dv" title="拖动调整，双击复位"></div>
    <div class="pane pq" id="pq">${vQs(b, u, it, id, refs)}</div></div></div><button class="fab" data-act="flip" aria-label="切换">⇄</button></div>`;
}
function vP5(it, id) {
  const a = S.ans[id], s = (it.s || '').replace(/-{3,}|_{3,}|\(\s*\)/, '\u0004');
  const doc = rich(s).replace('\u0004', `<span class="gap">${a ? esc(it.o[a.c] || '') : '&nbsp;'}</span>`);
  const who = ui().plain ? '选择' : '批注 · Ken：这里用哪个？';
  return `<div class="p5"><div class="paper"><div class="lab">文档 · 第 ${it.q} 句</div>${doc}</div>
    <div class="anno"><div class="ah">${who}</div>${vOpts(it, id)}${vFb(it, id)}</div></div>`;
}
function vPassage(b, it, id, refs, multi) {
  const done = !!S.ans[id], bp = done && S.mode !== 'mock' ? basisPhrase(id) : '';
  const tabs = multi ? `<div class="dtabs">${b.docs.map((d, i) => `<button class="${i === S.doc ? 'on' : ''}" data-act="doc" data-i="${i}">${TXN[d.t] || '文本'} ${i + 1}/${b.docs.length}${i === refs.doc ? '<b>•</b>' : ''}</button>`).join('')}</div>` : '';
  const qs = new Set(bundleIds(b)), cur = it.q;
  const blank = q => {
    const qid = b.qs.find(x => IT[x] && IT[x].q === q), a = qid && S.ans[qid];
    if (a && a.c >= 0) return `<span class="blank done" data-act="goq" data-q="${q}">${esc(IT[qid].o[a.c])}</span>`;
    return `<span class="blank ${q === cur ? 'cur' : ''}" data-act="goq" data-q="${q}">${q}${q === cur ? ' 当前' : ''}</span>`;
  };
  const show = multi && wide() && ui().sideBySide && typeof window !== 'undefined' && window.innerWidth >= 1440 ? b.docs.map((d, i) => i) : [S.doc];
  return tabs + show.map(i => {
    const d = b.docs[i]; let x = d.x;
    if (refs.q && !done) x = markIn(x, refs.q, '1') || x;
    if (bp) x = markIn(x, bp, '2') || x;
    return docHTML(d, i, { x, blank: b.p === 6 && qs.size ? blank : null, ins: b.p === 7,
      mk: k => k === '1' ? '<mark class="ref" id="mref">' : '<mark class="basis" id="mbasis">' });
  }).join('');
}
function bundleIds(b) { return b.qs.filter(q => IT[q]); }
function vQs(b, u, it, id, refs) {
  const nav = u.ids.length > 1 ? `<div class="qnav">${u.ids.map((q, i) => `<button class="${i === S.qi ? 'on' : ''} ${S.ans[q] ? 'd' : ''}" data-act="goi" data-i="${i}">${IT[q].q}${S.ans[q] ? ' ✓' : ''}</button>`).join('')}</div>` : '';
  let stem;
  if (b.p === 6) stem = `<p class="stem"><b>第 ${it.q} 空</b>${it.s ? '：' + rich(it.s) : '：选最合适的一项'} <a class="ref" data-act="jump" data-to="blank">看原文</a></p>`;
  else {
    let s = it.s; if (refs.q) s = markIn(s, refs.q, '3') || s;
    stem = `<p class="stem"><b>${it.q}.</b> ${rich(s, { mk: () => '<a class="ref" data-act="jump" data-to="ref">', mkEnd: '</a>' })}`;
    if (!refs.q && refs.para) stem += ` <a class="ref" data-act="jump" data-to="para">第 ${refs.para} 段</a>`;
    if (!refs.q && refs.ins) stem += ' <a class="ref" data-act="jump" data-to="ins">看 [1]–[4]</a>';
    if (!refs.q && !refs.para && !refs.ins && refs.doc >= 0 && b.docs.length > 1) stem += ` <a class="ref" data-act="jump" data-to="doc">看${TXN[b.docs[refs.doc].t] || '原文'}</a>`;
    stem += '</p>';
  }
  return nav + stem + vOpts(it, id) + vFb(it, id);
}
function vOpts(it, id) {
  const a = S.ans[id], show = a && S.mode !== 'mock';
  return `<div class="opts">${it.o.map((o, i) => {
    const cls = show ? (i === it.a ? 'ok' : i === a.c ? 'no' : '') : (a && a.c === i ? 'ok' : '');
    return `<button class="opt ${cls}" data-act="ans" data-c="${i}" ${a ? 'disabled' : ''}><b>${L4[i]}</b><span>${esc(o)}</span><span class="k">${i + 1}</span></button>`;
  }).join('')}</div>`;
}
function vFb(it, id) {
  const a = S.ans[id]; if (!a || S.mode === 'mock') return '';
  const sec = Math.round(a.ms / 1000);
  if (S.fb === 'fast') return `<p class="fast">✓ 对 · ${sec} 秒（目标 ${it.t}）</p>`;
  const x = API.explain(id), wrong = a.c !== it.a, mine = wrong && a.c >= 0 ? x.dis[L4[a.c]] : '';
  const L = API.lesson(it.n), nm = (ND[it.n] || {}).nm || '';
  const saved = (E.st.tips || []).some(t => t.id === id);
  const tip = wrong && x.tip ? `<div class="tip"><span><b>记一招</b> ${esc(x.tip)}</span><button class="chip ${saved ? 'on' : ''}" data-act="tip">${saved ? '已记下' : '记下☆'}</button></div>` : '';
  let pp = '';
  if (it.p === 7 && x.pp.length && (S.ppShown === id || S.ppn < 2)) { if (S.ppShown !== id) { S.ppn++; S.ppShown = id; } const p = x.pp[0];
    pp = `<div class="pp">${ui().plain ? '' : 'Leo 的备忘：'}这两个说法是一回事<br>原文 <b>${esc(p[0])}</b> ↔ 选项 <b>${esc(p[1])}</b></div>`; }
  const bj = it.p === 7 && basisPhrase(id) ? ` <a class="ref" data-act="jump" data-to="basis">在原文里看</a>` : '';
  return `<div class="fb"><div class="ans">${wrong ? '正确答案' : '答对了'} (${L4[it.a]}) ${esc(it.o[it.a])}</div><div class="mut sm">${sec} 秒 · 目标 ${it.t} 秒</div>
    <dl>${x.basis ? `<dt>依据</dt><dd>${esc(x.basis)}${bj}</dd>` : ''}${x.why ? `<dt>为什么</dt><dd>${esc(x.why)}</dd>` : ''}${mine ? `<dt>你选的</dt><dd>(${L4[a.c]}) ${esc(mine)}</dd>` : ''}</dl>
    ${tip}${pp}${nm ? `<p class="mut sm">考点：${esc(nm)}</p>` : ''}
    <div class="nextbar">${L && wrong ? `<button class="btn ghost" data-act="lesson">60 秒小讲解</button>` : ''}<button class="btn" style="flex:1" data-act="next">下一题</button></div></div>`;
}
function vLesson(L) {
  return `<h2>${esc(L.nm)}</h2><p class="mut sm">${ui().plain ? '' : 'Dana 带你看 · '}约 60 秒</p><p>${esc(L.r)}</p>
  ${L.ex.map(e => `<div class="pp"><div>${esc(e[0])}</div><div class="mut">${esc(e[1])}</div></div>`).join('')}
  ${L.sg ? `<p><b>信号</b> ${esc(L.sg)}</p>` : ''}${L.tr ? `<p><b>常见坑</b> ${esc(L.tr)}</p>` : ''}<button class="btn full" data-act="closeM">知道了</button>`;
}

/* ---------- 滚动记忆 / 跳转 ---------- */
function keepScroll() {
  if (!S || S.done || S.paused) return;
  ['pa', 'pq'].forEach(k => { const e = $('#' + k); if (e && e.clientHeight) S.sc[k] = e.scrollTop; });
}
function restoreScroll() {
  if (!S || S.done || S.paused) return;
  ['pa', 'pq'].forEach(k => { const e = $('#' + k); if (e && S.sc && S.sc[k] != null) e.scrollTop = S.sc[k]; });
  if (S.jumpTo) { const j = S.jumpTo; S.jumpTo = null; doJump(j); }
}
function doJump(sel) {
  const el = $(sel), pa = $('#pa'); if (!el || !pa || !el.getBoundingClientRect) return;
  const r = el.getBoundingClientRect(), pr = pa.getBoundingClientRect();
  pa.scrollTop += r.top - pr.top - pa.clientHeight / 3;
  el.classList.remove('on'); void el.offsetWidth; el.classList.add('on');
}

/* ---------- 查词浮层：手机按点词位置在底/顶弹出，PC 气泡限在本栏 ---------- */
function hidePop() { const p = $('#pop'); if (p && p.classList) p.classList.add('hide'); popW = null; }
function lookupWord(el) {
  const raw = el.textContent, x = API.lookup(raw), sent = (el.parentNode && el.parentNode.textContent || '').slice(0, 160);
  if (E.st && !(E.st.words || {})[x.w]) E.addWord(x.w, sent);
  if (S && !S.done && !S.paused) { const id = curId(); S.lu[id] = (S.lu[id] || 0) + 1; }
  save(); popW = x.w;
  $$('.w.lk').forEach(e => e.classList.remove('lk')); el.classList.add('lk');
  const p = $('#pop');
  p.innerHTML = `<div class="hw">${esc(x.w)} <span class="mut sm">${esc(x.pos)}</span></div><div>${esc(x.zh || '（词典暂无释义）')}</div>
    <div class="hi">${x.hi ? '★ 托业高频 · ' : ''}已加入生词本 <button class="link" data-act="unword" data-w="${esc(x.w)}">移除</button></div>`;
  p.className = 'pop'; p.style.cssText = '';
  const r = el.getBoundingClientRect(), pane = el.closest('.pane') || $('#main'), pr = pane.getBoundingClientRect();
  if (!wide()) {
    const inQ = !!el.closest('#pq') || !el.closest('#pa');
    p.classList.add(inQ && !!el.closest('.stem, .paper') ? 'top' : 'bottom');
    if (p.classList.contains('top') && el.closest('.paper')) { p.classList.remove('top'); p.classList.add('bottom'); }
    requestAnimationFrame(() => {   // 被点词保持可见：弹层盖住就把栏往上滚
      const ph = p.offsetHeight, wr = el.getBoundingClientRect();
      if (p.classList.contains('bottom') && wr.bottom > innerHeight - ph - 8) pane.scrollTop += wr.bottom - (innerHeight - ph - 16);
      if (p.classList.contains('top') && wr.top < ph + 8) pane.scrollTop -= ph + 16 - wr.top;
    });
  } else {
    p.classList.add('bubble');
    const w = 300, left = Math.max(pr.left + 8, Math.min(r.left, pr.right - w - 8));
    p.style.left = left + 'px'; p.style.top = (r.bottom + 6) + 'px';
    requestAnimationFrame(() => {   // 盖住选项或出屏 → 翻到词上方
      const hit = () => { const q = p.getBoundingClientRect(); return $$('.opt').some(o => { const x = o.getBoundingClientRect(); return !(x.bottom <= q.top || x.top >= q.bottom || x.right <= q.left || x.left >= q.right); }); };
      if (r.bottom + 6 + p.offsetHeight > innerHeight - 8 || hit()) p.style.top = Math.max(8, r.top - p.offsetHeight - 6) + 'px';
    });
  }
}

/* ---------- 计时环 ---------- */
function tick() {
  if (!S || S.done || S.paused) return;
  const f = $('#ringFg'); if (!f || !f.setAttribute) return;
  if (S.mode === 'mock') { const left = Math.max(0, S.end - Date.now()); f.setAttribute('stroke-dashoffset', String(94.25 * left / 4.5e6)); if (!left) finish(); return; }
  const id = curId(), it = IT[id]; if (!it || S.ans[id]) return;
  f.setAttribute('stroke-dashoffset', String(94.25 * (1 - Math.min(1, spent(id) / (it.t * 1000)))));
}

/* ---------- 动作 ---------- */
const A = {
  tg(el) { $$('[data-act=tg]').forEach(b => b.classList.toggle('on', b === el)); A._tg = +el.dataset.v; },
  setupGo(el) {
    const nm = ($('#sName').value || '').trim() || '我', dt = $('#sDate').value || '';
    Profiles.create(nm); E.st = newState(A._tg || 700, dt); setupNew = false; Profiles.save(E.st);
    if (el && el.dataset.d === '1') A.diag(); else render();
  },
  setupCancel() { setupNew = false; render(); },
  diag() { startSession('diag', E.diagPlan()); },
  start(el) {
    if (S) { S.paused = false; S.qt0 = Date.now(); save(); return render(); }
    const m = +(el && el.dataset.m) || 5, p = API.plan(m);
    if (p.words && p.words.length) E.log('plan_words', { n: p.words.length });
    startSession('train', p.units);
  },
  more() { R = null; A.start({ dataset: { m: 5 } }); },
  mock() { const f = E.nextForm(); if (!f) return alert('整套题都做过了'); startSession('mock', E.mockPlan(f), { form: f }); },
  rev() { startSession('review', E.reviewUnits(20)); },
  ans(el) { answer(+el.dataset.c); },
  next() { next(); },
  pause() { leaveQ(); S.paused = true; tab = 'today'; save(); render(); },
  closeR() { R = null; render(); },
  closeM() { modal(R ? vResult() : ''); },
  nostory() { S.noStory = true; save(); render(); },
  view(el) { S.v = el.dataset.v; save(); render(); },
  flip() { S.v = S.v === 'a' ? 'q' : 'a'; save(); render(); },
  doc(el) { S.doc = +el.dataset.i; S.docPinned = 1; S.sc.pa = 0; save(); render(); },
  goi(el) { S.docPinned = null; goQ(+el.dataset.i); },
  goq(el) { const q = +el.dataset.q, i = unit().ids.findIndex(x => IT[x].q === q); if (i >= 0) { goQ(i); if (!wide()) { S.v = 'q'; render(); } } },
  jump(el) {
    const to = el.dataset.to, it = IT[curId()], refs = refsOf(it, bundle());
    if (refs.doc >= 0 && to !== 'blank') S.doc = refs.doc;
    if (to === 'basis') { const bp = basisPhrase(curId()); const di = bundle().docs.findIndex(d => markIn(d.x, bp, 0)); if (di >= 0) S.doc = di; }
    S.v = 'a'; S.docPinned = 1;
    S.jumpTo = to === 'ref' ? '#mref' : to === 'basis' ? '#mbasis' : to === 'para' ? `#p${S.doc}-${refs.para}` : to === 'ins' ? '#ins1' : to === 'blank' ? '.blank.cur' : null;
    save(); render();
  },
  tip() { const id = curId(), x = API.explain(id); E.st.tips = E.st.tips || []; if (!E.st.tips.some(t => t.id === id)) { E.st.tips.push({ id, t: x.tip, ts: Date.now() }); E.log('tip_save', { id }); } save(); render(); },
  lesson() { const L = API.lesson(IT[curId()].n); if (L) { E.log('lesson_open', { node: L.node }); modal(vLesson(L)); } },
  unword(el) { const w = el.dataset.w; delete E.st.words[w]; E.log('word_remove', { lemma: w }); save(); hidePop(); },
  menu() {
    const u = ui();
    modal(`<h2>设置</h2><div class="li"><span>用时环</span><button class="chip" data-act="set" data-k="hideRing">${u.hideRing ? '显示' : '隐藏'}</button></div>
      <div class="li"><span>简洁外壳</span><button class="chip" data-act="set" data-k="plain">${u.plain ? '关' : '开'}</button></div>
      ${typeof window !== 'undefined' && window.innerWidth >= 1440 ? `<div class="li"><span>多篇并排看</span><button class="chip" data-act="set" data-k="sideBySide">${u.sideBySide ? '关' : '开'}</button></div>` : ''}
      <p class="mut sm">快捷键：A–D / 1–4 选，Enter 下一题，← → 换题，G 跳到引用，Space 切文章/题目，Alt+← → 调中缝</p><button class="btn full" data-act="closeM">好</button>`);
  },
  set(el) { const k = el.dataset.k; ui()[k] = !ui()[k]; save(); render(); },
  dm(el) { E.setSetting('daily_min', +el.dataset.m); save(); render(); },
  wg(el) { E.scheduleWord(el.dataset.w, +el.dataset.g); E.log('wordrev', { w: el.dataset.w, g: +el.dataset.g, tz: -new Date().getTimezoneOffset() }); save(); render(); },
  newp() { save(); setupNew = true; render(); },
  usep(el) { save(); Profiles.use(el.dataset.id); boot(); },
  delp(el) { if (!confirm('删除这个档案？')) return; Profiles.remove(el.dataset.id); if (!Profiles.cur()) { E.st = null; setupNew = true; return render(); } boot(); },
  exp() { const c = Code.enc({ app: 'toeic-r-v2', name: Profiles.name(), st: E.st }); $('#codeBox').value = c; try { navigator.clipboard.writeText(c); } catch (e) { } },
  imp() {
    try { const o = Code.dec($('#codeBox').value); if (!o || !o.st) throw 0; Profiles.create(o.name || '导入'); E.st = o.st; save(); boot(); }
    catch (e) { alert('进度码不对'); }
  }
};
/* ---------- 事件 ---------- */
if (typeof document !== 'undefined' && document.addEventListener) {
  document.addEventListener('click', e => {
    const t = e.target; if (!t || !t.closest) return;
    const a = t.closest('[data-act]');
    if (a) { if (A[a.dataset.act]) { e.preventDefault(); A[a.dataset.act](a); } return; }
    const w = t.closest('.w'); if (w) return lookupWord(w);
    if (!t.closest('#pop')) hidePop();
    const nb = t.closest('#nav button'); if (nb) { tab = nb.dataset.tab; render(); }
    if (t.id === 'modal' && !R) modal('');
  });
  document.addEventListener('keydown', e => {
    if (!S || S.done || S.paused) { if (R && e.key === 'Enter') A.closeR(); return; }
    if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
    const k = e.key, id = curId();
    if (e.altKey && (k === 'ArrowLeft' || k === 'ArrowRight')) { ui().split = Math.max(40, Math.min(70, (ui().split || 55) + (k === 'ArrowLeft' ? -5 : 5))); save(); render(); return e.preventDefault(); }
    const ci = 'abcd'.indexOf(k.toLowerCase()), ni = '1234'.indexOf(k);
    if ((ci >= 0 || ni >= 0) && !S.ans[id]) return answer(ci >= 0 ? ci : ni);
    if (k === 'Enter' && S.ans[id]) return next();
    if (k === 'ArrowLeft') return goQ(S.qi - 1);
    if (k === 'ArrowRight') return goQ(S.qi + 1);
    if (k === 'Escape') { hidePop(); if (!$('#modal').classList.contains('hide')) modal(''); return; }
    if (k === ' ' && bundle()) { e.preventDefault(); return A.flip(); }
    if ((k === 'g' || k === 'G') && bundle()) { const l = $('#pq .ref'); if (l) A.jump(l); }
  });
  /* 中缝拖动：40–70%，双击复位 */
  let drag = false;
  document.addEventListener('pointerdown', e => { if (e.target && e.target.id === 'dv') { drag = true; e.preventDefault(); } });
  document.addEventListener('pointermove', e => {
    if (!drag) return; const sp = $('#split'); if (!sp) return; const r = sp.getBoundingClientRect();
    const v = Math.max(40, Math.min(70, (e.clientX - r.left) / r.width * 100)); ui().split = Math.round(v); sp.style.setProperty('--sp', ui().split + '%');
  });
  document.addEventListener('pointerup', () => { if (drag) { drag = false; save(); } });
  document.addEventListener('dblclick', e => { if (e.target && e.target.id === 'dv') { ui().split = 55; save(); render(); } });
  document.addEventListener('visibilitychange', () => { if (S && !S.paused) leaveQ(); save(); });
  if (typeof window !== 'undefined' && window.addEventListener) { window.addEventListener('pagehide', () => { if (S && !S.paused) leaveQ(); save(); }); window.addEventListener('resize', () => { hidePop(); }); }
  setInterval(tick, 1000);
}
boot();
