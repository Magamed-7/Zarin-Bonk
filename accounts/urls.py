from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-2fa/', views.verify_2fa_view, name='verify_2fa'),
    path('resend-2fa/', views.resend_2fa_view, name='resend_2fa'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-verify/', views.password_reset_verify_view, name='password_reset_verify'),
    path('reset-new/', views.password_reset_new_view, name='password_reset_new'),
    path('profile/', views.profile_view, name='profile'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('verify-email/<str:token>/', views.verify_email_view,      name='verify_email'),
    path('resend-verification/',      views.resend_verification_view, name='resend_verification'),
]