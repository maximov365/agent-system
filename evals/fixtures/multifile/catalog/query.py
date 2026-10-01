def matching(items, query):
    return [item for item in items if query in item["title"]]
