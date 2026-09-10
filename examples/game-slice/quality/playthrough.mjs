import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const require=createRequire(new URL('../../../tools/visual/package.json',import.meta.url));
const {chromium}=require('playwright');
const project=new URL('../',import.meta.url).pathname;
const output=project+'.agent/evidence/normal-play-'+Date.now();fs.mkdirSync(output,{recursive:true});
const server=spawn('node',['server.mjs'],{cwd:project,stdio:'ignore'});
let browser;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
try {
 for(let i=0;i<40;i++){try{if((await fetch('http://127.0.0.1:4321')).ok)break;}catch{}await sleep(100);}
 browser=await chromium.launch();const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'no-preference'});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4321');await page.locator('#start').click();
 const events=[];let paused=false,mistake=false,captured=false;
 while(await page.evaluate(()=>window.__agentEvidence.snapshot().status)==='playing'){
  const state=await page.evaluate(()=>window.__agentEvidence.snapshot());
  if(!mistake){await page.locator('[data-product="flowers"]').click();mistake=true;events.push({action:'wrong-item',time:state.time_left});}
  if(state.orders>=2&&!paused){await page.locator('#pause').click();const before=await page.evaluate(()=>window.__agentEvidence.snapshot());await sleep(1500);const after=await page.evaluate(()=>window.__agentEvidence.snapshot());assert.equal(before.time_left,after.time_left);await page.locator('#resume').click();paused=true;events.push({action:'pause-resume',time:state.time_left});}
  const remaining=page.locator('.order-item:not(.packed)');
  const visible=await remaining.count() ? await remaining.first().getAttribute('data-order-product') : null;
  if(visible&&await page.locator(`[data-product="${visible}"]`).isEnabled()){await page.locator(`[data-product="${visible}"]`).click();await sleep(180);}
  else await sleep(120);
  if(state.orders>=4&&!captured){await page.screenshot({path:output+'/playing.png'});captured=true;}
 }
 const result=await page.evaluate(()=>window.__agentEvidence.snapshot());assert.equal(result.status,'finished');assert.ok(result.orders>5);assert.ok(result.frame_samples>2500);assert.ok(result.frame_p95_ms<=25);assert.deepEqual(errors,[]);await page.screenshot({path:output+'/result.png'});
 await page.reload();const restored=await page.evaluate(()=>window.__agentEvidence.snapshot());assert.equal(restored.best_score,result.score);
 fs.writeFileSync(output+'/report.json',JSON.stringify({method:'Owner-authored adaptive DOM playthrough; no human player study',motion:'no-preference',viewport:'1440x1000 desktop Chromium',events,result,reload_best:restored.best_score,errors},null,2));
 console.log(JSON.stringify({result,events,reload_best:restored.best_score,errors}));
}finally{await browser?.close();server.kill('SIGTERM');}
