from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        TRANSACTION = 'transaction', 'Транзакция'
        SECURITY = 'security', 'Безопасность'
        LOAN = 'loan', 'Кредит'
        SYSTEM = 'system', 'Система'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'уведомление'
        verbose_name_plural = 'уведомления'
        ordering = ['-created_at']

    def __str__(self):
        status = 'прочитано' if self.is_read else 'новое'
        return f'[{self.get_notification_type_display()}] {self.title} — {self.user} ({status})'