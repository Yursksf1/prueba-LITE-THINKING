"""
Application use cases for product management.

Use cases orchestrate domain services and coordinate between layers.
"""
from infrastructure.domain_loader import ensure_domain_in_path
ensure_domain_in_path()

from domain.entities.product import Product as DomainProduct
from domain.entities.money import Money
from domain.entities.currency import Currency
from domain.services.product_registration_service import ProductRegistrationService
from domain.exceptions.errors import InvalidProductError, InvalidCompanyError, InvalidPriceError

from infrastructure.repositories import DjangoCompanyRepository
from infrastructure.models import Product as DjangoProduct, Company as DjangoCompany


class RegisterProductUseCase:
    """
    Use case for registering a new product.
    
    Orchestrates:
    - Domain validation via ProductRegistrationService
    - Persistence via Django ORM
    """
    
    def __init__(self):
        self.company_repository = DjangoCompanyRepository()
        self.domain_service = ProductRegistrationService(self.company_repository)
    
    def execute(
        self,
        code: str,
        name: str,
        features: list,
        prices: dict,
        company_nit: str
    ) -> DjangoProduct:
        """
        Register a new product with domain validation.
        
        Args:
            code: Product code
            name: Product name
            features: List of product features
            prices: Dict with currency codes as keys and amounts as values
                   Format: {"USD": 100.00, "COP": 400000.00}
            company_nit: Company NIT
            
        Returns:
            Django Product model instance
            
        Raises:
            InvalidCompanyError: If company doesn't exist
            InvalidProductError: If product data is invalid
            InvalidPriceError: If price data is invalid
        """
        # Convert prices dict to domain Money objects
        domain_prices = {}
        for currency_code, amount in prices.items():
            currency = Currency.from_code(currency_code)
            domain_prices[currency_code] = Money(amount=amount, currency=currency)
        
        # Use domain service for validation
        domain_product = self.domain_service.register(
            code=code,
            name=name,
            features=features,
            prices=domain_prices,
            company_nit=company_nit
        )
        
        # Convert domain entity to Django model and persist
        try:
            company = DjangoCompany.objects.get(nit=company_nit)
        except DjangoCompany.DoesNotExist:
            # This should not happen as domain service validates company exists
            # But we handle it defensively to provide a clear error
            raise InvalidCompanyError(
                f"Company with NIT '{company_nit}' not found during persistence"
            )
        
        # Convert domain Money objects back to simple dict for Django
        django_prices = {}
        for currency_code, money in domain_product.prices.items():
            django_prices[currency_code] = float(money.amount)
        
        django_product = DjangoProduct.objects.create(
            code=domain_product.code,
            name=domain_product.name,
            features=list(domain_product.features),
            prices=django_prices,
            company=company
        )
        
        return django_product
