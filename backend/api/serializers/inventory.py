from rest_framework import serializers
from infrastructure.models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for InventoryItem model."""
    
    company_nit = serializers.CharField(source='company.nit', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    prices = serializers.JSONField(source='product.prices', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'company_nit', 'company_name', 
            'product_code', 'product_name', 
            'quantity', 'prices', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SendEmailSerializer(serializers.Serializer):
    """Serializer for send email request."""
    
    email = serializers.EmailField(required=True)
    company_nit = serializers.CharField(required=False, allow_blank=True)
