from django.urls import path
from api.views.companies import company_list_view, company_detail_view

urlpatterns = [
    path('', company_list_view, name='company-list'),
    path('<str:nit>/', company_detail_view, name='company-detail'),
]
