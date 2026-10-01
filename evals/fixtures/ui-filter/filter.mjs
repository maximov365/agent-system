export function filterItems(items, query = '') {
  return items.filter(item => item.name.includes(query));
}
