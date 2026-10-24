/* Service Worker（P0-4 通知 + D2 离线缓存）。VERSION 由 build.py 构建时注入（产物内容哈希），变了就是新版。
 * 策略：同源 GET cache-first；首次安装预缓存应用壳；新版安装后 waiting，页面提示「刷新获取新版」再 skipWaiting，不打断做题。 */
const VERSION = '1867301053';
const CACHE = 'toeic-r-' + VERSION;
const CORE = ['./', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'];
const PAGES = ['index.html', 'index.private.html', 'sw.js'];   // 不存在的忽略（公开部署没有 private）
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(CORE.concat(PAGES).map(u =>
    fetch(new Request(u, { cache: 'reload' })).then(r => (r && r.ok ? c.put(u, r) : null)).catch(() => null)))));
  /* 首装（没有旧 SW）直接激活；有旧版则等页面点「刷新获取新版」 */
  if (!self.registration.active) self.skipWaiting();
});
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k.indexOf('toeic-r-') === 0 && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim())));
self.addEventListener('message', e => { if (e.data === 'skipWaiting') self.skipWaiting(); });
self.addEventListener('fetch', e => {
  const q = e.request; if (q.method !== 'GET') return;
  const u = new URL(q.url); if (u.origin !== self.location.origin) return;
  const nav = q.mode === 'navigate';
  e.respondWith(caches.open(CACHE).then(c => c.match(q, { ignoreSearch: nav }).then(hit => {
    if (hit) return hit;
    return fetch(q).then(r => { if (r && r.ok && r.type === 'basic') c.put(q, r.clone()); return r; })
      .catch(() => (nav ? c.match('./').then(x => x || c.match('index.html')) : Response.error()));
  })));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => cs.length ? cs[0].focus() : self.clients.openWindow('./')));
});
