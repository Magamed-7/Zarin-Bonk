from django.contrib import admin

from .models import Loan, LoanPayment


class LoanPaymentInline(admin.TabularInline):
    model = LoanPayment
    extra = 0
    readonly_fields = ('due_date', 'amount', 'paid_date', 'is_paid')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    inlines = [LoanPaymentInline]
    list_display = (
        'id',
        'user',
        'amount',
        'term_months',
        'interest_rate',
        'monthly_payment',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('monthly_payment', 'created_at')

    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'user',
                    'amount',
                    'term_months',
                    'interest_rate',
                    'monthly_payment',
                ),
            },
        ),
        (
            'Статус',
            {
                'fields': (
                    'status',
                    'manager_comment',
                ),
            },
        ),
        (
            'Дата',
            {
                'fields': ('created_at',),
            },
        ),
    )


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'loan',
        'amount',
        'due_date',
        'paid_date',
        'is_paid',
    )
    list_filter = ('is_paid', 'due_date')
    search_fields = ('loan__user__username', 'loan__user__email')
    readonly_fields = ('loan', 'amount', 'due_date')