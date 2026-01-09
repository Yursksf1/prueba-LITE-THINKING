from rest_framework import serializers
from infrastructure.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class LoginSerializer(serializers.Serializer):
    """Serializer for login request."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response."""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
