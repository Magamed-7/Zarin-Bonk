from django.contrib import admin

from .models import Deposit


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'account',
        'amount',
        'interest_rate',
        'term_months',
        'total_earned',
        'status',
        'created_at',
        'end_date',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'account__account_number')
    readonly_fields = ('total_earned', 'created_at')

    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'user',
                    'account',
                    'amount',
                    'interest_rate',
                    'term_months',
                    'total_earned',
                ),
            },
        ),
        (
            'Статус и даты',
            {
                'fields': (
                    'status',
                    'created_at',
                    'end_date',
                ),
            },
        ),
    )