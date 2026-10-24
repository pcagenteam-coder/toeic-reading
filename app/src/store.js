'use strict';
/* ===== 存储适配器 =====
 * 接口：get(key) → string|null；set(key, string)；del(key)；kind: 'local'|'memory'
 * 预留云端：SupabaseAdapter 实现同样接口即可（get/set 走 table progress(profile_id, key, json)），
 * 本版本不联网，不实现。
 */
const Store = (() => {
  /* D2：内存缓存 C 是读写真相；同步双写 localStorage（启动快、和旧版兼容），
   * 节流写 IndexedDB（容量大、不易被清）。两边都记写入时间 t2:__ts；启动时 IDB 更新则以 IDB 为准（如 LS 配额满/被清）。
   * 微信/隐私模式 IDB 不可用或卡住（1.5s 超时）→ 只用 LS；LS 也不可用 → 内存（顶部提示导出）。 */
  const C = {}, TS = 't2:__ts', DB = 'toeic-r', OS = 'kv';
  let ls = null, lsOk = false, idb = null, idbOk = false, dirty = {}, timer = null, readyCbs = [];
  try { ls = window.localStorage; const t = '__t2'; ls.setItem(t, '1'); ls.removeItem(t); lsOk = true; } catch (e) { ls = null; }
  if (lsOk) try { for (let i = 0; i < ls.length; i++) { const k = ls.key(i); if (k && k.indexOf('t2:') === 0) C[k] = ls.getItem(k); } } catch (e) { }
  function lsSet(k, v) {
    if (!lsOk) return;
    try { ls.setItem(k, v); ls.setItem(TS, C[TS]); } catch (e) { lsOk = false; if (!idbOk && Store.onFallback) Store.onFallback(); }
  }
  function flush() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (!idbOk) return; const ks = Object.keys(dirty); if (!ks.length) return; dirty = {};
    try {
      const tx = idb.transaction(OS, 'readwrite'), os = tx.objectStore(OS);
      ks.forEach(k => (k in C ? os.put(C[k], k) : os.delete(k))); os.put(C[TS], TS);
      tx.onerror = () => { ks.forEach(k => { dirty[k] = 1; }); };
    } catch (e) { idbOk = false; }
  }
  function mark(k) { dirty[k] = 1; if (idbOk && !timer) timer = setTimeout(flush, 400); }
  function done() { const cbs = readyCbs; readyCbs = null; cbs.forEach(f => { try { f(); } catch (e) { } }); }
  function openIdb() {
    let fin = false; const end = ok => { if (fin) return; fin = true; idbOk = ok; done(); };
    try {
      if (typeof indexedDB === 'undefined' || !indexedDB) return end(false);
      setTimeout(() => end(false), 1500);
      const rq = indexedDB.open(DB, 1);
      rq.onupgradeneeded = () => rq.result.createObjectStore(OS);
      rq.onerror = () => end(false);
      rq.onsuccess = () => {
        if (fin) return; idb = rq.result;
        try {
          const all = {}, cur = idb.transaction(OS, 'readonly').objectStore(OS).openCursor();
          cur.onerror = () => end(false);
          cur.onsuccess = () => {
            const c = cur.result; if (c) { all[c.key] = c.value; return c.continue(); }
            if (fin) return;
            const restore = (+all[TS] || 0) > (+C[TS] || 0) || (!C['t2:index'] && !!all['t2:index']);
            if (restore) {   // IDB 更新：以 IDB 为准，并回写 LS
              Object.keys(C).forEach(k => delete C[k]); Object.assign(C, all);
              if (lsOk) Object.keys(C).forEach(k => { try { ls.setItem(k, C[k]); } catch (e) { } });
            } else {          // 迁移/对齐：LS → IDB 全量镜像
              Object.keys(C).forEach(k => { dirty[k] = 1; });   // IDB 里多出的旧键不删（防 LS 部分丢失时误删）
            }
            fin = true; idbOk = true; flush(); Store.restored = restore; done();
          };
        } catch (e) { end(false); }
      };
    } catch (e) { end(false); }
  }
  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist().then(r => { Store.persisted = r; }, () => { }); } catch (e) { }
  return {
    get kind() { return idbOk ? 'idb' : lsOk ? 'local' : 'memory'; },
    getJ(k, d) { try { const s = C[k]; return s ? JSON.parse(s) : d; } catch (e) { return d; } },
    setJ(k, v) { const s = JSON.stringify(v); C[k] = s; C[TS] = String(Date.now()); lsSet(k, s); mark(k); },
    del(k) { delete C[k]; C[TS] = String(Date.now()); if (lsOk) try { ls.removeItem(k); ls.setItem(TS, C[TS]); } catch (e) { } mark(k); },
    keys: () => Object.keys(C).filter(k => k !== TS),
    flush,
    /* cb 在 IDB 就绪（或确定不可用）后调用一次；Store.restored=true 表示从 IDB 恢复了比 LS 新的数据 */
    ready(cb) { if (readyCbs) { readyCbs.push(cb); if (readyCbs.length === 1) openIdb(); } else cb(); },
    restored: false, persisted: null,
    onFallback: null
  };
})();

/* ===== 多档案：每个档案一份独立 state，key = t2:p:<id> ===== */
const Profiles = (() => {
  const IDX = 't2:index';
  let idx = Store.getJ(IDX, null) || { list: [], cur: null };
  const reload = () => { idx = Store.getJ(IDX, null) || { list: [], cur: null }; };
  const saveIdx = () => Store.setJ(IDX, idx);
  const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  return {
    reload,
    list: () => idx.list,
    cur: () => idx.cur,
    create(name) {
      const id = uid(); idx.list.push({ id, name: name || ('档案' + (idx.list.length + 1)) });
      idx.cur = id; saveIdx(); return id;
    },
    use(id) { idx.cur = id; saveIdx(); },
    remove(id) {
      idx.list = idx.list.filter(p => p.id !== id); Store.del('t2:p:' + id);
      if (idx.cur === id) idx.cur = idx.list[0] ? idx.list[0].id : null; saveIdx();
    },
    rename(id, nm) { const p = idx.list.find(p => p.id === id); if (p) { p.name = nm; saveIdx(); } },
    name(id) { const p = idx.list.find(p => p.id === (id || idx.cur)); return p ? p.name : ''; },
    load(id) { return Store.getJ('t2:p:' + (id || idx.cur), null); },
    save(st, id) { Store.setJ('t2:p:' + (id || idx.cur), st); }
  };
})();

/* 进度码：base64(UTF-8 JSON) */
const Code = {
  enc(o) { return btoa(unescape(encodeURIComponent(JSON.stringify(o)))); },
  dec(s) { return JSON.parse(decodeURIComponent(escape(atob(s.trim())))); }
};
