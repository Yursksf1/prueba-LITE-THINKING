"""
Domain Service for company registration.

Orchestrates creation and validation of companies.
Encapsulates business rules that span company creation workflows.
"""
from ..entities.company import Company
from ..exceptions.errors import InvalidCompanyError


class CompanyRegistrationService:
    """
    Orchestrates company creation.
    
    Responsibilities:
    - Validate company data before construction
    - Apply company-level registration policies
    - Serve as single entry point for company creation
    
    Note: Future policies (e.g., NIT verification with external service)
    would live here, not in the Company entity.
    """
    
    def register(
        self,
        nit: str,
        name: str,
        address: str,
        phone: str,
    ) -> Company:
        """
        Register a new company.
        
        Args:
            nit: National identification tax number
            name: Company legal name
            address: Physical address
            phone: Contact phone number
        
        Returns:
            Valid Company instance
            
        Raises:
            InvalidCompanyError: If company data violates business rules
        """
        # Company.__post_init__ performs intrinsic validations
        try:
            company = Company(
                nit=nit,
                name=name,
                address=address,
                phone=phone,
            )
        except InvalidCompanyError as exc:
            raise InvalidCompanyError(f"Failed to register company: {exc}") from exc
        
        return company
