"""
Tests for Company Inventory API endpoints.

Tests inventory listing, PDF generation, and email sending for company-specific inventory.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from infrastructure.models import Company, Product, InventoryItem
from unittest.mock import patch, MagicMock
from io import BytesIO

User = get_user_model()


class CompanyInventoryListTestCase(TestCase):
    """Test cases for GET /api/v1/companies/{nit}/inventory/"""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMINISTRATOR'
        )
        
        self.external_user = User.objects.create_user(
            email='external@test.com',
            password='external123',
            first_name='External',
            last_name='User',
            role='EXTERNAL'
        )
        
        # Create companies
        self.company1 = Company.objects.create(
            nit='123456789',
            name='Test Company 1',
            address='Test Address 1',
            phone='+57 300 1111111'
        )
        
        self.company2 = Company.objects.create(
            nit='987654321',
            name='Test Company 2',
            address='Test Address 2',
            phone='+57 300 2222222'
        )
        
        # Create products
        self.product1 = Product.objects.create(
            code='PROD001',
            name='Laptop HP',
            features=['16GB RAM', '512GB SSD'],
            prices={'USD': 1000.00, 'COP': 4000000.00},
            company=self.company1
        )
        
        self.product2 = Product.objects.create(
            code='PROD002',
            name='Mouse Logitech',
            features=['Wireless', 'Ergonomic'],
            prices={'USD': 50.00, 'COP': 200000.00},
            company=self.company1
        )
        
        self.product3 = Product.objects.create(
            code='PROD003',
            name='Monitor Dell',
            features=['27 inch', '4K'],
            prices={'USD': 400.00, 'COP': 1600000.00},
            company=self.company2
        )
        
        # Create inventory items
        self.inv1 = InventoryItem.objects.create(
            company=self.company1,
            product=self.product1,
            quantity=50
        )
        
        self.inv2 = InventoryItem.objects.create(
            company=self.company1,
            product=self.product2,
            quantity=100
        )
        
        self.inv3 = InventoryItem.objects.create(
            company=self.company2,
            product=self.product3,
            quantity=25
        )
    
    def test_list_company_inventory_as_admin(self):
        """Test listing inventory for a company as administrator."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/v1/companies/{self.company1.nit}/inventory/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check product codes in response
        product_codes = [item['product_code'] for item in response.data]
        self.assertIn('PROD001', product_codes)
        self.assertIn('PROD002', product_codes)
        self.assertNotIn('PROD003', product_codes)
    
    def test_list_company_inventory_as_external(self):
        """Test listing inventory for a company as external user."""
        self.client.force_authenticate(user=self.external_user)
        
        response = self.client.get(f'/api/v1/companies/{self.company1.nit}/inventory/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_company_inventory_unauthenticated(self):
        """Test listing inventory without authentication fails."""
        response = self.client.get(f'/api/v1/companies/{self.company1.nit}/inventory/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_company_inventory_company_not_found(self):
        """Test listing inventory for non-existent company."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/v1/companies/INVALID_NIT/inventory/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
    
    def test_list_company_inventory_empty(self):
        """Test listing inventory for company with no inventory."""
        # Create company without inventory
        company_empty = Company.objects.create(
            nit='111111111',
            name='Empty Company',
            address='Test Address',
            phone='+57 300 3333333'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/v1/companies/{company_empty.nit}/inventory/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_inventory_data_structure(self):
        """Test that inventory data has correct structure."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/v1/companies/{self.company1.nit}/inventory/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check first item structure
        item = response.data[0]
        self.assertIn('product_code', item)
        self.assertIn('product_name', item)
        self.assertIn('quantity', item)
        self.assertIn('prices', item)
        self.assertIn('updated_at', item)


class CompanyInventoryPDFTestCase(TestCase):
    """Test cases for GET /api/v1/companies/{nit}/inventory/pdf/"""
    
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
        
        # Create company and product
        self.company = Company.objects.create(
            nit='123456789',
            name='Test Company',
            address='Test Address',
            phone='+57 300 1234567'
        )
        
        self.product = Product.objects.create(
            code='PROD001',
            name='Test Product',
            features=['Feature 1'],
            prices={'USD': 100.00},
            company=self.company
        )
        
        self.inventory = InventoryItem.objects.create(
            company=self.company,
            product=self.product,
            quantity=50
        )
    
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_download_inventory_pdf_success(self, mock_pdf_service):
        """Test downloading inventory PDF successfully."""
        # Mock PDF generation
        mock_buffer = BytesIO(b'PDF content')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/v1/companies/{self.company.nit}/inventory/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn(self.company.nit, response['Content-Disposition'])
    
    def test_download_inventory_pdf_company_not_found(self):
        """Test downloading PDF for non-existent company."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/v1/companies/INVALID_NIT/inventory/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_download_inventory_pdf_unauthenticated(self):
        """Test downloading PDF without authentication fails."""
        response = self.client.get(f'/api/v1/companies/{self.company.nit}/inventory/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_download_inventory_pdf_generation_error(self, mock_pdf_service):
        """Test handling PDF generation errors."""
        # Mock PDF service to raise exception
        mock_pdf_service.return_value.generate_inventory_pdf.side_effect = Exception('PDF error')
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/v1/companies/{self.company.nit}/inventory/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('detail', response.data)
    
    @patch('api.views.company_inventory.AIRecommendationsService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_download_inventory_pdf_with_ai_recommendations(self, mock_pdf_service, mock_ai_service):
        """Test downloading PDF with AI recommendations enabled."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content with AI')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        mock_ai_service.return_value.generate_recommendations.return_value = 'AI generated recommendations'
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(
            f'/api/v1/companies/{self.company.nit}/inventory/pdf/?include_ai_recommendations=true'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Verify AI service was called
        mock_ai_service.return_value.generate_recommendations.assert_called_once()
        
        # Verify PDF service was called with AI recommendations
        call_args = mock_pdf_service.return_value.generate_inventory_pdf.call_args
        self.assertIsNotNone(call_args[1]['ai_recommendations'])
        self.assertEqual(call_args[1]['ai_recommendations'], 'AI generated recommendations')
    
    @patch('api.views.company_inventory.AIRecommendationsService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_download_inventory_pdf_without_ai_recommendations(self, mock_pdf_service, mock_ai_service):
        """Test that AI is NOT invoked when flag is false."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content without AI')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(
            f'/api/v1/companies/{self.company.nit}/inventory/pdf/?include_ai_recommendations=false'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify AI service was NOT called
        mock_ai_service.return_value.generate_recommendations.assert_not_called()
        
        # Verify PDF service was called with None for AI recommendations
        call_args = mock_pdf_service.return_value.generate_inventory_pdf.call_args
        self.assertIsNone(call_args[1]['ai_recommendations'])
    
    @patch('api.views.company_inventory.AIRecommendationsService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_download_inventory_pdf_default_no_ai(self, mock_pdf_service, mock_ai_service):
        """Test that AI is NOT invoked by default (when no query param)."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/v1/companies/{self.company.nit}/inventory/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify AI service was NOT called
        mock_ai_service.return_value.generate_recommendations.assert_not_called()
    
    @patch('api.views.company_inventory.AIRecommendationsService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_download_inventory_pdf_ai_error_does_not_break_pdf(self, mock_pdf_service, mock_ai_service):
        """Test that AI errors don't prevent PDF generation."""
        # Mock AI service to return error message
        mock_ai_service.return_value.generate_recommendations.return_value = 'No fue posible generar recomendaciones automáticas en este momento.'
        
        # Mock PDF generation to succeed
        mock_buffer = BytesIO(b'PDF content with error message')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(
            f'/api/v1/companies/{self.company.nit}/inventory/pdf/?include_ai_recommendations=true'
        )
        
        # PDF should still be generated successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # PDF service should have been called with the error message
        call_args = mock_pdf_service.return_value.generate_inventory_pdf.call_args
        self.assertIn('No fue posible', call_args[1]['ai_recommendations'])



class CompanyInventorySendEmailTestCase(TestCase):
    """Test cases for POST /api/v1/companies/{nit}/inventory/send-email/"""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMINISTRATOR'
        )
        
        self.external_user = User.objects.create_user(
            email='external@test.com',
            password='external123',
            first_name='External',
            last_name='User',
            role='EXTERNAL'
        )
        
        # Create company and product
        self.company = Company.objects.create(
            nit='123456789',
            name='Test Company',
            address='Test Address',
            phone='+57 300 1234567'
        )
        
        self.product = Product.objects.create(
            code='PROD001',
            name='Test Product',
            features=['Feature 1'],
            prices={'USD': 100.00},
            company=self.company
        )
        
        self.inventory = InventoryItem.objects.create(
            company=self.company,
            product=self.product,
            quantity=50
        )
    
    @patch('api.views.company_inventory.EmailService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_send_inventory_email_success(self, mock_pdf_service, mock_email_service):
        """Test sending inventory email successfully."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        mock_email_service.return_value.validate_email_configuration.return_value = True
        mock_email_service.return_value.send_inventory_report.return_value = True
        
        self.client.force_authenticate(user=self.admin_user)
        
        data = {'email': 'recipient@example.com'}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('recipient@example.com', response.data['message'])
    
    def test_send_inventory_email_invalid_email(self):
        """Test sending email with invalid email address."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {'email': 'invalid-email'}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_send_inventory_email_missing_email(self):
        """Test sending email without email field."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_send_inventory_email_company_not_found(self):
        """Test sending email for non-existent company."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {'email': 'recipient@example.com'}
        response = self.client.post(
            '/api/v1/companies/INVALID_NIT/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_send_inventory_email_unauthenticated(self):
        """Test sending email without authentication fails."""
        data = {'email': 'recipient@example.com'}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.company_inventory.EmailService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_send_inventory_email_as_external_user(self, mock_pdf_service, mock_email_service):
        """Test that external users can send inventory emails."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        mock_email_service.return_value.validate_email_configuration.return_value = True
        mock_email_service.return_value.send_inventory_report.return_value = True
        
        self.client.force_authenticate(user=self.external_user)
        
        data = {'email': 'recipient@example.com'}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('api.views.company_inventory.EmailService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_send_inventory_email_not_configured(self, mock_pdf_service, mock_email_service):
        """Test sending email when email is not configured."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        mock_email_service.return_value.validate_email_configuration.return_value = False
        
        self.client.force_authenticate(user=self.admin_user)
        
        data = {'email': 'recipient@example.com'}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('not configured', response.data['message'])
    
    @patch('api.views.company_inventory.AIRecommendationsService')
    @patch('api.views.company_inventory.EmailService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_send_inventory_email_with_ai_recommendations(self, mock_pdf_service, mock_email_service, mock_ai_service):
        """Test sending email with AI recommendations enabled."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content with AI')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        mock_email_service.return_value.validate_email_configuration.return_value = True
        mock_email_service.return_value.send_inventory_report.return_value = True
        mock_ai_service.return_value.generate_recommendations.return_value = 'AI recommendations for email'
        
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'email': 'recipient@example.com',
            'include_ai_recommendations': True
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify AI service was called
        mock_ai_service.return_value.generate_recommendations.assert_called_once()
        
        # Verify PDF service was called with AI recommendations
        call_args = mock_pdf_service.return_value.generate_inventory_pdf.call_args
        self.assertIsNotNone(call_args[1]['ai_recommendations'])
        self.assertEqual(call_args[1]['ai_recommendations'], 'AI recommendations for email')
    
    @patch('api.views.company_inventory.AIRecommendationsService')
    @patch('api.views.company_inventory.EmailService')
    @patch('api.views.company_inventory.PDFGeneratorService')
    def test_send_inventory_email_without_ai_recommendations(self, mock_pdf_service, mock_email_service, mock_ai_service):
        """Test that AI is NOT invoked when sending email without flag."""
        # Mock services
        mock_buffer = BytesIO(b'PDF content')
        mock_pdf_service.return_value.generate_inventory_pdf.return_value = mock_buffer
        mock_email_service.return_value.validate_email_configuration.return_value = True
        mock_email_service.return_value.send_inventory_report.return_value = True
        
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'email': 'recipient@example.com',
            'include_ai_recommendations': False
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/send-email/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify AI service was NOT called
        mock_ai_service.return_value.generate_recommendations.assert_not_called()
        
        # Verify PDF service was called with None for AI recommendations
        call_args = mock_pdf_service.return_value.generate_inventory_pdf.call_args
        self.assertIsNone(call_args[1]['ai_recommendations'])



class CompanyInventoryCreateTestCase(TestCase):
    """Test cases for POST /api/v1/companies/{nit}/inventory/"""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMINISTRATOR'
        )
        
        self.external_user = User.objects.create_user(
            email='external@test.com',
            password='external123',
            first_name='External',
            last_name='User',
            role='EXTERNAL'
        )
        
        # Create company
        self.company = Company.objects.create(
            nit='123456789',
            name='Test Company',
            address='Test Address',
            phone='+57 300 1234567'
        )
        
        # Create products
        self.product1 = Product.objects.create(
            code='PROD001',
            name='Laptop HP',
            features=['16GB RAM', '512GB SSD'],
            prices={'USD': 1000.00, 'COP': 4000000.00},
            company=self.company
        )
        
        self.product2 = Product.objects.create(
            code='PROD002',
            name='Mouse Logitech',
            features=['Wireless', 'Ergonomic'],
            prices={'USD': 50.00, 'COP': 200000.00},
            company=self.company
        )
        
        # Create another company for validation tests
        self.company2 = Company.objects.create(
            nit='987654321',
            name='Another Company',
            address='Another Address',
            phone='+57 300 9876543'
        )
        
        self.product3 = Product.objects.create(
            code='PROD003',
            name='Monitor Dell',
            features=['27 inch', '4K'],
            prices={'USD': 400.00, 'COP': 1600000.00},
            company=self.company2
        )
    
    def test_create_inventory_success(self):
        """Test creating inventory item successfully as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'product_code': 'PROD001',
            'quantity': 50
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['product_code'], 'PROD001')
        self.assertEqual(response.data['product_name'], 'Laptop HP')
        self.assertEqual(response.data['quantity'], 50)
        self.assertIn('prices', response.data)
        self.assertIn('updated_at', response.data)
        
        # Verify it was created in DB
        self.assertTrue(
            InventoryItem.objects.filter(
                company=self.company,
                product=self.product1
            ).exists()
        )
    
    def test_create_inventory_unauthenticated(self):
        """Test creating inventory without authentication fails."""
        data = {
            'product_code': 'PROD001',
            'quantity': 50
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_inventory_as_external_user(self):
        """Test creating inventory as external user fails."""
        self.client.force_authenticate(user=self.external_user)
        
        data = {
            'product_code': 'PROD001',
            'quantity': 50
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_inventory_company_not_found(self):
        """Test creating inventory for non-existent company."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'product_code': 'PROD001',
            'quantity': 50
        }
        response = self.client.post(
            '/api/v1/companies/INVALID_NIT/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
    
    def test_create_inventory_product_not_found(self):
        """Test creating inventory for non-existent product."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'product_code': 'INVALID_CODE',
            'quantity': 50
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
    
    def test_create_inventory_product_not_belong_to_company(self):
        """Test creating inventory for product that doesn't belong to company."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Try to add product from company2 to company1's inventory
        data = {
            'product_code': 'PROD003',
            'quantity': 50
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertIn('does not belong', response.data['detail'])
    
    def test_create_inventory_duplicate(self):
        """Test creating duplicate inventory item fails."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create first inventory item
        InventoryItem.objects.create(
            company=self.company,
            product=self.product1,
            quantity=30
        )
        
        # Try to create duplicate
        data = {
            'product_code': 'PROD001',
            'quantity': 50
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertIn('already exists', response.data['detail'])
    
    def test_create_inventory_invalid_quantity(self):
        """Test creating inventory with invalid quantity."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test negative quantity
        data = {
            'product_code': 'PROD001',
            'quantity': -10
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
    
    def test_create_inventory_missing_fields(self):
        """Test creating inventory with missing required fields."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Missing product_code
        data = {'quantity': 50}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_code', response.data)
        
        # Missing quantity
        data = {'product_code': 'PROD001'}
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
    
    def test_create_inventory_zero_quantity(self):
        """Test creating inventory with zero quantity is allowed."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'product_code': 'PROD001',
            'quantity': 0
        }
        response = self.client.post(
            f'/api/v1/companies/{self.company.nit}/inventory/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 0)
