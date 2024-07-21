from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Product

@register(Product)
class ProductIndex(AlgoliaIndex):
    # should_index = 'is_public'
    fields = [
        'title',
        'description',
        'price',
        'public',
        'tag_name',
        'user',
        'public',
    ]
    tags='tag_name'
    settings = {
        'searchableAttributes': ['title', 'description'],
        'attributesForFaceting':['user', 'public']
    }