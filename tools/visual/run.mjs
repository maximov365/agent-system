#!/usr/bin/env node
/** Local, fixture-driven browser evidence. Capture does not imply visual approval. */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {spawn, execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const idPattern = /^[a-z0-9][a-z0-9_-]{0,79}$/;

export function inside(root, relative) {
  if (typeof relative !== 'string' || path.isAbsolute(relative)) throw Error('Expected a project-relative path');
  const result = path.resolve(root, relative);
  if (result !== root && !result.startsWith(root + path.sep)) throw Error('Path escapes project');
  let current = result;
  while (current !== root) {
    if (fs.existsSync(current) && fs.lstatSync(current).isSymbolicLink()) throw Error('Symlinked evidence/config path');
    current = path.dirname(current);
  }
  return result;
}

function localURL(value) {
  const url = new URL(value);
  if (!['http:', 'https:'].includes(url.protocol) || !['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)) {
    throw Error('Evidence runner requires a local URL');
  }
  if (url.username || url.password) throw Error('Credentials in URL are unsupported');
  return url;
}

export function validateConfig(config, project) {
  if (config.schema_version !== 1) throw Error('Unsupported visual config schema');
  localURL(config.baseURL);
  if (config.reducedMotion !== undefined && !['reduce', 'no-preference'].includes(config.reducedMotion)) throw Error('Invalid reducedMotion');
  if (config.maxDiffRatio !== undefined && (!Number.isFinite(config.maxDiffRatio) || config.maxDiffRatio < 0 || config.maxDiffRatio > 1)) throw Error('maxDiffRatio must be 0..1');
  for (const origin of config.allowedOrigins || []) {
    const url = new URL(origin);
    if (url.protocol !== 'https:' || url.origin !== origin || url.username || url.password) throw Error('Allowed resource origins must be exact HTTPS origins');
  }
  if (!Array.isArray(config.journeys) || !config.journeys.length) throw Error('At least one journey is required');
  if (!Array.isArray(config.viewports) || !config.viewports.length) throw Error('At least one viewport is required');
  const ids = new Set();
  for (const view of config.viewports) {
    if (!idPattern.test(view.name) || ids.has(view.name)) throw Error('Invalid/duplicate viewport name');
    ids.add(view.name);
    for (const dim of ['width', 'height']) if (!Number.isInteger(view[dim]) || view[dim] < 200 || view[dim] > 4096) throw Error('Invalid viewport dimension');
  }
  ids.clear();
  const types = new Set(['click', 'fill', 'press', 'keyDown', 'keyUp', 'waitFor', 'expectText', 'expectCount', 'capture', 'delay', 'tap', 'probe']);
  for (const journey of config.journeys) {
    if (!idPattern.test(journey.id) || ids.has(journey.id)) throw Error('Invalid/duplicate journey ID');
    ids.add(journey.id);
    const url = new URL(journey.route || '/', config.baseURL);
    if (url.origin !== new URL(config.baseURL).origin) throw Error('Journey escapes the configured origin');
    if (!Array.isArray(journey.steps) || !journey.steps.length) throw Error('Journey needs steps');
    const captures = new Set();
    for (const step of journey.steps) {
      if (!types.has(step.type)) throw Error(`Unsupported step: ${step.type}`);
      if (step.type === 'capture') {
        if (!idPattern.test(step.name) || captures.has(step.name)) throw Error('Invalid/duplicate capture name');
        captures.add(step.name);
      }
      if (step.type === 'delay' && (!Number.isFinite(step.ms) || step.ms < 0 || step.ms > 10000)) throw Error('Delay must be 0..10000 ms');
    }
    if (!captures.size) throw Error('Journey must capture at least one state');
    for (const fixture of journey.fixtures || []) {
      if (typeof fixture.path !== 'string' || !fixture.path.startsWith('/')) throw Error('Fixture needs an exact URL path');
    }
  }
  if (config.server) {
    const command = config.server.command;
    if (!Array.isArray(command) || !command.length || command.some(v => typeof v !== 'string' || !v || v.includes('\0'))) throw Error('Server command must be an argv array');
    inside(project, config.server.cwd || '.');
  }
  if (config.baselineDir) inside(project, config.baselineDir);
  return config;
}

function dependencies() {
  const require = process.env.AGENT_NODE_MODULES
    ? createRequire(path.join(path.resolve(process.env.AGENT_NODE_MODULES), '_agent_entry.cjs'))
    : createRequire(import.meta.url);
  try {
    return {chromium: require('playwright').chromium,
      version: require('playwright/package.json').version,
      PNG: require('pngjs').PNG, pixelmatch: require('pixelmatch').default || require('pixelmatch')};
  } catch (error) {
    throw Error('Install the optional visual dependencies with npm ci in .agent-system/visual (or tools/visual in the framework). ' + error.message);
  }
}

async function available(url) {
  try { const r = await fetch(url, {signal: AbortSignal.timeout(700), redirect: 'error'}); return r.status < 500; }
  catch { return false; }
}

function locator(page, step) {
  if (step.role) return page.getByRole(step.role, {name: step.name, exact: step.exact !== false});
  if (step.text !== undefined && !step.selector) return page.getByText(step.text, {exact: step.exact !== false});
  if (!step.selector) throw Error('Step requires a selector, role/name, or text');
  return page.locator(step.selector);
}

export async function run(config, {project, output}) {
  validateConfig(config, project);
  if (fs.existsSync(output)) throw Error('Evidence output already exists; choose a new run directory');
  const deps = dependencies();
  fs.mkdirSync(output, {recursive: true});
  let server, browser, serverLog;
  const report = {schema_version: 1, started_at: new Date().toISOString(), project: path.basename(project),
    config_sha256: hash(JSON.stringify(config)), environment: {platform: process.platform, arch: process.arch,
      node: process.version, playwright: deps.version, browser: null, cpu: os.cpus()[0]?.model},
    revision: null, checks_passed: false, visual_review: 'pending', journeys: []};
  try { report.revision = execFileSync('git', ['rev-parse', 'HEAD'], {cwd: project, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore']}).trim(); } catch {}
  try {
    if (config.server) {
      if (await available(config.baseURL)) throw Error('Configured port is already serving; choose an unused port to avoid touching another session');
      serverLog = fs.openSync(path.join(output, 'server.log'), 'w');
      server = spawn(config.server.command[0], config.server.command.slice(1), {
        cwd: inside(project, config.server.cwd || '.'), shell: false, detached: process.platform !== 'win32',
        stdio: ['ignore', serverLog, serverLog], env: {...process.env, ...config.server.env}});
      let spawnError;
      server.on('error', error => { spawnError = error; });
      const deadline = Date.now() + (config.server.timeoutMs || 30000);
      while (!(await available(config.baseURL))) {
        if (spawnError) throw spawnError;
        if (server.exitCode !== null || Date.now() > deadline) throw Error('Local server did not start; inspect server.log');
        await pause(150);
      }
    }
    browser = await deps.chromium.launch({headless: true,
      ...(process.env.AGENT_BROWSER_EXECUTABLE ? {executablePath: process.env.AGENT_BROWSER_EXECUTABLE} : {})});
    report.environment.browser = browser.version();
    for (const viewport of config.viewports) for (const journey of config.journeys) {
      const name = `${viewport.name}--${journey.id}`;
      const result = {id: name, route: journey.route || '/', viewport, fixtures: (journey.fixtures || []).length,
        captures: [], actions: [], errors: [], console_errors: [], external_resources: [], probes: [], passed: false};
      report.journeys.push(result);
      const context = await browser.newContext({viewport: {width: viewport.width, height: viewport.height},
        deviceScaleFactor: viewport.scale || 1, isMobile: !!viewport.mobile, hasTouch: !!viewport.mobile,
        locale: config.locale || 'en-US', timezoneId: config.timezone || 'UTC', reducedMotion: config.reducedMotion || 'reduce',
        colorScheme: viewport.colorScheme || 'dark', serviceWorkers: 'block',
        ...(config.video ? {recordVideo: {dir: path.join(output, 'video'), size: {width: viewport.width, height: viewport.height}}} : {})});
      const used = new Map();
      await context.route('**/*', async route => {
        const request = route.request(), url = new URL(request.url());
        if (url.origin !== new URL(config.baseURL).origin) {
          if ((config.allowedOrigins || []).includes(url.origin)) {
            result.external_resources.push(url.origin + url.pathname);
            return route.continue();
          }
          result.errors.push(`External request blocked: ${url.origin}${url.pathname}`);
          return route.abort();
        }
        const fixture = (journey.fixtures || []).find(f => f.path === url.pathname && (f.method || 'GET') === request.method());
        if (fixture) {
          const index = used.get(fixture) || 0; used.set(fixture, index + 1);
          const response = fixture.responses ? fixture.responses[Math.min(index, fixture.responses.length - 1)] : fixture;
          return route.fulfill({status: response.status || 200, contentType: 'application/json', body: JSON.stringify(response.body)});
        }
        if (journey.fixtures && url.pathname.startsWith('/api/')) {
          result.errors.push(`Unmocked API request: ${request.method()} ${url.pathname}`);
          return route.abort();
        }
        return route.continue();
      });
      await context.tracing.start({screenshots: true, snapshots: true, sources: false});
      const page = await context.newPage();
      page.setDefaultTimeout(config.timeoutMs || 5000);
      page.on('pageerror', e => result.errors.push(e.message));
      page.on('console', msg => { if (msg.type() === 'error') result.console_errors.push(msg.text()); });
      page.on('response', r => { if (r.status() >= 400) result.errors.push(`HTTP ${r.status()}: ${new URL(r.url()).pathname}`); });
      page.on('dialog', dialog => dialog.dismiss());
      if (config.fixedTime) await page.clock.setFixedTime(new Date(config.fixedTime));
      if (config.seed !== undefined) await context.addInitScript(seed => {
        let state = seed >>> 0; Math.random = () => { state = (1664525 * state + 1013904223) >>> 0; return state / 4294967296; };
      }, config.seed);
      try {
        await page.goto(new URL(result.route, config.baseURL).href, {waitUntil: 'networkidle'});
        for (const step of journey.steps) {
          const start = performance.now();
          switch (step.type) {
            case 'click': await locator(page, step).click(); break;
            case 'fill': await locator(page, step).fill(step.value); break;
            case 'press': await locator(page, step).press(step.key); break;
            case 'keyDown': await page.keyboard.down(step.key); break;
            case 'keyUp': await page.keyboard.up(step.key); break;
            case 'delay': await pause(step.ms); break;
            case 'waitFor': await locator(page, step).waitFor({state: step.state || 'visible'}); break;
            case 'expectText': {
              const element = locator(page, step); await element.waitFor({state: 'visible'});
              const text = await element.innerText();
              if (!text.includes(step.contains)) throw Error(`Expected text ${JSON.stringify(step.contains)}; got ${JSON.stringify(text)}`);
              break;
            }
            case 'expectCount': {
              const count = await locator(page, step).count();
              if (count !== step.count) throw Error(`Expected ${step.count} elements, got ${count}`);
              break;
            }
            case 'tap': await page.mouse.click(step.x, step.y); break;
            case 'probe': {
              const data = await page.evaluate(() => window.__agentEvidence?.snapshot?.() ?? null);
              if (data === null) throw Error('No application evidence snapshot hook');
              result.probes.push(data);
              for (const [key, expected] of Object.entries(step.equals || {})) {
                if (data[key] !== expected) throw Error(`Probe ${key}: expected ${expected}, got ${data[key]}`);
              }
              break;
            }
            case 'capture': {
              await page.evaluate(() => document.fonts.ready);
              const file = `${name}--${step.name}.png`;
              const buffer = await page.screenshot({path: path.join(output, file), fullPage: step.fullPage !== false, animations: 'disabled'});
              const capture = {file, sha256: hash(buffer), baseline: 'not_configured'};
              if (config.baselineDir) {
                const base = inside(project, path.join(config.baselineDir, file));
                capture.baseline = fs.existsSync(base) ? 'compared' : 'missing';
                if (!fs.existsSync(base)) throw Error(`Missing approved baseline: ${file}`);
                const actual = deps.PNG.sync.read(buffer), expected = deps.PNG.sync.read(fs.readFileSync(base));
                if (actual.width !== expected.width || actual.height !== expected.height) throw Error(`Baseline dimensions differ: ${file}`);
                const diff = new deps.PNG({width: actual.width, height: actual.height});
                capture.changed_pixels = deps.pixelmatch(expected.data, actual.data, diff.data, actual.width, actual.height, {threshold: 0.1});
                capture.changed_ratio = capture.changed_pixels / (actual.width * actual.height);
                if (capture.changed_ratio > (config.maxDiffRatio ?? 0.001)) {
                  fs.writeFileSync(path.join(output, file.replace('.png', '--diff.png')), deps.PNG.sync.write(diff));
                  result.errors.push(`Visual baseline changed: ${file} (${capture.changed_ratio})`);
                }
              }
              result.captures.push(capture);
              break;
            }
          }
          result.actions.push({type: step.type, duration_ms: Math.round(performance.now() - start)});
        }
        result.passed = !result.errors.length && !result.console_errors.length;
      } catch (error) {
        result.errors.push(error.message);
        try { await page.screenshot({path: path.join(output, `${name}--failure.png`)}); } catch {}
      } finally {
        await context.tracing.stop({path: path.join(output, `${name}--trace.zip`)});
        await context.close();
      }
    }
    report.checks_passed = report.journeys.every(j => j.passed);
  } catch (error) { report.error = error.message; }
  finally {
    if (browser) await browser.close();
    if (server?.pid) {
      try { process.kill(process.platform === 'win32' ? server.pid : -server.pid, 'SIGTERM'); } catch {}
      await pause(250);
      if (server.exitCode === null) try { process.kill(process.platform === 'win32' ? server.pid : -server.pid, 'SIGKILL'); } catch {}
    }
    if (serverLog !== undefined) fs.closeSync(serverLog);
    report.finished_at = new Date().toISOString();
    fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
    const escape = text => String(text).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
    const body = report.journeys.map(j => `<section><h2>${escape(j.id)} · ${j.passed ? 'checks passed' : 'failed'}</h2><pre>${escape(j.errors.concat(j.console_errors).join('\n'))}</pre>${j.captures.map(c => `<figure><img src="${c.file}" alt="${escape(c.file)}"><figcaption>${escape(c.file)}</figcaption></figure>`).join('')}</section>`).join('');
    fs.writeFileSync(path.join(output, 'index.html'), `<!doctype html><html lang="en"><meta charset="utf-8"><title>Visual evidence</title><style>body{font:16px system-ui;background:#111a22;color:#e7eef5;margin:32px}figure{display:inline-block;vertical-align:top;margin:8px}img{max-width:440px;max-height:760px}pre{color:#ffb4a0;white-space:pre-wrap}section{border-top:1px solid #45545c;margin-top:32px}</style><h1>Visual evidence · ${escape(report.project)}</h1><p>Automated checks: ${report.checks_passed ? 'passed' : 'failed'}. Visual review: pending.</p><p>${escape(report.error || '')}</p>${body}</html>`);
  }
  return report;
}

async function main() {
  const args = process.argv.slice(2), options = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--check') options.check = true;
    else if (['--project', '--config', '--output'].includes(args[i])) options[args[i].slice(2)] = args[++i];
    else throw Error(`Unknown argument: ${args[i]}`);
  }
  const project = fs.realpathSync(options.project || process.cwd());
  const configPath = inside(project, options.config || 'quality/visual.config.json');
  const config = validateConfig(JSON.parse(fs.readFileSync(configPath, 'utf8')), project);
  if (options.check) { console.log('Visual configuration valid; no commands or browser launched.'); return; }
  const output = inside(project, options.output || `.agent/evidence/visual/${new Date().toISOString().replace(/[:.]/g, '-')}`);
  const report = await run(config, {project, output});
  console.log(JSON.stringify({checks_passed: report.checks_passed, visual_review: report.visual_review, report: path.join(output, 'index.html')}));
  if (!report.checks_passed) process.exitCode = 1;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
