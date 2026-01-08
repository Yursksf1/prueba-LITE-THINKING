"""
Domain Service for product registration.

Orchestrates product creation with company validation.
Encapsulates the rule: "A product must belong to an existing company."
"""
from typing import Protocol

from ..entities.product import Product
from ..entities.money import Money
from ..exceptions.errors import InvalidProductError, InvalidCompanyError


class CompanyRepository(Protocol):
    """
    Port: Abstraction for checking if a company exists.
    Implemented in infrastructure layer, not part of domain.
    """
    
    def exists(self, nit: str) -> bool:
        """Check if company with given NIT exists."""
        ...


class ProductRegistrationService:
    """
    Orchestrates product creation and company validation.
    
    Responsibilities:
    - Validate product data
    - Verify company exists (cross-entity rule)
    - Ensure price structure is valid
    - Serve as single entry point for product registration
    
    This is a domain service because it coordinates:
    - Product entity validation
    - Company existence check (requires external verification)
    """
    
    def __init__(self, company_repository: CompanyRepository):
        """
        Initialize with dependency on company verification.
        
        Args:
            company_repository: Port for checking company existence
        """
        self.company_repository = company_repository
    
    def register(
        self,
        code: str,
        name: str,
        features: list,
        prices: dict,
        company_nit: str,
    ) -> Product:
        """
        Register a new product for a company.
        
        Args:
            code: Product identifier (SKU or similar)
            name: Product name
            features: List of product characteristics
            prices: Dict mapping currency codes to Money objects
            company_nit: NIT of the company that owns the product
        
        Returns:
            Valid Product instance
            
        Raises:
            InvalidCompanyError: If company does not exist
            InvalidProductError: If product data violates business rules
        """
        # Policy: Product must belong to an existing company
        if not self.company_repository.exists(company_nit):
            raise InvalidCompanyError(
                f"Cannot register product: Company with NIT '{company_nit}' does not exist"
            )
        
        # Product.__post_init__ performs intrinsic validations
        try:
            product = Product(
                code=code,
                name=name,
                features=tuple(features) if features else (),
                prices=prices,
                company_nit=company_nit,
            )
        except (InvalidProductError, InvalidCompanyError) as exc:
            raise InvalidProductError(f"Failed to register product: {exc}") from exc
        
        return product
