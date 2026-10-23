#!/usr/bin/env python3
"""UI 截图自检：今天 → 一组 P5 → P6 → 一组 P7 多篇 → 结算，4 种视口。
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
    pg.fill('#sName', 'UI'); pg.click('text=开始入职测试')
    pg.evaluate("while (S && S.mode === 'diag') answer(IT[curId()].a)")
    pg.wait_for_selector('#modal:not(.hide) .res'); shot(pg, d, '00_diag_result')
    pg.click('[data-act=closeR]'); shot(pg, d, '01_today')
    check(pg.locator('.task .btn.lg').count() <= 1, f'{tag}: today has >1 main button')
    # P5 一组
    pg.evaluate("startSession('train', D.items.filter(i => i.p === 5 && D.exp && D.exp[i.id] && /-{3,}/.test(i.s)).slice(0, 3).map(i => ({ ids: [i.id] })))")
    shot(pg, d, '02_p5')
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
    # 刷新后数据仍在
    pg.reload(); check(pg.evaluate('E.st && E.st.log.length > 10'), f'{tag}: state lost after reload')
    check(not errs, f'{tag}: page errors {errs[:2]}')
    pg.close()


with sync_playwright() as p:
    br = p.chromium.launch(executable_path=CH)
    for tag, w, h in VPS:
        print('viewport', tag); run(br, tag, w, h)
    br.close()
print('UI SCREENS', 'FAIL %d' % len(fails) if fails else 'OK', '->', os.path.relpath(OUT, ROOT))
sys.exit(1 if fails else 0)
