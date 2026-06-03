from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Клиент'
        MANAGER = 'manager', 'Менеджер'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.get_username()
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    






class LoginHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_history',
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device = models.CharField(max_length=200, blank=True)
    browser = models.CharField(max_length=200, blank=True)
    is_successful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = 'история входа'
        verbose_name_plural = 'история входов'
        ordering = ['-created_at']
 
    def __str__(self):
        status = 'успешно' if self.is_successful else 'неудачно'
        return f'{self.user} — {self.ip_address} ({status}) {self.created_at:%d.%m.%Y %H:%M}'


class FinancialScore(models.Model):
    class Level(models.TextChoices):
        BRONZE = 'bronze', 'Бронза'
        SILVER = 'silver', 'Серебро'
        GOLD = 'gold', 'Золото'
        PLATINUM = 'platinum', 'Платина'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='financial_score'
    )
    score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.BRONZE,
    )
    calculated_at = models.DateTimeField(auto_now=True)
    score_details = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'финансовый рейтинг'
        verbose_name_plural = 'финансовые рейтинги'

    def __str__(self):
        return f'{self.user} — {self.level} ({self.score}/100)'