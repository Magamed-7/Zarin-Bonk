from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Loan, LoanPayment
from notifications.models import Notification


@receiver(post_save, sender=Loan)
def create_loan_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            title='Заявка на кредит подана',
            message=f'Ваша заявка на кредит на сумму {instance.amount} TJS подана и ждёт рассмотрения.',
            notification_type=Notification.NotificationType.LOAN
        )
    else:
        if instance.status == Loan.Status.APPROVED:
            Notification.objects.create(
                user=instance.user,
                title='Кредит одобрен!',
                message=f'Ваш кредит на сумму {instance.amount} TJS одобрен. Поздравляем!',
                notification_type=Notification.NotificationType.LOAN
            )
            if instance.user.email:
                try:
                    send_mail(
                        'Кредит одобрен — ZarinPay',
                        f'Ваш кредит на сумму {instance.amount} TJS одобрен.',
                        settings.DEFAULT_FROM_EMAIL,
                        [instance.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
        elif instance.status == Loan.Status.REJECTED:
            Notification.objects.create(
                user=instance.user,
                title='Заявка на кредит отклонена',
                message=f'К сожалению, ваша заявка на кредит на сумму {instance.amount} TJS отклонена.',
                notification_type=Notification.NotificationType.LOAN
            )
            if instance.user.email:
                try:
                    send_mail(
                        'Заявка на кредит отклонена — ZarinPay',
                        f'К сожалению, ваша заявка на кредит на сумму {instance.amount} TJS отклонена.',
                        settings.DEFAULT_FROM_EMAIL,
                        [instance.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass


@receiver(post_save, sender=LoanPayment)
def create_loan_payment_notification(sender, instance, created, **kwargs):
    if instance.is_paid:
        Notification.objects.create(
            user=instance.loan.user,
            title='Платёж по кредиту выполнен',
            message=f'Платёж по кредиту на сумму {instance.amount} TJS выполнен.',
            notification_type=Notification.NotificationType.LOAN
        )
        if instance.loan.user.email:
            try:
                send_mail(
                    'Платёж по кредиту выполнен — ZarinPay',
                    f'Платёж по кредиту на сумму {instance.amount} TJS выполнен.',
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.loan.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
