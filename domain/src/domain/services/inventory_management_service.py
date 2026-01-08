"""
Domain Service for inventory management.

Orchestrates inventory operations with product and company validation.
Encapsulates multi-entity coordination rules.
"""
from typing import Protocol

from ..entities.inventory_item import InventoryItem
from ..exceptions.errors import InvalidInventoryError, InvalidCompanyError, InvalidProductError


class CompanyRepository(Protocol):
    """Port: Check if company exists."""
    
    def exists(self, nit: str) -> bool:
        """Check if company with given NIT exists."""
        ...


class ProductRepository(Protocol):
    """Port: Check if product exists."""
    
    def exists(self, code: str, company_nit: str) -> bool:
        """Check if product with given code exists for the company."""
        ...


class InventoryRepository(Protocol):
    """Port: Retrieve or store inventory items."""
    
    def find(self, company_nit: str, product_code: str) -> InventoryItem | None:
        """Find existing inventory item or None if not found."""
        ...
    
    def save(self, item: InventoryItem) -> None:
        """Persist or update inventory item."""
        ...


class InventoryManagementService:
    """
    Orchestrates inventory operations across multiple entities.
    
    Responsibilities:
    - Validate company exists
    - Validate product exists
    - Create or update inventory association
    - Coordinate stock adjustments
    
    This is a domain service because it enforces policies that span:
    - Company existence
    - Product existence
    - Inventory state management
    """
    
    def __init__(
        self,
        company_repository: CompanyRepository,
        product_repository: ProductRepository,
        inventory_repository: InventoryRepository,
    ):
        """
        Initialize with dependencies.
        
        Args:
            company_repository: Port for company lookup
            product_repository: Port for product lookup
            inventory_repository: Port for inventory persistence
        """
        self.company_repository = company_repository
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
    
    def add_to_inventory(
        self,
        company_nit: str,
        product_code: str,
        quantity: int,
    ) -> InventoryItem:
        """
        Add product to company inventory or increase existing quantity.
        
        Args:
            company_nit: Company NIT
            product_code: Product code
            quantity: Quantity to add
        
        Returns:
            Updated InventoryItem
            
        Raises:
            InvalidCompanyError: If company does not exist
            InvalidProductError: If product does not exist
            InvalidInventoryError: If quantity is invalid
        """
        # Policy: Company must exist
        if not self.company_repository.exists(company_nit):
            raise InvalidCompanyError(
                f"Cannot manage inventory: Company with NIT '{company_nit}' does not exist"
            )
        
        # Policy: Product must exist for this company
        if not self.product_repository.exists(product_code, company_nit):
            raise InvalidProductError(
                f"Cannot manage inventory: Product '{product_code}' does not exist for company '{company_nit}'"
            )
        
        # Find existing inventory or create new
        existing = self.inventory_repository.find(company_nit, product_code)
        
        if existing:
            updated_item = existing.increase(quantity)
        else:
            updated_item = InventoryItem(
                company_nit=company_nit,
                product_code=product_code,
                quantity=quantity,
            )
        
        self.inventory_repository.save(updated_item)
        return updated_item
    
    def remove_from_inventory(
        self,
        company_nit: str,
        product_code: str,
        quantity: int,
    ) -> InventoryItem:
        """
        Remove product quantity from inventory.
        
        Args:
            company_nit: Company NIT
            product_code: Product code
            quantity: Quantity to remove
        
        Returns:
            Updated InventoryItem
            
        Raises:
            InvalidCompanyError: If company does not exist
            InvalidProductError: If product does not exist or not in inventory
            InvalidInventoryError: If insufficient stock
        """
        # Policy: Company must exist
        if not self.company_repository.exists(company_nit):
            raise InvalidCompanyError(
                f"Cannot manage inventory: Company with NIT '{company_nit}' does not exist"
            )
        
        # Find inventory item
        existing = self.inventory_repository.find(company_nit, product_code)
        
        if not existing:
            raise InvalidProductError(
                f"Product '{product_code}' is not in inventory for company '{company_nit}'"
            )
        
        # Decrease quantity (InventoryItem validates insufficient stock)
        updated_item = existing.decrease(quantity)
        
        self.inventory_repository.save(updated_item)
        return updated_item
    
    def check_inventory(
        self,
        company_nit: str,
        product_code: str,
    ) -> int | None:
        """
        Get current stock for a product in a company.
        
        Args:
            company_nit: Company NIT
            product_code: Product code
        
        Returns:
            Current quantity or None if not in inventory
        """
        item = self.inventory_repository.find(company_nit, product_code)
        return item.quantity if item else None
