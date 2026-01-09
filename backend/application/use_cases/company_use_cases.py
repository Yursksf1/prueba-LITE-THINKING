"""
Application use cases for company management.

Use cases orchestrate domain services and coordinate between layers.
"""
from infrastructure.domain_loader import ensure_domain_in_path
ensure_domain_in_path()

from domain.entities.company import Company as DomainCompany
from domain.exceptions.errors import InvalidCompanyError

from infrastructure.models import Company as DjangoCompany


class RegisterCompanyUseCase:
    """
    Use case for registering a new company.
    
    Orchestrates:
    - Domain validation via Company entity
    - Persistence via Django ORM
    """
    
    def execute(
        self,
        nit: str,
        name: str,
        address: str,
        phone: str
    ) -> DjangoCompany:
        """
        Register a new company with domain validation.
        
        Args:
            nit: Company NIT
            name: Company name
            address: Company address
            phone: Company phone
            
        Returns:
            Django Company model instance
            
        Raises:
            InvalidCompanyError: If company data is invalid
        """
        # Use domain entity for validation
        domain_company = DomainCompany(
            nit=nit,
            name=name,
            address=address,
            phone=phone
        )
        
        # Create Django model from validated domain entity
        django_company = DjangoCompany.objects.create(
            nit=domain_company.nit,
            name=domain_company.name,
            address=domain_company.address,
            phone=domain_company.phone
        )
        
        return django_company


class UpdateCompanyUseCase:
    """
    Use case for updating company information.
    
    Orchestrates:
    - Domain validation via Company entity
    - Persistence via Django ORM
    """
    
    def execute(
        self,
        nit: str,
        name: str = None,
        address: str = None,
        phone: str = None
    ) -> DjangoCompany:
        """
        Update company with domain validation.
        
        Args:
            nit: Company NIT
            name: New company name (optional)
            address: New company address (optional)
            phone: New company phone (optional)
            
        Returns:
            Django Company model instance
            
        Raises:
            InvalidCompanyError: If company data is invalid
            DjangoCompany.DoesNotExist: If company doesn't exist
        """
        # Get existing company
        django_company = DjangoCompany.objects.get(nit=nit)
        
        # Prepare data for validation
        updated_name = name if name is not None else django_company.name
        updated_address = address if address is not None else django_company.address
        updated_phone = phone if phone is not None else django_company.phone
        
        # Validate with domain entity
        domain_company = DomainCompany(
            nit=nit,
            name=updated_name,
            address=updated_address,
            phone=updated_phone
        )
        
        # Update Django model
        django_company.name = domain_company.name
        django_company.address = domain_company.address
        django_company.phone = domain_company.phone
        django_company.save()
        
        return django_company
