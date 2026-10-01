from .service import search


def handle(items, params):
    return search(items, params.get("q", ""), int(params.get("offset", 0)), int(params.get("limit", 20)))
