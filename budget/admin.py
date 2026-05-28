from django.contrib import admin

from .models import Budget, BudgetCategory


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'icon', 'name', 'color')
    search_fields = ('name',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'category',
        'limit_amount',
        'current_amount',
        'month',
        'year',
    )
    list_filter = ('year', 'month', 'category')
    search_fields = ('user__username', 'user__email')

    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'user',
                    'category',
                    'month',
                    'year',
                ),
            },
        ),
        (
            'Бюджет',
            {
                'fields': (
                    'limit_amount',
                    'current_amount',
                ),
            },
        ),
    )