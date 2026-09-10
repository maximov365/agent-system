def get_document(records, actor_id, document_id):
    """Return (status, body). A nonempty string actor must authenticate first.
    Only a document's owner may read it. Missing/foreign documents both return
    (404, {'error': 'not_found'}). Unauthenticated requests return
    (401, {'error': 'unauthorized'}). Authorized body exposes only id and title.
    """
    record = records.get(document_id)
    if record is None:
        return 404, {'error': 'not_found'}
    return 200, dict(record)
