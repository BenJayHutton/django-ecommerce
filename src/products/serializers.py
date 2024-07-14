from rest_framework import serializers
from rest_framework.reverse import reverse

from api.serializers import UserPublicSerializer

from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    owner = UserPublicSerializer(source='user', read_only=True)
    edit_url = serializers.SerializerMethodField(read_only=True)
    url= serializers.HyperlinkedIdentityField(
        view_name='api:product-detail',
        lookup_field = 'pk',
    )
    class Meta:
        model= Product
        # required fields, if you don't send them for serialization, 
        # it will returna valid error
        fields = [
            'owner',
            'url',
            'edit_url',
            'pk',
            'title',
            'slug',
            'description',
            'price',
        ]
    def get_edit_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        return reverse("api:product-update", kwargs={"pk":obj.pk}, request=request)
    
    def get_my_discount(self, obj):
        if not hasattr(obj,'id'):
            return None
        if not isinstance(obj, Product):
            return None
        return obj.get_discount()