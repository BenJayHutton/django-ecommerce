from rest_framework import serializers

from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model= Product
        # required fields, if you don't send them for serialization, 
        # it will returna valid error
        fields = [
            'title',
            'slug',
        ]
        