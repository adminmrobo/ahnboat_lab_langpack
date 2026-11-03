// 언어 × 페이지 × 폭 헤드리스 검사 (언어팩 v1.3, 지시서 16장)
// 사용: node langpack/browser_check.js [--shots] [--no-click]     (필요: playwright)
// dist/를 작은 로컬 서버로 띄워 http로 연다 (HEAD로 번역 파일을 확인하는 404 방지가 file://에서는 돌지 않으므로).
// 검사
//  1. 페이지 × 언어 × 390/1280: 스크립트·콘솔 오류 0, 가로 넘침 0, <html lang>, 🌐 선택 상자와 🌐 배너가 화면 안에 보임
//  2. 버튼을 모두 눌러 본 뒤(1280 폭) 오류 0, 화면 글자·alt·aria-label·title·placeholder에 남은 한글 0 (data-i18n-skip·allowVisibleHangul 제외)
//  3. 언어 전환: 선택 상자(#섹션 유지), 배너, 고른 언어 기억, ?lang=, 브라우저 언어별 자동 전환(+ de → 한국어), 번역판 주소는 자동 전환 안 함,
//     번역 파일이 없으면(404) 한국어에 머묾
//  4. --shots: 캔버스가 있는 구역을 언어마다 390 폭으로 찍어 langpack/work/shots/ 에 저장 (눈으로 확인용)
const fs = require('fs'), path = require('path'), http = require('http');
const { chromium } = require('playwright');
const PACK = __dirname, CFG = JSON.parse(fs.readFileSync(path.join(PACK, 'config.json'), 'utf8'));
const PROJ = path.resolve(PACK, CFG.projectDir || '..'), DIST = path.join(PROJ, CFG.distDir || 'dist');
const LANGS = CFG.langs || ['en', 'zh', 'ja', 'ru', 'uz', 'vi'], ALL = ['ko', ...LANGS], layout = CFG.layout || 'suffix';
const HL = Object.assign({ zh: 'zh-CN' }, CFG.htmlLang || {}), code = l => HL[l] || l;
const SHOTS = process.argv.includes('--shots'), CLICK = !process.argv.includes('--no-click');
const koPages = fs.readdirSync(DIST, { recursive: true }).map(String)
  .filter(f => f.endsWith('.html') && !f.startsWith('_') && !new RegExp('\\.(' + LANGS.join('|') + ')\\.html$').test(f) && !LANGS.some(l => f.startsWith(l + path.sep)));
const fileOf = (p, l) => l === 'ko' ? p : layout === 'folder' ? path.join(l, p) : p.replace(/\.html$/, '.' + l + '.html');
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.mp4': 'video/mp4', '.json': 'application/json' };
let block = null;   // 404 시험용: 이 문자열이 든 주소는 없는 파일로
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0].split('#')[0]), f = path.join(DIST, u);
  if ((block && u.includes(block)) || !f.startsWith(DIST) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
  req.method === 'HEAD' ? res.end() : fs.createReadStream(f).pipe(res);
});

const SCAN = () => {   // 화면 글자 + 번역 대상 속성의 한글
  const skip = [...document.querySelectorAll('[data-i18n-skip]')];
  const inSkip = e => skip.some(s => s.contains(e));
  let t = document.body.innerText;
  skip.forEach(e => { if (e.innerText) t = t.split(e.innerText).join(''); });
  const at = [];
  document.querySelectorAll('[alt],[aria-label],[title],[placeholder]').forEach(e => {
    if (inSkip(e) || e.closest('#i18nBanner,.i18n-pick')) return;
    ['alt', 'aria-label', 'title', 'placeholder'].forEach(a => { const v = e.getAttribute(a); if (v && /[가-힣]/.test(v)) at.push(a + '=' + v); });
  });
  t = t.replace(/한국어/g, '') + '\n' + at.join('\n');
  (window.__ALLOW || []).forEach(re => { t = t.replace(new RegExp(re, 'g'), ''); });
  const vis = el => { if (!el) return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1 && r.left >= -1; };
  return { sw: document.documentElement.scrollWidth, lang: document.documentElement.lang,
    hangul: (t.match(/[가-힣]/g) || []).length, sample: (t.match(/[^\n]*[가-힣][^\n]*/g) || []).slice(0, 3),
    sel: !!document.querySelector('#i18nSel,#langSel'), banner: vis(document.querySelector('#i18nBanner > button')) || !document.querySelector('#i18nBanner') && CFG_BANNER === false };
};

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const BASE = 'http://127.0.0.1:' + server.address().port + '/', url = (p, l) => BASE + fileOf(p, l).split(path.sep).join('/');
  const b = await chromium.launch(); let fail = 0; const bad = (ok, ...msg) => { if (!ok) fail++; console.log(ok ? 'ok  ' : 'FAIL', ...msg); };
  const newPage = async (opt) => {
    const ctx = await b.newContext(opt), pg = await ctx.newPage(), errs = [];
    pg.on('pageerror', e => errs.push(e.message));
    pg.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|net::/.test(m.text())) errs.push(m.text()); });
    await pg.addInitScript(([a, bn]) => { window.__ALLOW = a; window.CFG_BANNER = bn; }, [CFG.allowVisibleHangul || [], CFG.banner !== false]);
    return { ctx, pg, errs };
  };
  // 1·2. 페이지 × 언어 × 폭
  for (const p of koPages) for (const L of ALL) for (const w of [390, 1280]) {
    const { ctx, pg, errs } = await newPage({ viewport: { width: w, height: 900 }, locale: L === 'ko' ? 'ko-KR' : 'en-US' });
    await pg.goto(url(p, L) + '?lang=' + L); await pg.waitForTimeout(700);
    let clicked = 0;
    if (CLICK && w === 1280) {   // 버튼 모두 누르기 (언어 UI·링크 이동 제외)
      const n = await pg.locator('button:not(#i18nBanner button), [role=button]:not(a)').count();
      for (let i = 0; i < Math.min(n, CFG.maxClicks || 300); i++) {
        const el = pg.locator('button:not(#i18nBanner button), [role=button]:not(a)').nth(i);
        try { if (await el.isVisible()) { await el.click({ timeout: 800, noWaitAfter: true }); clicked++; await pg.waitForTimeout(40); } } catch (e) { }
        if (!pg.url().startsWith(url(p, L))) { await pg.goto(url(p, L) + '?lang=' + L); await pg.waitForTimeout(400); }
      }
      await pg.waitForTimeout(400);
    }
    const r = await pg.evaluate(SCAN);
    const ok = !errs.length && r.sw <= w && r.lang === code(L) && (L === 'ko' || !r.hangul) && r.sel && r.banner;
    bad(ok, p, L, w, 'width', r.sw, 'lang', r.lang, clicked ? 'clicked ' + clicked : '', L === 'ko' ? '' : 'hangul ' + r.hangul,
      r.sel ? '' : 'NO-SELECT', r.banner ? '' : 'NO-BANNER', errs.slice(0, 2).join(' | '), L !== 'ko' && r.hangul ? JSON.stringify(r.sample) : '');
    if (SHOTS && w === 390) {
      const dir = path.join(PACK, 'work', 'shots'); fs.mkdirSync(dir, { recursive: true });
      const n = await pg.locator('canvas').count();
      for (let i = 0; i < Math.min(n, CFG.shotsPerPage || 4); i++) {
        const h = pg.locator('canvas').nth(i).locator('xpath=ancestor::*[self::section or contains(@class,"panel")][1]');
        try { await (await h.count() ? h : pg.locator('canvas').nth(i)).screenshot({ path: path.join(dir, `${path.basename(p, '.html')}.${L}.${i + 1}.png`), timeout: 3000 }); } catch (e) { }
      }
    }
    await ctx.close();
  }
  if (SHOTS) console.log('     스크린샷 →', path.join(PACK, 'work', 'shots'));
  // 3. 언어 전환
  const p = koPages.includes('index.html') ? 'index.html' : koPages[0];
  const pick = LANGS.includes('ja') ? 'ja' : LANGS[0], esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  {  // 선택 상자: #섹션 유지, 고른 언어 기억
    const { ctx, pg } = await newPage({ locale: 'ko-KR' });
    await pg.goto(url(p, 'ko')); await pg.waitForTimeout(400);
    const H = await pg.evaluate(() => { const e = document.querySelector('body [id]:not(#i18nSel):not(#langSel):not(#langSw):not(#i18nBanner)'); return e ? e.id : 'top'; });
    await pg.goto(url(p, 'ko') + '#' + H); await pg.waitForTimeout(400);
    await pg.selectOption('#i18nSel,#langSel', pick); await pg.waitForTimeout(700);
    bad(new RegExp(esc(fileOf(p, pick).split(path.sep).join('/')) + '\\?lang=' + pick + '#' + esc(H) + '$').test(pg.url()), 'select →', pick, '#' + H, pg.url().replace(BASE, ''));
    await pg.goto(url(p, 'ko')); await pg.waitForTimeout(800);   // 기억: 한국어 주소로 다시 와도 고른 언어로
    bad(pg.url().includes(fileOf(p, pick).split(path.sep).join('/')), 'remembered', pick, '→', pg.url().replace(BASE, ''));
    await ctx.close();
  }
  {  // 배너: 열기 → 언어 고르기, Esc로 닫힘
    const { ctx, pg } = await newPage({ locale: 'ko-KR', viewport: { width: 390, height: 800 } });
    await pg.goto(url(p, 'ko')); await pg.waitForTimeout(400);
    await pg.click('#i18nBanner > button'); const open1 = await pg.isVisible('#i18nBanner ul');
    await pg.keyboard.press('Escape'); const closed = !(await pg.isVisible('#i18nBanner ul'));
    await pg.click('#i18nBanner > button'); const L2 = LANGS[LANGS.length - 1];
    await pg.click(`#i18nBanner a[lang="${L2}"]`); await pg.waitForTimeout(700);
    bad(open1 && closed && pg.url().includes(fileOf(p, L2).split(path.sep).join('/')), 'banner open/Esc/pick →', L2, pg.url().replace(BASE, ''));
    await ctx.close();
  }
  for (const L of [...LANGS, 'de']) {  // 브라우저 언어별 자동 전환 (de는 한국어에 머묾)
    const { ctx, pg } = await newPage({ locale: L });
    await pg.goto(url(p, 'ko')); await pg.waitForTimeout(800);
    const want = CFG.autoRedirect === false || L === 'de' ? 'ko' : L;
    bad(pg.url().split('?')[0] === url(p, want), 'auto (' + L + ' browser) →', pg.url().replace(BASE, ''));
    await ctx.close();
  }
  {  // ?lang=, 번역판 주소는 그대로, 404면 머묾
    const L = LANGS.includes('ru') ? 'ru' : LANGS[0];
    let { ctx, pg } = await newPage({ locale: 'de-DE' });
    await pg.goto(url(p, 'ko') + '?lang=' + L); await pg.waitForTimeout(800);
    bad(pg.url().split('?')[0] === url(p, L), '?lang=' + L, '→', pg.url().replace(BASE, '')); await ctx.close();
    ({ ctx, pg } = await newPage({ locale: 'ko-KR' }));
    await pg.goto(url(p, LANGS[0])); await pg.waitForTimeout(800);
    bad(pg.url().split('?')[0] === url(p, LANGS[0]), 'translated URL stays (ko browser)', pg.url().replace(BASE, '')); await ctx.close();
    const AL = LANGS[LANGS.length - 1]; block = '.' + AL + '.html';
    ({ ctx, pg } = await newPage({ locale: AL }));
    await pg.goto(url(p, 'ko')); await pg.waitForTimeout(1200);
    const vis = await pg.evaluate(() => document.documentElement.style.visibility !== 'hidden');
    bad(pg.url().split('?')[0] === url(p, 'ko') && vis, '404 guard (' + AL + ' file missing) stays ko, visible', pg.url().replace(BASE, '')); await ctx.close(); block = null;
  }
  console.log(fail ? `\n실패 ${fail}건` : '\n모두 통과'); await b.close(); server.close(); process.exit(fail ? 1 : 0);
})();
