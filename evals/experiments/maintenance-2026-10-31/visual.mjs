// Opt-in synthetic comparison. No baseline updates, image edits or production dependencies.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const [output, pixelmatch8Path] = process.argv.slice(2);
if (!output || !pixelmatch8Path) throw Error('Usage: node visual.mjs OUTPUT PIXELMATCH_8_INDEX');
const require = createRequire(new URL('../../../tools/visual/package.json', import.meta.url));
const {chromium} = require('playwright'), {PNG} = require('pngjs');
const pm7 = (await import(pathToFileURL(require.resolve('pixelmatch')))).default;
const pm8 = (await import(pathToFileURL(path.resolve(pixelmatch8Path)))).default;
const html = fs.readFileSync(new URL('checkout.html', import.meta.url), 'utf8');
fs.mkdirSync(output, {recursive:true});
const browser = await chromium.launch({headless:true});
try {
  const page = await browser.newPage({viewport:{width:640,height:480},deviceScaleFactor:1});
  await page.setContent(html);
  const shots = {};
  for (const [name, classes] of Object.entries({baseline:'',identical:'',tint:'tint',shift:'shift',missing:'missing',clip:'clip',contrast:'contrast',broken:'clip contrast overlap'})) {
    await page.evaluate(value => document.body.className=value, classes);
    shots[name] = PNG.sync.read(await page.screenshot({path:path.join(output,`${name}.png`)}));
  }
  const base = shots.baseline, results = [];
  for (const [name, shot] of Object.entries(shots)) {
    const args = [base.data,shot.data,null,base.width,base.height];
    results.push({name,pixelmatch7_total:pm7(...args,{threshold:0.1}),pixelmatch8_total:pm8(...args,{threshold:0.1}),pixelmatch8_window32:pm8(...args,{threshold:0.1,windowSize:32})});
  }
  fs.writeFileSync(path.join(output,'pixelmatch.json'),JSON.stringify({width:base.width,height:base.height,browser:browser.version(),results},null,2)+'\n');
} finally { await browser.close(); }
