from django.urls import path
from api.views.company_inventory import (
    company_inventory_list_view,
    company_inventory_pdf_view,
    company_inventory_send_email_view
)
urlpatterns = [
    # Company-specific inventory endpoints
    path('', company_inventory_list_view, name='company-inventory-list'),
    path('pdf/', company_inventory_pdf_view, name='company-inventory-pdf'),
    path('send-email/', company_inventory_send_email_view, name='company-inventory-send-email'),
]
