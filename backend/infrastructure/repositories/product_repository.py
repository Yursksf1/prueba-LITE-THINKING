"""
Django ORM adapter for Product repository.

Implements the ProductRepository protocol from domain layer.
"""
from infrastructure.models import Product as DjangoProduct


class DjangoProductRepository:
    """
    Adapter that implements domain's ProductRepository protocol.
    
    Translates between domain needs and Django ORM operations.
    """
    
    def exists(self, code: str, company_nit: str) -> bool:
        """
        Check if product exists for a company.
        
        Args:
            code: Product code
            company_nit: Company NIT
            
        Returns:
            True if product exists for the company, False otherwise
        """
        return DjangoProduct.objects.filter(
            code=code,
            company__nit=company_nit
        ).exists()
