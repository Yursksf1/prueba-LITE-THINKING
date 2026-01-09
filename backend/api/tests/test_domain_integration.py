"""
Integration tests for domain layer architecture.

These tests demonstrate that the domain layer is properly integrated with Django,
validating business rules before persistence.
"""
from infrastructure.domain_loader import ensure_domain_in_path
ensure_domain_in_path()

from django.test import TestCase
from domain.exceptions.errors import (
    InvalidCompanyError,
    InvalidProductError,
    InvalidInventoryError,
    InvalidPriceError
)
from application.use_cases import (
    RegisterCompanyUseCase,
    UpdateCompanyUseCase,
    RegisterProductUseCase,
    AddInventoryUseCase
)
from infrastructure.models import Company, Product, InventoryItem


class DomainIntegrationTestCase(TestCase):
    """
    Test cases demonstrating domain layer integration.
    
    These tests show that:
    1. Business logic lives in the domain layer
    2. Domain entities validate business rules
    3. Use cases orchestrate domain services
    4. Infrastructure adapts to domain, not vice versa
    """
    
    def test_company_registration_with_domain_validation(self):
        """Test company registration validates through domain layer."""
        use_case = RegisterCompanyUseCase()
        
        # Valid company should succeed
        company = use_case.execute(
            nit='123456789',
            name='Test Company',
            address='Test Address',
            phone='+57 300 1234567'
        )
        
        self.assertIsNotNone(company)
        self.assertEqual(company.nit, '123456789')
        self.assertEqual(company.name, 'Test Company')
        
        # Domain validation: NIT too short should fail
        with self.assertRaises(InvalidCompanyError) as context:
            use_case.execute(
                nit='123',  # Too short
                name='Invalid Company',
                address='Address',
                phone='+57 300 1234567'
            )
        self.assertIn('at least 5 characters', str(context.exception))
        
        # Domain validation: Empty name should fail
        with self.assertRaises(InvalidCompanyError) as context:
            use_case.execute(
                nit='987654321',
                name='   ',  # Empty after strip
                address='Address',
                phone='+57 300 1234567'
            )
        self.assertIn('Name is required', str(context.exception))
        
        # Domain validation: Invalid phone should fail
        with self.assertRaises(InvalidCompanyError) as context:
            use_case.execute(
                nit='987654321',
                name='Test Company',
                address='Address',
                phone='invalid-phone'
            )
        self.assertIn('Phone must contain only digits', str(context.exception))
    
    def test_product_registration_with_domain_validation(self):
        """Test product registration validates through domain layer."""
        # Setup: Create company first
        company_use_case = RegisterCompanyUseCase()
        company_use_case.execute(
            nit='123456789',
            name='Test Company',
            address='Test Address',
            phone='+57 300 1234567'
        )
        
        product_use_case = RegisterProductUseCase()
        
        # Valid product should succeed
        product = product_use_case.execute(
            code='PROD001',
            name='Test Product',
            features=['Feature 1', 'Feature 2'],
            prices={'USD': 100.00, 'COP': 400000.00},
            company_nit='123456789'
        )
        
        self.assertIsNotNone(product)
        self.assertEqual(product.code, 'PROD001')
        self.assertEqual(product.name, 'Test Product')
        
        # Domain validation: Product for non-existent company should fail
        with self.assertRaises(InvalidCompanyError) as context:
            product_use_case.execute(
                code='PROD002',
                name='Orphan Product',
                features=[],
                prices={'USD': 100.00},
                company_nit='999999999'  # Doesn't exist
            )
        self.assertIn('does not exist', str(context.exception))
        
        # Domain validation: Empty product code should fail
        with self.assertRaises(InvalidProductError) as context:
            product_use_case.execute(
                code='   ',  # Empty
                name='Invalid Product',
                features=[],
                prices={'USD': 100.00},
                company_nit='123456789'
            )
        self.assertIn('Code is required', str(context.exception))
        
        # Domain validation: No prices should fail
        with self.assertRaises(InvalidPriceError) as context:
            product_use_case.execute(
                code='PROD003',
                name='No Price Product',
                features=[],
                prices={},  # Empty prices
                company_nit='123456789'
            )
        self.assertIn('At least one price is required', str(context.exception))
        
        # Domain validation: Invalid price amount should fail
        with self.assertRaises(InvalidPriceError) as context:
            product_use_case.execute(
                code='PROD004',
                name='Negative Price Product',
                features=[],
                prices={'USD': -10.00},  # Negative amount
                company_nit='123456789'
            )
        self.assertIn('must be greater than zero', str(context.exception))
    
    def test_inventory_management_with_domain_validation(self):
        """Test inventory management validates through domain layer."""
        # Setup: Create company and product
        company_use_case = RegisterCompanyUseCase()
        company_use_case.execute(
            nit='123456789',
            name='Test Company',
            address='Test Address',
            phone='+57 300 1234567'
        )
        
        product_use_case = RegisterProductUseCase()
        product_use_case.execute(
            code='PROD001',
            name='Test Product',
            features=[],
            prices={'USD': 100.00},
            company_nit='123456789'
        )
        
        inventory_use_case = AddInventoryUseCase()
        
        # Valid inventory should succeed
        inventory_item = inventory_use_case.execute(
            company_nit='123456789',
            product_code='PROD001',
            quantity=50
        )
        
        self.assertIsNotNone(inventory_item)
        self.assertEqual(inventory_item.quantity, 50)
        
        # Domain validation: Inventory for non-existent company should fail
        with self.assertRaises(InvalidCompanyError) as context:
            inventory_use_case.execute(
                company_nit='999999999',  # Doesn't exist
                product_code='PROD001',
                quantity=10
            )
        self.assertIn('does not exist', str(context.exception))
        
        # Domain validation: Inventory for non-existent product should fail
        with self.assertRaises(InvalidProductError) as context:
            inventory_use_case.execute(
                company_nit='123456789',
                product_code='PROD999',  # Doesn't exist
                quantity=10
            )
        self.assertIn('does not exist', str(context.exception))
        
        # Domain validation: Negative quantity should fail
        with self.assertRaises(InvalidInventoryError) as context:
            inventory_use_case.execute(
                company_nit='123456789',
                product_code='PROD001',
                quantity=-10  # Negative quantity
            )
        self.assertIn('must be positive', str(context.exception))
    
    def test_company_update_preserves_domain_validation(self):
        """Test company updates maintain domain validation."""
        # Setup: Create company
        register_use_case = RegisterCompanyUseCase()
        company = register_use_case.execute(
            nit='123456789',
            name='Original Name',
            address='Original Address',
            phone='+57 300 1234567'
        )
        
        update_use_case = UpdateCompanyUseCase()
        
        # Valid update should succeed
        updated = update_use_case.execute(
            nit='123456789',
            name='Updated Name',
            address='Updated Address',
            phone='+57 300 9876543'
        )
        
        self.assertEqual(updated.name, 'Updated Name')
        self.assertEqual(updated.address, 'Updated Address')
        self.assertEqual(updated.phone, '+57 300 9876543')
        
        # Domain validation: Invalid phone on update should fail
        with self.assertRaises(InvalidCompanyError) as context:
            update_use_case.execute(
                nit='123456789',
                phone='invalid-phone'
            )
        self.assertIn('Phone must contain only digits', str(context.exception))
        
        # Domain validation: Empty name on update should fail
        with self.assertRaises(InvalidCompanyError) as context:
            update_use_case.execute(
                nit='123456789',
                name='   '  # Empty
            )
        self.assertIn('Name is required', str(context.exception))
    
    def test_domain_entities_remain_independent_of_django(self):
        """Test that domain entities don't depend on Django."""
        # This test verifies the separation by checking that domain entities
        # can be instantiated without Django being involved
        
        from domain.entities.company import Company as DomainCompany
        from domain.entities.product import Product as DomainProduct
        from domain.entities.money import Money
        from domain.entities.currency import Currency
        
        # Domain entities should work without Django
        domain_company = DomainCompany(
            nit='123456789',
            name='Pure Domain Company',
            address='Domain Address',
            phone='+57 300 1234567'
        )
        
        self.assertEqual(domain_company.nit, '123456789')
        
        domain_product = DomainProduct(
            code='PROD001',
            name='Pure Domain Product',
            features=('Feature 1',),
            prices={
                'USD': Money(amount=100.00, currency=Currency.USD)
            },
            company_nit='123456789'
        )
        
        self.assertEqual(domain_product.code, 'PROD001')
        
        # Verify no Django imports in domain entities
        import inspect
        company_source = inspect.getsource(DomainCompany)
        product_source = inspect.getsource(DomainProduct)
        
        self.assertNotIn('django', company_source.lower())
        self.assertNotIn('django', product_source.lower())
