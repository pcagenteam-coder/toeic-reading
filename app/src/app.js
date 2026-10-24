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
const UI0 = {}, ui = () => (E.st ? (E.st.ui = E.st.ui || {}) : UI0);
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
  render(); rmArm();
}

/* ---------- 外壳 ---------- */
function render() {
  const inRun = !!(S && !S.done && !S.paused), m = $('#main');
  keepScroll();
  $('#app').classList.toggle('quiz', inRun);
  $$('#nav button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
  if (E.st) { const n = E.dueItems().length + E.dueWords().length; $('#revN').textContent = n ? String(n) : ''; }
  const o = !setupNew && !inRun && ob();
  $('#app').classList.toggle('onbm', !!(setupNew || o));
  if (WQ && !inRun && !setupNew) $('#app').classList.add('quiz');
  applyFz();
  try {
    if (setupNew) m.innerHTML = wrap(vSetup());
    else if (inRun) m.innerHTML = vQuiz();
    else if (o) m.innerHTML = wrap(vOnboard(o));
    else if (WQ) m.innerHTML = vWordQuiz();
    else m.innerHTML = wrap(({ today: vToday, review: vReview, progress: vProgress, me: vMe })[tab]());
    A._errN = 0;
  } catch (e) { console.error(e); A._err = String(e && e.stack || e); A._errN = (A._errN || 0) + 1; m.innerHTML = wrap(vError()); }
  if (setupNew) s1Upd();
  modal(R ? vResult() : '');
  hidePop();
  restoreScroll();
}
const wrap = h => `<div class="wrap">${h}</div>`;
/* 出错：先说进度已保存，再给能继续的按钮 */
function vError() {   // P2-6：重试 / 回今天页 / 离线说明；连续出错 2 次改为“先休息”，不再反复让人点“接着做”
  const off = typeof navigator !== 'undefined' && navigator.onLine === false;
  const note = `<p class="mut sm">题库和进度都存在这台设备上，离线也能做题${off ? '（现在没联网，不影响）' : ''}。</p>`;
  const tail = `<p></p><button class="link mut" data-act="errCopy">复制错误信息</button>`;
  if ((A._errN || 0) >= 2) return `<div class="card empty"><h2>先休息一下，明天再来，进度都在。</h2><p>连着出了两次问题，可能是浏览器一时不稳。今天的进度已经保存好了。</p>${note}<button class="btn full lg" data-act="recover">回今天页</button><button class="link" data-act="reload">刷新页面</button>${tail}</div>`;
  return `<div class="card empty"><h2>出了点问题，你的进度已保存。</h2>${note}<button class="btn full lg" data-act="retry">再试一次</button><p></p><button class="btn full ghost" data-act="recover">回今天页</button>${tail}</div>`;
}
function modal(h) { $('#sheet').innerHTML = h; $('#modal').classList.toggle('hide', !h); }

/* ---------- 首日 S1–S6：目标 → 入职测试 → 结果+作战卡 → 提醒（P0-3：词汇摸底移到诊断后、可选，从今天页“补测词汇”进入） ---------- */
const r5 = x => Math.round(x / 5) * 5;
const OBS = ['目标', '测试', '结果', '提醒'];
const ob = () => E.st && E.st.ob && E.st.ob.step !== 'done' ? E.st.ob : null;
function steps(k) {
  return `<div class="steps">${OBS.map((x, i) => `<i class="${i < k ? 'd' : i === k ? 'c' : ''}"><span>${x}</span></i>`).join('')}</div>`;
}
const obStory = t => ui().plain || ui().nostory ? '' : `<p class="scene">«入职第一天 · ${esc(t)}»</p>`;
function rtgCalc(total, listen) { return Math.max(5, Math.min(495, r5(listen ? total - listen : total * 0.45))); }
function examTip(dt) {
  if (!dt) return '';
  const d = Math.round((new Date(dt + 'T00:00') - new Date(today() + 'T00:00')) / 864e5);
  if (d < 0) return '<span class="warn">这个日期已经过了，换一个吧</span>';
  return `还有 ${d} 天，` + (d > 60 ? '时间充裕，每天 5 分钟够用' : d >= 15 ? '每天 5–20 分钟比较稳' : '进入冲刺，只练最能提分的部分');
}
function s1Vals() {
  const v = id => (($('#' + id) || {}).value || '').trim();
  const total = +v('sTotOther') || A._tg || 600, ls = +v('sLs') || 0, man = +v('sRtg') || 0;   // P2-7：听力默认留空 = 按总分 ×0.45 估
  return { total: Math.max(10, Math.min(990, total)), listen: ls, rtg: man ? Math.max(5, Math.min(495, r5(man))) : rtgCalc(total, ls), exam: A._noDate ? '' : v('sDate') };
}
function vSetup() {
  const t = A._tg || 600, first = !Profiles.list().length;
  return `<div class="onb">${steps(0)}${obStory('Dana：先认识一下你')}<div class="card">
  ${first ? '' : '<h3>新档案名</h3><input id="sName" placeholder="例如：小王">'}
  <h3>你想考到多少总分？</h3><div class="row wrapr">${[500, 600, 700, 800, 900].map(v => `<button class="chip ${v === t ? 'on' : ''}" data-act="tg" data-v="${v}">${v}</button>`).join('')}
    <input id="sTotOther" class="inl" inputmode="numeric" placeholder="其他"></div>
  <h3>听力大概能考多少？<span class="mut sm">（可不填）</span></h3><div class="row wrapr"><input id="sLs" class="inl" inputmode="numeric" placeholder="不知道就留空"></div>
  <p class="out" id="rtgOut"></p>
  <details id="rtgMan"><summary>改一下阅读目标</summary><input id="sRtg" inputmode="numeric" placeholder="阅读目标（5–495）"></details>
  <h3>什么时候考？</h3><div class="row"><input id="sDate" type="date" ${A._noDate ? 'disabled' : ''}><button class="chip ${A._noDate ? 'on' : ''}" data-act="noDate">还没定</button></div>
  <p class="out mut sm" id="dateOut"></p></div>
  <div class="thumb"><button class="btn full lg" data-act="setupGo" data-d="1">下一步 · 入职测试（约 5 分钟）</button>
  ${first ? '<button class="link" data-act="impOpen">我有进度码 → 导入</button>' : '<button class="btn ghost full" data-act="setupCancel">取消</button>'}</div></div>`;
}
function s1Upd() {
  const o = s1Vals(), r = $('#rtgOut'), d = $('#dateOut');
  if (r) r.innerHTML = `${o.listen ? '' : `<span class="mut sm">听力不填就按总分的 45% 算</span><br>`}→ 你的阅读目标：约 <b>${o.rtg}</b> 分 <span class="mut sm">（${o.listen ? `${o.total} − 听力 ${o.listen}` : `${o.total} × 45%`}，可在下方改）</span>`;
  if (d) d.innerHTML = examTip(o.exam);
}
/* S2–S3 词汇摸底：约 40 真词（四档各 10）+ 7 假词 + ≤6 次四选一抽查，3 分钟到点自动结束 */
const VT_MS = 180e3, VT_SIZE = { core: 2000, 600: 1500, 730: 1500, 860: 2000 };
function vtNew() {
  const V = (D.voc || []).map(v => ({ w: v[0], r: v[1], t: v[2], zh: v[3] })), sh = a => a.map(x => [Math.random(), x]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
  const q = [];
  ['core', '600', '730', '860'].forEach(t => q.push(...sh(V.filter(v => v.r && v.t === t)).slice(0, 10)));
  q.push(...sh(V.filter(v => !v.r)).slice(0, 7));
  return { q: sh(q).map(v => [v.w, v.r, v.t, v.zh]), i: 0, a: [], el: 0, chk: null, nc: 0 };
}
function vtLeft(vt) { return Math.max(0, VT_MS - vt.el - (vt.t0 ? Date.now() - vt.t0 : 0)); }
function vtClock(vt) { const s = Math.ceil(vtLeft(vt) / 1000); return `约 ${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; }
function vtScore(vt) {
  const by = {}, fk = { n: 0, y: 0 };
  vt.a.forEach(([i, y]) => { const [, r, t] = vt.q[i]; if (!r) { fk.n++; fk.y += y; return; } const b = by[t] = by[t] || { n: 0, y: 0 }; b.n++; b.y += y; });
  const fa = fk.n ? Math.min(0.9, fk.y / fk.n) : 0, adj = t => by[t] && by[t].n ? Math.max(0, (by[t].y / by[t].n - fa) / (1 - fa)) : null;
  let n = 0; Object.keys(VT_SIZE).forEach(t => { const a = adj(t); n += VT_SIZE[t] * (a == null ? 0.4 : a); });
  const biz = ['600', '730', '860'].map(adj).filter(x => x != null);
  return { n: Math.round(n / 100) * 100, biz: biz.length ? Math.round(biz.reduce((s, x) => s + x, 0) / biz.length * 100) : null, k: vt.a.length };
}
function vVocab(o) {
  if (o.step === 'vocab') return `<div class="onb">${obStory('Ken：再看看你认识多少词')}<div class="card"><h2>补测词汇 · 约 3 分钟</h2>
    <ul class="ln"><li>认识就点「认识」，不确定就点「不认识」</li><li>里面有几个编出来的假词</li><li>偶尔让你选一下意思</li><li>3 分钟到点自动结束</li></ul></div>
    <div class="thumb"><button class="btn full lg" data-act="vstart">开始</button><button class="link" data-act="vskip">先不测</button></div></div>`;
  const vt = o.vt;
  if (o.step === 'vtest') {
    const top = `<div class="vtop"><button class="x" data-act="vpause" aria-label="暂停">✕</button><span class="mut" id="vClock">${vtClock(vt)}</span></div>`;
    if (vt.paused) return `<div class="onb vt">${top}<div class="card"><h2>暂停了</h2><p class="mut">答过的都记下了。</p></div><div class="thumb">
      <button class="btn full lg" data-act="vresume">继续</button>${vt.a.length >= 20 ? '<button class="btn ghost full" data-act="vend">结束测试，看结果</button>' : ''}
      <button class="link" data-act="vskip">先不测</button></div></div>`;
    if (vt.chk) {
      const c = vt.chk;
      return `<div class="onb vt">${top}<div class="vw sm2"><b>${esc(c.w)}</b> 是什么意思？</div><div class="thumb vopts">${c.o.map((x, i) => `<button class="opt" data-act="vchk" data-i="${i}"><span>${esc(x)}</span></button>`).join('')}
        <button class="opt" data-act="vchk" data-i="-1"><span class="mut">不知道</span></button></div></div>`;
    }
    const w = vt.q[vt.i] || [''];
    return `<div class="onb vt">${top}<div class="vw" id="vWord">${esc(w[0])}</div><div class="thumb two"><button class="btn ghost lg" data-act="vk" data-y="0">不认识<span class="kb">←</span></button>
      <button class="btn lg" data-act="vk" data-y="1">认识<span class="kb">→</span></button></div></div>`;
  }
  if (!E.st.diag) return `<div class="onb">${steps(1)}${obStory('Ken：做一次入职测试')}<div class="card"><h2>入职测试 · 约 5 分钟</h2><ul class="ln"><li>约 12 题：6 句审稿 + 1 段改稿 + 1 封短邮件</li><li>不显示对错，不会就选一个，继续下一题</li><li>中途离开会保存，下次接着做</li></ul></div>
    <div class="thumb"><button class="btn full lg" data-act="diag">${S && S.mode === 'diag' ? '继续入职测试' : '开始入职测试'}</button></div></div>`;
  const sc = o.voc || { n: 3000, biz: null };   // 诊断后补测词汇的结果
  return `<div class="onb">${obStory('Dana：词汇补测做完了')}<div class="card">
    <h2>你大约认识 ${sc.n.toLocaleString('en-US')} 个常用词</h2><p>${sc.biz != null ? `商务词认识约 ${sc.biz}%。` : ''}文章里的生词会控制在你读得顺的范围。</p></div>
    <div class="thumb"><button class="btn full lg" data-act="obDone">好</button></div></div>`;
}
/* 作战卡：每档 ≤8 条行动句（UX §6.1 选定的 strategies_v2 id），数字按个人画像（Personal.battleCard）算 */
function battleLines() {
  const bc = API.profile().battle || API.progress().battle, band = E.band();
  if (!bc) return [];
  const fl = bc.finishLine.personal, k = Math.max(0, Math.min(100, bc.skipBudget.personal)), p56 = bc.p56Min, cut = bc.p5CutSec;
  const L = {
    '≤500': [`认真做约 ${100 - k} 题，其余 ${k} 题统一涂 B`, `P5+P6 用约 ${p56} 分钟，不用赶`, `P7 做到第 ${fl} 题就停，多篇整组涂`, '短通知、短信认真做，长新闻整篇涂',
      '读不完的篇看开头，只答第一题', 'P6 插入句直接涂', '一句读三遍没思路就涂、走', '跳过的当场先涂；最后 5 分钟全部涂满，别空着'],
    600: [`认真做约 ${100 - k} 题，其余统一涂 B`, `P5+P6 用约 ${p56} 分钟，不用赶`, `P7 做到第 ${fl} 题就停`, 'P6 插入句直接涂', '一句读三遍没思路就涂、走',
      '短的认真做，长新闻整篇涂', '跳过的当场先涂；最后 5 分钟全涂满', '涂满后再做“意思最接近”的词义题'],
    730: [`P5+P6 控制在 ${p56} 分钟内`, `最多放弃约 ${k} 题`, `P7 做到第 ${fl} 题`, `P5 一题超过 ${cut} 秒就涂最像的，走`, '插入句放最后，30 秒没思路就猜',
      '多篇只挑词义题和单篇细节题', '只在 P6 开头、第 147、176 题看表', '跳过的当场先涂；最后 5 分钟全涂满'],
    '860+': [`P5+P6 用约 ${p56} 分钟`, `放弃不超过 ${Math.min(k, 5)} 题`, '多篇组内先做看一篇就能答的题', `卡住超过 ${cut} 秒先涂最像的，做完回头看`, '插入句放最后，30 秒没思路就猜',
      '只在 P6 开头、第 147、176 题看表', '跳过的当场先涂；最后 5 分钟全涂满', 'NOT 题放到该篇最后']
  };
  return (L[band] || L[600]).slice(0, 8);
}
const BANDN = { '≤500': '入门档', 600: '600 档', 730: '730 档', '860+': '800+ 档' };
function battleCardHTML(open) {
  const ls = battleLines();
  return `<div class="card bc"><details ${open ? 'open' : ''}><summary><h2>你的考场作战卡 <span class="mut sm">${BANDN[E.band()]} · ${ls.length} 条</span></h2></summary>
    <ol>${ls.map(x => `<li>${esc(x)}</li>`).join('')}</ol><p class="mut sm">没做完是计划内的，不是失败。</p></details></div>`;
}
/* P1-1：主数字用天/周（照每天分钟数换算），小时只给区间（Planner.hoursText） */
function paceText(min) {
  if (!min) return '';
  const m = (E.st.settings && E.st.settings.daily_min) || 5, d = Math.max(1, Math.ceil(min / m));
  return `照现在的节奏约 ${d <= 10 ? d + ' 天' : Math.max(2, Math.round(d / 7)) + ' 周'}`;
}
/* P0-2 预测分呈现：low 不给数字（再做约 N 题）；mid 只给区间；high 给中值 + 区间；一律注“近似”。达标把握只在 mid/high 显示 */
const PROBW = p => p > 0.7 ? '很稳了' : p >= 0.3 ? '有希望，继续' : '还需要一段时间';
function predLine(pr) {
  if (pr.level === 'low') return `预测阅读分：估算中，再做约 ${pr.need} 题给出`;
  return pr.level === 'mid' ? `预测阅读分约 ${pr.lo}–${pr.hi}（近似）` : `预测阅读分 <b>${pr.p}</b> <span class="mut">（${pr.lo}–${pr.hi}，近似）</span>`;
}
function predBlock(pr, cls) {
  const lab = '<div class="mut sm">预测阅读分</div>';
  if (pr.level === 'low') return lab + `<div class="${cls}">估算中</div><p class="mut sm">再做约 ${pr.need} 题给出预测分 · 目标 ${pr.tg}</p>`;
  const prob = pr.prob != null ? `<p class="mut sm">达标把握 ${Math.round(pr.prob * 100)}% · ${PROBW(pr.prob)}</p>` : '';
  return lab + (pr.level === 'mid' ? `<div class="${cls}">约 ${pr.lo}–${pr.hi}</div><div class="mut sm">近似 · 目标 ${pr.tg}</div>`
    : `<div class="${cls}">${pr.p}</div><div class="mut sm">（${pr.lo}–${pr.hi}）近似 · 目标 ${pr.tg}</div>`) + prob;
}
/* 用 gap.nodes[].gain 替代考点数：“先补「X」「Y」，约 +N 分” */
function gainLine(pr) {
  const ns = pr.level !== 'low' && pr.gap && pr.gap.diff > 0 ? (pr.gap.nodes || []).filter(n => n.gain > 0).slice(0, 2) : [];
  return ns.length ? `先补${ns.map(n => `「${esc(n.nm)}」`).join('')}，约 +${ns.reduce((a, n) => a + n.gain, 0)} 分` : '';
}
/* 进度主句（今天页/入职结果共用，单一数据源 g.need） */
function needText(g, pr) {
  const n = g.need; if (!n || pr.level === 'low') return '';
  if (n.reached) return n.nodes ? `已够线，再稳 ${n.nodes} 个考点留出余量` : '已经够到目标了 ✓ 现在只需每天复习保持';
  if (!n.nodes) return '目标考点已全部达标，进入维持模式';
  return `离目标 ${pr.tg}：${paceText(n.min)}（先稳 ${n.nodes} 个考点，${n.hoursText}）`;
}
function vObResult(o) {
  const pr = API.predict(), g = API.progress(), res = o.res || {}, nt = needText(g, pr);
  const head = o.vskip && !E.st.diag ? '' : '';
  return `<div class="onb">${steps(2)}<div class="card"><h2>入职测试完成 ✓</h2>
    <p>${predLine(pr)}</p>
    ${nt ? `<p>${nt}</p>` : ''}
    ${res.strong && res.strong.length ? `<p class="sm">你拿得稳的：${res.strong.map(esc).join('、')}</p>` : ''}
    ${res.weak && res.weak.length ? `<p class="sm">最快涨分的 ${res.weak.length} 个：${res.weak.map(esc).join(' · ')}</p>` : ''}${head}</div>
    ${battleCardHTML(true)}
    <div class="thumb"><p class="ok sm">今天已算第 1 天 ✓</p><button class="btn full lg" data-act="obDone">明天见</button><button class="link" data-act="obMore">现在再做 5 分钟（可选）</button></div></div>`;
}
/* S7 每日提醒（可跳过）：建议时间按作息画像，没有画像就按现在这个时段（正在学的时间）；只做应用内提示，无推送 */
const RM_SLOT = { early: '07:30', morning: '10:00', noon: '12:30', afternoon: '15:30', evening: '20:30' };
function rmSuggest() {
  const c = API.profile().circadian || {}; if (c.best && RM_SLOT[c.best]) return RM_SLOT[c.best];
  const d = new Date(), m = d.getHours() * 60 + d.getMinutes(), r = Math.ceil(m / 30) * 30;
  if (r < 7 * 60 || r > 22 * 60) return '21:00';
  return String(Math.floor(r / 60)).padStart(2, '0') + ':' + (r % 60 ? '30' : '00');
}
const rmOk = v => /^([01]\d|2[0-3]):[0-5]\d$/.test(v || '');
/* P2-4：时间用自绘的 24 小时制 时/分 选择（原生 time input 会跟浏览器区域显示成“04:30 PM”） */
const p2 = n => String(n).padStart(2, '0');
function tmPick(id, v) {
  const [h, m] = (rmOk(v) ? v : rmSuggest()).split(':'), ms = [...new Set([...Array(12).keys()].map(i => p2(i * 5)).concat(m))].sort();
  const sel = (sid, list, cur, lb) => `<select id="${sid}" aria-label="${lb}" style="width:auto;padding:6px 10px;border-radius:20px">${list.map(x => `<option value="${x}"${x === cur ? ' selected' : ''}>${x}</option>`).join('')}</select>`;
  return `<span class="row tmp" id="${id}">${sel(id + 'H', [...Array(24).keys()].map(p2), h, '时')}<span>:</span>${sel(id + 'M', ms, m, '分')}</span>`;
}
const tmVal = id => { const h = ($('#' + id + 'H') || {}).value, m = ($('#' + id + 'M') || {}).value; return h && m ? h + ':' + m : ''; };
/* P0-4 提醒真正生效：(a) 加到手机日历——每日重复 .ics（RRULE:FREQ=DAILY，到点系统提醒，链接回应用）；
 * (b) 支持 Notification 的浏览器：应用开着（含后台）时到点用 SW showNotification / new Notification 弹本地通知；不支持就如实说明，引导用日历 */
const UA = () => (typeof navigator !== 'undefined' && navigator.userAgent) || '';
function appUrl() { try { return String(location.href).split('#')[0]; } catch (e) { return ''; } }
function icsText(hm) {
  const [h, m] = hm.split(':').map(Number), d = new Date(); if (d.getHours() * 60 + d.getMinutes() >= h * 60 + m) d.setDate(d.getDate() + 1);
  const ymd = d.getFullYear() + p2(d.getMonth() + 1) + p2(d.getDate()), n = new Date(), st = n.getUTCFullYear() + p2(n.getUTCMonth() + 1) + p2(n.getUTCDate()) + 'T' + p2(n.getUTCHours()) + p2(n.getUTCMinutes()) + '00Z', url = appUrl();
  return ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//toeic-reading//remind//ZH', 'CALSCALE:GREGORIAN', 'BEGIN:VEVENT', 'UID:toeic-reading-daily-' + Date.now() + '@local', 'DTSTAMP:' + st,
    'DTSTART:' + ymd + 'T' + p2(h) + p2(m) + '00', 'DURATION:PT5M', 'RRULE:FREQ=DAILY', 'SUMMARY:托业阅读 · 今天的 5 分钟', 'DESCRIPTION:打开应用做今天的活（约 5 分钟）' + (url ? '\\n' + url : ''),
    url ? 'URL:' + url : '', 'BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:托业阅读 · 今天的 5 分钟', 'TRIGGER:PT0M', 'END:VALARM', 'END:VEVENT', 'END:VCALENDAR'].filter(Boolean).join('\r\n') + '\r\n';
}
function ntSt() { if (typeof Notification === 'undefined') return 'no'; return Notification.permission === 'granted' ? ((E.st.settings || {}).notify === false ? 'off' : 'on') : Notification.permission === 'denied' ? 'denied' : 'ask'; }
function rmHow(v) {   // 提醒页 / 我的：日历按钮 + 通知状态（如实）
  const n = ntSt(), t = rmOk(v) ? v : '';
  const nl = n === 'no' ? '<span class="mut sm">这个浏览器不支持应用通知（iPhone 需先“添加到主屏幕”），用日历提醒最稳。</span>'
    : n === 'denied' ? '<span class="mut sm">通知被浏览器拦了，用日历提醒最稳。</span>'
    : n === 'on' ? `<span class="ok sm">✓ 通知已开：应用开着（含切到后台）时${t ? ' ' + t + ' ' : '到点'}弹出；关掉应用后靠日历提醒</span>`
    : '<button class="link" data-act="ntOn">同时开启通知（应用开着时到点弹出）</button>';
  return `<p class="rmhow"><button class="link" data-act="rmCal">加到手机日历（每天准时提醒）</button><br>${nl}</p>`;
}
let rmT = 0;
function rmArm() {   // 应用开着时排下一次本地通知；到点今天的活已做完就不弹
  try {
    if (rmT) { clearTimeout(rmT); rmT = 0; }
    const v = E.st && (E.st.settings || {}).remind; if (!rmOk(v) || ntSt() !== 'on') return;
    const [h, m] = v.split(':').map(Number), now = new Date(), at = new Date(now); at.setHours(h, m, 0, 0); if (at <= now) at.setDate(at.getDate() + 1);
    rmT = setTimeout(() => { rmT = 0; if (E.st && E.st.doneDay !== today()) ntShow('托业阅读 · 今天的 5 分钟', '今天的活还没做，点开接着来。'); rmArm(); }, Math.min(at - now, 2147483000));
  } catch (e) { }
}
function ntShow(title, body) {
  const o = { body, tag: 'toeic-daily', renotify: true };
  const fb = () => { try { new Notification(title, o); } catch (e) { } };
  try { if (navigator.serviceWorker && navigator.serviceWorker.getRegistration) navigator.serviceWorker.getRegistration().then(r => r ? r.showNotification(title, o) : fb(), fb); else fb(); } catch (e) { fb(); }
}
function swInit() { try { if (navigator.serviceWorker && /^https?:$/.test(location.protocol)) navigator.serviceWorker.register('sw.js').catch(() => { }); } catch (e) { } }
function vRemind(o) {
  const sg = rmSuggest(), sel = o.rm || sg, opts = [...new Set([sg, '08:00', '12:30', '21:00'])];
  return `<div class="onb">${steps(3)}${obStory('Dana：每天几点叫你一声？')}<div class="card"><h2>每天几点提醒你？</h2>
    <p class="mut sm">每天 ${sel} 叫你一声（约 5 分钟）。随时可在「我的」里改。</p>
    <div class="row wrapr">${opts.map(t => `<button class="chip ${t === sel ? 'on' : ''}" data-act="rmPick" data-v="${t}">${t === sg ? '建议 ' : ''}${t}</button>`).join('')}</div>
    <h3>或者自己定</h3>${tmPick('obRm', sel)}${rmHow(sel)}</div>
    <div class="thumb"><button class="btn full lg" data-act="rmSave">就这个时间</button><button class="link" data-act="rmSkip">先不设，跳过</button></div></div>`;
}
/* 今天页：到了提醒时间、今天的活还没做 → 一条应用内提示（当天可关） */
function rmTip(done) {
  const v = (E.st.settings || {}).remind, u = ui(); if (!rmOk(v) || done || u.rmX === today()) return '';
  const d = new Date(), hm = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
  if (hm < v) return '';
  return `<div class="card tipc rmtip"><span>⏰ ${v} 到了：今天的活还没做</span><span class="row"><button class="link mut" data-act="rmX">知道了</button></span></div>`;
}
function vOnboard(o) { return o.step === 'result' ? vObResult(o) : o.step === 'remind' ? vRemind(o) : vVocab(o); }

/* ---------- 今天 ---------- */
function dayName() { const h = new Date().getHours(); return h < 12 ? '上午' : h < 18 ? '下午' : '傍晚'; }
function weekDays() { const k = E.wkKey(); return Object.keys(E.st.days || {}).filter(d => E.wkKey(new Date(d + 'T12:00').getTime()) === k).length; }
function planSummary(p) {
  const c = { 5: 0, 6: 0, 7: 0, r: 0 };
  p.units.forEach(u => { if (u.kind === 'review') c.r += u.ids.length; else if (u.b) c[IT[u.ids[0]].p]++; else c[5] += u.ids.length; });
  c.r += (p.words || []).length;
  return [c[7] && `${c[7]} 封邮件`, c[5] && `${c[5]} 句审稿`, c[6] && `${c[6]} 段改稿`, c.r && `复习 ${c.r} 个`].filter(Boolean).join(' · ') || '今天的活已经排好';
}
function streakHTML() {
  const n = E.streakNow(), fz = E.freezeOk();
  return `<span class="mut sm streak">${n ? `连续 ${n} 天` : `本周 ${weekDays()} 天`} <b class="fz ${fz ? '' : 'used'}" title="${fz ? '断签保护：本周漏 1 天会自动补上' : '本周的断签保护已用过'}">❄${fz ? '' : '✓'}</b></span>`;
}
/* 作息建议：引擎给出 tip 才显示，每 2 周最多 1 次，可关 */
function circTip() {
  const set = E.st.settings || {}, u = ui(); if (set.circadian === false) return '';
  const c = API.profile().circadian; if (!c || !c.tip) return '';
  if (u.circAt && Date.now() - u.circAt < 14 * 864e5 && u.circTip !== c.best) return '';
  if (u.circClosed === c.best) return '';
  if (!u.circAt || u.circTip !== c.best) { u.circAt = Date.now(); u.circTip = c.best; }
  return `<div class="card tipc"><span>⏰ ${esc(c.tip)}</span><span class="row"><button class="link" data-act="circX">知道了</button><button class="link mut" data-act="circOff">不再提示</button></span></div>`;
}
/* P2-1：完成态给“明天还会来”的理由：明天先攻的考点 + 明天到期的复习数（题卡 + 生词，上限 20） */
function tmrLine() {
  const d = fxToday() + 1, due = o => Object.values(o || {}).filter(c => c && c.due != null && c.due <= d && c.rv !== fxToday()).length;
  const g = API.progress(), nr = Math.min(20, due(E.st.cards) + due(E.st.words)), nx = (g.next || [])[0];
  const t = [nx && `${g.mode === 'maintain' ? '巩固' : '先攻'}「${esc(nx.nm)}」`, nr && `复习 ${nr} 个`].filter(Boolean).join(' + ');
  return t ? `<div class="li"><span>明天</span><span>${t}</span></div>` : '';
}
function vToday() {
  const d = new Date(), wd = '日一二三四五六'[d.getDay()];
  const top = `<div class="hd"><h1>今天 · ${d.getMonth() + 1}月${d.getDate()}日 周${wd}</h1>${E.st.diag ? streakHTML() : ''}</div>
  ${ui().plain || ui().nostory ? '' : `<p class="scene">«${dayName()} · Halvorsen 运营部»</p>`}`;
  if (!E.st.diag) return top + `<div class="card task"><h2>入职第一天</h2><p class="sum">先定目标，再做一次入职测试（约 5 分钟 · 共 2 步），之后每天的活由系统来排。</p>
    <button class="btn full lg" data-act="diag">开始</button></div>`;
  const done = E.st.doneDay === today();
  const min = (E.st.settings && E.st.settings.daily_min) || 5;
  let main;
  if (S && S.paused) main = `<div class="card task"><h2>做到一半的活</h2><p class="sum">进度都在，接着上次的位置继续。</p><button class="btn full lg" data-act="start">继续</button></div>`;
  else if (done) main = `<div class="card task"><h2>今天的活干完了 ✓</h2><p class="sum">${ui().plain ? '明天见。' : 'Dana：辛苦了，明天见。'}</p>
    <div class="li"><span>本周</span><span><b>${Math.min(7, weekDays())}</b> / 5 天${weekDays() >= 5 ? ' ✓' : ''}</span></div>${tmrLine()}<button class="link" data-act="start" data-m="5">想再做 5 分钟</button></div>`;
  else {
    const p = API.plan(min), pm = Math.max(1, Math.round((p.estSec || min * 60) / 60));
    if (p.comeback) main = `<div class="card task"><h2>欢迎回来</h2><p class="sum">${ui().plain ? '' : 'Dana：'}今天先 ${pm} 分钟热身，进度都在。</p>
      <button class="btn full lg" data-act="start" data-m="${min}">${S ? '继续' : '开始热身'}</button></div>`;   // R21：不提断了几天、不显示积压
    else main = `<div class="card task"><h2>今天的活 · 约 ${Math.max(1, Math.round((p.estSec || min * 60) / 60))} 分钟</h2><p class="sum">${esc(p.first ? '先练入职测试里最弱的 2 个考点，再读 1 封短邮件' : planSummary(p))}</p>
      <button class="btn full lg" data-act="start" data-m="${min}">${S ? '继续' : '开始'}</button>
      <details><summary>今天时间多？ ˅</summary><div class="row wrapr"><button class="chip" data-act="start" data-m="15">多做 15 分钟</button>
      ${examLeft() != null && examLeft() >= 0 && examLeft() <= 1 ? '' : '<button class="chip" data-act="mock">紧急项目（全真模考）</button>'}</div></details></div>`;
  }
  const pr = API.predict(), g = API.progress(), b = wkSnap(g, pr), nt = needText(g, pr), gl = gainLine(pr);
  // P0-2：今天页不常驻分数，只给本周趋势（稳 / 上升，不写下降），点开才看数字
  const trend = pr.level === 'low' ? '估算中' : pr.p - (b.p || pr.p) >= 5 ? '上升' : '稳';
  const side = `<div class="card"><details class="pred"><summary><span class="mut sm">预测阅读分 · 本周趋势</span> <b>${trend}</b> ›</summary>${predBlock(pr, 'big')}</details>
    ${nt ? `<p class="sm">${nt}</p>` : ''}${gl ? `<p class="mut sm">${gl}</p>` : ''}</div>`;
  const ex = E.st.exam && examLeft() >= 0 && examLeft() <= 3 ? battleCardHTML(false) : '';
  const vre = E.st.ob && E.st.ob.vskip && !ui().vreX ? `<div class="card tipc"><span>补测词汇（约 3 分钟），推荐会更准</span><span class="row"><button class="link" data-act="vretest">去测</button><button class="link mut" data-act="vreX">关</button></span></div>` : '';
  return top + `<div class="grid2${done && !(S && S.paused) ? ' solo' : ''}"><div>${examCard()}${rmTip(done || (S && S.paused))}${main}${circTip() || vre}</div><div>${side}${ex}</div></div>`;
}
/* P1-8 考前节奏：≤21 天一行倒计时 + 本周重点；T-14/T-7 各推荐一次模考（可拆 P5+6 约 25 分钟 / P7 约 50 分钟两段）；
 * T-1 只做作战卡和轻复习；考试当天作战卡 +“考完回来填分数”；考后 14 天内未填分数时提示回填（接 API.calibrate） */
function examCard() {
  const L = examLeft(); if (L == null || L > 21 || L < -14) return '';
  const ex = new Date(E.st.exam + 'T00:00').getTime(), c = E.st.predCalib;
  if (L < 0) return c && c.at >= ex ? '' : `<div class="card tipc"><span>考完了？填一下真实阅读分，之后的预测会更准。</span><button class="link" data-act="goCalib">去填</button></div>`;
  if (L === 0) return `<div class="card exam"><h2>今天考试，按作战卡来 ✓</h2><p class="sum">不用再刷题。考完回来填一下分数。</p><button class="btn ghost full" data-act="goCalib">考完回来填分数</button></div>`;
  if (L === 1) return `<div class="card exam"><p><b>明天考试</b> · 今天只看作战卡 + 轻复习，早点休息。</p></div>`;
  const win = L <= 7 ? 7 : L <= 14 ? 14 : 0, since = ex - win * 864e5;
  const ms = win ? (E.st.mocks || []).filter(m => m.ts >= since) : [], full = ms.some(m => !m.part), has = p => full || ms.some(m => m.part === p);
  const focus = L > 14 ? '补最快涨分的考点' : L > 7 ? '做一次模考，找节奏' : '复习错题 + 熟悉作战卡';
  const mk = win && !(has('56') && has('7')) ? `<div class="row wrapr">${has('56') ? '' : '<button class="chip" data-act="mockPart" data-s="56">模考第 1 段 · P5+6（约 25 分钟）</button>'}${has('7') ? '' : '<button class="chip" data-act="mockPart" data-s="7">第 2 段 · P7（约 50 分钟）</button>'}</div>` : '';
  return `<div class="card exam"><p><b>距考试 ${L} 天</b> · 本周重点：${focus}</p>${mk ? `<p class="mut sm">这周建议做一次模考，可以分两段做。</p>${mk}` : ''}</div>`;
}
function examLeft() { return E.st.exam ? Math.round((new Date(E.st.exam + 'T00:00') - new Date(today() + 'T00:00')) / 864e5) : null; }

/* ---------- 复习：题卡 + 生词合计 ≤20；生词四选一自动评分 ---------- */
let WQ = null;
function revAlloc() {
  const it = E.dueItems(), ws = E.dueWords(), ni = Math.min(it.length, Math.max(20 - ws.length, 12)), nw = Math.min(ws.length, 20 - ni);
  return { it, ws, ni, nw };
}
function vReview() {
  const hd = '<div class="hd"><h1>复习</h1></div>';
  if (!E.st.diag) return hd + `<div class="card empty"><p>做完入职测试后，做错的题和你点过的生词会按记忆曲线出现在这里。</p><button class="btn full" data-act="diag">去做入职测试</button></div>`;
  const a = revAlloc(), n = a.ni + a.nw, g = API.progress(), tips = (E.st.tips || []).filter(t => t.t);
  const tl = tips.length ? `<details class="tips"><summary>顺便看看你记下的招 · ${tips.length} ›</summary>${tips.slice(-20).reverse().map(t => `<div class="li"><span class="sm">${esc(t.t)}</span></div>`).join('')}<p class="mut sm">遇到同类题时会在题目上方提醒你一次。</p></details>` : '';
  const main = n ? `<div class="card task"><h2>今天该复习 ${n} 个 · 约 ${Math.max(1, Math.round((a.ni * 40 + a.nw * 6) / 60))} 分钟</h2>
      <p class="sum">${[a.ni && `错题 ${a.ni}`, a.nw && `生词 ${a.nw}`].filter(Boolean).join(' · ')}</p><button class="btn full lg" data-act="rev">开始复习</button>
      <p class="mut sm">这些也会放进今天的活，不单独做也行。</p>${tl}</div>`
    : `<div class="card empty"><h2>今天没有要复习的，挺好。</h2><p class="mut">做题时点过的生词、做错的题，会在快忘的时候回来。</p><button class="btn full" data-act="goTab" data-t="today">去做今天的活</button>${tl}</div>`;
  // P2-2：只露 ROI 最高的 1 项、一个按钮（有复习任务时用次按钮，避免两个主按钮）；其余折叠成纯文字
  const nxs = g.next || [], mins = x => { const nd = (g.nodes || []).find(y => y.id === x.id); return nd && nd.remainMin ? Math.max(3, Math.min(30, nd.remainMin)) : 0; };
  const nx = nxs.length ? `<p class="sum">先练 <b>${esc(nxs[0].nm)}</b>${mins(nxs[0]) ? `（约 ${mins(nxs[0])} 分钟）` : ''}</p><button class="btn full ${n ? 'ghost' : ''}" data-act="weak" data-n="${esc(nxs[0].id)}">开始</button>${nxs.length > 1 ? `<details><summary>之后排着 · ${nxs.length - 1} ›</summary>${nxs.slice(1).map(x => `<div class="li"><span>${esc(x.nm)}</span>${mins(x) ? `<span class="mut sm">约 ${mins(x)} 分钟</span>` : ''}</div>`).join('')}</details>` : ''}` : '';
  const W = Object.keys(E.st.words || {});
  const lists = `<div class="card"><details><summary>生词本 · ${W.length} ›</summary>${W.length ? W.slice(-30).reverse().map(w => `<div class="li"><b>${esc(w)}</b><span class="mut sm">${esc(API.lookup(w).zh.slice(0, 24))}</span></div>`).join('') : '<p class="mut sm">做题时点生词，会自动加进来。</p>'}</details></div>`;
  return hd + `<div class="grid2"><div>${main}${nx ? `<div class="card"><h2>${ui().plain ? '最快涨分' : '主管带你练（最快涨分）'}</h2>${nx}</div>` : ''}</div><div>${lists}</div></div>`;
}
function wqOpts(w) {
  const zh = x => (API.lookup(x).zh || '').split(/[；;，,]/)[0].trim();
  const right = zh(w) || w, keys = Object.keys(D.dict || {}), out = new Set([right]);
  for (let k = 0; out.size < 4 && k < 200; k++) { const z = zh(keys[Math.floor(Math.random() * keys.length)]); if (z && z.length <= 12) out.add(z); }
  const o = [...out].sort(() => Math.random() - 0.5);
  return { o, a: o.indexOf(right) };
}
function vWordQuiz() {
  const w = WQ.ws[WQ.i], q = WQ.q || (WQ.q = wqOpts(w)), a = WQ.ans;
  return `<div class="qz"><div class="qh"><button class="x" data-act="wqX" aria-label="暂停">✕</button><div class="tt">复习 · 生词<small>${WQ.i + 1}/${WQ.ws.length}</small></div></div>
    <div class="qb pane"><div class="wq"><div class="vw">${esc(w)}</div><div class="thumb vopts">${q.o.map((x, i) => `<button class="opt ${a != null ? (i === q.a ? 'ok' : i === a ? 'no' : '') : ''}" data-act="wqA" data-i="${i}" ${a != null ? 'disabled' : ''}><b>${L4[i]}</b><span>${esc(x)}</span></button>`).join('')}
    <button class="opt ${a === -1 ? 'no' : ''}" data-act="wqA" data-i="-1" ${a != null ? 'disabled' : ''}><b>?</b><span class="mut">不知道</span></button>
    ${a != null && a !== q.a ? '<button class="btn full lg" data-act="wqN">下一个</button>' : ''}</div></div></div></div>`;
}

/* ---------- 进度：离目标 N 个考点 · X 小时 · 预测区间 · 职级 · 本周小结（不显示题数/正确率） ---------- */
const RANKN = RANKS.map(x => x[1]);
/* P1-2：职级按预测分档（UX §0.5，阈值同引擎 RANKS）；估算中时不给“还差几分” */
function rankOf(pr) {
  const i = pr.level === 'low' ? 0 : rIdx(pr.p), nx = RANKS[i + 1];
  return { i, nm: RANKN[i], next: nx && nx[1], at: nx && nx[0], low: pr.level === 'low' };
}
function wkSnap(g, pr) {   // 每周第一次打开时记周初基线，用于本周小结
  const k = E.wkKey(), W = E.st.wk = E.st.wk || {};
  if (!W[k]) { W[k] = { rem: g.need ? g.need.nodes : g.remainingNodes, p: pr.p, ach: (g.nodes || []).filter(x => x.achieved).map(x => x.id) }; Object.keys(W).sort().slice(0, -8).forEach(x => delete W[x]); }
  return W[k];
}
function vReviewWeek(g, pr) {
  const b = wkSnap(g, pr), k = E.wkKey(), d0 = new Date(k + 'T00:00'), d1 = new Date(d0.getTime() + 6 * 864e5);
  const fmt = d => `${d.getMonth() + 1}月${d.getDate()}日`, got = (g.nodes || []).filter(x => x.achieved && !b.ach.includes(x.id)).map(x => (ND[x.id] || {}).nm || x.id).slice(0, 3);
  const nx = (g.next || [])[0], days = weekDays(), say = got.length ? `“这周${esc(got[0])}稳多了，靠谱。”` : days ? '“这周的活都按时交了，稳。”' : '“休假回来，先处理几件简单的。”';
  return `<div class="card"><h2>本周小结 <span class="mut sm">${fmt(d0)}–${fmt(d1)}</span></h2>
    ${ui().plain ? '' : `<p class="say">Dana：${say}</p>`}
    <div class="li"><span>本周来了</span><span>${days} 天${days >= 4 ? ' ✓' : ''}</span></div>
    ${g.need && !g.need.reached && pr.level !== 'low' ? `<div class="li"><span>离目标还差</span><span>${g.need.nodes} 个考点${b.rem != null && b.rem > g.need.nodes ? `<span class="mut sm">（周初 ${b.rem}）</span>` : ''}</span></div>` : ''}
    <div class="li"><span>预测阅读分</span><span>${pr.level === 'low' ? '估算中' : pr.p - b.p >= 5 ? `${b.p} → ${pr.p}` : pr.p - b.p > -5 ? `${pr.level === 'mid' ? `约 ${pr.lo}–${pr.hi}` : pr.p} · 持平` : '小幅波动，正常'}</span></div>
    ${got.length ? `<div class="li"><span>这周拿下</span><span>${got.map(esc).join(' · ')}</span></div>` : ''}
    ${nx ? `<div class="li"><span>下周只盯一件事</span><span>${esc(nx.nm)}</span></div>` : ''}</div>`;
}
function vProgress() {
  const hd = '<div class="hd"><h1>进度</h1></div>';
  if (!E.st.diag) return hd + `<div class="card empty"><h2>还没有进度</h2><p class="mut">做完入职测试（约 5 分钟），这里会显示离目标还差多少、大约要多少小时。</p><button class="btn full" data-act="diag">去做入职测试</button></div>`;
  const g = API.progress(), pr = API.predict(), rk = rankOf(pr), n = g.need || {}, gl = gainLine(pr);
  // P0-1/P1-1：单一数据源 g.need（够达标的最少考点）；主数字用天/周，小时给区间，考点数降为次要
  const head = pr.level === 'low' ? `<div class="big">估算中</div><p class="mut">再练 2–3 次就能算出离目标还差多少。</p>`
    : n.reached ? (n.nodes ? `<div class="big">已够线 ✓</div><p>再稳 ${n.nodes} 个考点留出余量 · ${paceText(n.min)}</p>` : `<div class="big">已经够到目标了 ✓</div><p class="mut">现在只需每天复习保持。</p>`)
    : !n.nodes ? `<div class="big">目标考点已全部达标 ✓</div><p class="mut">进入维持模式，每天少量复习就够。</p>`
    : `<div class="mut sm">离目标 ${pr.tg}</div><div class="huge">${paceText(n.min).replace('照现在的节奏', '')}</div><p class="mut sm">照现在的节奏 · 先稳 ${n.nodes} 个考点（${n.hoursText}）</p>`;
  const main = `<div class="card hero">${head}${gl ? `<p class="sm">${gl}</p>` : ''}<div class="hr"></div>${predBlock(pr, 'big2')}</div>`;
  const rank = `<div class="card"><h2>职级 · ${rk.nm}</h2><div class="ladder">${RANKN.map((x, i) => `<i class="${i < rk.i ? 'd' : i === rk.i ? 'c' : ''}">${x}</i>`).join('')}</div>
    ${rk.low ? '<p class="mut sm">再练几次，职级会按预测分定下来。</p>' : rk.next ? `<p class="mut sm">预测分到 ${rk.at} 升${rk.next}</p>` : '<p class="mut sm">已经是经理了，保持住。</p>'}</div>`;
  const tm = g.targetMastery || 0.8, sc = v => Math.max(0, Math.min(100, Math.round((v - 0.3) / 0.7 * 100)));   // 条按掌握度 0.3–1 画，竖线 = 稳阈值
  const cur = (g.next || []).map(x => { const nd = (g.nodes || []).find(y => y.id === x.id), pct = Math.max(4, Math.min(sc(tm) - 2, sc(x.m || 0)));
    return `<div class="li"><span>${esc(x.nm)}${nd && nd.remainMin ? `<br><span class="mut sm">约 ${Math.max(3, Math.min(60, nd.remainMin))} 分钟可稳</span>` : ''}</span><span class="bar tkb" title="竖线 = 稳"><i style="width:${pct}%"></i><b class="tk" style="left:${sc(tm)}%"></b></span></div>`; }).join('');
  const nodes = `<div class="card"><h2>考点 <span class="mut sm">正在攻 ${(g.next || []).length} · 已稳 ${g.achievedNodes || 0}</span></h2>${cur || '<p class="mut sm">目标考点都稳了。</p>'}</div>`;
  const mk = (E.st.mocks || []).slice(-3).reverse().map(m => `<div class="li"><span>${new Date(m.ts).getMonth() + 1}月${new Date(m.ts).getDate()}日</span><span>约 ${m.scaled} 分</span></div>`).join('');
  const total = Object.keys(E.st.days || {}).length;
  return hd + `<div class="grid2"><div>${main}${rank}${nodes}</div><div>${battleCardHTML(wide())}${vReviewWeek(g, pr)}
    ${mk ? `<div class="card"><h2>紧急项目记录</h2>${mk}</div>` : ''}<p class="mut sm ctr">累计学习 ${total} 天</p></div></div>`;
}

/* P0-2：考完了？填真实阅读分 → Predict.calibrate，存 st.predCalib，以后的预测按它校准 */
function calibCard() {
  const c = E.st.predCalib;
  return `<div class="card" id="calib"><h2>考完了？填分数</h2><p class="mut sm">填上真实的阅读分，之后的预测会按你的实际情况校准。</p>
    <div class="row"><input id="mReal" class="inl" inputmode="numeric" placeholder="阅读分 5–495"><button class="chip" data-act="calib">保存</button></div>
    ${c && c.last ? `<p class="mut sm">已校准 ${c.n} 次 · 上次填 ${c.last.real} 分</p>` : ''}</div>`;
}
/* ---------- 我的 ---------- */
const FZ = [[0.9, '小'], [1, '标准'], [1.12, '大'], [1.25, '特大']];
function applyFz() { try { document.documentElement.style.setProperty('--fz', String(ui().fz || 1)); } catch (e) { } }
function vMe() {
  const u = ui(), L = Profiles.list(), set = E.st.settings || {}, pf = API.profile(), on = x => x ? '开' : '关';
  const sw = (k, v, act) => `<button class="chip ${v ? 'on' : ''}" data-act="${act || 'set'}" data-k="${k}">${on(v)}</button>`;
  const ls = E.st.listen;
  return `<div class="hd"><h1>我的</h1><span class="mut sm">${esc(Profiles.name())} · 阅读目标 ${E.rtg()}</span></div><div class="grid2"><div>
  <div class="card"><h2>阅读体验</h2>
    <div class="li"><span>字号</span><span class="row wrapr">${FZ.map(([v, n]) => `<button class="chip ${(u.fz || 1) === v ? 'on' : ''}" data-act="fz" data-v="${v}">${n}</button>`).join('')}</span></div>
    <div class="li"><span>剧情过渡（同事的一句话）</span>${sw('nostory', !u.nostory, 'tgl')}</div>
    <div class="li"><span>简洁外壳（不显示同事和剧情）</span>${sw('plain', u.plain)}</div>
    <div class="li"><span>用时环</span>${sw('showRing', !!u.showRing, 'tgl')}</div>
    <div class="li"><span>每日提醒</span><span class="row">${tmPick('mRm', set.remind)}<button class="chip" data-act="rmSet">保存</button><button class="chip ${rmOk(set.remind) ? '' : 'on'}" data-act="rmOff">关</button></span></div>
    ${rmOk(set.remind) ? rmHow(set.remind) : ''}
    <div class="li"><span>每天时长</span><span class="row">${[5, 10, 15].map(m => `<button class="chip ${(set.daily_min || 5) === m ? 'on' : ''}" data-act="dm" data-m="${m}">${m} 分钟</button>`).join('')}</span></div></div>
  <div class="card"><h2>越用越贴合</h2>
    <div class="li"><span>复习间隔</span><span class="mut sm">${pf.fsrs && pf.fsrs.personal ? '已按你的记忆速度调整' : '先用通用间隔，做得多了会按你的记忆速度调'}</span></div>
    <div class="li"><span>考点掌握</span><span class="mut sm">每做一题都会更新</span></div>
    <div class="li"><span>作息建议</span>${sw('circadian', set.circadian !== false, 'circ')}</div>
    <div class="li"><span>重置个性化（不删作答记录）</span><button class="chip" data-act="pReset">重置</button></div>
    <p class="mut sm">这些都只在你的设备上计算。</p></div></div><div>
  <div class="card"><h2>目标与考试</h2>
    <h3>目标总分</h3><div class="row wrapr">${[500, 600, 700, 800, 900].map(v => `<button class="chip ${v === (A._mtg || E.st.target) ? 'on' : ''}" data-act="mtg" data-v="${v}">${v}</button>`).join('')}</div>
    <h3>听力估分（可空）</h3><input id="mLs" inputmode="numeric" value="${ls || ''}" placeholder="不确定就空着">
    <h3>考试日期</h3><input id="mDate" type="date" value="${esc(E.st.exam || '')}"><p class="mut sm" id="mOut">${examTip(E.st.exam)}</p>
    <button class="btn ghost full" data-act="saveGoal">保存</button></div>
  ${calibCard()}
  <div class="card"><h2>数据</h2><div class="row wrapr"><button class="btn ghost" data-act="dl">导出数据（文件）</button><button class="btn ghost" data-act="exp">复制进度码</button></div>
    <p></p><input id="codeBox" placeholder="粘贴进度码导入"><p></p><button class="btn ghost full" data-act="imp">导入</button>
    <p></p>${u.clrArm ? `<div class="warnbox"><p>确定清空「${esc(Profiles.name())}」的全部进度？清空后不能恢复，建议先导出。</p><div class="row"><button class="btn danger" data-act="clr2">确定清空</button><button class="btn ghost" data-act="clr0">取消</button></div></div>` : '<button class="link mut" data-act="clr1">清空这个档案的数据…</button>'}</div>
  <div class="card"><h2>档案</h2>${L.map(p => `<div class="li"><span>${esc(p.name)}${p.id === Profiles.cur() ? ' ✓' : ''}</span>
    <span class="row">${p.id === Profiles.cur() ? '' : `<button class="chip" data-act="usep" data-id="${p.id}">切换</button><button class="chip" data-act="delp" data-id="${p.id}">删除</button>`}</span></div>`).join('')}
    <p></p><button class="btn ghost" data-act="newp">新档案</button></div></div></div>`;
}

/* ---------- 会话 ---------- */
function startSession(mode, units, extra) {
  if (!units || !units.length) { alert('没有可用的题目了'); return; }
  const nd0 = {}; units.forEach(u => u.ids.forEach(id => { const i = IT[id]; nd0[i.n] = E.mastery(i.n); }));
  const g = API.progress();
  S = Object.assign({ mode, units, ui: 0, qi: 0, ans: {}, lu: {}, mt: {}, t0: Date.now(), qt0: Date.now(), day: fxToday(), pred0: API.predict(), nd0,
    rem0: g.need ? g.need.nodes : null, fb: null, v: 'q', doc: 0, sc: {}, ppn: 0, tipN: 0 }, extra || {});
  if (mode === 'mock') { S.end = Date.now() + (S.part === '56' ? 25 : S.part === '7' ? 50 : 75) * 6e4; S.v = 'a'; }
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
  const ms = Date.now() - S.t0, p1 = API.predict(), g = API.progress();
  const nodes = Object.keys(S.nd0).map(n => ({ n, a: S.nd0[n], b: E.mastery(n) })).filter(x => x.b != null).map(x => Object.assign(x, { d: x.b - (x.a == null ? 0.5 : x.a) }));
  const p5 = ids.filter(id => IT[id].p === 5 && S.ans[id].ms), p5s = p5.reduce((s, id) => s + S.ans[id].ms, 0) / Math.max(1, p5.length) / 1000, p5t = p5.reduce((s, id) => s + IT[id].t, 0) / Math.max(1, p5.length);
  R = { mode: S.mode, n: ids.length, ok, ms, p0: S.pred0, p1, nodes, rem0: S.rem0, need: g.need, rem1: g.need ? g.need.nodes : null, p5: p5.length ? [Math.round(p5s), Math.round(p5t)] : null, form: S.form };
  if (S.mode === 'mock') { R.scaled = Math.round(E.scaled(ok / Math.max(1, ids.length) * 100) / 5) * 5; E.st.mocks.push(Object.assign({ ts: Date.now(), form: S.form, ok, n: ids.length, scaled: R.scaled, ms }, S.part ? { part: S.part } : {}));
    R.part = S.part || null; const mh = ui().mockHalf; ui().mockHalf = S.part && !(mh && mh.f === S.form && mh.done && mh.done !== S.part) ? { f: S.form, done: S.part } : null; }
  if (S.mode === 'diag') {
    E.st.diag = true; const o = E.st.ob = E.st.ob || {};
    const seen = Object.keys(S.nd0).map(n => ({ n, m: E.mastery(n) })).filter(x => x.m != null && ND[x.n]);
    o.step = 'result'; o.res = { strong: seen.filter(x => x.m >= 0.62).sort((a, b) => b.m - a.m).slice(0, 2).map(x => ND[x.n].nm),
      weak: (g.next || []).slice(0, 3).map(x => x.nm) };
    if (!o.res.weak.length) o.res.weak = seen.sort((a, b) => a.m - b.m).slice(0, 3).map(x => ND[x.n].nm);
  }
  if (S.mode === 'train' || S.mode === 'diag') E.st.doneDay = today();
  E.st.hist.push([Date.now(), p1.p]);
  E.log('end', { mode: S.mode, n: ids.length, ok, ms });
  const wasDiag = S.mode === 'diag'; S.done = true; S = null; tab = 'today'; if (wasDiag) R = null; save(); render();
}
/* P0-2：结算默认不显示分数；只在上涨 ≥5 分或跨职级档时显示一行；下降不显示（放进周报写“小幅波动”）；估算中不显示 */
const rIdx = p => Math.max(0, RANKS.filter(x => p >= x[0]).length - 1);   // 预测分 → 职级档（UX §0.5，阈值同引擎 RANKS）
function resPred(r) {
  const a = r.p0, b = r.p1; if (!a || !b || b.level === 'low' || r.mode === 'mock') return '';
  const up = b.p - a.p, ra = rIdx(a.level === 'low' ? 0 : a.p), rb = rIdx(b.p);
  if (rb > ra) return `<p class="say">${ui().plain ? '' : 'Dana：'}下周起你是${RANKS[rb][1]}了。</p><p class="sm">${predLine(b)}</p>`;
  return up >= 5 ? `<p class="sm">${predLine(b)} <span class="ok">↑ ${up}</span></p>` : '';
}
/* 10 秒结算：写 2–3 条具体进步，不显示题数和正确率 */
function vResult() {
  const r = R, ls = [];
  if (r.mode === 'mock') ls.push(r.part ? `模考${r.part === '56' ? '第 1 段（P5+6）' : '第 2 段（P7）'}交付：按这一段推算约 ${r.scaled} 分` : `紧急项目交付：预估阅读 ${r.scaled} 分`);
  r.nodes.filter(x => x.d > 0.02).sort((a, b) => b.d - a.d).slice(0, 2).forEach(x => ls.push(`${esc((ND[x.n] || {}).nm || x.n)}：又稳了一点`));
  if (r.p5 && r.p5[0] <= r.p5[1]) ls.push(`审稿节奏稳在考场节奏内：平均 ${r.p5[0]} 秒/句`);
  // P0-1：只计够达标的最少考点；N 下降才写“−k”，上升静默（UX §11.2）；预测估算中不写
  if (r.need && r.p1.level !== 'low') { if (r.need.reached) { if (r.rem0 > r.rem1) ls.push('离目标又近了一步：已够线'); } else if (r.rem1) ls.push(`离目标还差 ${r.rem1} 个考点${r.rem0 != null && r.rem0 > r.rem1 ? `（−${r.rem0 - r.rem1}）` : ''} · ${r.need.hoursText}`); }
  if (ls.length < 2 && !r.nodes.some(x => x.d > 0.02)) ls.unshift('碰到几个新考点，已经记下，明天换更顺手的题。');
  const t = Math.round(r.ms / 1000), title = r.mode === 'diag' ? '入职测试做完了 ✓' : `${dayName()}的活干完了 ✓`;
  return `<div class="res"><div class="hd"><h1>${title}</h1>${t >= 60 ? `<span class="mut sm">用时约 ${Math.round(t / 60)} 分钟</span>` : ''}</div>
  <ul>${ls.slice(0, 3).map(x => `<li>${x}</li>`).join('')}</ul>${resPred(r)}
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
  if (!ui().showRing && S.mode !== 'mock') return '';   // P1-7：计时环默认隐藏（模考除外），可在设置里打开
  return `<svg class="ring" viewBox="0 0 36 36"><circle class="bg" cx="18" cy="18" r="15"/><circle id="ringFg" class="fg" cx="18" cy="18" r="15" stroke-dasharray="94.25" stroke-dashoffset="94.25" transform="rotate(-90 18 18)"/></svg>`;
}
function vQuiz() {
  const u = unit(), id = curId(), it = IT[id], b = bundle(), part = it.p;
  const lab = S.mode === 'mock' ? '紧急项目' : S.mode === 'diag' ? '入职测试' : part === 5 ? '审稿' : part === 6 ? '改稿' : '收件箱';
  const sub = part === 7 && b ? (b.docs.length > 1 ? `Part 7 ${b.docs.length === 2 ? '双篇' : '三篇'}` : 'Part 7 单篇') : 'Part ' + part;
  const tot = S.units.length, dots = tot <= 12 ? `<div class="dots">${S.units.map((x, i) => `<i class="${i < S.ui ? 'd' : i === S.ui ? 'c' : ''}"></i>`).join('')}</div>` : `<span class="mut sm">${S.ui + 1}/${tot}</span>`;
  const sc = part === 7 && b && b.docs.some(d => KIND(d.t) === 'chat') ? ['运营部群里有几条新消息', 'Leo 把你拉进了一个群聊'] : SCENE[part];
  // P1-3：剧情句只在 Part 切换时出现，放在标题副标题位置 2.5 秒后淡出换回 Part 标签，不占阅读区、不盖内容
  let story = '';
  if (!ui().plain && !ui().nostory && S.mode !== 'mock' && !S.noStory) {
    if (S.stP !== part) { S.stP = part; S.stAt = Date.now(); }
    const el = Date.now() - (S.stAt || 0);
    if (el < 2600) story = `<span class="sts" style="animation-delay:-${el}ms">«${esc(sc[S.ui % 2])}»</span>`;
  }
  const head = `<div class="qh"><button class="x" data-act="pause" aria-label="暂停">✕</button><div class="tt">${lab}<small>${story}<span class="${story ? 'stb' : ''}"${story ? ` style="animation-delay:-${Date.now() - S.stAt}ms"` : ''}>${sub}</span></small></div>${dots}${ringSvg(id)}<button class="mm" data-act="menu" aria-label="更多">⋯</button></div>`;
  if (!b) return `<div class="qz">${head}<div class="qb pane" id="pq">${vP5(it, id)}</div></div>`;
  const multi = b.docs.length > 1, refs = refsOf(it, b), di = S.docPinned != null ? S.doc : (refs.doc >= 0 && !S.ans[id] ? refs.doc : S.doc);
  S.doc = Math.min(di, b.docs.length - 1);
  // P1-3：手机上文章切换和文档标签合成一行：[报道 1][群聊 2]｜[题目 1/5]
  const segA = multi ? b.docs.map((d, i) => `<button class="${S.v === 'a' && i === S.doc ? 'on' : ''}" data-act="docv" data-i="${i}">${TXN[d.t] || '文本'} ${i + 1}${i === refs.doc && S.v !== 'a' ? '<b>•</b>' : ''}</button>`).join('') : `<button class="${S.v === 'a' ? 'on' : ''}" data-act="view" data-v="a">文章</button>`;
  const seg = `<div class="seg">${segA}<button class="${S.v === 'q' ? 'on' : ''}" data-act="view" data-v="q">题目 ${S.qi + 1}/${u.ids.length}</button></div>`;
  return `<div class="qz">${head}${seg}<div class="qb"><div class="split" id="split" data-v="${S.v}" style="--sp:${ui().split || 55}%">
    <div class="pane pa" id="pa">${vPassage(b, it, id, refs, multi)}</div><div class="dv" id="dv" title="拖动调整，双击复位"></div>
    <div class="pane pq" id="pq">${vQs(b, u, it, id, refs)}</div></div></div>${S.v === 'a' ? vDrawer(b, u, it, id) : S.ans[id] ? '' : '<button class="fab" data-act="flip" aria-label="切换">⇄</button>'}</div>`;
}
/* P1-4：手机文章视图底部常驻当前题干，点开成半屏抽屉直接作答（≥768 不显示；切换保留各自滚动位置） */
function vDrawer(b, u, it, id) {
  const a = S.ans[id], open = !!S.dr, show = a && S.mode !== 'mock';
  const short = b.p === 6 ? `第 ${it.q} 空${it.s ? '：' + it.s : ''}` : `${it.q}. ${it.s || ''}`;
  const body = open ? `<div class="qdb">${b.p === 6 ? '' : `<p class="stem">${rich(it.s || '')}</p>`}${vOpts(it, id)}${show ? `<div class="qdf"><b>${a.c === it.a ? '答对了' : '正确答案'} (${L4[it.a]})</b><span class="row"><button class="btn ghost" data-act="view" data-v="q">看解析</button><button class="btn" data-act="next">下一题</button></span></div>` : ''}</div>` : '';
  return `<div class="qd ${open ? 'open' : ''}"><div class="qdh"><button class="qdt" data-act="dr" aria-expanded="${open}"><span class="qdn">${open ? '▾' : '▴'} 题目 ${S.qi + 1}/${u.ids.length}${a ? ' ✓' : ''}</span><span class="qds">${esc(short)}</span></button><button class="qdq" data-act="view" data-v="q" aria-label="去题目页">⇄</button></div>${body}</div>`;
}
/* P1-9：同类题（同主考点）出现时，在题干上方提示 1 次记下的招；每条招只提示一次（t.hinted） */
function tipHint(it, id) {
  S.tipH = S.tipH || {};
  if (!(id in S.tipH)) {
    const t = S.mode === 'mock' ? null : (E.st.tips || []).find(x => x.t && !x.hinted && x.id !== id && (x.n || (IT[x.id] || {}).n) === it.n);
    S.tipH[id] = t ? t.t : null; if (t) t.hinted = Date.now();
  }
  return S.tipH[id] ? `<div class="tiph">☆ 你记过的招：${esc(S.tipH[id])}</div>` : '';
}
function vP5(it, id) {
  const a = S.ans[id], s = (it.s || '').replace(/-{3,}|_{3,}|\(\s*\)/, '\u0004');
  const doc = rich(s).replace('\u0004', `<span class="gap">${a ? esc(it.o[a.c] || '') : '&nbsp;'}</span>`);
  const who = ui().plain ? '选择' : '批注 · Ken：这里用哪个？';
  return `${tipHint(it, id)}<div class="p5"><div class="paper"><div class="lab">文档 · 第 ${it.q} 句</div>${doc}</div>
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
  const sbs = show.length > 1;
  return (sbs ? '' : tabs) + (sbs ? '<div class="sbs">' : '') + show.map(i => {
    const d = b.docs[i]; let x = d.x;
    if (refs.q && !done) x = markIn(x, refs.q, '1') || x;
    if (bp) x = markIn(x, bp, '2') || x;
    const h = docHTML(d, i, { x, blank: b.p === 6 && qs.size ? blank : null, ins: b.p === 7,
      mk: k => k === '1' ? '<mark class="ref" id="mref">' : '<mark class="basis" id="mbasis">' });
    return sbs ? `<div><div class="sbh">${TXN[d.t] || '文本'} ${i + 1}/${b.docs.length}</div>${h}</div>` : h;
  }).join('') + (sbs ? '</div>' : '');
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
  return nav + tipHint(it, id) + stem + vOpts(it, id) + vFb(it, id);
}
function vOpts(it, id) {
  const a = S.ans[id], show = a && S.mode !== 'mock';
  return `<div class="opts">${it.o.map((o, i) => {
    const cls = show ? (i === it.a ? 'ok' : i === a.c ? 'no' : '') : (a && a.c === i ? 'ok' : '');
    return `<button class="opt ${cls}" data-act="ans" data-c="${i}" ${a ? 'disabled' : ''}><b>${L4[i]}</b><span>${esc(o)}</span><span class="k">${i + 1}</span></button>`;
  }).join('')}</div>${S.mode === 'diag' ? '<p class="mut sm hint">不会就选一个，继续下一题</p>' : ''}`;
}
/* P1-7：不显示每题秒数/目标；只有连续 3 题都 ≥1.5 倍参考用时，才温和提示一次（每次练习最多一次） */
function slowHint(id) {
  if (S.slowH && S.slowH !== id) return '';
  if (!S.slowH) {
    const xs = Object.keys(S.ans).filter(q => IT[q] && IT[q].t && S.ans[q].ms).slice(-3);
    if (xs.length < 3 || xs[2] !== id || !xs.every(q => S.ans[q].ms >= IT[q].t * 1500)) return '';
    S.slowH = id;
  }
  return '<p class="sm slowh">最近几题想得比较久。卡住时先选最像的，做完再回头看，正确率通常不掉。</p>';
}
function vFb(it, id) {
  const a = S.ans[id]; if (!a || S.mode === 'mock') return '';
  if (S.fb === 'fast') return `<p class="fast">✓ 对</p>`;
  const x = API.explain(id), wrong = a.c !== it.a, mine = wrong && a.c >= 0 ? x.dis[L4[a.c]] : '';
  const L = API.lesson(it.n), nm = (ND[it.n] || {}).nm || '';
  const saved = (E.st.tips || []).some(t => t.id === id);
  const tip = wrong && x.tip ? `<div class="tip"><span><b>记一招</b> ${esc(x.tip)}</span><button class="chip ${saved ? 'on' : ''}" data-act="tip">${saved ? '已记下' : '记下☆'}</button>${saved ? '<span class="mut sm tipok">下次遇到同类题会提醒你</span>' : ''}</div>` : '';
  let pp = '';
  if (it.p === 7 && x.pp.length && (S.ppShown === id || S.ppn < 2)) { if (S.ppShown !== id) { S.ppn++; S.ppShown = id; } const p = x.pp[0];
    pp = `<div class="pp">${ui().plain ? '' : 'Leo 的备忘：'}这两个说法是一回事<br>原文 <b>${esc(p[0])}</b> ↔ 选项 <b>${esc(p[1])}</b></div>`; }
  const bj = it.p === 7 && basisPhrase(id) ? ` <a class="ref" data-act="jump" data-to="basis">在原文里看</a>` : '';
  return `<div class="fb"><div class="ans">${wrong ? '正确答案' : '答对了'} (${L4[it.a]}) ${esc(it.o[it.a])}</div>${slowHint(id)}
    <dl>${x.basis ? `<dt>依据</dt><dd>${esc(x.basis)}${bj}</dd>` : ''}${x.why ? `<dt>为什么</dt><dd>${esc(x.why)}</dd>` : ''}${mine ? `<dt>你选的</dt><dd>(${L4[a.c]}) ${esc(mine)}</dd>` : ''}</dl>
    ${tip}${pp}${nm ? `<p class="mut sm">考点：${esc(nm)}</p>` : ''}
    <div class="nextbar">${it.p !== 5 ? '<button class="btn ghost mo" data-act="view" data-v="a">看原文</button>' : ''}${L && wrong ? `<button class="btn ghost" data-act="lesson">60 秒小讲解</button>` : ''}<button class="btn" style="flex:1" data-act="next">下一题</button></div></div>`;
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
  const hitOpt = () => { const q = p.getBoundingClientRect(); return $$('.opt').some(o => { const x = o.getBoundingClientRect(); return !(x.bottom <= q.top || x.top >= q.bottom || x.right <= q.left || x.left >= q.right); }); };
  if (!wide() && el.closest('.paper')) {   // 手机 P5：选项在拇指区，浮层贴在词下方的空白里，盖住选项就翻到词上方
    p.classList.add('bubble', 'mb'); p.style.left = '8px'; const pb = el.closest('.paper').getBoundingClientRect(); p.style.top = (pb.bottom + 8) + 'px';
    requestAnimationFrame(() => { if (hitOpt()) p.style.top = Math.max(8, r.top - p.offsetHeight - 6) + 'px'; });
  } else if (!wide()) {
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
  const o = E.st && ob();
  if (o && o.step === 'vtest' && o.vt && !o.vt.paused && !S) { const c = $('#vClock'); if (c) c.textContent = vtClock(o.vt); if (!vtLeft(o.vt) && !o.vt.chk) A.vend(); return; }
  if (!S || S.done || S.paused) return;
  const f = $('#ringFg'); if (!f || !f.setAttribute) return;
  if (S.mode === 'mock') { const left = Math.max(0, S.end - Date.now()); f.setAttribute('stroke-dashoffset', String(94.25 * left / 4.5e6)); if (!left) finish(); return; }
  const id = curId(), it = IT[id]; if (!it || S.ans[id]) return;
  f.setAttribute('stroke-dashoffset', String(94.25 * (1 - Math.min(1, spent(id) / (it.t * 1000)))));
}

/* ---------- 动作 ---------- */
const A = {
  tg(el) { $$('[data-act=tg]').forEach(b => b.classList.toggle('on', b === el)); A._tg = +el.dataset.v; const o = $('#sTotOther'); if (o) o.value = ''; s1Upd(); },
  noDate(el) { A._noDate = !A._noDate; el.classList.toggle('on', A._noDate); const i = $('#sDate'); if (i) i.disabled = A._noDate; s1Upd(); },
  impOpen() { const c = prompt('粘贴进度码'); if (!c) return; try { const o = Code.dec(c); if (!o || !o.st) throw 0; Profiles.create(o.name || '导入'); E.st = o.st; setupNew = false; save(); boot(); } catch (e) { alert('进度码不对'); } },
  setupGo(el) {
    const o = s1Vals();
    if (o.exam && examTip(o.exam).indexOf('已经过了') >= 0) return s1Upd();
    const nm = ((($('#sName') || {}).value) || '').trim() || (Profiles.list().length ? '档案 ' + (Profiles.list().length + 1) : '我');
    Profiles.create(nm); E.st = newState(o.total, o.exam); E.st.rtg = o.rtg; E.st.listen = o.listen || null; setupNew = false;
    E.log('goal_set', { total: o.total, listen: o.listen || null, rtg: o.rtg });
    if (el && el.dataset.d === '1') E.st.ob = { step: 'dintro', vskip: true };   // P0-3：先诊断（起始难度用默认序列），词汇补测可选
    A._tg = A._lsU = A._noDate = undefined; save(); render();
  },
  setupCancel() { setupNew = false; render(); },
  diag() {
    const o = E.st.ob;
    if (S && S.mode === 'diag') { S.paused = false; S.qt0 = Date.now(); save(); return render(); }
    if (!E.st.diag && (!o || o.step === 'done')) { E.st.ob = { step: 'dintro', vskip: true }; save(); return render(); }
    if (o && (o.step === 'vocab' || o.step === 'vtest')) return render();
    if (o) o.step = 'diag'; startSession('diag', E.diagPlan());
  },
  /* 词汇摸底 */
  vstart() { const o = E.st.ob; o.vt = o.vt || vtNew(); o.vt.t0 = Date.now(); o.vt.paused = false; o.step = 'vtest'; save(); render(); },
  vk(el) {
    const o = E.st.ob, vt = o.vt, y = +el.dataset.y, w = vt.q[vt.i]; if (!w) return A.vend();
    vt.a.push([vt.i, y]);
    if (y && w[1] && vt.nc < 6 && (vt.a.length % 6 === 3 || Math.random() < 0.12)) {   // 抽查：只抽点了“认识”的真词
      const others = vt.q.filter(x => x[1] && x[0] !== w[0] && x[3]).map(x => x[3].split(/[；;，,]/)[0]).filter((x, i, a) => a.indexOf(x) === i).sort(() => Math.random() - 0.5).slice(0, 3);
      const right = (w[3] || '').split(/[；;，,]/)[0], opts = [right].concat(others).sort(() => Math.random() - 0.5);
      if (right && others.length === 3) { vt.chk = { w: w[0], o: opts, a: opts.indexOf(right), k: vt.a.length - 1 }; vt.nc++; }
    }
    vt.i++; E.log('vocab_ans', { w: w[0], y });
    if (!vt.chk && (vt.i >= vt.q.length || !vtLeft(vt))) return A.vend();
    save(); render();
  },
  vchk(el) { const vt = E.st.ob.vt, c = vt.chk, i = +el.dataset.i; if (i !== c.a) vt.a[c.k][1] = 0; E.log('vocab_chk', { w: c.w, ok: i === c.a }); vt.chk = null;
    if (vt.i >= vt.q.length || !vtLeft(vt)) return A.vend(); save(); render(); },
  vpause() { const vt = E.st.ob.vt; vt.el += Date.now() - vt.t0; vt.t0 = 0; vt.paused = true; save(); render(); },
  vresume() { const vt = E.st.ob.vt; vt.t0 = Date.now(); vt.paused = false; save(); render(); },
  vend() { const o = E.st.ob, vt = o.vt; if (vt.t0) { vt.el += Date.now() - vt.t0; vt.t0 = 0; } o.voc = vtScore(vt); o.vskip = false; E.st.vocab = o.voc.n; o.step = 'dintro'; delete o.vt;
    E.log('vocab_done', o.voc); save(); render(); },
  vskip() { const o = E.st.ob; o.vskip = true; o.voc = { n: 3000, biz: null }; E.st.vocab = E.st.vocab || 3000; delete o.vt; o.step = E.st.diag ? 'done' : 'dintro'; if (E.st.diag) tab = 'today'; save(); render(); },
  vretest() { E.st.ob = { step: 'vocab', again: 1 }; save(); render(); },
  vreX() { ui().vreX = 1; save(); render(); },
  obDone() { const o = E.st.ob; if (o.step === 'result' && (E.st.settings || {}).remind === undefined) { o.step = 'remind'; o.then = 'done'; save(); return render(); } o.step = 'done'; tab = 'today'; save(); render(); },
  obMore() { const o = E.st.ob; if (o.step === 'result' && (E.st.settings || {}).remind === undefined) { o.step = 'remind'; o.then = 'more'; save(); return render(); } o.step = 'done'; save(); A.start({ dataset: { m: 5 } }); },
  rmPick(el) { E.st.ob.rm = el.dataset.v; save(); render(); },
  rmEnd(v) { const o = E.st.ob; E.setSetting('remind', v); rmArm(); const more = o.then === 'more'; o.step = 'done'; delete o.then; delete o.rm; tab = 'today'; save(); if (more) return A.start({ dataset: { m: 5 } }); render(); },
  rmSave() { const v = tmVal('obRm') || E.st.ob.rm || rmSuggest(); A.rmEnd(rmOk(v) ? v : rmSuggest()); },
  rmSkip() { A.rmEnd(false); },
  rmSet() { const v = tmVal('mRm'); if (!rmOk(v)) return; E.setSetting('remind', v); delete ui().rmX; save(); rmArm(); render(); },
  rmOff() { E.setSetting('remind', false); save(); rmArm(); render(); },
  rmX() { ui().rmX = today(); save(); render(); },
  rmCal() {
    const v = tmVal('obRm') || tmVal('mRm') || (E.st.settings || {}).remind; if (!rmOk(v)) return;
    if (/MicroMessenger/i.test(UA())) return modal('<div class="res"><h2>请先用浏览器打开</h2><p class="mut">微信里加不了日历：点右上角 ··· → 「在浏览器打开」，再点「加到手机日历」。</p><button class="btn full" data-act="closeM">好</button></div>');
    const txt = icsText(v); E.log('remind_ics', { t: v });
    if (/iP(hone|ad|od)/.test(UA())) { location.href = 'data:text/calendar;charset=utf-8,' + encodeURIComponent(txt); return; }   // iOS Safari 直接弹“添加到日历”
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([txt], { type: 'text/calendar;charset=utf-8' })); a.download = 'toeic-daily-' + v.replace(':', '') + '.ics';
    document.body.appendChild(a); a.click(); a.remove();
    modal('<div class="res"><h2>已生成日历文件</h2><p class="mut">打开下载的 .ics 文件，选「添加到日历」，之后每天 ' + v + ' 系统会准时提醒你。</p><button class="btn full" data-act="closeM">好</button></div>');
  },
  ntOn() {
    if (typeof Notification === 'undefined') return render();
    Notification.requestPermission().then(p => { E.setSetting('notify', p === 'granted'); save(); rmArm(); render(); if (p === 'granted') ntShow('通知已开启', '到点会在这里叫你一声。'); }).catch(() => render());
  },
  goTab(el) { tab = el.dataset.t; render(); },
  weak(el) { const u = E.weakPlan(el.dataset.n); startSession('train', u); },
  circX() { save(); render(); ui().circClosed = (API.profile().circadian || {}).best; save(); render(); },
  circOff() { E.setSetting('circadian', false); save(); render(); },
  circ() { E.setSetting('circadian', (E.st.settings || {}).circadian === false); save(); render(); },
  pReset() { if (!confirm('重置个性化？作答记录不会删。')) return; delete E.st.fsrsFit; const u = ui(); delete u.circAt; delete u.circTip; delete u.circClosed; E.log('personal_reset', {}); E.fxReplay(); save(); render(); },
  tgl(el) { const k = el.dataset.k; ui()[k] = !ui()[k]; save(); render(); },
  fzs(el) { const i = Math.max(0, FZ.findIndex(f => f[0] === (ui().fz || 1))), j = Math.min(FZ.length - 1, Math.max(0, i + +el.dataset.d)); ui().fz = FZ[j][0]; save(); applyFz(); A.menu(); },   // P2-5：阅读中 ··· 菜单 A−/A+，即时生效并记住
  fz(el) { ui().fz = +el.dataset.v; save(); render(); },
  mtg(el) { A._mtg = +el.dataset.v; render(); },
  saveGoal() {
    const t = A._mtg || E.st.target, ls = +(($('#mLs') || {}).value) || 0, dt = ($('#mDate') || {}).value || '';
    if (dt && examTip(dt).indexOf('已经过了') >= 0) { const o = $('#mOut'); if (o) o.innerHTML = examTip(dt); return; }
    E.st.target = t; E.st.listen = ls || null; E.st.rtg = rtgCalc(t, ls);
    if (dt !== (E.st.exam || '')) { E.st.exam = dt; E.log('exam_date_set', { tz: -new Date().getTimezoneOffset(), exam_date: dt }); }
    E.log('goal_set', { total: t, listen: ls || null, rtg: E.st.rtg }); A._mtg = null; save(); render();
  },
  dl() {
    const blob = JSON.stringify({ app: 'toeic-r-v2', name: Profiles.name(), exported: new Date().toISOString(), st: E.st });
    try { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([blob], { type: 'application/json' })); a.download = 'toeic-reading-' + today() + '.json'; document.body.appendChild(a); a.click(); a.remove(); } catch (e) { A.exp(); }
  },
  clr1() { ui().clrArm = 1; render(); },
  clr0() { ui().clrArm = 0; render(); },
  clr2() { const id = Profiles.cur(); E.st.ui.clrArm = 0; S = null; WQ = null; Profiles.remove(id); E.st = null; if (Profiles.cur()) return boot(); setupNew = true; render(); },
  recover() { if (S) { S.paused = true; } WQ = null; R = null; tab = 'today'; save(); render(); },
  retry() { render(); },
  reload() { try { location.reload(); } catch (e) { render(); } },
  errCopy() { try { navigator.clipboard.writeText(A._err || ''); } catch (e) { } },
  /* 生词四选一 */
  wqA(el) { const i = +el.dataset.i, w = WQ.ws[WQ.i], ok = i === WQ.q.a; WQ.ans = i; E.scheduleWord(w, ok ? 2 : 0); E.log('wordrev', { w, g: ok ? 2 : 0, mc: 1, tz: -new Date().getTimezoneOffset() }); save(); render();
    if (ok) { const k = WQ.i; setTimeout(() => { if (WQ && WQ.i === k && WQ.ans != null) A.wqN(); }, 700); } },
  wqN() { WQ.i++; WQ.q = null; WQ.ans = null; if (WQ.i >= WQ.ws.length) { const ni = WQ.ni; WQ = null; $('#app').classList.remove('quiz'); if (ni) return startSession('review', E.reviewUnits(ni)); modal('<div class="res"><h2>复习做完了 ✓</h2><p class="mut">这些词会在快忘的时候再回来。</p><button class="btn full" data-act="closeM">好</button></div>'); return render(); } render(); },
  wqX() { WQ = null; $('#app').classList.remove('quiz'); render(); },
  start(el) {
    if (S) { S.paused = false; S.qt0 = Date.now(); save(); return render(); }
    const m = +(el && el.dataset.m) || 5, p = API.plan(m);
    if (p.words && p.words.length) E.log('plan_words', { n: p.words.length });
    startSession('train', p.units);
  },
  more() { R = null; A.start({ dataset: { m: 5 } }); },
  mockPart(el) {
    const sp = el.dataset.s, mh = ui().mockHalf, f = mh && mh.f && mh.done !== sp ? mh.f : E.nextForm(); if (!f) return alert('整套题都做过了');
    const ps = sp === '56' ? [5, 6] : [7], units = E.mockPlan(f).filter(u => ps.includes(IT[u.ids[0]].p));
    startSession('mock', units, { form: f, part: sp });
  },
  goCalib() { tab = 'me'; render(); },
  mock() { const f = E.nextForm(); if (!f) return alert('整套题都做过了'); startSession('mock', E.mockPlan(f), { form: f }); },
  rev() { const a = revAlloc(); if (a.nw) { WQ = { ws: a.ws.slice(0, a.nw), i: 0, ni: a.ni, q: null, ans: null }; return render(); } startSession('review', E.reviewUnits(a.ni || 20)); },
  ans(el) { answer(+el.dataset.c); },
  next() { next(); },
  pause() { leaveQ(); S.paused = true; tab = 'today'; save(); render(); },
  closeR() { R = null; render(); },
  calib() {
    const v = parseInt(($('#mReal') || {}).value, 10);
    if (!(v >= 5 && v <= 495)) return alert('阅读分在 5–495 之间');
    if (!API.calibrate(Math.round(v / 5) * 5)) return alert('预测模块没加载，暂时不能校准');
    ui().calibAt = Date.now(); save(); render();
  },
  closeM() { modal(R ? vResult() : ''); },
  nostory() { S.noStory = true; save(); render(); },
  view(el) { S.v = el.dataset.v; save(); render(); },
  dr() { S.dr = !S.dr; save(); render(); },
  flip() { S.v = S.v === 'a' ? 'q' : 'a'; save(); render(); },
  docv(el) { if (S.v === 'a' && S.doc === +el.dataset.i) return; S.v = 'a'; A.doc(el); },
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
  tip() { const id = curId(), x = API.explain(id); E.st.tips = E.st.tips || []; if (!E.st.tips.some(t => t.id === id)) { E.st.tips.push({ id, n: IT[id].n, t: x.tip, ts: Date.now() }); E.log('tip_save', { id }); } save(); render(); },
  lesson() { const L = API.lesson(IT[curId()].n); if (L) { E.log('lesson_open', { node: L.node }); modal(vLesson(L)); } },
  unword(el) { const w = el.dataset.w; delete E.st.words[w]; E.log('word_remove', { lemma: w }); save(); hidePop(); },
  menu() {
    const u = ui();
    const fi = Math.max(0, FZ.findIndex(f => f[0] === (u.fz || 1)));
    modal(`<h2>设置</h2><div class="li"><span>字号 · ${FZ[fi][1]}</span><span class="row"><button class="chip" data-act="fzs" data-d="-1" aria-label="字小一点" ${fi ? '' : 'disabled'}>A−</button><button class="chip" data-act="fzs" data-d="1" aria-label="字大一点" ${fi < FZ.length - 1 ? '' : 'disabled'}>A+</button></span></div>
      <div class="li"><span>用时环</span><button class="chip" data-act="set" data-k="showRing">${u.showRing ? '隐藏' : '显示'}</button></div>
      <div class="li"><span>简洁外壳</span><button class="chip" data-act="set" data-k="plain">${u.plain ? '关' : '开'}</button></div>
      ${typeof window !== 'undefined' && window.innerWidth >= 1440 ? `<div class="li"><span>多篇并排看</span><button class="chip" data-act="set" data-k="sideBySide">${u.sideBySide ? '关' : '开'}</button></div>` : ''}
      <p class="mut sm">快捷键：A–D / 1–4 选，Enter 下一题，← → 换题，G 跳到引用，Space 切文章/题目，Alt+← → 调中缝</p><button class="btn full" data-act="closeM">好</button>`);
  },
  set(el) { const k = el.dataset.k; ui()[k] = !ui()[k]; save(); render(); },
  dm(el) { E.setSetting('daily_min', +el.dataset.m); save(); render(); },
  wg(el) { E.scheduleWord(el.dataset.w, +el.dataset.g); E.log('wordrev', { w: el.dataset.w, g: +el.dataset.g, tz: -new Date().getTimezoneOffset() }); save(); render(); },
  newp() { save(); setupNew = true; render(); },
  usep(el) { save(); Profiles.use(el.dataset.id); boot(); },
  delp(el) { if (!confirm('删除这个档案？删除后不能恢复。')) return; Profiles.remove(el.dataset.id); if (!Profiles.cur()) { E.st = null; setupNew = true; return render(); } boot(); },
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
  document.addEventListener('input', e => { if (setupNew && e.target && /^s/.test(e.target.id || '')) s1Upd(); if (e.target && e.target.id === 'mDate') { const o = $('#mOut'); if (o) o.innerHTML = examTip(e.target.value); } });
  document.addEventListener('keydown', e => {
    const o = ob(); if (o && o.step === 'vtest' && o.vt && !o.vt.paused) {
      if (o.vt.chk) { const i = '1234'.indexOf(e.key); if (i >= 0) A.vchk({ dataset: { i: i < o.vt.chk.o.length ? i : -1 } }); return; }
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { e.preventDefault(); A.vk({ dataset: { y: e.key === 'ArrowRight' ? '1' : '0' } }); } return; }
    if (WQ && !S) { const i = '1234'.indexOf(e.key); if (WQ.ans == null && i >= 0) A.wqA({ dataset: { i } }); else if (WQ.ans != null && e.key === 'Enter') A.wqN(); return; }
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
swInit(); boot();
