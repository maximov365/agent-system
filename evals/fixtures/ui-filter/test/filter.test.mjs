import test from 'node:test';
import assert from 'node:assert/strict';
import {filterItems} from '../filter.mjs';
import {items} from '../data.mjs';
test('trimmed case-insensitive search and stable source', () => {
  const before = JSON.stringify(items);
  assert.equal(filterItems(items, ' MARKET ')[0].name, 'Market notes');
  assert.equal(filterItems(items, 'КАРТА')[0].name, 'Карта маршрутов');
  assert.equal(filterItems(items, '').length, 3);
  assert.equal(JSON.stringify(items), before);
});
