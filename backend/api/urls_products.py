from django.urls import path
from api.views.products import product_list_view

urlpatterns = [
    path('', product_list_view, name='product-list'),
]
