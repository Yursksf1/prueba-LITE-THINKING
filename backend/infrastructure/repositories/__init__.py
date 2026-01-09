"""
Repository implementations for domain protocols.

These adapters connect the domain layer (business logic) with the infrastructure layer (Django ORM).
They implement the repository protocols defined in domain services.
"""
from .company_repository import DjangoCompanyRepository
from .product_repository import DjangoProductRepository
from .inventory_repository import DjangoInventoryRepository

__all__ = [
    'DjangoCompanyRepository',
    'DjangoProductRepository',
    'DjangoInventoryRepository',
]
