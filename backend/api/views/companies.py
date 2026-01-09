from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.permissions import IsAdministratorOrReadOnly
from api.serializers.company import CompanySerializer, CompanyListSerializer
from infrastructure.models import Company


@api_view(['GET', 'POST'])
@permission_classes([IsAdministratorOrReadOnly])
def company_list_view(request):
    """
    List companies or create a new company.
    
    GET /api/v1/companies/ - All authenticated users can view
    POST /api/v1/companies/ - Only administrators can create
    
    Request Body (POST):
    {
        "nit": "123456789",
        "name": "Company Name",
        "address": "Company Address",
        "phone": "+57 300 1234567"
    }
    
    Response (GET):
    [
        {
            "nit": "123456789",
            "name": "Company Name",
            "address": "Company Address",
            "phone": "+57 300 1234567"
        }
    ]
    
    Response (POST):
    {
        "nit": "123456789",
        "name": "Company Name",
        "address": "Company Address",
        "phone": "+57 300 1234567",
        "created_at": "2026-01-09T00:00:00Z",
        "updated_at": "2026-01-09T00:00:00Z"
    }
    
    Error Codes:
    - 400: Bad Request (invalid data)
    - 401: Unauthorized
    - 403: Forbidden (non-admin trying to create)
    """
    if request.method == 'GET':
        companies = Company.objects.all()
        serializer = CompanyListSerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdministratorOrReadOnly])
def company_detail_view(request, nit):
    """
    Retrieve, update or delete a company.
    
    GET /api/v1/companies/{nit}/ - All authenticated users can view
    PUT /api/v1/companies/{nit}/ - Only administrators can update
    DELETE /api/v1/companies/{nit}/ - Only administrators can delete
    
    Request Body (PUT):
    {
        "name": "Updated Company Name",
        "address": "Updated Address",
        "phone": "+57 300 9876543"
    }
    
    Response (GET, PUT):
    {
        "nit": "123456789",
        "name": "Company Name",
        "address": "Company Address",
        "phone": "+57 300 1234567",
        "created_at": "2026-01-09T00:00:00Z",
        "updated_at": "2026-01-09T00:00:00Z"
    }
    
    Error Codes:
    - 400: Bad Request (invalid data)
    - 401: Unauthorized
    - 403: Forbidden (non-admin trying to update/delete)
    - 404: Not Found
    """
    try:
        company = Company.objects.get(nit=nit)
    except Company.DoesNotExist:
        return Response(
            {'detail': 'Company not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
