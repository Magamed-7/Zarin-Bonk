from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Goal
from notifications.models import Notification


@receiver(post_save, sender=Goal)
def create_goal_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            title='Цель накопления создана',
            message=f'Вы создали цель "{instance.title}" на сумму {instance.target_amount} TJS.',
            notification_type=Notification.NotificationType.SYSTEM
        )
    else:
        if instance.is_completed:
            # Проверим, не было ли уведомления уже
            existing_notification = Notification.objects.filter(
                user=instance.user,
                title='Цель достигнута!',
                message__contains=instance.title
            ).exists()
            
            if not existing_notification:
                Notification.objects.create(
                    user=instance.user,
                    title='Цель достигнута!',
                    message=f'Поздравляем! Вы достигли цели "{instance.title}"!',
                    notification_type=Notification.NotificationType.SYSTEM
                )
                if instance.user.email:
                    try:
                        send_mail(
                            'Цель накопления достигнута! — ZarinPay',
                            f'Поздравляем! Вы достигли цели "{instance.title}"!',
                            settings.DEFAULT_FROM_EMAIL,
                            [instance.user.email],
                            fail_silently=True,
                        )
                    except Exception:
                        pass
