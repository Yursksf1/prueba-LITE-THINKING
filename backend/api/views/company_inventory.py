"""
Company-specific inventory views.

Implements endpoints for inventory management per company:
- GET /companies/{nit}/inventory/ - List inventory for a company
- GET /companies/{nit}/inventory/pdf/ - Download PDF for company inventory
- POST /companies/{nit}/inventory/send-email/ - Send PDF by email
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from api.permissions import IsAdministratorOrReadOnly
from api.serializers.inventory import SendEmailSerializer, CreateInventorySerializer
from infrastructure.models import InventoryItem, Company, Product
from application.services import PDFGeneratorService, EmailService, AIRecommendationsService

import logging

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([IsAdministratorOrReadOnly])
def company_inventory_list_view(request, nit):
    """
    List inventory items or create a new inventory item for a specific company.
    
    GET /api/v1/companies/{nit}/inventory/
    
    Permissions:
    - Administrator: Full access
    - External: Read-only access
    
    Response:
    [
        {
            "product_code": "PROD001",
            "product_name": "Laptop HP",
            "quantity": 50,
            "prices": {"USD": 1000.00, "COP": 4000000.00}
        }
    ]
    
    POST /api/v1/companies/{nit}/inventory/
    
    Permissions:
    - Administrator only
    
    Request Body:
    {
        "product_code": "PROD001",
        "quantity": 50
    }
    
    Response:
    {
        "product_code": "PROD001",
        "product_name": "Laptop HP",
        "quantity": 50,
        "prices": {"USD": 1000.00, "COP": 4000000.00},
        "updated_at": "2026-01-09T19:00:00.000Z"
    }
    
    Error Codes:
    - 400: Bad Request (POST only - invalid data, product doesn't belong to company, or duplicate)
    - 401: Unauthorized
    - 403: Forbidden (POST only - not an administrator)
    - 404: Company or Product Not Found
    """
    # Validate company exists
    try:
        company = Company.objects.get(nit=nit)
    except Company.DoesNotExist:
        return Response(
            {'detail': 'Company not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Handle GET request (list inventory)
    if request.method == 'GET':
        # Get inventory items with related data
        inventory_items = InventoryItem.objects.filter(
            company=company
        ).select_related('product')
        
        # Serialize data manually for consistency
        data = []
        for item in inventory_items:
            data.append({
                'product_code': item.product.code,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'prices': item.product.prices,
                'updated_at': item.updated_at.isoformat()
            })
        
        return Response(data, status=status.HTTP_200_OK)
    
    # Handle POST request (create inventory)
    # Validate request data
    serializer = CreateInventorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    product_code = serializer.validated_data['product_code']
    quantity = serializer.validated_data['quantity']
    
    # Validate product exists
    try:
        product = Product.objects.get(code=product_code)
    except Product.DoesNotExist:
        return Response(
            {'detail': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Validate product belongs to the company
    if product.company.nit != company.nit:
        return Response(
            {'detail': 'Product does not belong to this company'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if inventory item already exists
    if InventoryItem.objects.filter(company=company, product=product).exists():
        return Response(
            {'detail': 'Inventory item already exists for this product and company'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create inventory item
    inventory_item = InventoryItem.objects.create(
        company=company,
        product=product,
        quantity=quantity
    )
    
    logger.info(f"Inventory item created: {company.nit} - {product.code} - Quantity: {quantity}")
    
    # Return response in the same format as the list endpoint
    return Response(
        {
            'product_code': inventory_item.product.code,
            'product_name': inventory_item.product.name,
            'quantity': inventory_item.quantity,
            'prices': inventory_item.product.prices,
            'updated_at': inventory_item.updated_at.isoformat()
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAdministratorOrReadOnly])
def company_inventory_pdf_view(request, nit):
    """
    Download inventory PDF for a specific company.
    
    GET /api/v1/companies/{nit}/inventory/pdf/?include_ai_recommendations=true
    
    Query Parameters:
    - include_ai_recommendations (optional): 'true' to include AI-generated recommendations
    
    Permissions:
    - Administrator: Full access
    - External: Read-only access (can download)
    
    Response: PDF file
    
    Error Codes:
    - 401: Unauthorized
    - 404: Company Not Found
    - 500: PDF Generation Error
    """
    try:
        company = Company.objects.get(nit=nit)
    except Company.DoesNotExist:
        return Response(
            {'detail': 'Company not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get the include_ai_recommendations query parameter
    include_ai_recommendations = request.query_params.get('include_ai_recommendations', 'false').lower() == 'true'
    
    # Get inventory items with related data
    inventory_items = InventoryItem.objects.filter(
        company=company
    ).select_related('product')
    
    # Prepare data for PDF
    items_data = []
    for item in inventory_items:
        items_data.append({
            'product_code': item.product.code,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'prices': item.product.prices
        })
    
    # Generate AI recommendations if requested
    ai_recommendations = None
    if include_ai_recommendations:
        logger.info(f"AI recommendations requested for company {nit}")
        ai_service = AIRecommendationsService()
        ai_recommendations = ai_service.generate_recommendations(
            inventory_items=items_data,
            company_name=company.name
        )
    
    try:
        # Generate PDF
        pdf_service = PDFGeneratorService()
        pdf_buffer = pdf_service.generate_inventory_pdf(
            inventory_items=items_data,
            company_name=company.name,
            company_nit=company.nit,
            ai_recommendations=ai_recommendations
        )
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="inventario_{nit}.pdf"'
        
        logger.info(f"PDF generated successfully for company {nit}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF for company {nit}: {str(e)}")
        return Response(
            {'detail': 'Error generating PDF report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def company_inventory_send_email_view(request, nit):
    """
    Send inventory PDF via email for a specific company.
    
    POST /api/v1/companies/{nit}/inventory/send-email/
    
    Permissions:
    - All authenticated users (both Administrator and External) can send emails
    
    Request Body:
    {
        "email": "recipient@example.com",
        "include_ai_recommendations": true  // optional, defaults to false
    }
    
    Response:
    {
        "message": "Inventory report for Company Name sent successfully to recipient@example.com"
    }
    
    Error Codes:
    - 400: Bad Request (invalid email)
    - 401: Unauthorized
    - 404: Company Not Found
    - 500: Email Sending Error
    """
    try:
        company = Company.objects.get(nit=nit)
    except Company.DoesNotExist:
        return Response(
            {'detail': 'Company not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Validate request data
    serializer = SendEmailSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    recipient_email = serializer.validated_data['email']
    
    # Get the include_ai_recommendations flag from request body (optional)
    include_ai_recommendations = request.data.get('include_ai_recommendations', False)
    if isinstance(include_ai_recommendations, str):
        include_ai_recommendations = include_ai_recommendations.lower() == 'true'
    
    # Get inventory items with related data
    inventory_items = InventoryItem.objects.filter(
        company=company
    ).select_related('product')
    
    # Prepare data for PDF
    items_data = []
    for item in inventory_items:
        items_data.append({
            'product_code': item.product.code,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'prices': item.product.prices
        })
    
    # Generate AI recommendations if requested
    ai_recommendations = None
    if include_ai_recommendations:
        logger.info(f"AI recommendations requested for email to {recipient_email}")
        ai_service = AIRecommendationsService()
        ai_recommendations = ai_service.generate_recommendations(
            inventory_items=items_data,
            company_name=company.name
        )
    
    try:
        # Generate PDF
        pdf_service = PDFGeneratorService()
        pdf_buffer = pdf_service.generate_inventory_pdf(
            inventory_items=items_data,
            company_name=company.name,
            company_nit=company.nit,
            ai_recommendations=ai_recommendations
        )
        
        # Send email
        email_service = EmailService()
        
        # Check if email is configured
        if not email_service.validate_email_configuration():
            logger.warning(f"Email not configured, simulating send to {recipient_email}")
            # In development/testing, we can still return success
            return Response(
                {
                    'message': f'Inventory report for {company.name} would be sent to {recipient_email} (email not configured)'
                },
                status=status.HTTP_200_OK
            )
        
        # Send the email
        success = email_service.send_inventory_report(
            recipient_email=recipient_email,
            pdf_buffer=pdf_buffer,
            company_name=company.name,
            company_nit=company.nit
        )
        
        if success:
            return Response(
                {
                    'message': f'Inventory report for {company.name} sent successfully to {recipient_email}'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'detail': 'Failed to send email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error sending email for company {nit}: {str(e)}")
        return Response(
            {'detail': f'Error sending email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
