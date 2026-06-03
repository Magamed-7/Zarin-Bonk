from django.core.management.base import BaseCommand
from accounts.models import User
from accounts.services import calculate_score


class Command(BaseCommand):
    help = 'Updates financial scores for all users'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            score, level, details = calculate_score(user)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Рейтинг обновлён: {user.username} → {score} ({level.label})'
                )
            )
