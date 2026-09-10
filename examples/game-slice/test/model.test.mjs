import test from 'node:test';
import assert from 'node:assert/strict';
import {Market, readBest, saveBest} from '../model.mjs';
test('order rewards, pending lock, next order and reproducible seed', () => {
  const a = new Market(), b = new Market(); a.start(); b.start();
  for (const m of [a,b]) {
    assert.equal(m.pick('bread').kind, 'packed'); m.pick('orange');
    assert.equal(m.pick('fish').kind, 'order'); assert.equal(m.orders, 1); assert.equal(m.score, 125);
    assert.equal(m.pick('bread').kind, 'ignored'); m.tick(.7);
  }
  assert.deepEqual(a.snapshot(), b.snapshot()); assert.equal(new Set(a.order).size, 3);
});
test('pause freezes time and input; resume and reset work', () => {
  const m = new Market(); m.start(); m.pause(); m.tick(10);
  assert.equal(m.timeLeft, 60); assert.equal(m.pick('bread').kind, 'ignored');
  m.resume(); m.tick(1); assert.equal(m.timeLeft, 59); m.reset(); assert.equal(m.status, 'ready');
});
test('wrong/duplicate input penalizes time and cannot create a negative score', () => {
  const m = new Market({seconds: 3}); m.start();
  assert.equal(m.pick('flowers').kind, 'mistake'); assert.equal(m.score, 0);
  m.pick('bread'); assert.equal(m.pick('bread').kind, 'mistake');
  assert.equal(m.status, 'finished'); assert.equal(m.timeLeft, 0);
  assert.equal(m.pick('fish').kind, 'ignored');
});
test('timer ends session and retry creates a clean state', () => {
  const m = new Market({seconds: 1}); m.start(); m.tick(2);
  assert.equal(m.status, 'finished'); m.start(); assert.equal(m.status, 'playing');
  assert.equal(m.score, 0); assert.equal(m.mistakes, 0); assert.equal(m.timeLeft, 1);
});
test('corrupt/unavailable persistence is safe and cannot lower the best score', () => {
  let value = 'corrupt'; const storage = {getItem: () => value, setItem: (_, v) => { value = v; }};
  assert.equal(readBest(storage), 0); assert.equal(saveBest(storage, 125), 125);
  assert.equal(saveBest(storage, 20), 125); value = '-8'; assert.equal(readBest(storage), 0);
  const unavailable = {getItem() {throw Error('blocked')}, setItem() {throw Error('blocked')}};
  assert.equal(saveBest(unavailable, 100), 100);
});
