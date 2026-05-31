from decimal import Decimal

from django.db import models
from django.conf import settings


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        TRANSFER = 'transfer', 'Перевод'
        PAYMENT = 'payment', 'Платёж'
        DEPOSIT = 'deposit', 'Пополнение'
        WITHDRAWAL = 'withdrawal', 'Снятие'

    class Status(models.TextChoices):
        PENDING = 'pending', 'В обработке'
        COMPLETED = 'completed', 'Выполнена'
        FAILED = 'failed', 'Ошибка'
        CANCELLED = 'cancelled', 'Отменена'

    sender_account = models.ForeignKey(
        'banking.Account',
        on_delete=models.PROTECT,
        related_name='sent_transactions',
        null=True,
        blank=True,
    )
    receiver_account = models.ForeignKey(
        'banking.Account',
        on_delete=models.PROTECT,
        related_name='received_transactions',
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
    )
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = 'транзакция'
        verbose_name_plural = 'транзакции'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_transaction_type_display()} — {self.amount} ({self.status})'


class PaymentTemplate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_templates'
    )
    name = models.CharField(max_length=100, verbose_name="Название шаблона")
    category = models.CharField(max_length=50, verbose_name="Категория") 
    service_provider = models.CharField(max_length=100, verbose_name="Провайдер")
    requisite = models.CharField(max_length=50, verbose_name="Реквизит")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'шаблон платежа'
        verbose_name_plural = 'шаблоны платежей'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.service_provider})"

