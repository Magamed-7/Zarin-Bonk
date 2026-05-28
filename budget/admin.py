from django.contrib import admin
from django.utils.html import format_html

from .models import Budget, BudgetCategory


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'icon', 'name', 'color_preview')
    search_fields = ('name',)

    @admin.display(description='Цвет')
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;'
            'border-radius:4px;background:{}"></span> {}',
            obj.color,
            obj.color,
        )


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'category',
        'limit_amount',
        'current_amount',
        'usage_display',
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

    @admin.display(description='Использовано')
    def usage_display(self, obj):
        percent = obj.usage_percent
        color = '#ff4655' if obj.is_exceeded else '#ffd700' if percent >= 80 else '#00ffaa'
        return format_html(
            '<span style="color:{}">{} %</span>',
            color,
            percent,
        )