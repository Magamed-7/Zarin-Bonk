from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('verify-2fa/',  views.verify_2fa_view,  name='verify_2fa'),
    path('resend-2fa/',  views.resend_2fa_view,  name='resend_2fa'),
]