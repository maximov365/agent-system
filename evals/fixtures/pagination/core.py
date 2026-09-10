def page(items, offset=0, limit=20):
    """Return an independent page list. Negative offset is clamped to zero;
    nonpositive limit returns []; a page may end exactly at the sequence end.
    Inputs are a finite sequence and integer offset/limit. Never mutate items.
    """
    return items[offset:offset + limit - 1]
