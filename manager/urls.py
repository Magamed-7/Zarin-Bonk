from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('', views.ManagerDashboardView.as_view(), name='dashboard'),
    path('loans/', views.LoanRequestsListView.as_view(), name='loan_requests'),
    path('loans/<int:loan_id>/', views.LoanRequestDetailView.as_view(), name='loan_request_detail'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/<int:user_id>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/<int:ticket_id>/', views.TicketDetailView.as_view(), name='ticket_detail'),
]
