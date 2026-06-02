from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SupportTicket
from notifications.models import Notification


@receiver(post_save, sender=SupportTicket)
def create_ticket_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            title='Тикет в поддержке создан!',
            message=f'Ваш тикет "{instance.subject}" был создан.',
            notification_type=Notification.NotificationType.SYSTEM
        )
