from django.contrib import admin

from .models import SupportMessage, SupportTicket


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ('sender', 'message', 'created_at')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    inlines = [SupportMessageInline]
    list_display = (
        'id',
        'subject',
        'user',
        'manager',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'subject',
        'user__username',
        'user__email',
        'manager__username',
    )
    readonly_fields = ('created_at',)

    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'user',
                    'manager',
                    'subject',
                ),
            },
        ),
        (
            'Статус',
            {
                'fields': (
                    'status',
                    'created_at',
                ),
            },
        ),
    )


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ticket',
        'sender',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = (
        'message',
        'sender__username',
        'sender__email',
        'ticket__subject',
    )
    readonly_fields = ('created_at',)

    fieldsets = (
        (
            'Сообщение',
            {
                'fields': (
                    'ticket',
                    'sender',
                    'message',
                    'created_at',
                ),
            },
        ),
    )