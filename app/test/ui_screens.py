#!/usr/bin/env python3
"""UI 截图自检：首日 S1–S6 → 今天 → P5 → P6 → P7 多篇/并排/快捷键 → 结算 → 复习 → 进度 → 我的 → 状态页，4 种视口。
用法：bash work/setup_browser.sh（打印 CHROME=…）后  python3 app/test/ui_screens.py [dist]
截图存 work/screens/<视口>/；检查：无横向溢出、查词浮层不盖住选项、关键元素存在。"""
import os, sys, re, subprocess
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIST = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'app/dist/index.html')
OUT = os.path.join(ROOT, 'work/screens')
CH = os.environ.get('CHROME') or re.search(r'CHROME=(\S+)', subprocess.run(['bash', os.path.join(ROOT, 'work/setup_browser.sh')], capture_output=True, text=True).stdout).group(1)
VPS = [('m390', 390, 844), ('t820', 820, 1180), ('t1180', 1180, 820), ('pc1440', 1440, 900)]
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg); print('  FAIL', msg)


def no_overflow(pg, tag):
    w = pg.evaluate('[document.documentElement.scrollWidth, innerWidth]')
    check(w[0] <= w[1] + 1, f'{tag}: horizontal overflow {w}')


def shot(pg, d, name):
    pg.wait_for_timeout(250); pg.screenshot(path=os.path.join(d, name + '.png')); no_overflow(pg, os.path.basename(d) + '/' + name)


def run(br, tag, w, h):
    d = os.path.join(OUT, tag); os.makedirs(d, exist_ok=True)
    pg = br.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + DIST)
    # 首日 S1：目标 + 听力 + 考试日期
    pg.wait_for_selector('#rtgOut'); check('270' in pg.inner_text('#rtgOut'), f'{tag}: S1 reading target default 600×0.45')
    check(pg.input_value('#sLs') == '' and '45%' in pg.inner_text('#rtgOut'), f'{tag}: P2-7 listening default empty + 45% hint'); pg.fill('#sLs', '300'); pg.fill('#sDate', '2026-12-13'); shot(pg, d, '00a_s1_goal')
    check('300' in pg.inner_text('#rtgOut'), f'{tag}: S1 total−listening')
    pg.fill('#sDate', '2020-01-01'); check('已经过了' in pg.inner_text('#dateOut'), f'{tag}: past date not flagged')
    pg.fill('#sDate', '2026-12-13'); pg.click('[data-act=setupGo]'); shot(pg, d, '00b_diag_intro')
    check(pg.locator('#nav').is_hidden(), f'{tag}: nav visible during first day')
    check('入职测试' in pg.inner_text('#main') and '词汇' not in pg.inner_text('#main'), f'{tag}: P0-3 diag intro should come right after goal')
    pg.click('[data-act=diag]'); shot(pg, d, '00f_diag_p5')
    check(pg.locator('.hint').count() == 1, f'{tag}: diag hint missing')
    pg.evaluate("while (S && S.mode === 'diag') answer(IT[curId()].a)")
    pg.wait_for_selector('.bc'); shot(pg, d, '00g_diag_result')
    txt = pg.inner_text('#main'); check(not re.search(r'正确率|\d+\s*/\s*\d+ 题', txt), f'{tag}: S6 shows counts')
    check(1 <= pg.locator('.bc li').count() <= 8, f'{tag}: battle card lines'); check('第 1 天' in txt, f'{tag}: day 1 not shown')
    pg.click('[data-act=obDone]'); pg.wait_for_selector('#obRm'); shot(pg, d, '00h_remind'); no_overflow(pg, f'{tag} remind')
    check('每天几点提醒你' in pg.inner_text('#main') and pg.locator('[data-act=rmSkip]').count() == 1, f'{tag}: S7 remind/skip missing')
    pg.click('[data-act=rmSave]'); shot(pg, d, '01_today')
    check(pg.evaluate("E.st.settings.remind") not in (None, False), f'{tag}: remind not saved')
    check(pg.locator('.fz').count() == 1, f'{tag}: streak freeze ❄ missing')
    check(pg.locator('.task .btn.lg').count() <= 1, f'{tag}: today has >1 main button')
    # P0-3：词汇摸底改为诊断后可选补测（今天页“补测词汇”）
    pg.evaluate("A.vretest()"); shot(pg, d, '00b_vocab_intro')
    pg.click('[data-act=vstart]'); shot(pg, d, '00c_vocab_word')
    pg.evaluate("(() => { let k = 0; while (!E.st.ob.vt.chk && k++ < 60) A.vk({ dataset: { y: '1' } }); })()"); shot(pg, d, '00d_vocab_check')
    if w >= 1024:   # PC：← / → 答词汇
        pg.evaluate("A.vchk({ dataset: { i: String(E.st.ob.vt.chk.a) } })"); n0 = pg.evaluate('E.st.ob.vt.a.length'); pg.keyboard.press('ArrowRight')
        check(pg.evaluate('E.st.ob.vt ? E.st.ob.vt.a.length : 99') == n0 + 1, f'{tag}: vocab arrow key')
    pg.evaluate("(() => { let k = 0; while (E.st.ob.step === 'vtest' && k++ < 80) { const vt = E.st.ob.vt; if (vt.chk) A.vchk({ dataset: { i: String(vt.chk.a) } }); else A.vk({ dataset: { y: vt.q[vt.i][1] && k % 4 ? '1' : '0' } }); } })()")
    shot(pg, d, '00e_vocab_result'); check('个常用词' in pg.inner_text('#main'), f'{tag}: vocab result')
    pg.click('[data-act=obDone]'); pg.wait_for_selector('.task')
    # P5 一组
    pg.evaluate("startSession('train', D.items.filter(i => i.p === 5 && D.exp && D.exp[i.id] && /-{3,}/.test(i.s)).slice(0, 3).map(i => ({ ids: [i.id] })))")
    shot(pg, d, '02_p5')
    if w < 768:
        oz = pg.evaluate("(() => { const o = [...document.querySelectorAll('.opt')].map(x => x.getBoundingClientRect()); return [o[0].top, o[o.length - 1].bottom]; })()")
        check(oz[0] >= h * 0.5 and oz[1] <= h, f'{tag}: P5 options not in thumb zone {oz}')
    pg.locator('.paper .w').nth(2).click(); pg.wait_for_timeout(200); shot(pg, d, '03_p5_lookup')
    pr = pg.evaluate("(() => { const p = document.querySelector('#pop').getBoundingClientRect(); return [...document.querySelectorAll('.opt')].some(o => { const r = o.getBoundingClientRect(); return !(r.bottom <= p.top || r.top >= p.bottom || r.right <= p.left || r.left >= p.right); }); })()")
    check(not pr, f'{tag}: lookup popover covers options')
    pg.keyboard.press('Escape'); pg.mouse.click(5, h - 5) if w < 768 else None
    wrong = pg.evaluate("(IT[curId()].a + 1) % 4")
    pg.locator('.opt').nth(wrong).click(); shot(pg, d, '04_p5_feedback')
    check(pg.locator('.fb').count() == 1, f'{tag}: no feedback panel')
    pg.evaluate("while (S) { const id = curId(); if (!S.ans[id]) answer(IT[id].a); else next(); }"); pg.evaluate('R = null; render()')
    # P6
    pg.evaluate("(() => { const b = D.bundles.find(b => b.p === 6 && b.qs.every(q => IT[q])); startSession('train', [{ b: b.id, ids: b.qs.slice() }]); answer(IT[curId()].a); })()")
    pg.wait_for_timeout(900); shot(pg, d, '05_p6')
    if w < 768:
        pg.click('.seg button[data-v=a]'); shot(pg, d, '05b_p6_article')
    pg.evaluate("S = null; E.st.run = null; render()")
    # P7 多篇（优先含群聊/短信）
    pg.evaluate("""(() => { const ok = b => b.p === 7 && b.docs.length > 1 && b.qs.every(q => IT[q]);
      const b = D.bundles.find(b => ok(b) && b.docs.some(d => /CHAT|TEXT_MSG/.test(d.t))) || D.bundles.find(b => ok(b) && b.docs.some(d => d.t === 'TX.EMAIL')) || D.bundles.find(ok);
      const qi = b.qs.findIndex(q => /["“]/.test(IT[q].s));
      startSession('train', [{ b: b.id, ids: b.qs.slice() }]); if (qi > 0) { S.qi = qi; render(); } })()""")
    shot(pg, d, '06_p7_multi')
    if w >= 1440:
        pg.evaluate("ui().sideBySide = true; render()"); shot(pg, d, '06b_p7_side_by_side')
        cols = pg.evaluate("(() => { const x = [...document.querySelectorAll('.sbs > div')].map(e => e.getBoundingClientRect()); return x.length >= 2 && Math.abs(x[0].top - x[1].top) < 4 && x[1].left > x[0].right - 1; })()")
        check(cols, f'{tag}: multi docs not side by side'); pg.evaluate("ui().sideBySide = false; render()")
        sp0 = pg.evaluate('ui().split || 55'); pg.keyboard.press('Alt+ArrowLeft'); check(pg.evaluate('ui().split') == sp0 - 5, f'{tag}: Alt+← split')
        pg.keyboard.press('Alt+ArrowRight')
    if pg.locator('#pq a.ref').count():
        pg.locator('#pq a.ref').first.click(); pg.wait_for_timeout(300); shot(pg, d, '07_p7_jump')
        vis = pg.evaluate("(() => { const m = document.querySelector('#mref,.p.on,.ins.on'); if (!m) return null; const r = m.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; })()")
        check(vis is not False, f'{tag}: jump target not visible')
    if w < 768:
        pg.click('.fab'); pg.wait_for_timeout(200)
    pg.locator('.opt').nth(pg.evaluate("(IT[curId()].a + 1) % 4")).click(); shot(pg, d, '08_p7_feedback')
    # 群聊单篇
    pg.evaluate("(() => { const b = D.bundles.find(b => b.p === 7 && b.docs.length === 1 && /CHAT|TEXT_MSG/.test(b.docs[0].t) && b.qs.every(q => IT[q])); S = null; startSession('train', [{ b: b.id, ids: b.qs.slice() }]); S.v = 'a'; render(); })()")
    shot(pg, d, '09_chat')
    check(pg.locator('.msg .bb').count() >= 2, f'{tag}: chat bubbles not rendered')
    pg.evaluate("while (S) { const id = curId(); if (!S.ans[id]) answer(IT[id].a); else next(); }")
    pg.wait_for_selector('#modal:not(.hide) .res'); shot(pg, d, '10_result')
    txt = pg.inner_text('#sheet')
    check(not re.search(r'正确率|\d+\s*/\s*\d+', txt), f'{tag}: result shows counts/accuracy')
    pg.click('[data-act=closeR]')
    if w >= 1024:   # PC 快捷键：1–4 作答、Enter 下一题、← 回上一题、Esc
        pg.evaluate("startSession('train', D.items.filter(i => i.p === 5).slice(10, 13).map(i => ({ ids: [i.id] })))")
        a0 = pg.evaluate('IT[curId()].a'); pg.keyboard.press(str((a0 + 1) % 4 + 1)); check(pg.evaluate('!!S.ans[curId()]'), f'{tag}: key 1–4 no answer')
        pg.keyboard.press('Enter'); check(pg.evaluate('S && S.ui') == 1, f'{tag}: Enter next')
        pg.keyboard.press('Escape'); pg.evaluate("S = null; E.st.run = null; R = null; render()")
    # 复习：题卡 + 生词四选一（合计 ≤20）
    pg.evaluate("(() => { ['invoice', 'deadline', 'budget', 'shipment', 'warranty'].forEach(w => { E.addWord(w, 'x'); E.st.words[w].due = 0; }); Object.keys(E.st.cards).forEach(k => E.st.cards[k].due = 0); tab = 'review'; render(); })()")
    shot(pg, d, '11_review'); check(pg.evaluate('(a => a.ni + a.nw)(revAlloc())') <= 20, f'{tag}: review > 20')
    pg.click('[data-act=rev]'); shot(pg, d, '12_review_word')
    pg.evaluate("A.wqA({ dataset: { i: String((WQ.q.a + 1) % 4) } })"); shot(pg, d, '12b_review_word_wrong')
    pg.evaluate("while (WQ) { if (WQ.ans == null) A.wqA({ dataset: { i: String(WQ.q.a) } }); else A.wqN(); } while (S) { const id = curId(); if (!S.ans[id]) answer(IT[id].a); else next(); } R = null; modal(''); render()")
    pg.evaluate("Object.keys(E.st.cards).forEach(k => E.st.cards[k].due = 1e9); Object.keys(E.st.words).forEach(k => E.st.words[k].due = 1e9); tab = 'review'; render()")
    shot(pg, d, '13_review_empty'); check('挺好' in pg.inner_text('#main'), f'{tag}: review empty state')
    # 进度
    pg.evaluate("tab = 'progress'; render()"); shot(pg, d, '14_progress')
    txt = pg.inner_text('#main'); check('职级' in txt and '本周小结' in txt and re.search('个考点|估算中|够到目标|已够线', txt) and '绩效' not in txt, f'{tag}: progress content')
    check(not re.search(r'正确率|\d+\s*/\s*\d+|做了 \d+ 题', txt), f'{tag}: progress shows counts/accuracy')
    pg.evaluate("window.scrollTo(0, 99999)"); shot(pg, d, '14b_progress_bottom'); pg.evaluate("window.scrollTo(0, 0)")
    # 我的
    pg.evaluate("tab = 'me'; render()"); shot(pg, d, '15_me')
    pg.click('[data-act=clr1]'); pg.locator('.warnbox').scroll_into_view_if_needed(); shot(pg, d, '16_me_clear_confirm'); pg.click('[data-act=clr0]')
    pg.click('[data-act=fz][data-v="1.25"]'); pg.evaluate("startSession('train', [{ ids: [D.items.find(i => i.p === 5).id] }])"); shot(pg, d, '17_p5_bigfont')
    pg.evaluate("S = null; E.st.run = null; ui().fz = 1; tab = 'today'; render()")
    # 出错 / 首次（复习、进度在入职前）
    pg.evaluate("tab = 'nope'; render()"); shot(pg, d, '18_error'); check('进度已保存' in pg.inner_text('#main'), f'{tag}: error state')
    pg.click('[data-act=recover]')
    # 刷新后数据仍在
    pg.reload(); check(pg.evaluate('E.st && E.st.log.length > 10'), f'{tag}: state lost after reload')
    pg.evaluate("Profiles.create('新人'); E.st = newState(600, ''); save(); tab = 'progress'; render()"); shot(pg, d, '19_progress_first')
    check('还没有进度' in pg.inner_text('#main'), f'{tag}: progress first state')
    check(not errs, f'{tag}: page errors {errs[:2]}')
    pg.close()


with sync_playwright() as p:
    br = p.chromium.launch(executable_path=CH)
    for tag, w, h in VPS:
        print('viewport', tag); run(br, tag, w, h)
    br.close()
print('UI SCREENS', 'FAIL %d' % len(fails) if fails else 'OK', '->', os.path.relpath(OUT, ROOT))
sys.exit(1 if fails else 0)
