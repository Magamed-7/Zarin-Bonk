from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.GoalListView.as_view(), name='goal_list'),
    path('create/', views.GoalCreateView.as_view(), name='goal_create'),
    path('<slug:slug>/update/', views.GoalUpdateView.as_view(), name='goal_update'),
    path('<slug:slug>/delete/', views.GoalDeleteView.as_view(), name='goal_delete'),
    path('<slug:slug>/deposit/', views.GoalDepositView.as_view(), name='goal_deposit'),
]
