// Virtual fitting room server: serves the page and turns (person photo + product photos) into
// generated try-on photos through the OpenAI Images API. No npm dependencies (Node 18+).
//
//   OPENAI_API_KEY=sk-... node server.js            -> live generation
//   node server.js                                   -> demo mode (sample results only)
//   node server.js --generate-models                 -> create missing virtual model photos
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const P = require('./prompt.js');

const ROOT = __dirname;
loadDotEnv(path.join(ROOT, '.env'));

const CFG = {
  port: +(process.env.PORT || 3000),
  key: process.env.OPENAI_API_KEY || '',
  base: (process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1').replace(/\/$/, ''),
  model: process.env.OPENAI_IMAGE_MODEL || 'gpt-image-1',
  quality: process.env.IMAGE_QUALITY || 'high',
  size: process.env.IMAGE_SIZE || '1024x1536',
  fidelity: process.env.INPUT_FIDELITY !== 'off',
  ownerPassword: process.env.OWNER_PASSWORD || '',
  ratePerHour: +(process.env.TRYONS_PER_HOUR || 20)
};
const LIVE = !!CFG.key;
const DATA = path.join(ROOT, 'data');
for (const d of ['cache', 'models', 'products']) fs.mkdirSync(path.join(DATA, d), { recursive: true });

function loadDotEnv(file) {
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
}

/* ---------- catalog ---------- */
const EXTRA = path.join(DATA, 'catalog-extra.json');
function catalog() {
  const base = JSON.parse(fs.readFileSync(path.join(ROOT, 'catalog.json'), 'utf8'));
  const extra = fs.existsSync(EXTRA) ? JSON.parse(fs.readFileSync(EXTRA, 'utf8')) : [];
  base.products = base.products.concat(extra);
  for (const m of base.models) {
    const gen = path.join(DATA, 'models', m.id + '.png');
    if (fs.existsSync(gen)) m.img = 'data/models/' + m.id + '.png';
    // Demo mode may show the sample model photo; live mode needs a generated neutral one.
    else if (!LIVE && m.demoImg) m.img = m.demoImg;
  }
  return base;
}

/* ---------- images ---------- */
const MIME = { '.png': 'image/png', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg' };
function readImage(rel) {
  const abs = safeJoin(ROOT, rel);
  if (!abs || !fs.existsSync(abs)) throw httpError(400, 'صورة غير موجودة: ' + rel);
  return { buf: fs.readFileSync(abs), type: MIME[path.extname(abs).toLowerCase()] || 'image/png', name: path.basename(abs) };
}
function fromDataUrl(url, name) {
  const m = /^data:(image\/(png|jpeg|webp));base64,(.+)$/.exec(url || '');
  if (!m) throw httpError(400, 'الصورة لازم تكون PNG أو JPG أو WEBP');
  const buf = Buffer.from(m[3], 'base64');
  if (buf.length > 12 * 1024 * 1024) throw httpError(413, 'حجم الصورة أكبر من 12 ميجا');
  return { buf, type: m[1], name: name + '.' + (m[2] === 'jpeg' ? 'jpg' : m[2]) };
}

async function openaiImage(endpoint, prompt, images) {
  if (!LIVE) throw httpError(503, 'التوليد يحتاج مفتاح OPENAI_API_KEY على السيرفر');
  const send = async (withFidelity) => {
    let body, headers = { Authorization: 'Bearer ' + CFG.key };
    if (endpoint === 'edits') {
      body = new FormData();
      body.append('model', CFG.model);
      body.append('prompt', prompt);
      body.append('size', CFG.size);
      body.append('quality', CFG.quality);
      body.append('n', '1');
      if (withFidelity) body.append('input_fidelity', 'high');
      for (const im of images) body.append('image[]', new Blob([im.buf], { type: im.type }), im.name);
    } else {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify({ model: CFG.model, prompt, size: CFG.size, quality: CFG.quality, n: 1 });
    }
    const r = await fetch(`${CFG.base}/images/${endpoint}`, { method: 'POST', headers, body });
    const j = await r.json().catch(() => ({}));
    return { r, j };
  };
  let { r, j } = await send(endpoint === 'edits' && CFG.fidelity);
  // Some image models don't accept input_fidelity; retry once without it.
  if (!r.ok && CFG.fidelity && /input_fidelity/i.test(JSON.stringify(j))) {
    CFG.fidelity = false;
    console.warn('[openai] input_fidelity not supported by this model; continuing without it');
    ({ r, j } = await send(false));
  }
  if (!r.ok) {
    console.error('[openai]', r.status, j.error && j.error.message);
    const msg = r.status === 400 && /safety|moderation/i.test(JSON.stringify(j))
      ? 'الصورة انرفضت من فلتر الأمان، جرّب صورة ثانية'
      : 'خدمة توليد الصور رجعت خطأ (' + r.status + ')';
    throw httpError(502, msg);
  }
  const item = j.data && j.data[0];
  if (!item || !item.b64_json) throw httpError(502, 'خدمة توليد الصور ما رجعت صورة');
  return Buffer.from(item.b64_json, 'base64');
}

/* ---------- try-on ---------- */
function hash(...parts) { const h = crypto.createHash('sha256'); for (const p of parts) h.update(p); return h.digest('hex').slice(0, 32); }
const toDataUrl = buf => 'data:image/png;base64,' + buf.toString('base64');

async function tryOn(body) {
  const cat = catalog();
  const mode = body.mode === 'self' ? 'self' : 'virtual';
  const ids = Array.isArray(body.items) ? body.items.slice(0, 6) : [];
  const items = ids.map(id => cat.products.find(p => p.id === id)).filter(Boolean);
  if (!items.some(p => p.cat === 'top') || !items.some(p => p.cat === 'bottom')) throw httpError(400, 'اختر قطعة علوية وبنطلون على الأقل');
  items.sort((a, b) => ['top', 'bottom', 'shoes', 'acc'].indexOf(a.cat) - ['top', 'bottom', 'shoes', 'acc'].indexOf(b.cat));

  let person;
  if (mode === 'self') person = fromDataUrl(body.personImage, 'person');
  else {
    const m = cat.models.find(x => x.id === body.modelId);
    if (!m) throw httpError(400, 'اختر موديل');
    if (!m.img) throw httpError(409, 'صورة هالموديل ما تولدت بعد. شغّل: node server.js --generate-models');
    person = readImage(m.img);
  }
  const prompt = P.tryOnPrompt({ mode, items });
  const views = (Array.isArray(body.views) ? body.views : ['front']).filter(v => v === 'front' || v === 'side');

  // Virtual-model results are the same for every customer, so they are cached on disk.
  // Customer photos are never written to disk.
  const cacheKey = mode === 'virtual' ? hash(person.buf, prompt, CFG.model, CFG.quality, CFG.size) : null;
  const cached = v => cacheKey && path.join(DATA, 'cache', `${cacheKey}-${v}.png`);
  const out = {};
  if (cacheKey && views.every(v => fs.existsSync(cached(v)))) {
    for (const v of views) out[v] = fs.readFileSync(cached(v));
    return { prompt, images: views.map(v => toDataUrl(out[v])), cached: true };
  }
  const front = cacheKey && fs.existsSync(cached('front')) ? fs.readFileSync(cached('front'))
    : await openaiImage('edits', prompt, [person, ...items.map(p => readImage(p.img))]);
  if (cacheKey) fs.writeFileSync(cached('front'), front);
  out.front = front;
  if (views.includes('side')) {
    out.side = await openaiImage('edits', P.sideViewPrompt(), [{ buf: front, type: 'image/png', name: 'front.png' }]);
    if (cacheKey) fs.writeFileSync(cached('side'), out.side);
  }
  return { prompt, images: views.map(v => toDataUrl(out[v])), cached: false };
}

async function generateModels(onlyId) {
  const cat = catalog();
  for (const m of cat.models) {
    if (onlyId && m.id !== onlyId) continue;
    const file = path.join(DATA, 'models', m.id + '.png');
    if (m.img && !onlyId) { console.log(`- ${m.id}: موجود`); continue; }
    console.log(`- ${m.id}: جاري التوليد...`);
    fs.writeFileSync(file, await openaiImage('generations', P.modelPrompt(m)));
    console.log(`  تم: ${path.relative(ROOT, file)}`);
  }
}

/* ---------- owner ---------- */
function checkOwner(req) {
  if (!CFG.ownerPassword) throw httpError(403, 'حدد OWNER_PASSWORD في إعدادات السيرفر عشان تفعّل لوحة التاجر');
  const got = Buffer.from(String(req.headers['x-owner-password'] || ''));
  const want = Buffer.from(CFG.ownerPassword);
  if (got.length !== want.length || !crypto.timingSafeEqual(got, want)) throw httpError(401, 'كلمة مرور التاجر غير صحيحة');
}
function addProduct(body) {
  const cats = ['top', 'bottom', 'shoes', 'acc'];
  const name = String(body.name || '').trim().slice(0, 60);
  const price = Math.round(+body.price);
  if (!name || !(price > 0) || !cats.includes(body.cat)) throw httpError(400, 'بيانات المنتج ناقصة');
  const img = fromDataUrl(body.image, 'product');
  const id = 'x' + Date.now().toString(36);
  const file = `data/products/${id}${path.extname(img.name)}`;
  fs.writeFileSync(path.join(ROOT, file), img.buf);
  const color = String(body.color || '').trim().slice(0, 30);
  const ai = String(body.ai || '').trim().slice(0, 400) || `${name}${color ? ', colour: ' + color : ''}`;
  const p = { id, cat: body.cat, name, price, color, img: file, ai, custom: true };
  const extra = fs.existsSync(EXTRA) ? JSON.parse(fs.readFileSync(EXTRA, 'utf8')) : [];
  extra.push(p);
  fs.writeFileSync(EXTRA, JSON.stringify(extra, null, 2));
  return p;
}

/* ---------- http ---------- */
function httpError(status, message) { const e = new Error(message); e.status = status; return e; }
function safeJoin(root, rel) {
  const abs = path.resolve(root, '.' + path.sep + String(rel).replace(/^[/\\]+/, ''));
  return abs.startsWith(root + path.sep) ? abs : null;
}
function readJson(req, limit = 16 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on('data', c => { size += c.length; if (size > limit) { reject(httpError(413, 'الطلب كبير')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => { try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}')); } catch { reject(httpError(400, 'JSON غير صالح')); } });
    req.on('error', reject);
  });
}
const hits = new Map();
function rateLimit(ip) {
  const now = Date.now(), list = (hits.get(ip) || []).filter(t => now - t < 3600e3);
  if (list.length >= CFG.ratePerHour) throw httpError(429, 'وصلت الحد المسموح من التجارب لهالساعة، جرّب بعدين');
  list.push(now); hits.set(ip, list);
}
function send(res, status, obj) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(obj));
}
// Only these paths are public; server code, .env and the cache stay private.
const PUBLIC = [/^\/(index\.html|catalog\.json|prompt\.js)$/, /^\/(products|samples)\/[\w.-]+\.(webp|png|jpe?g)$/, /^\/data\/(models|products)\/[\w.-]+\.(webp|png|jpe?g)$/];
const TYPES = { '.html': 'text/html; charset=utf-8', '.json': 'application/json; charset=utf-8', '.js': 'text/javascript; charset=utf-8', ...MIME };

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  const ip = req.socket.remoteAddress;
  try {
    if (url.pathname === '/api/health') return send(res, 200, { ok: true, live: LIVE, model: LIVE ? CFG.model : null });
    if (url.pathname === '/api/catalog') return send(res, 200, catalog());
    if (url.pathname === '/api/tryon' && req.method === 'POST') {
      rateLimit(ip);
      const t = Date.now();
      const r = await tryOn(await readJson(req));
      console.log(`[tryon] ${r.cached ? 'cache' : 'generated'} in ${((Date.now() - t) / 1000).toFixed(1)}s`);
      return send(res, 200, r);
    }
    if (url.pathname === '/api/products' && req.method === 'POST') { checkOwner(req); return send(res, 200, addProduct(await readJson(req))); }
    if (url.pathname === '/api/models/generate' && req.method === 'POST') { checkOwner(req); const b = await readJson(req); await generateModels(b.id); return send(res, 200, catalog()); }

    const p = url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname);
    if (req.method === 'GET' && PUBLIC.some(rx => rx.test(p))) {
      const abs = safeJoin(ROOT, p);
      if (abs && fs.existsSync(abs)) {
        res.writeHead(200, { 'Content-Type': TYPES[path.extname(abs).toLowerCase()] || 'application/octet-stream' });
        return fs.createReadStream(abs).pipe(res);
      }
    }
    send(res, 404, { error: 'غير موجود' });
  } catch (e) {
    if (!e.status) console.error(e);
    send(res, e.status || 500, { error: e.status ? e.message : 'صار خطأ في السيرفر' });
  }
});

if (process.argv.includes('--generate-models')) {
  const i = process.argv.indexOf('--generate-models');
  generateModels(process.argv[i + 1]).catch(e => { console.error(e.message); process.exit(1); });
} else {
  server.listen(CFG.port, () => {
    console.log(`غرفة القياس شغالة على http://localhost:${CFG.port}`);
    console.log(LIVE ? `التوليد الحي مفعّل (${CFG.model}, ${CFG.quality}, ${CFG.size})` : 'وضع العرض: أضف OPENAI_API_KEY في ملف .env لتفعيل التوليد');
  });
}
