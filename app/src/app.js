/* ===== 界面层 ===== */
const $ = s => document.querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const pct = x => Math.round(x * 100) + '%';
const LAYERS = [['foundation', '基础层'], ['grammar', '语法'], ['vocab', '词汇'], ['qtype', '题型'], ['texttype', '文本类型'], ['strategy', '技巧']];
const MODE_NM = { train: '训练', diag: '入职诊断', mock: '整套模考', review: '复习', weak: '攻克薄弱点' };
const FB_OK = ['客户很满意，这封邮件可以发了。', '主管点头：思路清楚。', '报告一次过审。', '同事来问你怎么做到这么快的。', '这单签下来了。'];
const FB_NO = ['这份文件被退回修改了，看看哪里错。', '主管在旁边批注：再核对一下。', '客户回邮件问了一个问题。', '还好是内部草稿，改掉就行。'];
const pick = a => a[Math.floor(Math.random() * a.length)];
let tab = 'home', S = null, R = null, setupNew = false, flash = null;
const save = () => { if (E.st) { E.st.run = S && !S.done ? S : null; Profiles.save(E.st); } };

function banner() {
  if (Store.kind !== 'memory') return;
  const b = $('#banner'); b.textContent = '当前环境不能自动保存，离开前请到「我的」复制进度码。'; b.classList.remove('hide');
}
Store.onFallback = banner;

function boot() {
  banner();
  if (!Profiles.cur()) { setupNew = true; return render(); }
  E.st = Profiles.load() || newState(); S = E.st.run || null; if (S) S.qt0 = Date.now(); render();
}

function render() {
  const m = $('#main'), inRun = S && !S.done;
  $('#tabs').classList.toggle('hide', !!(setupNew || inRun || R));
  $('#who').textContent = E.st ? Profiles.name() + ' · 目标 ' + E.st.target : '';
  document.querySelectorAll('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
  if (setupNew) m.innerHTML = vSetup();
  else if (R) m.innerHTML = vResult();
  else if (inRun && S.view) m.innerHTML = vQuiz();
  else m.innerHTML = ({ home: vHome, weak: vWeak, review: vReview, graph: vGraph, me: vMe })[tab]();
  if (inRun && S.view) tick();
}

/* ---------- 新建档案 / 入职 ---------- */
function vSetup() {
  const t = (E.st && E.st.target) || 700;
  return `<div class="card"><h2>入职登记</h2><p class="mut">选目标和考试日期，做约 12 题诊断（P5 + 1 组 P6 + 1 组 P7），系统给你定岗。</p>
  <h3>档案名</h3><input id="sName" placeholder="例如：我" value="${esc(Profiles.list().length ? '' : '我')}">
  <h3>目标总分</h3><div class="row wrap" id="sTg">${[600, 700, 800, 900].map(v => `<span class="chip ${v === t ? 'on' : ''}" data-act="tg" data-v="${v}">${v}</span>`).join('')}</div>
  <h3>考试日期</h3><input id="sDate" type="date">
  <p></p><button class="btn full" data-act="setupGo" data-d="1">开始入职诊断</button><p></p>
  <button class="btn ghost full" data-act="setupGo" data-d="0">先跳过诊断</button>
  ${Profiles.list().length ? '<p></p><button class="btn ghost full" data-act="setupCancel">取消</button>' : ''}</div>`;
}

/* ---------- 工作台 ---------- */
function gauge(p) {
  const x = v => ((v - 5) / 490 * 100).toFixed(1) + '%';
  return `<div class="gauge"><div class="rng" style="left:${x(p.lo)};width:calc(${x(p.hi)} - ${x(p.lo)})"></div><div class="pt" style="left:${x(p.p)}"></div><div class="tg" style="left:${x(p.tg)}"></div></div>
  <div class="row sp sm mut"><span>5</span><span>目标 ${p.tg}</span><span>495</span></div>`;
}
function vHome() {
  const st = E.st, p = E.predict(), due = E.dueItems().length, dw = E.dueWords().length, f = E.nextForm();
  const days = st.exam ? Math.ceil((new Date(st.exam) - new Date(today())) / 864e5) : null;
  return `${!st.diag ? `<div class="card"><b>还没做入职诊断</b><p class="mut sm">约 12 题、8 分钟，做完预测分会准很多。</p><button class="btn acc full" data-act="diag">开始诊断</button></div>` : ''}
  ${S && !S.done ? `<div class="card row sp"><span>有未完成的${MODE_NM[S.mode]}（${Object.keys(S.ans).length} 题已答）</span><button class="btn sm" data-act="resume">继续</button></div>` : ''}
  <div class="card"><div class="row sp"><span class="mut">预测阅读分</span><span class="rank">${E.rank(p.p)}</span></div>
  <div class="row sp"><span class="big">${p.p}</span><span class="mut">${p.lo}–${p.hi}</span></div>${gauge(p)}
  <div class="grid2" style="margin-top:8px"><div class="kpi"><b>${pct(p.prob)}</b><span class="sm mut">达标概率</span></div>
  <div class="kpi"><b>${E.streakNow()}</b><span class="sm mut">连续打卡天</span></div></div>
  <p class="sm mut">今天已做 ${st.days[today()] || 0} 题${days != null ? ` · 距考试 ${days} 天` : ''} · 累计 ${st.N} 题</p></div>
  <div class="card"><h2>今天的任务</h2><div class="tasks">
   <div class="task" data-act="plan" data-m="5"><div><b>5</b> 分钟<div class="sm mut">到期复习 ${Math.min(due, 4)} + P5 薄弱点快练</div></div><span>›</span></div>
   <div class="task" data-act="plan" data-m="20"><div><b>20</b> 分钟<div class="sm mut">复习 + P5 ×8 + P6 1 篇 + P7 1 组</div></div><span>›</span></div>
   <div class="task" data-act="mock" ${f ? '' : 'style="opacity:.5"'}><div><b>75</b> 分钟<div class="sm mut">${f ? `整套模考 ${f}（${FORMS[f].length} 题，计时、无提示）` : '套题已全部用完'}</div></div><span>›</span></div>
  </div><p class="sm mut">到期复习 ${due} 题 · 生词 ${dw} 个</p></div>`;
}

/* ---------- 会话 ---------- */
function startSession(mode, units, extra) {
  if (!units || !units.length) return alert('没有可用的题目了');
  const nd0 = {};
  units.forEach(u => u.ids.forEach(id => { const i = IT[id]; nd0[i.n] = E.mastery(i.n); }));
  S = Object.assign({ mode, units, ui: 0, qi: 0, ans: {}, lu: {}, t0: Date.now(), qt0: Date.now(), pred0: E.predict(), nd0, fb: false, tool: '', fold: false, doc: 0, view: 1 }, extra || {});
  if (mode === 'mock') { S.flat = units.reduce((a, u) => a.concat(u.ids), []); S.pos = 0; S.mt = {}; S.end = Date.now() + 75 * 6e4; }
  E.log('start', { mode, n: units.reduce((s, u) => s + u.ids.length, 0), form: S.form });
  save(); render(); scrollTo(0, 0);
}
function curId() { return S.mode === 'mock' ? S.flat[S.pos] : S.units[S.ui].ids[S.qi]; }
function curUnit() { if (S.mode !== 'mock') return S.units[S.ui]; const id = curId(); return S.units.find(u => u.ids.includes(id)); }
function total() { return S.mode === 'mock' ? S.flat.length : S.units.reduce((s, u) => s + u.ids.length, 0); }

function words(t) { return esc(t).replace(/[A-Za-z][A-Za-z'’-]*/g, w => `<span class="w">${w}</span>`); }
function passageText(x, qid, bid, di) {
  const cur = IT[qid].q, hl = new Set(E.st.hl[bid + ':' + di] || []);
  let k = 0;
  return x.split(/(\n+)/).map(seg => {
    if (/^\n+$/.test(seg)) return seg;
    return (seg.match(/[^.!?]+[.!?"”’)]*\s*|.+$/g) || [seg]).map(sn => {
      const i = k++;
      let h = words(sn).replace(/\{\{(\d+)\}\}/g, (m, n) => `<span class="blank ${+n === cur ? 'cur' : ''}">${n}</span>`);
      return `<span class="sen ${hl.has(i) ? 'hl' : ''}" data-s="${i}">${h}</span>`;
    }).join('');
  }).join('');
}
function vPassage(u, qid) {
  const b = BU[u.b], tools = S.mode !== 'mock' && S.mode !== 'diag';
  const di = Math.min(S.doc, b.docs.length - 1), d = b.docs[di];
  return `<div class="row sp sm mut"><span>Part ${b.p} · ${b.k === 'single' ? '单篇' : b.k === 'double' ? '双篇' : '三篇'}</span><span class="chip" data-act="fold">${S.fold ? '展开原文' : '收起原文'}</span></div>
  ${b.docs.length > 1 ? `<div class="tabsx">${b.docs.map((x, k) => `<span class="chip ${k === di ? 'on' : ''}" data-act="doc" data-k="${k}">文${k + 1}</span>`).join('')}</div>` : ''}
  <div class="passage ${S.fold ? 'fold' : ''}" data-bid="${b.id}" data-di="${di}">${d.h ? `<div class="ph">${words(d.h).replace(/\{\{(\d+)\}\}/g, '<span class="blank">$1</span>')}</div>` : ''}${passageText(d.x, qid, b.id, di)}</div>`;
}
function vQuiz() {
  const id = curId(), it = IT[id], u = curUnit(), a = S.ans[id], mock = S.mode === 'mock', tools = !mock && S.mode !== 'diag';
  const n = mock ? S.pos + 1 : Object.keys(S.ans).length + (S.fb ? 0 : 1);
  let stem = it.p === 6 ? `第 ${it.q} 空（原文高亮处）` : it.s;
  stem = words(stem).replace(/-{4,}/g, '<span class="blank cur">&nbsp;</span>');
  const opts = it.o.map((o, k) => {
    let c = '';
    if (S.fb) c = k === it.a ? 'ok' : (a && a.c === k ? 'no' : '');
    else if (a && a.c === k) c = 'sel';
    return `<button class="opt ${c}" data-act="pick" data-c="${k}">(${'ABCD'[k]}) ${esc(o)}</button>`;
  }).join('');
  let fb = '';
  if (S.fb && a) {
    const ok = a.c === it.a, why = it.dr && it.dr[a.c];
    const rules = !ok && (E.st.cons[it.n] || 0) >= 2 && E.rules(it.n).length;
    fb = `<div class="fb ${ok ? '' : 'bad'}"><b>${ok ? '✓ ' + pick(FB_OK) : '✗ ' + pick(FB_NO)}</b>
     <div>正确答案：(${'ABCD'[it.a]}) ${esc(it.o[it.a])} · 用时 ${Math.round(a.ms / 1000)}s / 目标 ${it.t}s</div>
     ${it.e ? `<div class="mut" style="margin-top:4px">${esc(it.e)}</div>` : ''}
     ${why ? `<div style="margin-top:4px">你选的 (${'ABCD'[a.c]})：${esc(why)}</div>` : ''}
     <div class="sm mut">考点：${esc((ND[it.n] || {}).nm || it.n)}</div></div>
     ${rules ? '<button class="btn ghost full" data-act="rules">同类连错 2 次 · 看工作规则卡</button><p></p>' : ''}
     <button class="btn full" data-act="next">下一题</button>`;
  }
  const head = `<div class="q-top"><div class="row sp"><span><b>${MODE_NM[S.mode]}</b> <span class="mut sm">${n}/${total()}</span></span>
   ${mock ? `<span id="cd" class="rank">--:--</span>` : ''}<button class="btn ghost sm" data-act="pause">${mock ? '离开' : '暂停'}</button></div>
   ${mock ? '' : `<div class="tbar" id="tb"><i style="width:0"></i></div>`}</div>`;
  const tl = tools ? `<div class="tools"><span class="chip" data-act="later">稍后处理</span><span class="chip ${S.tool === 'hl' ? 'on' : ''}" data-act="tool" data-t="hl">划依据</span><span class="chip ${S.tool === 'w' ? 'on' : ''}" data-act="tool" data-t="w">点词进生词本</span></div>` : '';
  const nav = mock ? `<div class="row sp" style="margin:8px 0"><button class="btn ghost sm" data-act="mv" data-d="-1">上一题</button><button class="btn acc sm" data-act="submit">交卷</button><button class="btn ghost sm" data-act="mv" data-d="1">下一题</button></div>
   <details><summary>题号导航（已答 ${Object.keys(S.ans).length}/${S.flat.length}）</summary><div class="qnav">${S.flat.map((q, k) => `<button class="${S.ans[q] ? 'an' : ''} ${k === S.pos ? 'cu' : ''}" data-act="go" data-k="${k}">${IT[q].q}</button>`).join('')}</div></details>` : '';
  return head + (u.b ? vPassage(u, id) : '') + tl + `<div class="stem" data-stem="1"><span class="mut sm">Q${it.q}</span> ${stem}</div>` + opts + fb + nav;
}

let timer = null;
function tick() {
  clearInterval(timer);
  timer = setInterval(() => {
    if (!S || S.done || !S.view) return clearInterval(timer);
    if (S.mode === 'mock') {
      const left = Math.max(0, S.end - Date.now()), el = $('#cd');
      if (el) el.textContent = String(Math.floor(left / 6e4)).padStart(2, '0') + ':' + String(Math.floor(left / 1e3) % 60).padStart(2, '0');
      if (!left) { clearInterval(timer); submitMock(); }
      return;
    }
    const tb = $('#tb'); if (!tb || S.fb) return;
    const r = (Date.now() - S.qt0) / 1000 / IT[curId()].t;
    tb.firstChild.style.width = Math.min(100, r * 100) + '%'; tb.classList.toggle('over', r > 1);
  }, 500);
}

function answer(c) {
  const id = curId(), it = IT[id];
  if (S.mode === 'mock') { S.ans[id] = { c }; leaveQ(); if (S.pos < S.flat.length - 1) S.pos++; S.qt0 = Date.now(); save(); return render(); }
  if (S.fb) return;
  const a = { c, ms: Date.now() - S.qt0, lu: !!S.lu[id] }; S.ans[id] = a;
  E.record(it, a, S.mode);
  if (S.mode === 'diag') return next();
  S.fb = true; save(); render();
}
function next() {
  S.fb = false; S.qi++;
  if (S.qi >= S.units[S.ui].ids.length) { S.ui++; S.qi = 0; S.doc = 0; }
  if (S.ui >= S.units.length) return finish();
  S.qt0 = Date.now(); save(); render(); scrollTo(0, 0);
}
function leaveQ() { const id = curId(); S.mt[id] = (S.mt[id] || 0) + (Date.now() - S.qt0); }
function submitMock() {
  if (!S || S.mode !== 'mock') return;
  leaveQ(); const parts = {};
  S.flat.forEach(id => {
    const a = S.ans[id] || { c: -1 }; a.ms = S.mt[id] || 0; S.ans[id] = a;
    const ok = E.record(IT[id], a, 'mock'), p = parts[IT[id].p] || (parts[IT[id].p] = [0, 0]); p[0] += ok ? 1 : 0; p[1]++;
  });
  if (!E.st.used.includes(S.form)) E.st.used.push(S.form);
  S.parts = parts; finish();
}
function finish() {
  const ids = Object.keys(S.ans), ok = ids.filter(id => S.ans[id].c === IT[id].a).length;
  const ms = ids.reduce((s, id) => s + (S.ans[id].ms || 0), 0), tgt = ids.reduce((s, id) => s + IT[id].t, 0);
  const p1 = E.predict(), nodes = Object.keys(S.nd0).map(n => ({ n, a: S.nd0[n], b: E.mastery(n) })).filter(x => x.b != null)
    .map(x => Object.assign(x, { d: x.b - (x.a == null ? 0.5 : x.a) }));
  R = { mode: S.mode, n: ids.length, ok, ms, tgt, p0: S.pred0, p1, nodes, form: S.form, parts: S.parts };
  if (S.mode === 'mock') {
    const raw = ok / Math.max(1, ids.length) * 100;
    R.scaled = Math.round(E.scaled(raw) / 5) * 5; E.st.mocks.push({ ts: Date.now(), form: S.form, ok, n: ids.length, scaled: R.scaled, ms });
  }
  if (S.mode === 'diag') E.st.diag = true;
  E.st.hist.push([Date.now(), p1.p]);
  E.log('end', { mode: S.mode, n: ids.length, ok, ms });
  S.done = true; S = null; save(); render(); scrollTo(0, 0);
}
function vResult() {
  const r = R, d = r.p1.p - r.p0.p, up = r.nodes.filter(x => x.d > 0.005).sort((a, b) => b.d - a.d).slice(0, 4), dn = r.nodes.filter(x => x.d < -0.005).sort((a, b) => a.d - b.d).slice(0, 4);
  const li = x => `<div class="li"><span class="nm">${esc((ND[x.n] || {}).nm || x.n)}</span><span class="${x.d > 0 ? 'up' : 'dn'}">${x.d > 0 ? '▲' : '▼'}${Math.abs(Math.round(x.d * 100))}</span><span class="sm mut">${pct(x.b)}</span></div>`;
  const r0 = E.rank(r.p0.p), r1 = E.rank(r.p1.p);
  return `<div class="card"><h2>${r.mode === 'diag' ? '入职诊断结果' : r.mode === 'mock' ? '模考报告 ' + r.form : '本次结算'}</h2>
  ${r.mode === 'mock' ? `<div class="big">${r.scaled}</div><p class="mut sm">按正确率换算的阅读分估计（未答题按错计）</p>
   <div class="grid2">${Object.keys(r.parts || {}).map(p => `<div class="kpi"><b>${r.parts[p][0]}/${r.parts[p][1]}</b><span class="sm mut">Part ${p}</span></div>`).join('')}</div><p></p>` : ''}
  <div class="grid2"><div class="kpi"><b>${r.n}</b><span class="sm mut">题数</span></div><div class="kpi"><b>${pct(r.ok / Math.max(1, r.n))}</b><span class="sm mut">正确率</span></div>
  <div class="kpi"><b>${Math.round(r.ms / 1000)}s</b><span class="sm mut">用时（目标 ${r.tgt}s）</span></div>
  <div class="kpi"><b class="${d >= 0 ? 'up' : 'dn'}">${d >= 0 ? '+' : ''}${d}</b><span class="sm mut">预测分 ${r.p0.p}→${r.p1.p}</span></div></div>
  <p>职级：<span class="rank">${r1}</span> ${r0 !== r1 ? `<span class="mut sm">（原 ${r0}）${RANKS.findIndex(x => x[1] === r1) > RANKS.findIndex(x => x[1] === r0) ? '🎉 晋升！' : ''}</span>` : ''}</p>
  <p class="mut sm">预测区间 ${r.p1.lo}–${r.p1.hi} · 达标概率 ${pct(r.p1.prob)}</p></div>
  ${up.length ? `<div class="card"><h3>上涨节点</h3><div class="list">${up.map(li).join('')}</div></div>` : ''}
  ${dn.length ? `<div class="card"><h3>下跌节点</h3><div class="list">${dn.map(li).join('')}</div></div>` : ''}
  <button class="btn full" data-act="closeR">回工作台</button>`;
}

/* ---------- 薄弱点 / 复习 / 图谱 ---------- */
function mbar(m) { return m == null ? '<span class="sm mut" style="width:90px">未测</span>' : `<div class="bar" style="max-width:90px"><i style="width:${pct(m)}"></i></div>`; }
function vWeak() {
  const L = E.weakList().slice(0, 15);
  return `<div class="card"><h2>薄弱点排行</h2><p class="mut sm">按 考频 × (1 − 掌握度) 排序；未测节点按整体水平估。</p><div class="list">
  ${L.map((x, k) => `<div class="li"><span class="sm mut">${k + 1}</span><span class="nm">${esc(x.n.nm)}<br><span class="sm mut">考频 ${x.n.w} · ${x.m == null ? '未测' : '掌握 ' + pct(x.m)}</span></span>${mbar(x.m)}<button class="btn sm" data-act="weak" data-n="${x.n.id}">攻克</button></div>`).join('')}</div></div>`;
}
function vReview() {
  const due = E.dueItems(), dw = E.dueWords(), wr = Object.keys(E.st.wrong).filter(id => IT[id]).sort((a, b) => E.st.wrong[b] - E.st.wrong[a]).slice(0, 40);
  const ws = Object.keys(E.st.words).sort((a, b) => E.st.words[b].ts - E.st.words[a].ts);
  return `<div class="card"><h2>今日复习</h2><p class="mut sm">到期 ${due.length} 题（一次最多 20）· 生词 ${dw.length} 个</p>
  <div class="row"><button class="btn" data-act="rev" ${due.length ? '' : 'disabled'}>复习错题</button><button class="btn ghost" data-act="flash" ${dw.length ? '' : 'disabled'}>背生词</button></div></div>
  <div class="card"><h2>错题本 <span class="mut sm">${Object.keys(E.st.wrong).length}</span></h2><div class="list">
  ${wr.map(id => { const i = IT[id]; return `<div class="li"><span class="nm">${esc((i.s || (BU[i.b] ? 'P' + i.p + ' ' + i.id : '')).slice(0, 60))}<br><span class="sm mut">${esc((ND[i.n] || {}).nm || i.n)}</span></span><button class="btn ghost sm" data-act="redo" data-id="${id}">重做</button></div>`; }).join('') || '<p class="mut sm">暂无错题</p>'}</div></div>
  <div class="card"><h2>生词本 <span class="mut sm">${ws.length}</span></h2><div class="list">
  ${ws.slice(0, 80).map(w => `<div class="li"><span class="nm"><b>${esc(w)}</b><br><span class="sm mut">${esc(E.st.words[w].c)}</span></span><button class="btn ghost sm" data-act="delw" data-w="${esc(w)}">删</button></div>`).join('') || '<p class="mut sm">做题时打开「点词进生词本」，点原文里的词即可加入</p>'}</div></div>`;
}
function vGraph() {
  return `<div class="card"><h2>能力图谱</h2><p class="mut sm">${D.nodes.length} 个节点，按层分组；条形为掌握度。</p></div>` + LAYERS.map(([l, nm]) => {
    const ns = D.nodes.filter(n => n.l === l), lv = ns.filter(n => !n.g && E.mastery(n.id) != null);
    const avg = lv.length ? lv.reduce((s, n) => s + E.mastery(n.id), 0) / lv.length : null;
    return `<div class="card"><details><summary>${nm} <span class="mut sm">${ns.length} 节点 · 已测 ${lv.length}${avg != null ? ' · 平均 ' + pct(avg) : ''}</span></summary><div class="list">
     ${ns.map(n => n.g ? `<h3>${esc(n.nm)}</h3>` : `<div class="li"><span class="nm sm">${esc(n.nm)} <span class="mut">${n.bd}</span></span>${mbar(E.mastery(n.id))}</div>`).join('')}</div></details></div>`;
  }).join('');
}

/* ---------- 我的 ---------- */
function vMe() {
  const L = Profiles.list(), st = E.st, ms = st.mocks.slice(-5).reverse();
  return `<div class="card"><h2>档案</h2><div class="list">${L.map(p => `<div class="li"><span class="nm">${esc(p.name)}${p.id === Profiles.cur() ? ' <span class="chip on">当前</span>' : ''}</span>
   ${p.id === Profiles.cur() ? '' : `<button class="btn ghost sm" data-act="use" data-id="${p.id}">切换</button>`}<button class="btn ghost sm" data-act="delp" data-id="${p.id}">删除</button></div>`).join('')}</div>
   <button class="btn ghost full" data-act="newp">新建档案</button></div>
  <div class="card"><h2>目标</h2><div class="row">${[600, 700, 800, 900].map(v => `<span class="chip ${v === st.target ? 'on' : ''}" data-act="setTg" data-v="${v}">${v}</span>`).join('')}</div>
   <h3>考试日期</h3><input type="date" id="exDate" value="${esc(st.exam)}" data-act="exam"></div>
  <div class="card"><h2>进度码</h2><p class="mut sm">换手机/浏览器时：复制进度码 → 在新设备「导入为新档案」。存储：${Store.kind === 'local' ? '本机自动保存' : '内存（不会自动保存）'}</p>
   <div class="row"><button class="btn sm" data-act="exp">生成并复制</button><button class="btn ghost sm" data-act="imp">导入为新档案</button><button class="btn ghost sm" data-act="logx">导出作答日志</button></div>
   <p></p><textarea id="codeBox" placeholder="进度码"></textarea></div>
  <div class="card"><h2>本周 PK（本地演示）</h2>${L.length < 2 ? '<p class="mut sm">再建一个档案就能对比。</p>' : vPK(L)}</div>
  <div class="card"><h2>模考记录</h2>${ms.map(m => `<div class="li row sp"><span>${m.form}</span><span>${m.ok}/${m.n}</span><b>${m.scaled}</b></div>`).join('') || '<p class="mut sm">还没有模考</p>'}</div>
  <div class="card"><button class="btn ghost full" data-act="reset">重置当前档案</button><p class="sm mut">数据版本 ${esc(D.v)} · 题库 ${D.items.length} 题</p></div>`;
}
function vPK(L) {
  const rows = L.slice(0, 6).map(p => {
    const st = p.id === Profiles.cur() ? E.st : Profiles.load(p.id); if (!st) return null;
    const keep = E.st; E.st = st; const pr = E.predict(); E.st = keep; const w = E.weekStats(st);
    return { nm: p.name, n: w.n, acc: w.acc, p: pr.p };
  }).filter(Boolean);
  const best = k => Math.max.apply(null, rows.map(r => r[k]));
  return `<div class="list">${rows.map(r => `<div class="li"><span class="nm">${esc(r.nm)}</span><span class="${r.n === best('n') ? 'up' : ''}">${r.n}题</span><span class="${r.acc === best('acc') ? 'up' : ''}">${pct(r.acc)}</span><b class="${r.p === best('p') ? 'up' : ''}">${r.p}</b></div>`).join('')}</div><p class="sm mut">本周题数 / 正确率 / 预测阅读分</p>`;
}
function copy(t) {
  const box = $('#codeBox'); if (box) { box.value = t; box.select(); }
  try { navigator.clipboard.writeText(t).then(() => alert('已复制'), () => { document.execCommand('copy'); alert('已选中，可手动复制'); }); }
  catch (e) { try { document.execCommand('copy'); } catch (x) { } alert('已选中，可手动复制'); }
}
function modal(h) { $('#sheet').innerHTML = h; $('#modal').classList.toggle('hide', !h); }
function vFlash() {
  const w = flash[0]; if (!w) { modal(''); render(); return; }
  modal(`<h2>${esc(w)}</h2><p class="mut">${esc(E.st.words[w].c)}</p><p class="sm mut">剩 ${flash.length} 个</p>
  <div class="row"><button class="btn ghost" data-act="fg" data-g="0">不认识</button><button class="btn ghost" data-act="fg" data-g="1">模糊</button><button class="btn" data-act="fg" data-g="2">认识</button></div><p></p><button class="btn ghost full" data-act="closeM">结束</button>`);
}

/* ---------- 事件 ---------- */
const A = {
  tg: el => { document.querySelectorAll('#sTg .chip').forEach(c => c.classList.toggle('on', c === el)); },
  setupGo: el => {
    const tg = +(document.querySelector('#sTg .on') || {}).dataset.v || 700, ex = $('#sDate').value, nm = $('#sName').value.trim();
    Profiles.create(nm); E.st = newState(tg, ex); S = null; setupNew = false; E.log('profile', { tg, ex }); save();
    if (el.dataset.d === '1') startSession('diag', E.diagPlan()); else render();
  },
  setupCancel: () => { setupNew = false; render(); },
  diag: () => startSession('diag', E.diagPlan()),
  resume: () => { S.view = 1; S.qt0 = Date.now(); render(); },
  plan: el => startSession('train', E.plan(+el.dataset.m)),
  mock: () => { const f = E.nextForm(); if (f && confirm(`开始整套模考 ${f}？75 分钟倒计时，期间无提示。`)) startSession('mock', E.mockPlan(f), { form: f }); },
  pick: el => answer(+el.dataset.c),
  next: () => next(),
  pause: () => { if (S.mode === 'mock') leaveQ(); S.view = 0; save(); tab = 'home'; render(); },
  later: () => {
    const u = S.units[S.ui]; E.log('later', { id: curId() });
    if (u.b && S.qi < u.ids.length - 1) u.ids.push(u.ids.splice(S.qi, 1)[0]);
    else if (!u.b && S.ui < S.units.length - 1) S.units.push(S.units.splice(S.ui, 1)[0]);
    else return alert('已经是最后一题');
    S.qt0 = Date.now(); save(); render();
  },
  tool: el => { S.tool = S.tool === el.dataset.t ? '' : el.dataset.t; render(); },
  fold: () => { S.fold = !S.fold; render(); },
  doc: el => { S.doc = +el.dataset.k; render(); },
  rules: () => { const it = IT[curId()]; E.log('rule', { n: it.n }); modal(`<h2>工作规则卡</h2>${E.rules(it.n).map(r => `<div class="fb"><b>${esc(r.ti)}</b><div>${esc(r.wr)}</div><div class="mut sm">${esc(r.r)}</div></div>`).join('')}<button class="btn full" data-act="closeM">记住了</button>`); },
  closeM: () => { modal(''); flash = null; render(); },
  mv: el => { leaveQ(); S.pos = clamp(S.pos + +el.dataset.d, 0, S.flat.length - 1); S.qt0 = Date.now(); render(); },
  go: el => { leaveQ(); S.pos = +el.dataset.k; S.qt0 = Date.now(); render(); },
  submit: () => { const left = S.flat.length - Object.keys(S.ans).length; if (confirm(left ? `还有 ${left} 题没答，确定交卷？` : '确定交卷？')) submitMock(); },
  closeR: () => { R = null; tab = 'home'; render(); },
  weak: el => startSession('weak', E.weakPlan(el.dataset.n)),
  rev: () => startSession('review', E.reviewUnits(20)),
  redo: el => { const i = IT[el.dataset.id]; startSession('review', [i.b ? { b: i.b, ids: [i.id] } : { ids: [i.id] }]); },
  flash: () => { flash = E.dueWords(); vFlash(); },
  fg: el => { const w = flash.shift(); E.scheduleWord(w, +el.dataset.g); E.log('wordrev', { w, g: +el.dataset.g }); save(); vFlash(); },
  delw: el => { delete E.st.words[el.dataset.w]; save(); render(); },
  use: el => { save(); Profiles.use(el.dataset.id); E.st = Profiles.load() || newState(); S = E.st.run || null; render(); },
  delp: el => { if (!confirm('删除档案「' + Profiles.name(el.dataset.id) + '」？数据不可恢复。')) return; Profiles.remove(el.dataset.id); if (!Profiles.cur()) { E.st = null; setupNew = true; } else { E.st = Profiles.load() || newState(); S = E.st.run || null; } render(); },
  newp: () => { save(); setupNew = true; render(); },
  setTg: el => { E.st.target = +el.dataset.v; save(); render(); },
  exp: () => { E.log('export', {}); save(); copy(Code.enc({ app: 'toeic-r-v2', name: Profiles.name(), st: Object.assign({}, E.st, { log: [] }) })); },
  imp: () => {
    try { const o = Code.dec($('#codeBox').value); if (o.app !== 'toeic-r-v2' || !o.st || o.st.ver !== 2) throw 0; save(); Profiles.create((o.name || '导入') + '（导入）'); E.st = o.st; S = o.st.run || null; save(); alert('已导入为新档案'); render(); }
    catch (e) { alert('进度码无效'); }
  },
  logx: () => {
    const s = JSON.stringify({ profile: Profiles.name(), log: E.st.log }), a = document.createElement('a');
    try { a.href = URL.createObjectURL(new Blob([s], { type: 'application/json' })); a.download = 'toeic_log_' + today() + '.json'; document.body.appendChild(a); a.click(); a.remove(); }
    catch (e) { copy(s); }
  },
  reset: () => { if (confirm('重置当前档案的全部进度？')) { const t = E.st.target, x = E.st.exam; E.st = newState(t, x); S = null; save(); render(); } }
};
document.addEventListener('click', ev => {
  const tb = ev.target.closest('#tabs button'); if (tb) { tab = tb.dataset.tab; if (S) S.view = 0; return render(); }
  if (ev.target.id === 'modal') return A.closeM();
  const el = ev.target.closest('[data-act]');
  if (el && A[el.dataset.act] && el.tagName !== 'INPUT') return A[el.dataset.act](el);
  if (!S || !S.view || !S.tool) return;
  // 练习工具：点句划依据 / 点词加生词本
  const w = ev.target.closest('.w'), sen = ev.target.closest('.sen'), ps = ev.target.closest('.passage'), stem = ev.target.closest('[data-stem]');
  if (S.tool === 'w' && w && (ps || stem)) {
    const ctx = sen ? sen.textContent : stem.textContent; E.addWord(w.textContent, ctx.trim()); S.lu[curId()] = true; w.classList.add('vw'); save();
  } else if (S.tool === 'hl' && sen && ps) {
    const key = ps.dataset.bid + ':' + ps.dataset.di, a = E.st.hl[key] || (E.st.hl[key] = []), i = +sen.dataset.s, k = a.indexOf(i);
    if (k < 0) a.push(i); else a.splice(k, 1); sen.classList.toggle('hl'); E.log('hl', { b: ps.dataset.bid, s: i }); save();
  }
});
document.addEventListener('change', ev => { if (ev.target.id === 'exDate') { E.st.exam = ev.target.value; save(); } });
window.addEventListener('pagehide', save);
boot();
