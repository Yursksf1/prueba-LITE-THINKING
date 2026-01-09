import sys
import os

# Add domain package to Python path
domain_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'domain', 'src')
if domain_path not in sys.path:
    sys.path.insert(0, domain_path)

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from domain.exceptions.errors import InvalidCompanyError

from api.permissions import IsAdministratorOrReadOnly
from api.serializers.company import CompanySerializer, CompanyListSerializer
from application.use_cases import RegisterCompanyUseCase, UpdateCompanyUseCase
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
            try:
                # Use domain-driven use case for company registration
                use_case = RegisterCompanyUseCase()
                company = use_case.execute(
                    nit=serializer.validated_data['nit'],
                    name=serializer.validated_data['name'],
                    address=serializer.validated_data['address'],
                    phone=serializer.validated_data['phone']
                )
                response_serializer = CompanySerializer(company)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except InvalidCompanyError as e:
                return Response(
                    {'detail': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
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
            try:
                # Use domain-driven use case for company update
                use_case = UpdateCompanyUseCase()
                updated_company = use_case.execute(
                    nit=nit,
                    name=serializer.validated_data.get('name'),
                    address=serializer.validated_data.get('address'),
                    phone=serializer.validated_data.get('phone')
                )
                response_serializer = CompanySerializer(updated_company)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except InvalidCompanyError as e:
                return Response(
                    {'detail': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
