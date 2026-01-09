from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from api.serializers.inventory import InventoryItemSerializer, SendEmailSerializer
from infrastructure.models import InventoryItem, Company


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_list_view(request):
    """
    List inventory items, optionally filtered by company.
    
    GET /api/v1/inventory/ - All authenticated users can view
    Query Parameters:
    - company_nit (optional): Filter by company NIT
    
    Response:
    [
        {
            "id": 1,
            "company_nit": "123456789",
            "company_name": "Company Name",
            "product_code": "PROD001",
            "product_name": "Product Name",
            "quantity": 100,
            "created_at": "2026-01-09T00:00:00Z",
            "updated_at": "2026-01-09T00:00:00Z"
        }
    ]
    
    Error Codes:
    - 401: Unauthorized
    - 404: Company Not Found (if company_nit provided)
    """
    company_nit = request.query_params.get('company_nit')
    
    if company_nit:
        try:
            company = Company.objects.get(nit=company_nit)
            inventory_items = InventoryItem.objects.filter(company=company)
        except Company.DoesNotExist:
            return Response(
                {'detail': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        inventory_items = InventoryItem.objects.all()
    
    serializer = InventoryItemSerializer(inventory_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_pdf_view(request):
    """
    Download inventory as PDF.
    
    GET /api/v1/inventory/pdf - All authenticated users can download
    Query Parameters:
    - company_nit (optional): Filter by company NIT
    
    Response: PDF file
    
    Note: This is a placeholder implementation. In production, 
    this would generate a real PDF using a library like ReportLab or WeasyPrint.
    
    Error Codes:
    - 401: Unauthorized
    - 404: Company Not Found (if company_nit provided)
    """
    company_nit = request.query_params.get('company_nit')
    
    if company_nit:
        try:
            company = Company.objects.get(nit=company_nit)
            # select_related optimization to reduce DB queries
            inventory_items = InventoryItem.objects.filter(company=company).select_related('company', 'product')
            filename = f"inventory_{company_nit}.pdf"
        except Company.DoesNotExist:
            return Response(
                {'detail': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # select_related optimization to reduce DB queries
        # Note: For production with large datasets, consider adding pagination
        inventory_items = InventoryItem.objects.all().select_related('company', 'product')
        filename = "inventory_all.pdf"
    
    # Placeholder PDF generation
    # TODO: In production, use a proper PDF library (ReportLab, WeasyPrint)
    # and change content_type to 'application/pdf'
    pdf_content = "PDF PLACEHOLDER\n\n"
    pdf_content += "INVENTORY REPORT\n"
    pdf_content += "=" * 50 + "\n\n"
    
    for item in inventory_items:
        pdf_content += f"Company: {item.company.name} ({item.company.nit})\n"
        pdf_content += f"Product: {item.product.name} ({item.product.code})\n"
        pdf_content += f"Quantity: {item.quantity}\n"
        pdf_content += "-" * 50 + "\n"
    
    # Using text/plain for placeholder; will be application/pdf in production
    response = HttpResponse(pdf_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inventory_send_email_view(request):
    """
    Send inventory PDF via email.
    
    POST /api/v1/inventory/send-email - All authenticated users can send
    
    Request Body:
    {
        "email": "recipient@example.com",
        "company_nit": "123456789"  // optional
    }
    
    Response:
    {
        "message": "Inventory report sent successfully to recipient@example.com"
    }
    
    Note: This is a placeholder implementation. In production,
    this would integrate with an email service provider.
    
    Error Codes:
    - 400: Bad Request (invalid email)
    - 401: Unauthorized
    - 404: Company Not Found (if company_nit provided)
    """
    serializer = SendEmailSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    company_nit = serializer.validated_data.get('company_nit')
    
    if company_nit:
        try:
            company = Company.objects.get(nit=company_nit)
            message = f"Inventory report for {company.name} sent successfully to {email}"
        except Company.DoesNotExist:
            return Response(
                {'detail': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        message = f"Inventory report sent successfully to {email}"
    
    # Placeholder email sending
    # In production, integrate with an email service (SendGrid, AWS SES, etc.)
    
    return Response(
        {'message': message},
        status=status.HTTP_200_OK
    )
