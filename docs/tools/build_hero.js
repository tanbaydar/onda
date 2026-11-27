// Build the README hero image (three screens with captions) for the light and the dark theme.
//
// Run:    node docs/tools/build_hero.js
// Needs:  playwright, and pngquant on the PATH
//
// The script reads the screenshots in docs/assets/screens and the product fonts in frontend/fonts.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const repo = path.resolve(__dirname, '..', '..');
const out = path.join(repo, 'docs', 'assets');
const font = name => `file://${path.join(repo, 'frontend', 'fonts', name)}`;
const shot = name => `file://${path.join(out, 'screens', name)}`;

const SCREENS = [
  ['home.png', '01 · Home', 'See what your friends are up to'],
  ['discover.png', '02 · Discover', 'Find events in your city'],
  ['event.png', '03 · Event', 'Hear it from people who were there'],
];
const THEMES = {
  light: '--hair:#DCDCDC;--muted:#6E6E6E;--ink:#1B1B1B',
  dark: '--hair:#30363D;--muted:#8B949E;--ink:#E6EDF3',
};

const page = theme => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"General Sans";src:url("${font('GeneralSans-Medium.woff2')}");font-weight:500}
@font-face{font-family:"Rozha One";src:url("${font('RozhaOne-Regular.woff2')}")}
html,body{margin:0;background:transparent}
.wrap{${THEMES[theme]};width:896px;padding:8px 0 4px;display:flex;justify-content:center;gap:44px}
.cell{width:236px}
.shot{width:236px;height:512px;overflow:hidden;border:1px solid var(--hair);background:#fff;box-sizing:border-box}
.shot img{width:234px;display:block}
.over{margin-top:16px;font:500 11px "General Sans",sans-serif;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.name{margin-top:4px;font:21px/1.15 "Rozha One",serif;color:var(--ink)}
</style></head><body><div class="wrap">${SCREENS.map(([file, over, name]) =>
  `<div class="cell"><div class="shot"><img src="${shot(file)}"></div><div class="over">${over}</div><div class="name">${name}</div></div>`).join('')}
</div></body></html>`;

(async () => {
  const browser = await chromium.launch();
  for (const theme of Object.keys(THEMES)) {
    const html = path.join(out, `.hero-${theme}.html`);
    const png = path.join(out, `hero-${theme}.png`);
    fs.writeFileSync(html, page(theme));
    const context = await browser.newContext({ viewport: { width: 896, height: 700 }, deviceScaleFactor: 2 });
    const tab = await context.newPage();
    await tab.goto(`file://${html}`);
    await tab.waitForTimeout(600);
    await (await tab.$('.wrap')).screenshot({ path: png, omitBackground: true });
    await context.close();
    fs.unlinkSync(html);
    execFileSync('pngquant', ['--quality=85-98', '--speed', '1', '--force', '--output', png, png]);
    console.log(`wrote ${path.relative(repo, png)}`);
  }
  await browser.close();
})();
