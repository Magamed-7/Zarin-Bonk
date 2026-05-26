from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction_type',
        'amount',
        'sender_account',
        'receiver_account',
        'status',
        'category',
        'created_at',
    )
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = (
        'category',
        'description',
        'sender_account__account_number',
        'receiver_account__account_number',
    )
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
