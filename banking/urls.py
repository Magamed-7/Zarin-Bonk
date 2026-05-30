from django.urls import path

from . import views

app_name = 'banking'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
]