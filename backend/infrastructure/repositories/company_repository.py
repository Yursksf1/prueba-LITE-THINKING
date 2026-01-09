"""
Django ORM adapter for Company repository.

Implements the CompanyRepository protocol from domain layer.
"""
from infrastructure.models import Company as DjangoCompany


class DjangoCompanyRepository:
    """
    Adapter that implements domain's CompanyRepository protocol.
    
    Translates between domain needs and Django ORM operations.
    """
    
    def exists(self, nit: str) -> bool:
        """
        Check if company with given NIT exists in database.
        
        Args:
            nit: Company NIT identifier
            
        Returns:
            True if company exists, False otherwise
        """
        return DjangoCompany.objects.filter(nit=nit).exists()
