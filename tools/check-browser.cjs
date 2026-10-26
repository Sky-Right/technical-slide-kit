/* Optional visual check. The presentation itself has no npm dependencies. */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.join(root, 'dist/preview');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true,
    ...(process.env.CHROME_BIN ? { executablePath: process.env.CHROME_BIN } : {}) });
  const context = await browser.newContext({ viewport: { width: 1600, height: 900 }, offline: true });
  const page = await context.newPage();
  const errors = [], network = [], slides = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (/^https?:/.test(request.url())) network.push(request.url()); });
  await page.goto(pathToFileURL(path.join(root, 'dist/index.html')).href);
  await page.waitForFunction(() => !!window.slideshow);
  await page.evaluate(() => document.fonts.ready);
  const states = await page.evaluate(() => slideshow.getSlideCount());
  for (let n = 1; n <= states; n++) {
    await page.evaluate(n => slideshow.gotoSlide(n), n);
    await page.waitForTimeout(40);
    slides.push(await page.locator('.remark-visible .remark-slide-content').evaluate(s => {
      const bounds = s.getBoundingClientRect(), scale = bounds.width / 1210;
      const issues = [];
      for (const element of s.querySelectorAll('h1,h2,h3,p,li,pre,table,img')) {
        const r = element.getBoundingClientRect();
        if (r.left < bounds.left - 2 || r.right > bounds.right + 2 || r.bottom > bounds.bottom - 70 * scale) {
          issues.push(element.textContent.trim().slice(0, 80) || element.getAttribute('alt'));
        }
        if (element.clientWidth && element.scrollWidth > element.clientWidth + 2) issues.push('horizontal overflow');
      }
      return { title: s.querySelector('h1')?.textContent, issues,
        brokenImages: [...s.querySelectorAll('img')].filter(i => !i.complete || !i.naturalWidth).length };
    }));
    await page.screenshot({ path: path.join(out, `${String(n).padStart(2, '0')}.png`) });
  }
  await page.evaluate(() => slideshow.gotoSlide(1));
  await page.keyboard.press('ArrowRight');
  const next = await page.evaluate(() => slideshow.getCurrentSlideIndex() === 1);
  await page.keyboard.press('ArrowLeft');
  const previous = await page.evaluate(() => slideshow.getCurrentSlideIndex() === 0);
  await page.keyboard.press('p');
  const presenter = await page.locator('body').evaluate(b => b.classList.contains('remark-presenter-mode'));
  await page.keyboard.press('p');
  await page.keyboard.press('?');
  const help = await page.locator('.remark-help').isVisible();
  await page.keyboard.press('Escape');
  await page.evaluate(() => slideshow.gotoSlide('reveal'));
  await page.keyboard.press('ArrowRight');
  const reveal = await page.locator('.remark-visible .answer').isVisible();
  await page.emulateMedia({ media: 'print' });
  const printPages = await page.locator('.remark-slides-area > .remark-slide-container').evaluateAll(es => es.filter(e => getComputedStyle(e).display !== 'none').length);
  await page.pdf({ path: path.join(out, 'print-proof.pdf'), preferCSSPageSize: true, printBackground: true });
  await page.emulateMedia({ media: 'screen' });
  const sizes = [];
  for (const [width, height] of [[1280,720],[1920,1080],[1440,900]]) {
    await page.setViewportSize({ width, height });
    await page.evaluate(() => { slideshow.gotoSlide(1); window.dispatchEvent(new Event('resize')); });
    await page.waitForTimeout(120);
    const r = await page.locator('.remark-visible .remark-slide-content').boundingBox();
    sizes.push({ width, height, fits: r.x >= -1 && r.y >= -1 && r.x + r.width <= width + 1 && r.y + r.height <= height + 1 });
  }
  const report = { browser: browser.version(), states, printPages, slides, errors, network, next, previous, presenter, help, reveal, sizes };
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
  console.log(JSON.stringify(report, null, 2));
  if (states !== 13 || printPages !== 12 || slides.some(s => s.issues.length || s.brokenImages) || errors.length || network.length || !next || !previous || !presenter || !help || !reveal || sizes.some(s => !s.fits)) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
