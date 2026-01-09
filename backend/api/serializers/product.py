from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from infrastructure.models import Product


# Valid currency codes - MUST match domain.entities.currency.Currency enum
# Located at: domain/src/domain/entities/currency.py
# If currencies are added to domain, they MUST be added here as well
# Current valid currencies: USD, EUR, COP
VALID_CURRENCIES = ['USD', 'EUR', 'COP']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    company_nit = serializers.CharField(source='company.nit', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    prices = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'code', 'name', 'features', 'prices',
            'company_nit', 'company_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_prices(self, obj):
        # Expose as {"USD": 100.0, ...}
        if not obj.prices:
            return {}
        # If legacy structure, convert
        result = {}
        for k, v in obj.prices.items():
            if isinstance(v, dict) and 'amount' in v:
                try:
                    result[k] = float(v['amount'])
                except Exception:
                    result[k] = v['amount']
            else:
                result[k] = v
        return result


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
        Validate prices structure and business rules for new format.
        Expected format:
        {
            "USD": 100.00,
            "COP": 400000.00
        }
        Validates:
        - Prices is a non-empty dictionary
        - Each currency code is valid
        - Each price is a positive number
        """
        if not value:
            raise serializers.ValidationError("At least one price is required")
        if not isinstance(value, dict):
            raise serializers.ValidationError("Prices must be a dictionary with currency codes as keys")
        validated_prices = {}
        for currency_code, amount in value.items():
            currency_upper = currency_code.strip().upper()
            if currency_upper not in VALID_CURRENCIES:
                raise serializers.ValidationError(
                    f"Invalid currency code: '{currency_code}'. Valid currencies are: {', '.join(VALID_CURRENCIES)}"
                )
            try:
                amount_val = Decimal(str(amount))
            except (InvalidOperation, ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Invalid amount for {currency_upper}: must be a valid number"
                )
            if amount_val <= 0:
                raise serializers.ValidationError(
                    f"Amount for {currency_upper} must be greater than zero"
                )
            validated_prices[currency_upper] = float(amount_val)
        return validated_prices


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Product list."""
    
    company_nit = serializers.CharField(source='company.nit', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['code', 'name', 'company_nit', 'company_name']
