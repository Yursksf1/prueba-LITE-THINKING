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
from django.http import HttpResponse

from api.permissions import IsAdministratorOrReadOnly
from api.serializers.inventory import SendEmailSerializer
from infrastructure.models import InventoryItem, Company
from application.services import PDFGeneratorService, EmailService

import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAdministratorOrReadOnly])
def company_inventory_list_view(request, nit):
    """
    List inventory items for a specific company.
    
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
    
    Error Codes:
    - 401: Unauthorized
    - 404: Company Not Found
    """
    try:
        company = Company.objects.get(nit=nit)
    except Company.DoesNotExist:
        return Response(
            {'detail': 'Company not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
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


@api_view(['GET'])
@permission_classes([IsAdministratorOrReadOnly])
def company_inventory_pdf_view(request, nit):
    """
    Download inventory PDF for a specific company.
    
    GET /api/v1/companies/{nit}/inventory/pdf/
    
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
    
    try:
        # Generate PDF
        pdf_service = PDFGeneratorService()
        pdf_buffer = pdf_service.generate_inventory_pdf(
            inventory_items=items_data,
            company_name=company.name,
            company_nit=company.nit
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
@permission_classes([IsAdministratorOrReadOnly])
def company_inventory_send_email_view(request, nit):
    """
    Send inventory PDF via email for a specific company.
    
    POST /api/v1/companies/{nit}/inventory/send-email/
    
    Permissions:
    - Administrator: Full access
    - External: Can send emails (read-only equivalent for this action)
    
    Request Body:
    {
        "email": "recipient@example.com"
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
    
    try:
        # Generate PDF
        pdf_service = PDFGeneratorService()
        pdf_buffer = pdf_service.generate_inventory_pdf(
            inventory_items=items_data,
            company_name=company.name,
            company_nit=company.nit
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
