"""
Django ORM adapter for Inventory repository.

Implements the InventoryRepository protocol from domain layer.
"""
import sys
import os

# Add domain package to Python path
domain_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'domain', 'src')
if domain_path not in sys.path:
    sys.path.insert(0, domain_path)

from domain.entities.inventory_item import InventoryItem as DomainInventoryItem
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
        """
        # Get company and product instances
        company = Company.objects.get(nit=item.company_nit)
        product = Product.objects.get(code=item.product_code)
        
        # Update or create Django model
        DjangoInventoryItem.objects.update_or_create(
            company=company,
            product=product,
            defaults={'quantity': item.quantity}
        )
