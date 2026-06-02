from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Transaction
from notifications.models import Notification


@receiver(post_save, sender=Transaction)
def create_transaction_notification(sender, instance, created, **kwargs):
    if instance.status == Transaction.Status.COMPLETED:
        # Уведомляем отправителя, если есть
        if instance.sender_account:
            notification_title = {
                Transaction.TransactionType.TRANSFER: 'Перевод выполнен',
                Transaction.TransactionType.PAYMENT: 'Платёж выполнен',
                Transaction.TransactionType.DEPOSIT: 'Счёт пополнен',
                Transaction.TransactionType.WITHDRAWAL: 'Средства сняты'
            }.get(instance.transaction_type, 'Транзакция выполнена')
            
            notification_msg = (
                f'{notification_title} на сумму {instance.amount} {instance.sender_account.currency}.'
                f'{" Категория: " + instance.category if instance.category else ""}'
                f'{" Описание: " + instance.description if instance.description else ""}'
            )
            
            Notification.objects.create(
                user=instance.sender_account.user,
                title=notification_title,
                message=notification_msg,
                notification_type=Notification.NotificationType.TRANSACTION
            )
            
            # Отправляем email
            if instance.sender_account.user.email:
                try:
                    send_mail(
                        subject=f'{notification_title} — ZarinPay',
                        message=notification_msg,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[instance.sender_account.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
        
        # Уведомляем получателя, если есть
        if instance.receiver_account and instance.sender_account != instance.receiver_account:
            notification_title = 'Пополнение счёта'
            notification_msg = (
                f'Ваш счёт пополнен на сумму {instance.amount} {instance.receiver_account.currency}.'
                f'{" Описание: " + instance.description if instance.description else ""}'
            )
            
            Notification.objects.create(
                user=instance.receiver_account.user,
                title=notification_title,
                message=notification_msg,
                notification_type=Notification.NotificationType.TRANSACTION
            )
            
            # Отправляем email
            if instance.receiver_account.user.email:
                try:
                    send_mail(
                        subject=f'{notification_title} — ZarinPay',
                        message=notification_msg,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[instance.receiver_account.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
