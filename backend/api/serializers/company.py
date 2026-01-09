from rest_framework import serializers
from infrastructure.models import Company


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""
    
    class Meta:
        model = Company
        fields = ['nit', 'name', 'address', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CompanyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Company list."""
    
    class Meta:
        model = Company
        fields = ['nit', 'name', 'address', 'phone']
