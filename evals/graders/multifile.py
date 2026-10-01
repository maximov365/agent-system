import copy
import sys
sys.path.insert(0, sys.argv[1])
from catalog.api import handle
from catalog.service import search

items = [{"title": "Straße", "tag": "one"}, {"title": "STRASSE", "tag": "two"}, {"title": "Карта"}]
before = copy.deepcopy(items)
for query, total in [(" STRASSE ", 2), ("кар", 1), ("", 3), ("unknown", 0)]:
    for offset in [-2, 0, 1, 20]:
        for limit in [-1, 0, 1, 20]:
            matches = [x for x in items if query.strip().casefold() in x["title"].casefold()]
            expected = matches[max(offset, 0):max(offset, 0) + max(limit, 0)]
            result = handle(items, {"q": query, "offset": str(offset), "limit": str(limit)})
            assert result == {"items": expected, "total": total}, (query, offset, limit, result)
            if result["items"]:
                result["items"][0]["tag"] = "changed"
            assert items == before
for name in ["offset", "limit"]:
    for bad in [True, False, 1.5, "1.5", "abc", None, []]:
        try:
            handle(items, {name: bad})
        except ValueError:
            pass
        else:
            raise AssertionError((name, bad))
assert search(items, "кар", -1, 1)["items"] == [{"title": "Карта"}]
print("64 search combinations, input independence and 14 invalid API parameters passed")
