# AI-Powered Recommendations Feature

## Overview
The inventory PDF generation now supports optional AI-powered recommendations using the Hugging Face Inference API. This feature provides automated insights about inventory levels, helping administrators identify low stock, excess inventory, and general observations.

## Configuration

### Environment Variables
Add the following variables to your `.env` file:

```env
# LLM provider (currently supports 'huggingface')
LLM_PROVIDER=huggingface

# API key from https://huggingface.co/settings/tokens
LLM_API_KEY=your_api_key_here

# Model to use (e.g., 'facebook/bart-large-cnn' for summarization)
LLM_MODEL=facebook/bart-large-cnn
```

**Note:** The feature works without configuration - if no API key is provided, the system will continue to work normally without AI recommendations.

## Usage

### PDF Download Endpoint
Request AI recommendations by adding the `include_ai_recommendations` query parameter:

```bash
# Without AI recommendations (default)
GET /api/v1/companies/{nit}/inventory/pdf/

# With AI recommendations
GET /api/v1/companies/{nit}/inventory/pdf/?include_ai_recommendations=true
```

### Email Sending Endpoint
Include AI recommendations by adding a flag to the request body:

```bash
POST /api/v1/companies/{nit}/inventory/send-email/
Content-Type: application/json

{
  "email": "recipient@example.com",
  "include_ai_recommendations": true
}
```

## How It Works

1. **Opt-in Design**: AI recommendations are only generated when explicitly requested via the flag parameter
2. **No Database Impact**: The AI service doesn't store any data - it's used only during PDF generation
3. **Graceful Degradation**: If the AI service fails (network error, timeout, invalid API key, etc.), the PDF is still generated with an error message in the recommendations section
4. **Smart Prompting**: The system builds an intelligent prompt from inventory data, identifying products with:
   - Low stock (< 10 units)
   - Excess inventory (> 100 units)
   - General observations

## Error Handling

The implementation handles all potential errors gracefully:

- **No API Key**: Shows "Servicio de IA no configurado" message
- **Network Errors**: Shows connection error message
- **Timeout**: Shows timeout message
- **Invalid API Key**: Shows invalid key message
- **Empty Response**: Shows generic error message

In all cases, the PDF is still generated successfully.

## Technical Details

### AI Service (`AIRecommendationsService`)
- Located in: `backend/application/services/ai_recommendations_service.py`
- Integrates with Hugging Face Inference API
- Configurable timeout (30 seconds)
- Limits inventory items to 20 in prompt to avoid token limits
- Provider-agnostic design allows future support for other LLM providers

### PDF Service Updates (`PDFGeneratorService`)
- New optional parameter: `ai_recommendations`
- Adds "Recomendaciones" section when AI content is provided
- Uses styled formatting with title, separator line, and formatted content

### API Views
- `company_inventory_pdf_view`: Accepts query parameter `include_ai_recommendations`
- `company_inventory_send_email_view`: Accepts body parameter `include_ai_recommendations`

## Testing

The implementation includes comprehensive tests:
- 14 tests for AI service (all error scenarios covered)
- 8 tests for PDF generation with/without AI
- All tests use mocked API calls (no real Hugging Face calls)

Run tests with:
```bash
cd backend
python manage.py test api.tests.test_ai_recommendations --settings=config.test_settings
python manage.py test api.tests.test_company_inventory --settings=config.test_settings
```

## Security Considerations

- ✅ API keys stored in environment variables (never hardcoded)
- ✅ No sensitive data sent to external API
- ✅ Timeout configured to prevent hanging requests
- ✅ Error messages don't expose internal details
- ✅ No security vulnerabilities detected by CodeQL scan

## Future Enhancements

Potential future improvements:
- Add caching of recommendations to reduce API calls
- Support for additional LLM providers (OpenAI, Claude, etc.)
- Configurable prompt templates
- Frontend checkbox to enable/disable from UI
- Analytics on AI recommendation usage
