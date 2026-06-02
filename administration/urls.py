from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/change-role/', views.ChangeRoleView.as_view(), name='change_role'),
    path('users/<int:user_id>/toggle-block/', views.ToggleBlockView.as_view(), name='toggle_block'),
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('settings/', views.BankSettingsView.as_view(), name='settings'),
    path('exchange-rates/', views.ExchangeRateListView.as_view(), name='exchange_rates'),
    path('exchange-rates/add/', views.ExchangeRateCreateView.as_view(), name='exchange_rate_add'),
    path('exchange-rates/<int:rate_id>/edit/', views.ExchangeRateUpdateView.as_view(), name='exchange_rate_edit'),
    path('exchange-rates/<int:rate_id>/delete/', views.ExchangeRateDeleteView.as_view(), name='exchange_rate_delete'),
    path('loan-programs/', views.LoanProgramListView.as_view(), name='loan_programs'),
    path('loan-programs/add/', views.LoanProgramCreateView.as_view(), name='loan_program_add'),
    path('loan-programs/<int:program_id>/edit/', views.LoanProgramUpdateView.as_view(), name='loan_program_edit'),
    path('loan-programs/<int:program_id>/delete/', views.LoanProgramDeleteView.as_view(), name='loan_program_delete'),
]
