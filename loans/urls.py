from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loans_view, name='loans_page'),
    path('repay/<int:loan_id>/', views.repay_loan_view, name='repay_loan'),
]
