from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/change-role/', views.ChangeRoleView.as_view(), name='change_role'),
    path('users/<int:user_id>/toggle-block/', views.ToggleBlockView.as_view(), name='toggle_block'),
]
