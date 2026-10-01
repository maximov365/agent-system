from .query import matching


def search(items, query="", offset=0, limit=20):
    rows = matching(items, query)
    return {"items": rows[offset:offset + limit], "total": len(rows)}
