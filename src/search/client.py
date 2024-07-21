from algoliasearch_django import algolia_engine

def get_client():
    return algolia_engine.client

def get_index(index_name='Product'):
    client = get_client()
    index = client.init_index(index_name)
    return index


def perform_serch(query, **kwargs):
    index = get_index()
    params = []
    tag = ""
    if "tags" in kwargs:
        tags = kwargs.pop("tags") or []
        if len(tags) != 0:
            params["tagsFilters"] = tags
    results = index.search(query)
    return results