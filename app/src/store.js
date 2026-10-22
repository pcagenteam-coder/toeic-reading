'use strict';
/* ===== 存储适配器 =====
 * 接口：get(key) → string|null；set(key, string)；del(key)；kind: 'local'|'memory'
 * 预留云端：SupabaseAdapter 实现同样接口即可（get/set 走 table progress(profile_id, key, json)），
 * 本版本不联网，不实现。
 */
const Store = (() => {
  const mem = {};
  const memory = { kind: 'memory', get: k => (k in mem ? mem[k] : null), set: (k, v) => { mem[k] = v; }, del: k => { delete mem[k]; } };
  let local = null;
  try {
    const ls = window.localStorage, t = '__t2';
    ls.setItem(t, '1'); ls.removeItem(t);
    local = { kind: 'local', get: k => ls.getItem(k), set: (k, v) => ls.setItem(k, v), del: k => ls.removeItem(k) };
  } catch (e) { local = null; }
  let ad = local || memory;
  function safeSet(k, v) {
    try { ad.set(k, v); } catch (e) { // 配额满等 → 降级内存
      ad = memory; ad.set(k, v); if (Store.onFallback) Store.onFallback();
    }
  }
  return {
    get kind() { return ad.kind; },
    getJ(k, d) { try { const s = ad.get(k); return s ? JSON.parse(s) : d; } catch (e) { return d; } },
    setJ(k, v) { safeSet(k, JSON.stringify(v)); },
    del(k) { try { ad.del(k); } catch (e) { } },
    onFallback: null
  };
})();

/* ===== 多档案：每个档案一份独立 state，key = t2:p:<id> ===== */
const Profiles = (() => {
  const IDX = 't2:index';
  let idx = Store.getJ(IDX, null) || { list: [], cur: null };
  const saveIdx = () => Store.setJ(IDX, idx);
  const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  return {
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
