from django.urls import path
from . import views


app_name = 'ai_assistant'

urlpatterns = [
    path('', views.AIChatView.as_view(), name='chat'),
    path('api/send/', views.AIChatAPIView.as_view(), name='api_send'),
]
