import {Market, PRODUCTS, readBest, saveBest} from './model.mjs';

const $ = selector => document.querySelector(selector);
const fixture = new URLSearchParams(location.search).get('evidence') === '1';
const market = new Market({seconds: fixture ? 8 : 60, seed: fixture ? 42 : Math.floor(Math.random() * 2 ** 32)});
const storage = {getItem: key => localStorage.getItem(key), setItem: (key, value) => localStorage.setItem(key, value)};
let best = readBest(storage), lastOrder = '', lastStatus = 'ready', soundEnabled = true;
const frames = []; let frameCount = 0, startedAt = performance.now(), lastFrame = performance.now();

class Soundscape {
  constructor() { this.context = null; this.buffers = {}; this.master = null; this.loop = null; this.active = false; }
  async unlock() {
    if (!soundEnabled) return;
    try {
      if (!this.context) {
        this.context = new AudioContext(); this.master = this.context.createGain();
        this.master.gain.value = 0.5; this.master.connect(this.context.destination);
        this.loading = Promise.all(['sea', 'packed', 'complete', 'mistake'].map(async key => {
          const response = await fetch(`assets/runtime/${key}.wav`);
          if (!response.ok) throw Error('Audio unavailable');
          this.buffers[key] = await this.context.decodeAudioData(await response.arrayBuffer());
        }));
      }
      await this.context.resume(); await this.loading;
      if (!this.loop) {
        this.loop = this.context.createBufferSource(); this.loop.buffer = this.buffers.sea;
        this.loop.loop = true; const gain = this.context.createGain(); gain.gain.value = 0.35;
        this.loop.connect(gain).connect(this.master); this.loop.start();
      }
      this.setActive(market.status === 'playing');
    } catch { $('#sound').textContent = 'Звук недоступен'; }
  }
  setActive(active) { this.active = active; if (this.master) this.master.gain.setTargetAtTime(active && soundEnabled ? 0.5 : 0, this.context.currentTime, 0.08); }
  play(key) {
    if (!this.context || !soundEnabled || !this.active || !this.buffers[key]) return;
    const source = this.context.createBufferSource(); source.buffer = this.buffers[key];
    source.connect(this.master); source.start(); source.onended = () => source.disconnect();
  }
}
const audio = new Soundscape();

$('#inventory').innerHTML = PRODUCTS.map(p => `<button class="product" data-product="${p.id}" aria-label="${p.name} — клавиша ${p.key}" disabled><img src="assets/runtime/${p.id}.svg" alt=""><span><b>${p.name}</b><small>${p.detail}</small></span><kbd>${p.key}</kbd></button>`).join('');
function feedback(text, wrong = false) { $('#feedback').textContent = text; $('#feedback').classList.toggle('mistake', wrong); }
function render() {
  const state = market.snapshot(), playing = ['playing', 'paused', 'finished'].includes(state.status);
  document.body.classList.toggle('playing', playing);
  $('.intro-actions').hidden = playing; $('.session-actions').hidden = !playing;
  $('#best').textContent = best;
  const seconds = Math.ceil(state.time_left), clock = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  if ($('#time').textContent !== clock) $('#time').textContent = clock;
  $('#score').textContent = String(state.score).padStart(3, '0'); $('#orders').textContent = String(state.orders).padStart(2, '0');
  $('#time-fill').style.width = `${state.time_left / market.duration * 100}%`;
  $('.time-track').setAttribute('aria-valuemax', market.duration); $('.time-track').setAttribute('aria-valuenow', seconds);
  $('.counter').classList.toggle('urgent', state.time_left < Math.min(10, market.duration / 3));
  const signature = JSON.stringify([state.order, state.packed, state.orders, market.pending > 0]);
  if (signature !== lastOrder) {
    lastOrder = signature;
    $('#order-items').innerHTML = state.order.map((id, index) => {
      const product = PRODUCTS.find(p => p.id === id);
      return `<div class="order-item ${state.packed[index] ? 'packed' : ''}" data-order-product="${id}"><span class="check" aria-label="Добавлено">✓</span><img src="assets/runtime/${id}.svg" alt=""><span>${product.name}</span></div>`;
    }).join('');
    $('#customer').textContent = state.customer;
    $('#order-number').textContent = `№ ${String(state.orders + 1 - (market.pending > 0 ? 1 : 0)).padStart(3, '0')}`;
    $('#order-count').textContent = `${state.packed.filter(Boolean).length} / 3`;
    $('#order-status').textContent = market.pending > 0 ? 'Всё собрано. Спасибо!' : 'Собери всё из списка';
    $('.receipt').classList.toggle('complete', market.pending > 0);
    for (const button of document.querySelectorAll('.product')) button.disabled = state.status !== 'playing' || market.pending > 0;
  }
  if (state.status !== lastStatus) {
    for (const button of document.querySelectorAll('.product')) button.disabled = state.status !== 'playing' || market.pending > 0;
    if (state.status === 'finished') finish();
    lastStatus = state.status;
  }
}
function pick(id) {
  const result = market.pick(id); if (result.kind === 'ignored') return;
  const product = PRODUCTS.find(p => p.id === id), button = $(`[data-product="${id}"]`);
  const effect = result.kind === 'mistake' ? 'wrong' : 'bounce';
  button.classList.remove(effect); void button.offsetWidth; button.classList.add(effect);
  setTimeout(() => button.classList.remove(effect), 350);
  if (result.kind === 'mistake') { feedback('Этого нет в списке. Ничего страшного — ещё раз! −2 сек', true); audio.play('mistake'); }
  else if (result.kind === 'order') {
    feedback(`Заказ готов! +${result.points} очков · Собрано заказов: ${market.orders}`); audio.play('complete');
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) for (let i = 0; i < 10; i++) {
      const spark = document.createElement('span'); spark.className = 'spark'; spark.textContent = '✦';
      spark.style.setProperty('--dx', `${Math.cos(i / 10 * Math.PI * 2) * 100}px`);
      spark.style.setProperty('--dy', `${Math.sin(i / 10 * Math.PI * 2) * 80 - 40}px`);
      $('.counter').append(spark); setTimeout(() => spark.remove(), 700);
    }
  } else { feedback(`${product.name} в корзине. +${result.points}`); audio.play('packed'); }
  render();
}
function start() {
  market.start(); frames.length = 0; frameCount = 0; startedAt = performance.now(); lastFrame = performance.now();
  lastOrder = ''; feedback('Собери три товара из списка. Клавиши 1–4 тоже работают.');
  void audio.unlock(); audio.setActive(true); render();
}
function pauseGame() {
  if (market.status !== 'playing') return;
  market.pause(); audio.setActive(false); $('#pause-dialog').showModal(); render();
}
function resume() {
  $('#pause-dialog').close(); market.resume(); lastFrame = performance.now(); audio.setActive(true); render();
}
function finish() {
  best = saveBest(storage, Math.max(best, market.score)); audio.setActive(false);
  $('#final-score').textContent = market.score;
  $('#result-summary').textContent = `Заказов собрано: ${market.orders}. ${market.mistakes ? `Ошибок: ${market.mistakes}.` : 'И ни одной ошибки.'} Соседи скажут спасибо.`;
  $('#result-dialog').showModal(); $('#best').textContent = best;
}
function back() { $('#result-dialog').close(); market.reset(); lastOrder = ''; feedback('Открой лавку, чтобы принять первый заказ.'); render(); }
$('#start').addEventListener('click', start);
$('#pause').addEventListener('click', pauseGame); $('#resume').addEventListener('click', resume);
$('#retry').addEventListener('click', () => { $('#result-dialog').close(); start(); }); $('#back').addEventListener('click', back);
$('#pause-dialog').addEventListener('cancel', event => { event.preventDefault(); resume(); });
$('#result-dialog').addEventListener('cancel', event => { event.preventDefault(); back(); });
$('#sound').addEventListener('click', () => {
  soundEnabled = !soundEnabled; $('#sound').setAttribute('aria-pressed', String(soundEnabled));
  $('#sound').textContent = soundEnabled ? 'Звук включён' : 'Без звука';
  audio.setActive(market.status === 'playing'); if (soundEnabled) void audio.unlock();
});
for (const button of document.querySelectorAll('.product')) button.addEventListener('click', () => pick(button.dataset.product));
document.addEventListener('keydown', event => {
  if (event.repeat || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.key === 'Escape' && market.status === 'playing') { event.preventDefault(); pauseGame(); return; }
  const product = PRODUCTS.find(p => p.key === event.key);
  if (product) { event.preventDefault(); pick(product.id); }
});
document.addEventListener('visibilitychange', () => { if (document.hidden) pauseGame(); });
function tick(now) {
  const elapsed = now - lastFrame; lastFrame = now;
  if (market.status === 'playing') {
    frameCount++;
    if (frameCount > 30 && elapsed > 0) { frames.push(elapsed); if (frames.length > 7200) frames.shift(); }
    market.tick(elapsed / 1000); render();
  }
  requestAnimationFrame(tick);
}
if (fixture) $('.start-note').textContent = 'Короткая проверочная смена · 8 секунд';
render(); requestAnimationFrame(tick);
window.__agentEvidence = Object.freeze({snapshot: () => {
  const sorted = frames.toSorted((a, b) => a - b);
  const q = p => sorted.length ? Number(sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * p))].toFixed(2)) : null;
  return {...market.snapshot(), evidence_fixture: fixture, best_score: best,
    sound_enabled: soundEnabled, audio_context_state: audio.context?.state || 'not_started',
    frame_samples: frames.length, frame_p50_ms: q(.5), frame_p95_ms: q(.95), frame_p99_ms: q(.99),
    stalls_over_50ms: frames.filter(ms => ms > 50).length, elapsed_wall_seconds: Number(((performance.now() - startedAt) / 1000).toFixed(2)),
    heap_bytes: performance.memory?.usedJSHeapSize ?? null};
}});
