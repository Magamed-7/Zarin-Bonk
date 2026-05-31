from django.urls import path

from . import views

app_name = 'banking'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('accounts/create/', views.create_account_view, name='create_account'),
    path('accounts/<int:account_id>/',   views.account_detail_view,  name='account_detail'),
    path('cards/<int:card_id>/freeze/', views.toggle_card_freeze_view, name='toggle_card_freeze'),
    path('topup/', views.topup_account_view, name='topup'),
    path('currency/', views.currency_convert_view, name='currency'),
    path('rates/', views.currency_rates_view, name='rates'),
    path('transfer/', views.transfer_money_view, name='transfer'),
    path('lookup-account/', views.receiver_lookup_view, name='lookup_account'),
]