from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.permissions import IsAdministratorOrReadOnly
from api.serializers.product import ProductSerializer, ProductCreateSerializer, ProductListSerializer
from infrastructure.models import Product, Company


@api_view(['GET', 'POST'])
@permission_classes([IsAdministratorOrReadOnly])
def product_list_view(request, nit):
    """
    List products for a company or create a new product.
    
    GET /api/v1/companies/{nit}/products - All authenticated users can view
    POST /api/v1/companies/{nit}/products - Only administrators can create
    
    Request Body (POST):
    {
        "code": "PROD001",
        "name": "Product Name",
        "features": ["Feature 1", "Feature 2"],
        "prices": {
            "USD": {"amount": 100.00, "currency": "USD"},
            "COP": {"amount": 400000.00, "currency": "COP"}
        }
    }
    
    Response (GET):
    [
        {
            "code": "PROD001",
            "name": "Product Name",
            "company_nit": "123456789",
            "company_name": "Company Name"
        }
    ]
    
    Response (POST):
    {
        "code": "PROD001",
        "name": "Product Name",
        "features": ["Feature 1", "Feature 2"],
        "prices": {
            "USD": {"amount": 100.00, "currency": "USD"},
            "COP": {"amount": 400000.00, "currency": "COP"}
        },
        "company_nit": "123456789",
        "company_name": "Company Name",
        "created_at": "2026-01-09T00:00:00Z",
        "updated_at": "2026-01-09T00:00:00Z"
    }
    
    Error Codes:
    - 400: Bad Request (invalid data)
    - 401: Unauthorized
    - 403: Forbidden (non-admin trying to create)
    - 404: Company Not Found
    """
    try:
        company = Company.objects.get(nit=nit)
    except Company.DoesNotExist:
        return Response(
            {'detail': 'Company not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        products = Product.objects.filter(company=company)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(company=company)
            response_serializer = ProductSerializer(product)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
