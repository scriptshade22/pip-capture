const { chromium } = require('playwright');

const URL        = process.env.PIP_CAPTURE_URL || 'http://localhost:3000/pip?capture=1';
const VIEWPORT   = { width: 1440, height: 900 };
const COVER_WAIT = 2000;   // book mount + first video frame settle
const FLIP_TIME  = 1000;   // matches flippingTime:1000 in HTMLFlipBook
const PAGE_WAIT  = 1500;   // dwell per spread after flip completes
const FLIPS      = 13;

const cursorHelper = () => {
  if (window.__mh) return; window.__mh = true;
  const attach = () => {
    const s = document.createElement('style');
    s.textContent = '.mh-ptr{position:fixed;top:0;left:0;width:26px;height:26px;z-index:2147483647;pointer-events:none;margin:-2px 0 0 -2px;transition:transform .08s}.mh-rip{position:fixed;width:12px;height:12px;border-radius:50%;background:rgba(127,176,105,.55);z-index:2147483646;pointer-events:none;margin:-6px 0 0 -6px;transition:transform .45s,opacity .45s}';
    document.head.appendChild(s);
    const p = document.createElement('img'); p.className='mh-ptr';
    p.src='data:image/svg+xml;base64,'+btoa('<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l15 8-6.5 1.6L9 19z" fill="#F4E8D0" stroke="#0F1F1A" stroke-width="1.6" stroke-linejoin="round"/></svg>');
    document.body.appendChild(p);
    addEventListener('mousemove',e=>{p.style.left=e.clientX+'px';p.style.top=e.clientY+'px';},true);
    addEventListener('mousedown',e=>{p.style.transform='scale(.82)';const r=document.createElement('div');r.className='mh-rip';r.style.left=e.clientX+'px';r.style.top=e.clientY+'px';document.body.appendChild(r);requestAnimationFrame(()=>{r.style.transform='scale(3.2)';r.style.opacity='0';});setTimeout(()=>r.remove(),480);},true);
    addEventListener('mouseup',()=>{p.style.transform='scale(1)';},true);
  };
  document.body ? attach() : addEventListener('DOMContentLoaded', attach);
};

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const context = await browser.newContext({
    viewport: VIEWPORT, deviceScaleFactor: 2,
    recordVideo: { dir: 'recording', size: VIEWPORT },
  });
  const page = await context.newPage();
  await page.addInitScript(cursorHelper);

  await page.goto(URL, { waitUntil: 'networkidle', timeout: 120000 });
  await page.waitForSelector('.stf__parent', { timeout: 60000 });

  // wait for first video frame
  await page.waitForFunction(() => {
    const v = document.querySelector('video[data-page-number]');
    return v && v.readyState >= 3;
  }, { timeout: 30000 }).catch(() => {});
  await sleep(COVER_WAIT);

  // probe — bail fast if hook isn't wired
  const probe = await page.evaluate(() => {
    const f = window.__pip?.instance?.();
    return {
      hook:     !!window.__pip,
      callable: typeof f?.flipNext === 'function',
      idx:      f?.getCurrentPageIndex?.() ?? 'n/a',
    };
  });
  console.log('PROBE:', probe);
  if (!probe.callable) {
    await context.close();
    await browser.close();
    throw new Error('flipNext not reachable — is ?capture=1 in the URL and Book.tsx deployed?');
  }

  // flip loop — programmatic, no drags
  for (let i = 0; i < FLIPS; i++) {
    await page.evaluate(() => window.__pip.flipNext());
    console.log(`flip ${i + 1}/${FLIPS}`);
    await sleep(FLIP_TIME + PAGE_WAIT);  // animation completes + dwell
  }

  await sleep(800);  // settle on last spread before cut
  await context.close();
  await browser.close();
  console.log('done -> recording/*.webm');
})();
