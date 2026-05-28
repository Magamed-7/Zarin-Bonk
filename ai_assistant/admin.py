from django.contrib import admin

from .models import AIMessage


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'role',
        'short_message',
        'created_at',
    )
    list_filter = ('role', 'created_at')
    search_fields = ('message', 'user__username', 'user__email')
    readonly_fields = ('user', 'role', 'message', 'created_at')

    fieldsets = (
        (
            'Сообщение',
            {
                'fields': (
                    'user',
                    'role',
                    'message',
                    'created_at',
                ),
            },
        ),
    )

    @admin.display(description='Сообщение')
    def short_message(self, obj):
        if len(obj.message) > 80:
            return f'{obj.message[:80]}...'
        return obj.message