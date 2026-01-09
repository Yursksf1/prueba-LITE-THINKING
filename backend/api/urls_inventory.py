from django.urls import path
from api.views.inventory import (
    inventory_list_view,
    inventory_pdf_view,
    inventory_send_email_view
)

urlpatterns = [
    path('', inventory_list_view, name='inventory-list'),
    path('pdf', inventory_pdf_view, name='inventory-pdf'),
    path('send-email', inventory_send_email_view, name='inventory-send-email'),
]
