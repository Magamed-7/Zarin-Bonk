from django.core.management.base import BaseCommand
from banking.currency_service import fetch_rates, get_latest_rates


class Command(BaseCommand):
    help = 'Обновляет курсы валют из внешнего API'

    def handle(self, *args, **options):
        self.stdout.write('Обновление курсов валют...')
        fetch_rates()
        rates = get_latest_rates()
        if rates:
            for currency, data in rates.items():
                self.stdout.write(self.style.SUCCESS(f'Курсы обновлены: USD/{currency} = {data["rate"]:.4f}'))
        else:
            self.stdout.write(self.style.WARNING('Курсы не найдены'))
