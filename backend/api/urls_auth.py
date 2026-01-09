from django.urls import path
from api.views.auth import login_view, refresh_token_view, me_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('refresh/', refresh_token_view, name='token_refresh'),
    path('me/', me_view, name='me'),
]
