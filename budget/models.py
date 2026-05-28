from decimal import Decimal

from django.conf import settings
from django.db import models


class BudgetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=10,
        default='📦',
        help_text='Эмодзи-иконка категории',
    )
    color = models.CharField(
        max_length=7,
        default='#ffd700',
        help_text='HEX-цвет категории, например #ffd700',
    )

    class Meta:
        verbose_name = 'категория бюджета'
        verbose_name_plural = 'категории бюджета'
        ordering = ['name']

    def __str__(self):
        return f'{self.icon} {self.name}'


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets',
    )
    category = models.ForeignKey(
        BudgetCategory,
        on_delete=models.PROTECT,
        related_name='budgets',
    )
    limit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Максимальный лимит расходов за месяц',
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Уже потрачено в этом месяце',
    )
    month = models.PositiveSmallIntegerField(
        help_text='Месяц (1–12)',
    )
    year = models.PositiveSmallIntegerField(
        help_text='Год, например 2025',
    )

    class Meta:
        verbose_name = 'бюджет'
        verbose_name_plural = 'бюджеты'
        ordering = ['-year', '-month']
        unique_together = ('user', 'category', 'month', 'year')

    def __str__(self):
        return f'{self.user} — {self.category} ({self.month:02d}/{self.year})'

    @property
    def remaining(self):
        return self.limit_amount - self.current_amount

    @property
    def usage_percent(self):
        if self.limit_amount == 0:
            return 0
        percent = self.current_amount / self.limit_amount * 100
        return min(round(float(percent), 1), 100.0)

    @property
    def is_exceeded(self):
        return self.current_amount > self.limit_amount