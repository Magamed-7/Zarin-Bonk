from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.SupportTicketListView.as_view(), name='ticket_list'),
    path('create/', views.SupportTicketCreateView.as_view(), name='ticket_create'),
    path('<int:ticket_id>/', views.SupportTicketDetailView.as_view(), name='ticket_detail'),
]
