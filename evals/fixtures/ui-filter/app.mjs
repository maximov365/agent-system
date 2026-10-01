import {items} from './data.mjs';
import {filterItems} from './filter.mjs';
const input = document.querySelector('#query');
const list = document.querySelector('#results');
function render() {
  list.replaceChildren(...filterItems(items, input.value).map(item => {
    const row = document.createElement('li');
    row.textContent = `${item.name} — ${item.category}`;
    return row;
  }));
  document.querySelector('#count').textContent = `${list.children.length} results`;
  document.querySelector('#empty').hidden = list.children.length !== 0;
}
input.addEventListener('input', render);
render();
