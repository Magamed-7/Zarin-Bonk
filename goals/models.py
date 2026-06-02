from decimal import Decimal
from django.utils import timezone
import secrets

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
    slug = models.SlugField(max_length=50, unique=True, editable=False, default='')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'цель'
        verbose_name_plural = 'цели'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.icon} {self.title} — {self.user}'

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = self.generate_slug()
        
        if self.current_amount >= self.target_amount and self.target_amount > 0:
            self.is_completed = True
        super().save(*args, **kwargs)

    def generate_slug(self):
        while True:
            slug = secrets.token_urlsafe(16)
            if not Goal.objects.filter(slug=slug).exists():
                return slug

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

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