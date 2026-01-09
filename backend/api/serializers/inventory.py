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


class CreateInventorySerializer(serializers.Serializer):
    """Serializer for creating inventory items."""
    
    product_code = serializers.CharField(required=True, max_length=100)
    quantity = serializers.IntegerField(required=True, min_value=0)
    
    def validate_quantity(self, value):
        """Ensure quantity is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Quantity must be greater than or equal to 0")
        return value


class SendEmailSerializer(serializers.Serializer):
    """Serializer for send email request."""
    
    email = serializers.EmailField(required=True)
    company_nit = serializers.CharField(required=False, allow_blank=True)
