from decimal import Decimal, InvalidOperation
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
    """Serializer for creating a Product with domain validation."""
    
    class Meta:
        model = Product
        fields = ['code', 'name', 'features', 'prices']
    
    def validate_code(self, value):
        """Validate product code is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty")
        return value.strip()
    
    def validate_name(self, value):
        """Validate product name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()
    
    def validate_features(self, value):
        """Validate features is a list."""
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Features must be a list")
        # Validate each feature is a non-empty string
        validated_features = []
        for feature in value:
            if not isinstance(feature, str):
                raise serializers.ValidationError("Each feature must be a string")
            feature_stripped = feature.strip()
            if not feature_stripped:
                raise serializers.ValidationError("Features cannot be empty strings")
            validated_features.append(feature_stripped)
        return validated_features
    
    def validate_prices(self, value):
        """
        Validate prices structure and business rules.
        
        Expected format:
        {
            "USD": {"amount": 100.00, "currency": "USD"},
            "COP": {"amount": 400000.00, "currency": "COP"}
        }
        
        Validates:
        - Prices is a non-empty dictionary
        - Each currency code is valid (USD, EUR, COP)
        - Each price has 'amount' and 'currency' fields
        - Amount is a positive number
        - Currency matches the key
        """
        if not value:
            raise serializers.ValidationError("At least one price is required")
        
        if not isinstance(value, dict):
            raise serializers.ValidationError("Prices must be a dictionary with currency codes as keys")
        
        # Valid currencies from domain layer
        VALID_CURRENCIES = ['USD', 'EUR', 'COP']
        
        validated_prices = {}
        for currency_code, price_data in value.items():
            # Validate currency code
            currency_upper = currency_code.strip().upper()
            if currency_upper not in VALID_CURRENCIES:
                raise serializers.ValidationError(
                    f"Invalid currency code: '{currency_code}'. Valid currencies are: {', '.join(VALID_CURRENCIES)}"
                )
            
            # Validate price structure
            if not isinstance(price_data, dict):
                raise serializers.ValidationError(
                    f"Price for {currency_upper} must be an object with 'amount' and 'currency' fields"
                )
            
            if 'amount' not in price_data:
                raise serializers.ValidationError(
                    f"Price for {currency_upper} must include 'amount' field"
                )
            
            if 'currency' not in price_data:
                raise serializers.ValidationError(
                    f"Price for {currency_upper} must include 'currency' field"
                )
            
            # Validate currency field matches key
            price_currency = str(price_data['currency']).strip().upper()
            if price_currency != currency_upper:
                raise serializers.ValidationError(
                    f"Currency mismatch: key is '{currency_upper}' but currency field is '{price_currency}'"
                )
            
            # Validate amount is positive
            try:
                amount = Decimal(str(price_data['amount']))
            except (InvalidOperation, ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Invalid amount for {currency_upper}: must be a valid number"
                )
            
            if amount <= 0:
                raise serializers.ValidationError(
                    f"Amount for {currency_upper} must be greater than zero"
                )
            
            # Store validated price
            validated_prices[currency_upper] = {
                'amount': float(amount),
                'currency': currency_upper
            }
        
        return validated_prices


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Product list."""
    
    company_nit = serializers.CharField(source='company.nit', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['code', 'name', 'company_nit', 'company_name']
