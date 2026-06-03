from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, LoginHistory, FinancialScore


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_verified', 'is_deleted', 'deleted_at', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_deleted', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            'ZarinPay',
            {
                'fields': (
                    'role',
                    'phone',
                    'avatar',
                    'date_of_birth',
                    'address',
                    'is_verified',
                    'is_deleted',
                    'deleted_at',
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            'ZarinPay',
            {
                'fields': (
                    'role',
                    'phone',
                    'avatar',
                    'date_of_birth',
                    'address',
                    'is_verified',
                ),
            },
        ),
    )









@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'device', 'browser', 'is_successful', 'created_at')
    list_filter = ('is_successful', 'created_at')
    search_fields = ('user__username', 'user__email', 'ip_address', 'device', 'browser')
    readonly_fields = ('user', 'ip_address', 'device', 'browser', 'is_successful', 'created_at')
 
    fieldsets = (
        (
            'Основное',
            {
                'fields': ('user', 'ip_address', 'device', 'browser'),
            },
        ),
        (
            'Статус',
            {
                'fields': ('is_successful', 'created_at'),
            },
        ),
    )
 
    def has_add_permission(self, request):
        return False
 
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FinancialScore)
class FinancialScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'level', 'calculated_at')
    list_filter = ('level',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'score', 'level', 'calculated_at', 'score_details')

    fieldsets = (
        (
            'Основное',
            {
                'fields': ('user',),
            },
        ),
        (
            'Рейтинг',
            {
                'fields': ('score', 'level', 'calculated_at'),
            },
        ),
        (
            'Детали',
            {
                'fields': ('score_details',),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
 