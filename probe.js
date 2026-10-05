const { chromium } = require('playwright');

// Diagnostic helper for inspecting the reader's page-flip integration.
const URL      = process.env.PIP_PROBE_URL || 'https://pip-book.vercel.app/pip';
const VIEWPORT = { width: 1000, height: 760 };

(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 1 });
  const page = await context.newPage();

  await page.goto(URL, { waitUntil: 'commit', timeout: 120000 });
  await page.waitForSelector('.stf__parent, canvas, .flipbook', { timeout: 60000 }).catch(() => {});
  await page.waitForFunction(() => {
    const v = document.querySelector('video[data-page-number]');
    return v && v.readyState >= 3 && v.currentTime > 0;
  }, { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(1500);

  const probe = await page.evaluate(() => {
    const out = {};
    const parent = document.querySelector('.stf__parent');
    out.parentFound = !!parent;
    if (!parent) return out;

    // 1) own enumerable keys that look relevant
    out.ownKeys = Object.keys(parent).filter(k =>
      k.startsWith('__') || /flip|page|stf/i.test(k));

    // 2) walk the React fiber upward looking for the StPageFlip instance
    const fk = Object.keys(parent).find(k => k.startsWith('__reactFiber'));
    out.hasFiber = !!fk;
    if (fk) {
      let node = parent[fk], hops = 0;
      while (node && hops < 40) {
        const sn = node.stateNode;
        if (sn && typeof sn === 'object') {
          if (sn.pageFlip || sn.getPageFlip || sn.flipNext) {
            out.fiber = {
              hop: hops,
              hasPageFlip: typeof sn.pageFlip,
              hasGetPageFlip: typeof sn.getPageFlip,
              hasFlipNext: typeof sn.flipNext,
              ctor: sn.constructor && sn.constructor.name,
            };
            // try to actually reach the engine and read its method list
            try {
              const eng = sn.pageFlip || (sn.getPageFlip && sn.getPageFlip()) || sn;
              if (eng) out.engineMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(eng)).slice(0, 40);
            } catch (e) { out.engineErr = String(e); }
            break;
          }
        }
        node = node.return; hops++;
      }
    }
    return out;
  });

  console.log('PROBE RESULT:\n' + JSON.stringify(probe, null, 2));

  await browser.close();
})();
