from django.contrib import admin

from .models import Account, Card


class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    readonly_fields = ('card_number', 'cvv', 'created_at')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = [CardInline]
    list_display = (
        'account_number',
        'user',
        'account_type',
        'balance',
        'currency',
        'is_active',
        'created_at',
    )
    list_filter = ('account_type', 'currency', 'is_active')
    search_fields = ('account_number', 'user__username', 'user__email')
    readonly_fields = ('account_number', 'created_at')


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        'masked_number',
        'account',
        'card_type',
        'expiry_date',
        'is_frozen',
        'created_at',
    )
    list_filter = ('card_type', 'is_frozen')
    search_fields = ('card_number', 'account__account_number')
    readonly_fields = ('card_number', 'cvv', 'created_at')

    @admin.display(description='Номер карты')
    def masked_number(self, obj):
        return obj.masked_number
