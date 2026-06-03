from django.conf import settings
from django.db import models


class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Открыт'
        IN_PROGRESS = 'in_progress', 'В работе'
        RESOLVED = 'resolved', 'Решено'
        CLOSED = 'closed', 'Закрыт'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets',
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='managed_tickets',
        null=True,
        blank=True,
    )
    subject = models.CharField(max_length=300)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'тикет поддержки'
        verbose_name_plural = 'тикеты поддержки'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} {self.subject} — {self.user} ({self.get_status_display()})'


class SupportMessage(models.Model):
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_messages',
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'сообщение поддержки'
        verbose_name_plural = 'сообщения поддержки'
        ordering = ['created_at']

    def __str__(self):
        return f'Тикет #{self.ticket.pk} — {self.sender} ({self.created_at:%d.%m.%Y %H:%M})'