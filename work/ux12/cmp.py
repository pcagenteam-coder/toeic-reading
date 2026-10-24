import os,sys,re,subprocess
from playwright.sync_api import sync_playwright
R=os.getcwd(); CH=re.search(r'CHROME=(\S+)',subprocess.run(['bash','work/setup_browser.sh'],capture_output=True,text=True).stdout).group(1)
OUT='work/ux12/cmp'; V1='file://'+R+'/demo/prototype_v1/index.html'; D='file://'+R+'/app/dist/index.html'
which=sys.argv[1] if len(sys.argv)>1 else 'both'
def s(pg,n): pg.wait_for_timeout(300); pg.screenshot(path=f'{OUT}/{n}.png')
with sync_playwright() as p:
  br=p.chromium.launch(executable_path=CH)
  for tag,w,h in [('m',390,844),('pc',1280,800)]:
    if which in('both','v1'):
      pg=br.new_page(viewport={'width':w,'height':h}); pg.goto(V1); pg.wait_for_timeout(300)
      pg.click('#startDiag'); s(pg,f'v1_{tag}_diag')
      for i in range(8):
        pg.locator('.x-opt').first.click(); 
        if i==0: s(pg,f'v1_{tag}_feedback')
        pg.click('#sheetNext'); pg.wait_for_timeout(100)
      pg.click('#toHome'); s(pg,f'v1_{tag}_home')
      pg.click('[data-tab=inbox]'); pg.locator('[data-mail]').nth(1).click(); s(pg,f'v1_{tag}_p7')
      pg.click('[data-tab=draft]'); s(pg,f'v1_{tag}_p6'); pg.close()
    if which in('both','dist'):
      pg=br.new_page(viewport={'width':w,'height':h}); pg.goto(D); pg.wait_for_selector('#rtgOut')
      pg.fill('#sLs','300'); pg.fill('#sDate','2026-12-13'); pg.click('[data-act=setupGo]'); pg.click('[data-act=diag]')
      pg.evaluate("while (S && S.mode === 'diag') answer(IT[curId()].a)"); pg.click('[data-act=obDone]'); pg.wait_for_selector('#obRm'); pg.click('[data-act=rmSave]')
      s(pg,f'd_{tag}_home')
      pg.evaluate("startSession('train', D.items.filter(i => i.p === 5).slice(0, 3).map(i => ({ ids: [i.id] })))"); s(pg,f'd_{tag}_p5')
      pg.locator('.opt').nth(pg.evaluate("(IT[curId()].a + 1) % 4")).click(); s(pg,f'd_{tag}_feedback')
      pg.evaluate("S=null;E.st.run=null;(() => { const b = D.bundles.find(b => b.p === 7 && b.docs.length > 1 && b.docs.some(d=>d.t==='TX.EMAIL') && b.qs.every(q => IT[q])); startSession('train', [{ b: b.id, ids: b.qs.slice() }]); if(innerWidth<768){S.v='a';render();} })()"); s(pg,f'd_{tag}_p7')
      pg.evaluate("(() => { const b = D.bundles.find(b => b.p === 6 && b.qs.every(q => IT[q])); S=null; startSession('train', [{ b: b.id, ids: b.qs.slice() }]); })()"); s(pg,f'd_{tag}_p6')
      if os.environ.get('RES'):
        pg.evaluate("while (S) { const id = curId(); if (!S.ans[id]) answer(IT[id].a); else next(); }"); s(pg,f'd_{tag}_result')
      pg.close()
  br.close()
print('ok')
