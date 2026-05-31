from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loans_view, name='loans_page'),
]
