from django.conf import settings
from django.db import models


class AIMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ASSISTANT = 'assistant', 'Ассистент'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_messages',
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'сообщение ИИ'
        verbose_name_plural = 'сообщения ИИ'
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.get_role_display()}] {self.user} — {self.created_at:%d.%m.%Y %H:%M}'