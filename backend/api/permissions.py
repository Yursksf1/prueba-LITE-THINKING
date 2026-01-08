from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    """
    Permission class to allow only administrators.
    """
    
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.is_administrator
        )


class IsAdministratorOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow administrators full access,
    and external users read-only access.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to administrators
        return request.user.is_administrator
