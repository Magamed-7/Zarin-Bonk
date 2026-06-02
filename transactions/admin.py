from django.contrib import admin

from .models import Transaction, PaymentTemplate


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
        'is_deleted',
        'deleted_at',
        'created_at',
    )
    list_filter = ('transaction_type', 'status', 'is_deleted', 'created_at')
    search_fields = (
        'category',
        'description',
        'sender_account__account_number',
        'receiver_account__account_number',
    )
    readonly_fields = ('created_at', 'deleted_at')
    date_hierarchy = 'created_at'


@admin.register(PaymentTemplate)
class PaymentTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'user',
        'category',
        'service_provider',
        'amount',
        'is_deleted',
        'deleted_at',
        'created_at',
    )
    list_filter = ('category', 'is_deleted', 'created_at')
    search_fields = ('name', 'service_provider', 'user__username')
    readonly_fields = ('created_at', 'deleted_at')

