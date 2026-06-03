import logging
import requests
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
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
            ExchangeRate.objects.create(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=Decimal(str(rate_value)),
                updated_at=timezone.now()
            )
        
        logger.info("Курсы валют успешно обновлены")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")


def get_latest_rates():
    rates = {}
    # Get one latest entry for each target currency
    seen_currencies = set()
    for exchange_rate in ExchangeRate.objects.filter(base_currency='USD'):
        if exchange_rate.target_currency not in seen_currencies:
            rates[exchange_rate.target_currency] = {
                'rate': float(exchange_rate.rate),
                'updated_at': exchange_rate.updated_at
            }
            seen_currencies.add(exchange_rate.target_currency)
    
    return rates


def get_rates_last_7_days(target_currency):
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)
    
    # Get one entry per day for the last 7 days
    rates = []
    labels = []
    
    for i in range(7):
        current_date = week_ago + timedelta(days=i)
        # Get rates for that date
        day_rates = ExchangeRate.objects.filter(
            base_currency='USD',
            target_currency=target_currency,
            updated_at__date=current_date
        ).order_by('updated_at')
        
        if day_rates.exists():
            rates.append(float(day_rates.first().rate))
        else:
            # If no rate for that day, use previous rate if available
            if rates:
                rates.append(rates[-1])
            else:
                rates.append(0)
        
        labels.append(current_date.strftime('%d.%m'))
    
    return labels, rates


def get_rate_change(target_currency):
    """Get current rate and compare with yesterdays rate, return 'up', 'down', or 'same'"""
    latest = ExchangeRate.objects.filter(
        base_currency='USD',
        target_currency=target_currency
    ).order_by('-updated_at').first()
    
    yesterday = timezone.now().date() - timedelta(days=1)
    yesterday_rate = ExchangeRate.objects.filter(
        base_currency='USD',
        target_currency=target_currency,
        updated_at__date=yesterday
    ).order_by('-updated_at').first()
    
    if not latest:
        return None, None
    
    if not yesterday_rate:
        return 'same', float(latest.rate)
    
    latest_value = float(latest.rate)
    yesterday_value = float(yesterday_rate.rate)
    
    if latest_value > yesterday_value:
        return 'up', latest_value
    elif latest_value < yesterday_value:
        return 'down', latest_value
    else:
        return 'same', latest_value
