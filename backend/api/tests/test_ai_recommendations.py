"""
Tests for AI Recommendations Service.

Tests the AI service with mocked Hugging Face API calls.
"""
from django.test import TestCase
from unittest.mock import patch, MagicMock
from application.services import AIRecommendationsService
import requests


class AIRecommendationsServiceTestCase(TestCase):
    """Test cases for AIRecommendationsService"""
    
    def setUp(self):
        """Set up test data."""
        self.inventory_items = [
            {
                'product_code': 'PROD001',
                'product_name': 'Laptop HP',
                'quantity': 5
            },
            {
                'product_code': 'PROD002',
                'product_name': 'Mouse Logitech',
                'quantity': 150
            },
            {
                'product_code': 'PROD003',
                'product_name': 'Monitor Dell',
                'quantity': 25
            }
        ]
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    def test_is_configured_with_api_key(self):
        """Test that service is configured when API key is present."""
        service = AIRecommendationsService()
        self.assertTrue(service.is_configured())
    
    @patch.dict('os.environ', {'LLM_API_KEY': ''})
    def test_is_configured_without_api_key(self):
        """Test that service is not configured when API key is missing."""
        service = AIRecommendationsService()
        self.assertFalse(service.is_configured())
    
    @patch.dict('os.environ', {'LLM_API_KEY': ''})
    def test_generate_recommendations_not_configured(self):
        """Test that service returns error message when not configured."""
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('no configurado', result.lower())
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_success(self, mock_post):
        """Test successful AI recommendation generation."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'generated_text': 'Recomendación: Considere reabastecer el Laptop HP.'}
        ]
        mock_post.return_value = mock_response
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(
            self.inventory_items,
            company_name='Test Company'
        )
        
        self.assertIn('Recomendación', result)
        self.assertIn('Laptop HP', result)
        
        # Verify API was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('Authorization', call_args[1]['headers'])
        self.assertIn('test-api-key', call_args[1]['headers']['Authorization'])
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_with_summary_text(self, mock_post):
        """Test AI response with summary_text format."""
        # Mock API response with summary_text format
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'summary_text': 'Resumen: Stock bajo en varios productos.'}
        ]
        mock_post.return_value = mock_response
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('Resumen', result)
        self.assertIn('Stock bajo', result)
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_timeout(self, mock_post):
        """Test handling of timeout errors."""
        # Mock timeout exception
        mock_post.side_effect = requests.exceptions.Timeout()
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('No fue posible', result)
        self.assertIn('tardó demasiado', result.lower())
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_connection_error(self, mock_post):
        """Test handling of connection errors."""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('No fue posible', result)
        self.assertIn('conexión', result.lower())
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'invalid-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_invalid_api_key(self, mock_post):
        """Test handling of invalid API key (401 error)."""
        # Mock 401 response
        mock_response = MagicMock()
        mock_response.status_code = 401
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_post.side_effect = http_error
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('No fue posible', result)
        self.assertIn('API Key inválida', result)
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_http_error(self, mock_post):
        """Test handling of other HTTP errors."""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 500
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_post.side_effect = http_error
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('No fue posible', result)
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_empty_response(self, mock_post):
        """Test handling of empty responses."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{}]
        mock_post.return_value = mock_response
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('No fue posible', result)
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_generate_recommendations_unexpected_error(self, mock_post):
        """Test handling of unexpected errors."""
        # Mock unexpected exception
        mock_post.side_effect = Exception('Unexpected error')
        
        service = AIRecommendationsService()
        result = service.generate_recommendations(self.inventory_items)
        
        self.assertIn('No fue posible', result)
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    def test_build_prompt(self):
        """Test prompt building from inventory data."""
        service = AIRecommendationsService()
        prompt = service._build_prompt(self.inventory_items, 'Test Company')
        
        # Check prompt contains key elements
        self.assertIn('Test Company', prompt)
        self.assertIn('Laptop HP', prompt)
        self.assertIn('PROD001', prompt)
        self.assertIn('5 unidades', prompt)
        self.assertIn('Mouse Logitech', prompt)
        self.assertIn('150 unidades', prompt)
        self.assertIn('Recomendaciones', prompt)
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    def test_build_prompt_limits_items(self):
        """Test that prompt building limits items to avoid token limits."""
        # Create a large inventory
        large_inventory = [
            {
                'product_code': f'PROD{i:03d}',
                'product_name': f'Product {i}',
                'quantity': i
            }
            for i in range(50)
        ]
        
        service = AIRecommendationsService()
        prompt = service._build_prompt(large_inventory)
        
        # Should indicate there are more items
        self.assertIn('más', prompt.lower())
    
    @patch.dict('os.environ', {'LLM_API_KEY': 'test-api-key', 'LLM_MODEL': 'test-model'})
    @patch('application.services.ai_recommendations_service.requests.post')
    def test_api_call_parameters(self, mock_post):
        """Test that API is called with correct parameters."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'generated_text': 'Test recommendation'}
        ]
        mock_post.return_value = mock_response
        
        service = AIRecommendationsService()
        service.generate_recommendations(self.inventory_items)
        
        # Verify API call parameters
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['timeout'], 30)
        self.assertIn('Authorization', call_args[1]['headers'])
        self.assertIn('Content-Type', call_args[1]['headers'])
        self.assertIn('inputs', call_args[1]['json'])
        self.assertIn('parameters', call_args[1]['json'])
