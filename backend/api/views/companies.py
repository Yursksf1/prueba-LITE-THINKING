from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.permissions import IsAdministratorOrReadOnly


@api_view(['GET', 'POST'])
@permission_classes([IsAdministratorOrReadOnly])
def company_list_view(request):
    """
    List companies or create a new company.
    
    GET /api/companies/ - All authenticated users can view
    POST /api/companies/ - Only administrators can create
    """
    if request.method == 'GET':
        # TODO: Implement list companies logic
        # This would call the domain service through application layer
        return Response({
            'message': 'List of companies',
            'data': [],
            'user_role': request.user.role
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Only administrators can reach here due to permission class
        # TODO: Implement create company logic
        # This would call the domain service through application layer
        return Response({
            'message': 'Company created successfully',
            'data': request.data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdministratorOrReadOnly])
def company_detail_view(request, nit):
    """
    Retrieve, update or delete a company.
    
    GET /api/companies/{nit}/ - All authenticated users can view
    PUT /api/companies/{nit}/ - Only administrators can update
    DELETE /api/companies/{nit}/ - Only administrators can delete
    """
    if request.method == 'GET':
        # TODO: Implement retrieve company logic
        return Response({
            'message': f'Company details for NIT: {nit}',
            'data': {},
            'user_role': request.user.role
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Only administrators can reach here
        # TODO: Implement update company logic
        return Response({
            'message': f'Company {nit} updated successfully',
            'data': request.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # Only administrators can reach here
        # TODO: Implement delete company logic
        return Response({
            'message': f'Company {nit} deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
