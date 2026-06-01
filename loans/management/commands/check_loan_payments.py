from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from loans.models import Loan, LoanPayment
from banking.models import Account
from transactions.models import Transaction
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Проверяет платежи по кредитам и выполняет автосписание или помечает просроченными'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        payments_today = LoanPayment.objects.filter(
            due_date=today,
            is_paid=False
        )
        
        self.stdout.write(f'Найдено платежей на сегодня: {payments_today.count()}')
        
        for payment in payments_today:
            loan = payment.loan
            
          
            if loan.status != Loan.Status.ACTIVE:
                self.stdout.write(f'Кредит #{loan.id} не активен, пропускаем')
                continue
            
            account = Account.objects.filter(
                user=loan.user,
                is_active=True
            ).first()
            
            if not account:
                self.stdout.write(f'У пользователя {loan.user} нет активного счёта')
                # Помечаем как просроченный
                self.mark_as_overdue(payment)
                continue
            
         
            total_amount = payment.amount + payment.penalty_amount
            
            if account.balance >= total_amount:
                # Списываем деньги
                self.process_payment(payment, account, total_amount)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Платёж {payment.amount} TJS по кредиту #{loan.id} успешно списан'
                    )
                )
            else:
                # Недостаточно средств - помечаем как просроченный
                self.mark_as_overdue(payment)
                self.stdout.write(
                    self.style.WARNING(
                        f'Недостаточно средств для платежа {payment.amount} TJS по кредиту #{loan.id}. Помечен как просроченный'
                    )
                )
        
        # Проверяем просроченные платежи (старше 1 дня)
        overdue_payments = LoanPayment.objects.filter(
            due_date__lt=today,
            is_paid=False,
            is_overdue=False
        )
        
        self.stdout.write(f'Найдено новых просроченных платежей: {overdue_payments.count()}')
        
        for payment in overdue_payments:
            self.mark_as_overdue(payment)
            self.stdout.write(
                self.style.WARNING(
                    f'Платёж {payment.amount} TJS от {payment.due_date} помечен как просроченный'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Проверка платежей завершена'))
    
    def process_payment(self, payment, account, amount):
        with transaction.atomic():
            # Списываем деньги со счёта
            account.balance -= amount
            account.save()
            
            # Помечаем платёж как оплаченный
            payment.is_paid = True
            payment.paid_date = timezone.now().date()
            payment.save()
            
            # Создаём транзакцию
            Transaction.objects.create(
                sender_account=account,
                receiver_account=None,
                amount=amount,
                transaction_type=Transaction.TransactionType.PAYMENT,
                status=Transaction.Status.COMPLETED,
                category='loans',
                description=f"Автоматический платёж по кредиту #{payment.loan.id}"
            )
            
            # Отправляем уведомление
            Notification.objects.create(
                user=payment.loan.user,
                title='Автоматический платёж по кредиту',
                message=f'С вашего счёта списано {amount} TJS в счёт погашения кредита #{payment.loan.id}',
                notification_type=Notification.NotificationType.LOAN,
            )
            
            # Проверяем, все ли платежи оплачены
            remaining_payments = payment.loan.payments.filter(is_paid=False).count()
            if remaining_payments == 0:
                payment.loan.status = Loan.Status.CLOSED
                payment.loan.save()
                
                Notification.objects.create(
                    user=payment.loan.user,
                    title='Кредит полностью погашен',
                    message=f'Поздравляем! Кредит #{payment.loan.id} полностью погашен',
                    notification_type=Notification.NotificationType.LOAN,
                )
    
    def mark_as_overdue(self, payment):
        with transaction.atomic():
            payment.is_overdue = True
            
            penalty = payment.amount * Decimal('0.05')
            payment.penalty_amount = penalty
            payment.save()
            
            # Отправляем уведомление
            Notification.objects.create(
                user=payment.loan.user,
                title='Просрочка платежа по кредиту',
                message=f'Платёж {payment.amount} TJS по кредиту #{payment.loan.id} просрочен. Начислен штраф: {penalty} TJS',
                notification_type=Notification.NotificationType.LOAN,
            )
