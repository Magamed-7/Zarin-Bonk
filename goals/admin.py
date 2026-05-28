from django.contrib import admin

from .models import Goal


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'icon',
        'title',
        'user',
        'target_amount',
        'current_amount',
        'deadline',
        'is_completed',
        'created_at',
    )
    list_filter = ('is_completed', 'deadline', 'created_at')
    search_fields = ('title', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'is_completed')

    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'user',
                    'title',
                    'icon',
                    'description',
                ),
            },
        ),
        (
            'Накопление',
            {
                'fields': (
                    'target_amount',
                    'current_amount',
                    'deadline',
                ),
            },
        ),
        (
            'Статус',
            {
                'fields': (
                    'is_completed',
                    'created_at',
                ),
            },
        ),
    )