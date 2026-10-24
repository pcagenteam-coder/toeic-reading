#!/usr/bin/env python3
"""D2 离线自检（Playwright + 本地 http 服务，SW 需要 http(s)）：
1 首次在线加载 → SW 接管并缓存 → 断网刷新仍能打开、出现离线提示、能做题；做题中途断网刷新，进度和断点都在
2 IndexedDB：状态镜像进 IDB；localStorage 被清后从 IDB 恢复；旧版只有 localStorage 的数据自动迁移进 IDB
3 导出 JSON 文件 → 从文件导入 往返一致
4 新版本：sw.js 版本变 → 出现「刷新获取新版」，点了切到新版
用法：bash work/setup_browser.sh 后  python3 app/test/offline.py [dist 目录]"""
import os, sys, re, json, shutil, socket, subprocess, tempfile, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'app/dist')
CH = os.environ.get('CHROME') or re.search(r'CHROME=(\S+)', subprocess.run(['bash', os.path.join(ROOT, 'work/setup_browser.sh')], capture_output=True, text=True).stdout).group(1)
fails = []


def check(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)


TMP = tempfile.mkdtemp(prefix='d2off_')
for f in ('index.html', 'sw.js', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'):
    shutil.copyfile(os.path.join(SRC, f), os.path.join(TMP, f))
s = socket.socket(); s.bind(('127.0.0.1', 0)); PORT = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=TMP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
URL = f'http://127.0.0.1:{PORT}/'
for _ in range(50):
    try: socket.create_connection(('127.0.0.1', PORT), 0.2).close(); break
    except OSError: time.sleep(0.1)

IDB_GET = """k => new Promise(res => { const r = indexedDB.open('toeic-r', 1); r.onsuccess = () => { try { const q = r.result.transaction('kv').objectStore('kv').get(k); q.onsuccess = () => res(q.result || null); q.onerror = () => res(null); } catch (e) { res(null); } }; r.onerror = () => res(null); })"""
SW_READY = "() => navigator.serviceWorker.ready.then(() => new Promise(r => { const t = () => navigator.serviceWorker.controller ? r(1) : setTimeout(t, 50); t(); }))"
CACHED = "() => caches.keys().then(ks => Promise.all(ks.map(k => caches.open(k).then(c => c.keys().then(rs => rs.map(x => new URL(x.url).pathname)))))).then(a => [].concat(...a))"


def onboard(pg):
    pg.wait_for_selector('#rtgOut'); pg.fill('#sLs', '300'); pg.fill('#sDate', '2026-12-13'); pg.click('[data-act=setupGo]')
    pg.click('[data-act=diag]'); pg.evaluate("while (S && S.mode === 'diag') answer(IT[curId()].a)")
    pg.wait_for_selector('.bc'); pg.click('[data-act=obDone]'); pg.wait_for_selector('#obRm'); pg.click('[data-act=rmSkip]'); pg.wait_for_selector('.task')


def flush_wait(pg): pg.evaluate("Store.flush()"); pg.wait_for_timeout(300)


errs = []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=CH)
    # ---------- 1 在线首装 → 断网 ----------
    ctx = br.new_context(viewport={'width': 390, 'height': 844}, accept_downloads=True)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL + 'index.html'); onboard(pg)
    pg.evaluate(SW_READY); pg.wait_for_function("() => caches.keys().then(k => k.length > 0)")
    pg.wait_for_timeout(500); cached = pg.evaluate(CACHED)
    check(all(any(c.endswith(x) for c in cached) for x in ('/', '/index.html', '/manifest.webmanifest', '/icon-192.png')), f'SW 预缓存应用壳 {sorted(set(cached))}')
    check(pg.evaluate("Store.kind") == 'idb', 'Store.kind = idb')
    n0 = pg.evaluate("E.st.log.length")
    ctx.set_offline(True); pg.reload(); pg.wait_for_selector('.task')
    check(pg.evaluate("E.st.log.length") == n0, '断网刷新：页面打开、进度在')
    check(pg.locator('#offl').is_visible() and '离线中' in pg.inner_text('#offl'), '断网：顶部离线提示')
    check(pg.evaluate("D.items.length") > 100, '断网：题库内联可用')
    # 断网做题，做到一半刷新
    pg.evaluate("startSession('train', D.items.filter(i => i.p === 5).slice(0, 3).map(i => ({ ids: [i.id] })))")
    pg.evaluate("answer(IT[curId()].a)"); n1 = pg.evaluate("E.st.log.length"); done1 = pg.evaluate("S.ans ? Object.keys(S.ans).length : -1")
    check(n1 > n0, '断网做题：作答写入日志')
    pg.reload(); pg.wait_for_selector('#main')
    check(pg.evaluate("E.st.log.length") >= n1, '做题中途刷新：作答日志不丢')
    check(pg.evaluate("!!(E.st.run || (S && !S.done))"), '做题中途刷新：断点续做还在')
    pg.wait_for_timeout(600)
    idx = pg.evaluate(IDB_GET, 't2:index'); cur = json.loads(idx)['cur'] if idx else None
    st_idb = pg.evaluate(IDB_GET, 't2:p:' + cur) if cur else None
    check(bool(st_idb) and len(json.loads(st_idb)['log']) >= n1, 'IDB 镜像了档案状态')
    # localStorage 被清（如 Safari 7 天清理/配额）→ 从 IDB 恢复
    pg.close(); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL + 'manifest.webmanifest'); pg.evaluate("localStorage.clear()")   # 页面关闭后 LS 被清（不经过 pagehide 回写）
    pg.goto(URL + 'index.html'); pg.wait_for_function("() => E.st && E.st.log.length > 0", timeout=5000)
    check(pg.evaluate("E.st.log.length") >= n1, 'localStorage 被清后从 IDB 恢复进度')
    ctx.set_offline(False); pg.wait_for_timeout(200)
    check(pg.locator('#offl').is_hidden(), '恢复联网：离线提示消失')
    # ---------- 3 导出 / 从文件导入 往返 ----------
    pg.evaluate("S = null; E.st.run = null; tab = 'me'; render()")
    with pg.expect_download() as dl: pg.click('[data-act=dl]')
    fp = os.path.join(TMP, 'export.json'); dl.value.save_as(fp)
    ex = json.load(open(fp, encoding='utf-8')); nexp = len(ex['st']['log'])
    check(ex.get('app') == 'toeic-r-v2' and nexp >= n1, '导出 JSON 文件')
    np0 = pg.evaluate("Profiles.list().length")
    pg.evaluate("tab = 'me'; render()"); pg.set_input_files('#impFile', fp); pg.wait_for_function(f"() => Profiles.list().length === {np0 + 1}")
    check(pg.evaluate("E.st.log.length") == nexp and pg.evaluate("JSON.stringify(E.st.fsrs || E.st.cards || null)") == json.dumps(ex['st'].get('fsrs', ex['st'].get('cards')), ensure_ascii=False, separators=(',', ':')), '从文件导入：新档案日志/卡片一致')
    bad = os.path.join(TMP, 'bad.json'); open(bad, 'w').write('{"x":1}')
    msgs = []; pg.on('dialog', lambda d: (msgs.append(d.message), d.accept()))
    pg.evaluate("tab = 'me'; render()"); pg.set_input_files('#impFile', bad); pg.wait_for_timeout(300)
    check(msgs and '不是' in msgs[0] and pg.evaluate("Profiles.list().length") == np0 + 1, '坏文件：提示且不建档案')
    # ---------- 4 新版本提示 ----------
    sw = open(os.path.join(TMP, 'sw.js'), encoding='utf-8').read()
    open(os.path.join(TMP, 'sw.js'), 'w', encoding='utf-8').write(re.sub(r"const VERSION = '[^']*'", "const VERSION = 'testnew'", sw))
    pg.evaluate("tab = 'today'; S = null; render(); navigator.serviceWorker.getRegistration().then(r => r.update())")
    try: pg.wait_for_selector('#upd:not(.hide)', timeout=8000); vis = True
    except Exception: vis = False
    check(vis, '新版 SW 装好后提示「刷新获取新版」')
    if vis:
        with pg.expect_navigation(timeout=8000): pg.click('[data-act=updGo]')
        pg.wait_for_selector('#main .task'); pg.wait_for_timeout(500)
        check(pg.evaluate("caches.keys()") == ['toeic-r-testnew'], '点刷新后切到新版缓存、旧缓存清掉')
        check(pg.evaluate("E.st && E.st.log.length") == nexp, '更新后进度在')
    ctx.close()
    # ---------- 2 旧 localStorage 数据迁移 ----------
    ctx = br.new_context(); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL + 'index.html'); pg.wait_for_selector('#rtgOut')
    legacy = ex['st']; legacy['run'] = None
    pg.evaluate("""st => { localStorage.clear(); localStorage.setItem('t2:index', JSON.stringify({ list: [{ id: 'old1', name: '旧档案' }], cur: 'old1' })); localStorage.setItem('t2:p:old1', JSON.stringify(st)); }""", legacy)
    pg.evaluate("indexedDB.deleteDatabase('toeic-r')"); pg.reload(); pg.wait_for_selector('#main .task, #main .card')
    check(pg.evaluate("Profiles.name()") == '旧档案' and pg.evaluate("E.st.log.length") == nexp, '旧版 localStorage 数据：直接读出')
    pg.wait_for_timeout(800)
    m = pg.evaluate(IDB_GET, 't2:p:old1')
    check(bool(m) and len(json.loads(m)['log']) == nexp, '旧版 localStorage 数据：自动迁移进 IDB')
    ctx.close()
    # ---------- IDB 不可用（模拟微信/隐私模式）→ 降级 localStorage ----------
    ctx = br.new_context(); ctx.add_init_script("Object.defineProperty(window, 'indexedDB', { get() { throw new Error('blocked'); } })")
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL + 'index.html'); onboard(pg); pg.wait_for_timeout(300)
    check(pg.evaluate("Store.kind") == 'local', 'IDB 不可用：降级 localStorage')
    n2 = pg.evaluate("E.st.log.length"); pg.reload(); pg.wait_for_selector('.task')
    check(pg.evaluate("E.st.log.length") == n2 and pg.locator('#banner').is_hidden(), 'IDB 不可用：刷新进度在、无报错提示')
    ctx.close(); br.close()
srv.terminate()
check(not errs, f'page errors {errs[:2]}')
print('OFFLINE', 'FAIL %d' % len(fails) if fails else 'OK')
sys.exit(1 if fails else 0)
