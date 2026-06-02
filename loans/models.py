from decimal import Decimal

from django.conf import settings
from django.db import models


class LoanProgram(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название программы')
    description = models.TextField(blank=True, verbose_name='Описание')
    min_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1000.00'),
        verbose_name='Минимальная сумма'
    )
    max_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1000000.00'),
        verbose_name='Максимальная сумма'
    )
    min_term = models.PositiveIntegerField(
        default=3,
        verbose_name='Минимальный срок (месяцев)'
    )
    max_term = models.PositiveIntegerField(
        default=60,
        verbose_name='Максимальный срок (месяцев)'
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00'),
        verbose_name='Процентная ставка (%)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'кредитная программа'
        verbose_name_plural = 'кредитные программы'
        ordering = ['-is_active', 'name']

    def __str__(self):
        return self.name


class Loan(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'На рассмотрении'
        APPROVED = 'approved', 'Одобрен'
        REJECTED = 'rejected', 'Отклонён'
        ACTIVE = 'active', 'Активен'
        CLOSED = 'closed', 'Закрыт'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loans',
    )
    program = models.ForeignKey(
        LoanProgram,
        on_delete=models.PROTECT,
        related_name='loans',
        null=True,
        blank=True,
        help_text='Кредитная программа'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    term_months = models.PositiveIntegerField()
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Годовая процентная ставка, %',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    monthly_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    manager_comment = models.TextField(blank=True)
    credit_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Кредитный рейтинг клиента (0-100)',
    )
    credit_score_explanation = models.TextField(
        blank=True,
        help_text='Объяснение кредитного рейтинга от ИИ',
    )

    class Meta:
        verbose_name = 'кредит'
        verbose_name_plural = 'кредиты'
        ordering = ['-created_at']

    def __str__(self):
        return f'Кредит #{self.pk} — {self.user} ({self.get_status_display()})'

    def calculate_monthly_payment(self):
        if self.interest_rate == 0:
            return (self.amount / self.term_months).quantize(Decimal('0.01'))

        r = self.interest_rate / Decimal('12') / Decimal('100')
        n = self.term_months
        factor = (1 + r) ** n
        payment = self.amount * r * factor / (factor - 1)
        return payment.quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        if not self.monthly_payment or self.monthly_payment == Decimal('0.00'):
            self.monthly_payment = self.calculate_monthly_payment()
        super().save(*args, **kwargs)


class LoanPayment(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    is_overdue = models.BooleanField(default=False)
    penalty_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Штраф за просрочку',
    )

    class Meta:
        verbose_name = 'платёж по кредиту'
        verbose_name_plural = 'платежи по кредиту'
        ordering = ['due_date']

    def __str__(self):
        status = 'оплачен' if self.is_paid else 'просрочен' if self.is_overdue else 'не оплачен'
        return f'Платёж {self.amount} — {self.due_date} ({status})'