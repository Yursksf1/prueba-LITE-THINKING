"""
Tests for Product API endpoints.

Tests product creation with multiple currency prices.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from infrastructure.models import Company, Product

User = get_user_model()


class ProductCreationTestCase(TestCase):
    """Test cases for POST /api/v1/companies/{nit}/products/"""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMINISTRATOR'
        )
        
        # Create external user
        self.external_user = User.objects.create_user(
            email='external@test.com',
            password='external123',
            first_name='External',
            last_name='User',
            role='EXTERNAL'
        )
        
        # Create test company
        self.company = Company.objects.create(
            nit='123456789',
            name='Test Company',
            address='Test Address',
            phone='+57 300 1234567'
        )
    
    def test_create_product_success_with_multiple_currencies(self):
        """Test successful product creation with multiple currency prices."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD001',
            'name': 'Test Product',
            'features': ['Feature 1', 'Feature 2'],
            'prices': {
                'USD': 100.00,
                'COP': 400000.00,
                'EUR': 90.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'PROD001')
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['company_nit'], self.company.nit)
        self.assertIn('USD', response.data['prices'])
        self.assertIn('COP', response.data['prices'])
        self.assertIn('EUR', response.data['prices'])
        
        # Verify product was created in database
        product = Product.objects.get(code='PROD001')
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.company, self.company)
    
    def test_create_product_with_single_currency(self):
        """Test creating product with only one currency price."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD002',
            'name': 'Single Currency Product',
            'features': [],
            'prices': {
                'COP': 50000.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('COP', response.data['prices'])
    
    def test_create_product_without_prices_fails(self):
        """Test that creating product without prices fails."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD003',
            'name': 'No Price Product',
            'features': [],
            'prices': {}
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prices', response.data)
    
    def test_create_product_with_invalid_currency_fails(self):
        """Test that invalid currency codes are rejected."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD004',
            'name': 'Invalid Currency Product',
            'features': [],
            'prices': {
                'XXX': 100.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prices', response.data)
    
    def test_create_product_with_negative_amount_fails(self):
        """Test that negative amounts are rejected."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD005',
            'name': 'Negative Price Product',
            'features': [],
            'prices': {
                'USD': -10.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prices', response.data)
    
    def test_create_product_with_zero_amount_fails(self):
        """Test that zero amounts are rejected."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD006',
            'name': 'Zero Price Product',
            'features': [],
            'prices': {
                'USD': 0
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prices', response.data)
    
    def test_create_product_without_authentication_fails(self):
        """Test that unauthenticated requests are rejected."""
        product_data = {
            'code': 'PROD007',
            'name': 'Unauthenticated Product',
            'features': [],
            'prices': {
                'USD': 100.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_product_as_external_user_fails(self):
        """Test that external users cannot create products (403 Forbidden)."""
        self.client.force_authenticate(user=self.external_user)
        
        product_data = {
            'code': 'PROD008',
            'name': 'External User Product',
            'features': [],
            'prices': {
                'USD': 100.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_product_for_nonexistent_company_fails(self):
        """Test that creating product for non-existent company returns 404."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD009',
            'name': 'Orphan Product',
            'features': [],
            'prices': {
                'USD': 100.00
            }
        }
        
        response = self.client.post(
            '/api/v1/companies/999999999/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_product_with_empty_code_fails(self):
        """Test that empty product code is rejected."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': '   ',
            'name': 'Empty Code Product',
            'features': [],
            'prices': {
                'USD': 100.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
    
    def test_create_product_with_empty_name_fails(self):
        """Test that empty product name is rejected."""
        self.client.force_authenticate(user=self.admin_user)
        
        product_data = {
            'code': 'PROD010',
            'name': '   ',
            'features': [],
            'prices': {
                'USD': 100.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_create_product_with_valid_single_currency(self):
        """Test that valid single currency product is accepted by domain validation."""
        self.client.force_authenticate(user=self.admin_user)
        
        # With domain-driven validation, {'USD': 100.00} is correctly accepted
        product_data = {
            'code': 'PROD011',
            'name': 'Valid Currency Product',
            'features': [],
            'prices': {
                'USD': 100.00
            }
        }
        
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/products/',
            product_data,
            format='json'
        )
        
        # With proper domain validation, this should succeed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'PROD011')
    
    def test_get_products_still_works(self):
        """Test that GET endpoint still works after creating products."""
        # Create a product first
        Product.objects.create(
            code='EXISTING001',
            name='Existing Product',
            features=['Feature A'],
            prices={'USD': 50.00 },
            company=self.company
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/v1/companies/{self.company.nit}/products/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'EXISTING001')


class ProductSerializerValidationTestCase(TestCase):
    """Test cases for product serializer validation logic."""
    
    def setUp(self):
        """Set up test data."""
        from api.serializers.product import ProductCreateSerializer
        self.serializer_class = ProductCreateSerializer
    
    def test_valid_prices_structure(self):
        """Test that valid prices structure is accepted."""
        data = {
            'code': 'TEST001',
            'name': 'Test Product',
            'features': [],
            'prices': {
                'USD': 100.00,
                'COP': 400000.00,
            }
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_invalid_prices_not_dict(self):
        """Test that prices must be a dictionary."""
        data = {
            'code': 'TEST002',
            'name': 'Test Product',
            'features': [],
            'prices': [{'currency': 'USD', 'amount': 100}]  # List instead of dict
        }
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('prices', serializer.errors)
    
    def test_features_can_be_empty_list(self):
        """Test that features can be an empty list."""
        data = {
            'code': 'TEST003',
            'name': 'Test Product',
            'features': [],
            'prices': {
                'USD':  100.00,
            }
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
