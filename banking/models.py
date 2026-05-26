import secrets

from decimal import Decimal

from django.conf import settings
from django.db import models


class Account(models.Model):
    class AccountType(models.TextChoices):
        CHECKING = 'checking', 'Расчётный'
        SAVING = 'saving', 'Сберегательный'
        CURRENCY = 'currency', 'Валютный'

    class Currency(models.TextChoices):
        TJS = 'TJS', 'TJS'
        USD = 'USD', 'USD'
        EUR = 'EUR', 'EUR'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
    )
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TJS,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'счёт'
        verbose_name_plural = 'счета'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.account_number} ({self.get_currency_display()})'

    @classmethod
    def generate_account_number(cls):
        while True:
            suffix = ''.join(str(secrets.randbelow(10)) for _ in range(14))
            number = f'40817810{suffix}'
            if not cls.objects.filter(account_number=number).exists():
                return number

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
