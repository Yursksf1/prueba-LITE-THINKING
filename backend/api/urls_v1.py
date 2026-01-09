"""
API v1 URL Configuration
"""
from django.urls import path, include

urlpatterns = [
    # Authentication endpoints
    path('auth/', include('api.urls_auth')),
    
    # Company endpoints
    path('companies/', include('api.urls_companies')),
    
    # Product endpoints (nested under companies)
    path('companies/<str:nit>/products/', include('api.urls_products')),
    
    # Inventory endpoints
    path('inventory/', include('api.urls_inventory')),
]
