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
        'remaining_amount',
        'progress_percent',
        'deadline',
        'is_completed',
        'is_deleted',
        'deleted_at',
        'created_at',
    )
    list_filter = ('is_completed', 'is_deleted', 'deadline', 'created_at')
    search_fields = ('title', 'user__username', 'user__email')
    readonly_fields = ('slug', 'created_at', 'deleted_at', 'progress_percent', 'remaining_amount')

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
                    'remaining_amount',
                    'progress_percent',
                    'deadline',
                ),
            },
        ),
        (
            'Статус',
            {
                'fields': (
                    'is_completed',
                    'is_deleted',
                    'deleted_at',
                    'created_at',
                ),
            },
        ),
        (
            'Система',
            {
                'fields': (
                    'slug',
                ),
            },
        ),
    )
