"""
Django ORM adapter for Inventory repository.

Implements the InventoryRepository protocol from domain layer.
"""
from infrastructure.domain_loader import ensure_domain_in_path
ensure_domain_in_path()

from domain.entities.inventory_item import InventoryItem as DomainInventoryItem
from domain.exceptions.errors import InvalidCompanyError, InvalidProductError
from infrastructure.models import InventoryItem as DjangoInventoryItem, Company, Product


class DjangoInventoryRepository:
    """
    Adapter that implements domain's InventoryRepository protocol.
    
    Translates between domain entities and Django ORM models.
    Handles conversion between domain InventoryItem and Django InventoryItem.
    """
    
    def find(self, company_nit: str, product_code: str) -> DomainInventoryItem | None:
        """
        Find inventory item by company and product.
        
        Args:
            company_nit: Company NIT
            product_code: Product code
            
        Returns:
            Domain InventoryItem if found, None otherwise
        """
        try:
            django_item = DjangoInventoryItem.objects.get(
                company__nit=company_nit,
                product__code=product_code
            )
            # Convert Django model to domain entity
            return DomainInventoryItem(
                company_nit=company_nit,
                product_code=product_code,
                quantity=django_item.quantity
            )
        except DjangoInventoryItem.DoesNotExist:
            return None
    
    def save(self, item: DomainInventoryItem) -> None:
        """
        Save or update inventory item.
        
        Args:
            item: Domain InventoryItem to persist
            
        Raises:
            InvalidCompanyError: If company doesn't exist
            InvalidProductError: If product doesn't exist
        """
        # Get company and product instances with proper error handling
        try:
            company = Company.objects.get(nit=item.company_nit)
        except Company.DoesNotExist:
            raise InvalidCompanyError(
                f"Cannot save inventory: Company with NIT '{item.company_nit}' does not exist"
            )
        
        try:
            product = Product.objects.get(code=item.product_code)
        except Product.DoesNotExist:
            raise InvalidProductError(
                f"Cannot save inventory: Product '{item.product_code}' does not exist"
            )
        
        # Update or create Django model
        DjangoInventoryItem.objects.update_or_create(
            company=company,
            product=product,
            defaults={'quantity': item.quantity}
        )
