from decimal import Decimal

from django.conf import settings
from django.db import models


class Deposit(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активен'
        CLOSED = 'closed', 'Закрыт'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deposits',
    )
    account = models.ForeignKey(
        'banking.Account',
        on_delete=models.PROTECT,
        related_name='deposits',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Годовая процентная ставка, %',
    )
    term_months = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField()
    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )

    class Meta:
        verbose_name = 'депозит'
        verbose_name_plural = 'депозиты'
        ordering = ['-created_at']

    def __str__(self):
        return f'Депозит #{self.pk} — {self.user} ({self.get_status_display()})'

    def calculate_total_earned(self):
        earned = (
            self.amount
            ,* self.interest_rate
            / Decimal('100')
            * self.term_months
            / Decimal('12')
        )
        return earned.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        if not self.total_earned or self.total_earned == Decimal('0.00'):
            self.total_earned = self.calculate_total_earned()
        super().save(*args, **kwargs)