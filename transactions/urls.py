from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('services/', views.services_view, name='services'),
    path('services/pay/', views.pay_service_view, name='pay_service'),
    path('services/quick-pay/<int:template_id>/', views.quick_pay_view, name='quick_pay'),
    path('services/delete-template/<int:template_id>/', views.delete_template_view, name='delete_template'),
]
