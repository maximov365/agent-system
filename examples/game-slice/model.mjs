export const PRODUCTS = [
  {id: 'bread', name: 'Хлеб', detail: 'Ещё тёплый', key: '1'},
  {id: 'orange', name: 'Апельсины', detail: 'Солнечные и сладкие', key: '2'},
  {id: 'fish', name: 'Рыба', detail: 'Утренний улов', key: '3'},
  {id: 'flowers', name: 'Цветы', detail: 'Маленькая радость', key: '4'},
];
export const CUSTOMERS = ['Соседка Анна', 'Капитан Марко', 'Хранитель маяка', 'Садовница Мила', 'Пекарь Лука', 'Рыбачка Нина'];
export class Market {
  constructor({seconds = 60, seed = 42} = {}) {
    if (!Number.isFinite(seconds) || seconds <= 0) throw Error('Positive session duration required');
    this.duration = seconds; this.seed = seed >>> 0; this.reset();
  }
  reset() {
    this.randomState = this.seed; this.status = 'ready'; this.timeLeft = this.duration;
    this.score = 0; this.orders = 0; this.mistakes = 0; this.combo = 0; this.pending = 0;
    this.order = ['bread', 'orange', 'fish']; this.packed = [false, false, false];
  }
  random() { this.randomState = (1664525 * this.randomState + 1013904223) >>> 0; return this.randomState / 4294967296; }
  start() { this.reset(); this.status = 'playing'; }
  pause() { if (this.status === 'playing') this.status = 'paused'; }
  resume() { if (this.status === 'paused') this.status = 'playing'; }
  pick(id) {
    if (this.status !== 'playing' || this.pending > 0 || !PRODUCTS.some(p => p.id === id)) return {kind: 'ignored'};
    const index = this.order.findIndex((product, i) => product === id && !this.packed[i]);
    if (index === -1) {
      this.mistakes++; this.combo = 0; this.timeLeft = Math.max(0, this.timeLeft - 2);
      if (this.timeLeft === 0) this.status = 'finished';
      return {kind: 'mistake', product: id};
    }
    this.packed[index] = true;
    const points = 25 + Math.min(3, this.combo) * 5; this.score += points;
    if (this.packed.every(Boolean)) {
      this.orders++; this.combo++; this.score += 50; this.pending = 0.65;
      return {kind: 'order', points: points + 50, product: id};
    }
    return {kind: 'packed', points, product: id};
  }
  tick(seconds) {
    if (this.status !== 'playing' || !Number.isFinite(seconds) || seconds <= 0) return;
    this.timeLeft = Math.max(0, this.timeLeft - seconds);
    if (this.timeLeft === 0) { this.status = 'finished'; return; }
    if (this.pending > 0) {
      this.pending -= seconds;
      if (this.pending <= 0) {
        const pool = PRODUCTS.map(p => p.id);
        for (let i = pool.length - 1; i > 0; i--) {
          const j = Math.floor(this.random() * (i + 1)); [pool[i], pool[j]] = [pool[j], pool[i]];
        }
        this.order = pool.slice(0, 3); this.packed = [false, false, false]; this.pending = 0;
      }
    }
  }
  snapshot() {
    return {status: this.status, score: this.score, orders: this.orders, mistakes: this.mistakes,
      time_left: Number(this.timeLeft.toFixed(2)), combo: this.combo,
      order: [...this.order], packed: [...this.packed], customer: CUSTOMERS[Math.max(0, this.orders - (this.pending > 0 ? 1 : 0)) % CUSTOMERS.length]};
  }
}

export function readBest(storage) {
  try { const value = Number(storage.getItem('lantern-market-best-v1')); return Number.isSafeInteger(value) && value >= 0 ? value : 0; }
  catch { return 0; }
}
export function saveBest(storage, score) {
  const best = Math.max(readBest(storage), Number.isSafeInteger(score) && score >= 0 ? score : 0);
  try { storage.setItem('lantern-market-best-v1', String(best)); } catch {}
  return best;
}
