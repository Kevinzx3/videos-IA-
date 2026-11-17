// Usage: node render.js <dir-with-escena.html,words.json> <duration> <outFramesDir> [t1,t2,...]  (no times = full 30fps render)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [dir, dur, out, times] = [process.argv[2], +process.argv[3], process.argv[4], process.argv[5]];
  const html = fs.readFileSync(path.join(dir, 'escena.html'), 'utf8')
    .replace('__WORDS__', fs.readFileSync(path.join(dir, 'words.json'), 'utf8')).replace('__DUR__', dur);
  fs.mkdirSync(out, { recursive: true }); const tmp = path.join(out, '_page.html'); fs.writeFileSync(tmp, html);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
  if (errs.length) { console.error(errs); process.exit(1); }
  const list = times ? times.split(',').map(Number) : Array.from({ length: Math.ceil(dur * 30) }, (_, i) => i / 30);
  for (let i = 0; i < list.length; i++) {
    await p.evaluate(t => render(t), list[i]);
    await p.screenshot({ path: path.join(out, (times ? 't' + list[i] : String(i).padStart(5, '0')) + '.jpg'), type: 'jpeg', quality: 92 });
  }
  if (errs.length) { console.error(errs); process.exit(1); }
  await b.close(); console.log('frames', list.length);
})();
