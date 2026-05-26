from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser')
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
