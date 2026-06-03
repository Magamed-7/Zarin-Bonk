import logging
import requests
from decimal import Decimal
from django.utils import timezone
from .models import ExchangeRate, Account

logger = logging.getLogger(__name__)


def fetch_rates():
    try:
        response = requests.get(
            'https://api.frankfurter.app/latest',
            params={
                'from': 'USD',
                'to': 'TJS,EUR,RUB'
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        base_currency = data['base']
        rates = data['rates']
        
        for target_currency, rate_value in rates.items():
            ExchangeRate.objects.update_or_create(
                base_currency=base_currency,
                target_currency=target_currency,
                defaults={
                    'rate': Decimal(str(rate_value)),
                    'updated_at': timezone.now()
                }
            )
        
        logger.info("Курсы валют успешно обновлены")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")


def get_latest_rates():
    rates = {}
    
    for exchange_rate in ExchangeRate.objects.filter(base_currency='USD').order_by('-updated_at'):
        rates[exchange_rate.target_currency] = float(exchange_rate.rate)
    
    return rates
