from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('services/', views.ServicesView.as_view(), name='services'),
    path('services/pay/', views.pay_service_view, name='pay_service'),
    path('services/quick-pay/<int:template_id>/', views.quick_pay_view, name='quick_pay'),
    path('services/delete-template/<int:template_id>/', views.delete_template_view, name='delete_template'),
    path('services/<str:category_id>/', views.category_services_view, name='category_services'),
    
    # Detail and PDF features
    path('<int:transaction_id>/', views.transaction_detail_view, name='transaction_detail'),
    path('<int:transaction_id>/repeat/', views.repeat_transaction_view, name='repeat_transaction'),
    path('<int:transaction_id>/pdf/', views.transaction_pdf_view, name='transaction_pdf'),
    path('export-statement/', views.export_statement_pdf_view, name='export_statement_pdf'),
]
