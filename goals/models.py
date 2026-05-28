from decimal import Decimal

from django.conf import settings
from django.db import models


class Goal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals',
    )
    title = models.CharField(max_length=200)
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Целевая сумма накопления',
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Уже накоплено',
    )
    deadline = models.DateField(
        blank=True,
        null=True,
        help_text='Дата достижения цели',
    )
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=10,
        default='🎯',
        help_text='Эмодзи-иконка цели',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'цель'
        verbose_name_plural = 'цели'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.icon} {self.title} — {self.user}'

    @property
    def progress_percent(self):
        if self.target_amount == 0:
            return 0
        percent = self.current_amount / self.target_amount * 100
        return min(round(float(percent), 1), 100.0)

    @property
    def remaining_amount(self):
        remaining = self.target_amount - self.current_amount
        return max(remaining, Decimal('0.00'))

    def save(self, *args, **kwargs):
        if self.current_amount >= self.target_amount and self.target_amount > 0:
            self.is_completed = True
        super().save(*args, **kwargs)