from rest_framework import serializers
from infrastructure.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    company_nit = serializers.CharField(source='company.nit', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'code', 'name', 'features', 'prices', 
            'company_nit', 'company_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a Product."""
    
    class Meta:
        model = Product
        fields = ['code', 'name', 'features', 'prices']


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Product list."""
    
    company_nit = serializers.CharField(source='company.nit', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['code', 'name', 'company_nit', 'company_name']
