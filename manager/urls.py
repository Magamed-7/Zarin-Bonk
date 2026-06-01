from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('loans/', views.LoanRequestsListView.as_view(), name='loan_requests'),
    path('loans/<int:loan_id>/', views.LoanRequestDetailView.as_view(), name='loan_request_detail'),
]
