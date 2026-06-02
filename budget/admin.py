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
        'remaining',
        'usage_percent',
        'month',
        'year',
        'is_deleted',
        'deleted_at',
        'created_at',
    )
    list_filter = ('year', 'month', 'category', 'is_deleted')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('slug', 'created_at', 'deleted_at', 'remaining', 'usage_percent')

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
                    'remaining',
                    'usage_percent',
                ),
            },
        ),
        (
            'Система',
            {
                'fields': (
                    'slug',
                    'is_deleted',
                    'deleted_at',
                    'created_at',
                ),
            },
        ),
    )
