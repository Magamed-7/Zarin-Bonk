import logging
import requests
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import ExchangeRate, Account

logger = logging.getLogger(__name__)

# Fallback rates if API doesn't provide them
FALLBACK_RATES = {
    "TJS": 10.95,
    "RUB": 92.50,
    "USD": 1.0,
}


def fetch_rates():
    try:
        response = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": "USD"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        base_currency = data["base"]
        rates = data["rates"]

        # Merge with fallback rates
        all_rates = {**rates, **FALLBACK_RATES}

        for target_currency, rate_value in all_rates.items():
            ExchangeRate.objects.create(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=Decimal(str(rate_value)),
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
    for exchange_rate in ExchangeRate.objects.filter(base_currency="USD").order_by(
        "-updated_at"
    ):
        if exchange_rate.target_currency not in seen_currencies:
            rates[exchange_rate.target_currency] = {
                "rate": float(exchange_rate.rate),
                "updated_at": exchange_rate.updated_at,
            }
            seen_currencies.add(exchange_rate.target_currency)

    # Add fallback rates if missing
    for currency, rate in FALLBACK_RATES.items():
        if currency not in rates:
            rates[currency] = {
                "rate": rate,
                "updated_at": timezone.now(),
            }

    return rates


def get_rates_last_7_days(target_currency):
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    # Get one entry per day for the last 7 days
    rates = []
    labels = []

    for i in range(7):
        current_date = week_ago + timedelta(days=i)
        labels.append(current_date.strftime("%d.%m"))

        # Get rates for that date
        day_rates = ExchangeRate.objects.filter(
            base_currency="USD",
            target_currency=target_currency,
            updated_at__date=current_date,
        ).order_by("updated_at")

        if day_rates.exists():
            rates.append(float(day_rates.first().rate))
        else:
            # If no rate for that day, use previous or fallback
            if rates:
                rates.append(rates[-1])
            else:
                rates.append(FALLBACK_RATES.get(target_currency, 1.0))

    return labels, rates


def get_rate_change(target_currency):
    latest = ExchangeRate.objects.filter(
        base_currency="USD", target_currency=target_currency
    ).order_by("-updated_at").first()

    yesterday = timezone.now().date() - timedelta(days=1)
    yesterday_rate = ExchangeRate.objects.filter(
        base_currency="USD", target_currency=target_currency, updated_at__date=yesterday
    ).order_by("-updated_at").first()

    if not latest:
        return None, FALLBACK_RATES.get(target_currency, 1.0)

    if not yesterday_rate:
        return "same", float(latest.rate)

    latest_val = float(latest.rate)
    yesterday_val = float(yesterday_rate.rate)

    if latest_val > yesterday_val:
        return "up", latest_val
    elif latest_val < yesterday_val:
        return "down", latest_val
    else:
        return "same", latest_val


def check_and_update_rates():
    latest_rate = ExchangeRate.objects.order_by("-updated_at").first()

    if not latest_rate:
        fetch_rates()
        return

    time_diff = timezone.now() - latest_rate.updated_at
    if time_diff > timedelta(hours=6):
        fetch_rates()
