from django.urls import path
from api.views.companies import company_list_view, company_detail_view
from api.views.company_inventory import (
    company_inventory_list_view,
    company_inventory_pdf_view,
    company_inventory_send_email_view
)

urlpatterns = [
    path('', company_list_view, name='company-list'),
    path('<str:nit>/', company_detail_view, name='company-detail'),
    # Company-specific inventory endpoints
    path('<str:nit>/inventory/', company_inventory_list_view, name='company-inventory-list'),
    path('<str:nit>/inventory/pdf/', company_inventory_pdf_view, name='company-inventory-pdf'),
    path('<str:nit>/inventory/send-email/', company_inventory_send_email_view, name='company-inventory-send-email'),
]
