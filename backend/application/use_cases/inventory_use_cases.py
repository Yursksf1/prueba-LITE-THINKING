"""
Application use cases for inventory management.

Use cases orchestrate domain services and coordinate between layers.
"""
import sys
import os

# Add domain package to Python path
domain_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'domain', 'src')
if domain_path not in sys.path:
    sys.path.insert(0, domain_path)

from domain.services.inventory_management_service import InventoryManagementService
from domain.exceptions.errors import InvalidInventoryError, InvalidCompanyError, InvalidProductError

from infrastructure.repositories import (
    DjangoCompanyRepository,
    DjangoProductRepository,
    DjangoInventoryRepository
)
from infrastructure.models import InventoryItem as DjangoInventoryItem


class AddInventoryUseCase:
    """
    Use case for adding items to inventory.
    
    Orchestrates:
    - Domain validation via InventoryManagementService
    - Persistence via repository adapters
    """
    
    def __init__(self):
        self.company_repository = DjangoCompanyRepository()
        self.product_repository = DjangoProductRepository()
        self.inventory_repository = DjangoInventoryRepository()
        self.domain_service = InventoryManagementService(
            self.company_repository,
            self.product_repository,
            self.inventory_repository
        )
    
    def execute(
        self,
        company_nit: str,
        product_code: str,
        quantity: int
    ) -> DjangoInventoryItem:
        """
        Add product to company inventory with domain validation.
        
        Args:
            company_nit: Company NIT
            product_code: Product code
            quantity: Quantity to add
            
        Returns:
            Django InventoryItem model instance
            
        Raises:
            InvalidCompanyError: If company doesn't exist
            InvalidProductError: If product doesn't exist
            InvalidInventoryError: If quantity is invalid
        """
        # Use domain service for business logic validation
        domain_item = self.domain_service.add_to_inventory(
            company_nit=company_nit,
            product_code=product_code,
            quantity=quantity
        )
        
        # Retrieve the persisted Django model
        django_item = DjangoInventoryItem.objects.get(
            company__nit=domain_item.company_nit,
            product__code=domain_item.product_code
        )
        
        return django_item


class RemoveInventoryUseCase:
    """
    Use case for removing items from inventory.
    
    Orchestrates:
    - Domain validation via InventoryManagementService
    - Persistence via repository adapters
    """
    
    def __init__(self):
        self.company_repository = DjangoCompanyRepository()
        self.product_repository = DjangoProductRepository()
        self.inventory_repository = DjangoInventoryRepository()
        self.domain_service = InventoryManagementService(
            self.company_repository,
            self.product_repository,
            self.inventory_repository
        )
    
    def execute(
        self,
        company_nit: str,
        product_code: str,
        quantity: int
    ) -> DjangoInventoryItem:
        """
        Remove product quantity from inventory with domain validation.
        
        Args:
            company_nit: Company NIT
            product_code: Product code
            quantity: Quantity to remove
            
        Returns:
            Django InventoryItem model instance
            
        Raises:
            InvalidCompanyError: If company doesn't exist
            InvalidProductError: If product doesn't exist or not in inventory
            InvalidInventoryError: If insufficient stock
        """
        # Use domain service for business logic validation
        domain_item = self.domain_service.remove_from_inventory(
            company_nit=company_nit,
            product_code=product_code,
            quantity=quantity
        )
        
        # Retrieve the persisted Django model
        django_item = DjangoInventoryItem.objects.get(
            company__nit=domain_item.company_nit,
            product__code=domain_item.product_code
        )
        
        return django_item
