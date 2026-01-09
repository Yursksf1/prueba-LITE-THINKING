"""
AI Recommendations Service for generating inventory insights.

This service integrates with LLM providers (Hugging Face) to generate
automated recommendations and insights based on inventory data.
"""
import os
import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class AIRecommendationsService:
    """
    Service for generating AI-powered recommendations for inventory data.
    
    This service is designed to:
    - Be provider-agnostic (currently supports Hugging Face)
    - Handle errors gracefully without breaking the PDF generation
    - Not persist any data to the database
    - Be used exclusively within the PDF generation flow
    """
    
    def __init__(self):
        """Initialize the AI service with configuration from environment variables."""
        self.provider = os.getenv('LLM_PROVIDER', 'huggingface')
        self.api_key = os.getenv('LLM_API_KEY', '')
        self.model = os.getenv('LLM_MODEL', 'facebook/bart-large-cnn')
        self.timeout = 30  # seconds
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model}"
        
    def is_configured(self) -> bool:
        """
        Check if the AI service is properly configured.
        
        Returns:
            bool: True if API key is configured, False otherwise
        """
        return bool(self.api_key and self.api_key.strip())
    
    def generate_recommendations(
        self,
        inventory_items: List[Dict],
        company_name: Optional[str] = None
    ) -> str:
        """
        Generate AI-powered recommendations based on inventory data.
        
        Args:
            inventory_items: List of inventory items with product and quantity info
            company_name: Optional company name for context
            
        Returns:
            str: Generated recommendations text or error message
            
        Example:
            >>> items = [
            ...     {'product_code': 'PROD001', 'product_name': 'Laptop', 'quantity': 5},
            ...     {'product_code': 'PROD002', 'product_name': 'Mouse', 'quantity': 150}
            ... ]
            >>> service = AIRecommendationsService()
            >>> recommendations = service.generate_recommendations(items)
        """
        # Check if service is configured
        if not self.is_configured():
            logger.warning("AI service not configured (missing API key)")
            return "No fue posible generar recomendaciones automáticas. Servicio de IA no configurado."
        
        try:
            # Build the prompt from inventory data
            prompt = self._build_prompt(inventory_items, company_name)
            logger.error(">>> AI service")
            logger.error(f">>> prompt: {prompt}")
            # Call the LLM API
            response_text = self._call_huggingface_api(prompt)

            logger.error(f">>> response: {response_text}")
            
            if not response_text or not response_text.strip():
                logger.warning("AI service returned empty response")
                return "No fue posible generar recomendaciones automáticas en este momento."
            
            return response_text
            
        except requests.exceptions.Timeout:
            logger.error("AI service timeout")
            return "No fue posible generar recomendaciones automáticas. El servicio tardó demasiado en responder."
            
        except requests.exceptions.ConnectionError:
            logger.error("AI service connection error")
            return "No fue posible generar recomendaciones automáticas. Error de conexión con el servicio."
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"AI service HTTP error: {e}")
            if hasattr(e, 'response') and e.response.status_code == 401:
                return "No fue posible generar recomendaciones automáticas. API Key inválida."
            return "No fue posible generar recomendaciones automáticas en este momento."
            
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {str(e)}")
            return "No fue posible generar recomendaciones automáticas en este momento."
    
    def _build_prompt(
        self,
        inventory_items: List[Dict],
        company_name: Optional[str] = None
    ) -> str:
        """
        Build a prompt for the LLM based on inventory data.
        
        Args:
            inventory_items: List of inventory items
            company_name: Optional company name
            
        Returns:
            str: Formatted prompt for the LLM
        """
        # Start with context
        company_text = f" de {company_name}" if company_name else ""
        prompt_parts = [
            f"Se recomienda a la empresa {company_text} Considere reabastecer los siguientes productos.",
            "",
            "Inventario:"
        ]
        
        # Add inventory items
        for item in inventory_items[:20]:  # Limit to first 20 items to avoid token limits
            quantity = item.get('quantity', 0)
            if quantity<10:
                product_name = item.get('product_name', 'Producto')
                product_code = item.get('product_code', 'N/A')
                prompt_parts.append(f"- {product_name} (código: {product_code}): {quantity} unidades")
        
        if len(inventory_items) > 20:
            prompt_parts.append(f"... y {len(inventory_items) - 20} productos más.")
        
        prompt_parts.append("")
        prompt_parts.append("Recomendaciones:")
        
        return "\n".join(prompt_parts)
    
    def _call_huggingface_api(self, prompt: str) -> str:
        """
        Call Hugging Face Inference API.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            str: Generated text from the model
            
        Raises:
            requests.exceptions.RequestException: On API errors
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 500,
                "min_length": 50,
                "do_sample": False,
                "temperature": 0.7
            }
        }
        
        logger.info(f"Calling Hugging Face API with model: {self.model}")
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        # Raise exception for HTTP errors
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        logger.error(f">>> result: {result}")

        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], dict) and 'generated_text' in result[0]:
                return result[0]['generated_text']
            elif isinstance(result[0], dict) and 'summary_text' in result[0]:
                return result[0]['summary_text']
        
        if isinstance(result, dict):
            if 'generated_text' in result:
                return result['generated_text']
            elif 'summary_text' in result:
                return result['summary_text']
        
        logger.warning(f"Unexpected API response format: {result}")
        return ""
