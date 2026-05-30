from django.urls import path

from . import views

app_name = 'banking'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('accounts/create/', views.create_account_view, name='create_account'),
    path('accounts/<int:account_id>/',   views.account_detail_view,  name='account_detail'),
]