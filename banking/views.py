from datetime import date, timedelta
import json

from dateutil.relativedelta import relativedelta
 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
 
from transactions.models import Transaction
from .models import Account, Card
from .forms import TopUpForm
from .services import get_rates
from .constants import EXCHANGE_RATES
from .forms import CurrencyConvertForm
from django.http import JsonResponse
from .forms import TransferForm
import requests
from notifications.models import Notification


@login_required
def dashboard_view(request):
    account = Account.objects.filter(user=request.user, is_active=True).first()

    card = None
    if account:
        card = Card.objects.filter(account=account).first()

    recent_transactions = []
    if account:
        recent_transactions = Transaction.objects.filter(
            sender_account=account
        ) | Transaction.objects.filter(
            receiver_account=account
        )
        recent_transactions = recent_transactions.order_by('-created_at')[:5]

    today       = timezone.now().date()
    week_labels = []
    week_data   = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        week_labels.append(day.strftime('%d.%m'))

        if account:
            spent = Transaction.objects.filter(
                sender_account=account,
                status='completed',
                created_at__date=day,
            ).aggregate(total=Sum('amount'))['total'] or 0
        else:
            spent = 0

        week_data.append(float(spent))

    return render(request, 'banking/dashboard.html', {
        'account':             account,
        'card':                card,
        'recent_transactions': recent_transactions,
        'week_labels':         week_labels,
        'week_data':           week_data,
    })



@login_required
def accounts_view(request):
    accounts = Account.objects.filter(user=request.user).order_by('-created_at')
 
    total_balance = accounts.filter(
        currency=Account.Currency.TJS
    ).aggregate(total=Sum('balance'))['total'] or 0
 
    return render(request, 'banking/accounts.html', {
        'accounts':      accounts,
        'total_balance': total_balance,
    })
 
 
@login_required
def create_account_view(request):
    if request.method == 'POST':
        account_type = request.POST.get('account_type', '').strip()
        currency     = request.POST.get('currency', '').strip()
 
        valid_types     = [t[0] for t in Account.AccountType.choices]
        valid_currencies = [c[0] for c in Account.Currency.choices]
 
        if account_type not in valid_types:
            messages.error(request, 'Выберите корректный тип счёта.')
        elif currency not in valid_currencies:
            messages.error(request, 'Выберите корректную валюту.')
        else:
            account = Account.objects.create(
                user=request.user,
                account_type=account_type,
                currency=currency,
            )
 
            Card.objects.create(
                account=account,
                expiry_date=date.today() + relativedelta(years=3),
                card_type=Card.CardType.VIRTUAL,
            )
 
            messages.success(request, f'Счёт {account.account_number} успешно создан.')
            return redirect('banking:accounts')
 
    return render(request, 'banking/create_account.html', {
        'account_types': Account.AccountType.choices,
        'currencies':    Account.Currency.choices,
    })



@login_required
def account_detail_view(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user)
 
    cards = Card.objects.filter(account=account)
 
    sent     = Transaction.objects.filter(sender_account=account)
    received = Transaction.objects.filter(receiver_account=account)
    transactions = (sent | received).order_by('-created_at')[:10]
 
    today      = timezone.now().date()
    start_date = today - timedelta(days=29)
 
    sent_30     = Transaction.objects.filter(
        sender_account=account,
        status=Transaction.Status.COMPLETED,
        created_at__date__gte=start_date,
    )
    received_30 = Transaction.objects.filter(
        receiver_account=account,
        status=Transaction.Status.COMPLETED,
        created_at__date__gte=start_date,
    )
 
    total_received = received_30.aggregate(t=Sum('amount'))['t'] or 0
    total_sent     = sent_30.aggregate(t=Sum('amount'))['t'] or 0
    balance_30_days_ago = float(account.balance) - float(total_received) + float(total_sent)
 
    balance_labels = []
    balance_data   = []
    running_balance = balance_30_days_ago
 
    for i in range(30):
        day = start_date + timedelta(days=i)
        balance_labels.append(day.strftime('%d.%m'))
 
        day_received = received_30.filter(
            created_at__date=day
        ).aggregate(t=Sum('amount'))['t'] or 0
 
        day_sent = sent_30.filter(
            created_at__date=day
        ).aggregate(t=Sum('amount'))['t'] or 0
 
        running_balance += float(day_received) - float(day_sent)
        balance_data.append(round(running_balance, 2))
 
    return render(request, 'banking/account_detail.html', {
        'account':      account,
        'cards':        cards,
        'transactions': transactions,
        'balance_labels': json.dumps(balance_labels),
        'balance_data':   json.dumps(balance_data),
    })
 


@login_required
def toggle_card_freeze_view(request, card_id):
    if request.method != 'POST':
        return redirect('banking:dashboard')

    card = get_object_or_404(
        Card.objects.select_related('account'),
        id=card_id,
        account__user=request.user,
    )

    card.is_frozen = not card.is_frozen
    card.save(update_fields=['is_frozen'])

    return redirect('banking:dashboard')



@login_required
def topup_account_view(request):

    account = request.user.accounts.first()

    if not account:

        messages.error(
            request,
            'Счёт не найден'
        )

        return redirect(
            'banking:dashboard'
        )

    if request.method == 'POST':

        form = TopUpForm(
            request.POST
        )

        if form.is_valid():

            amount = form.cleaned_data[
                'amount'
            ]

            account.balance += amount

            account.save()

            messages.success(
                request,
                f'Счёт пополнен на {amount}'
            )

    return redirect(
        'banking:dashboard'
    )



@login_required
def currency_convert_view(request):

    converted = None
    rate = None

    form = CurrencyConvertForm(
        request.POST or None
    )

    if request.method == 'POST':

        if form.is_valid():

            amount = form.cleaned_data[
                'amount'
            ]

            source = form.cleaned_data[
                'from_currency'
            ]

            target = form.cleaned_data[
                'to_currency'
            ]

            url = (

                'https://api.exchangerate.host/convert'

                f'?from={source}'

                f'&to={target}'

                f'&amount={amount}'

            )

            response = requests.get(
                url,
                timeout=5
            )

            data = response.json()

            converted = round(

                data.get(
                    'result',
                    0
                ),

                2

            )

            rate = data.get(
                'info',
                {}
            ).get(
                'rate'
            )

    context = {

        'form':form,

        'converted':converted,

        'rate':rate,

    }

    return render(

        request,

        'banking/currency.html',

        context

    )




@login_required
def currency_rates_view(request):

    rates = get_rates()

    return render(

        request,

        'banking/rates.html',

        {

            'rates':rates

        }

    )


@login_required
def receiver_lookup_view(request):
    """
    AJAX: ищем счёт по номеру и возвращаем имя владельца.
    Используется JS-ом при вводе номера получателя.
    """
    number = request.GET.get('number', '').strip()
    account = Account.objects.filter(
        account_number=number
    ).select_related('user').first()
 
    if not account:
        return JsonResponse({'found': False})
 
    return JsonResponse({
        'found':    True,
        'name':     account.user.get_full_name() or account.user.username,
        'currency': account.currency,
    })


@login_required
def transfer_money_view(request):
    # Счета пользователя для кастомного селектора
    user_accounts = Account.objects.filter(user=request.user, is_active=True)
    form = TransferForm(request.POST or None, user=request.user)
 
    if request.method == 'POST' and form.is_valid():
        sender          = form.cleaned_data['sender_account']
        receiver_number = form.cleaned_data['receiver_number']
        amount          = form.cleaned_data['amount']
        description     = form.cleaned_data.get('description', '')
 
        receiver = Account.objects.filter(account_number=receiver_number).first()
 
        if not receiver:
            messages.error(request, 'Счёт получателя не найден.')
 
        elif sender == receiver:
            messages.error(request, 'Нельзя переводить на тот же счёт.')
 
        elif sender.balance < amount:
            messages.error(
                request,
                f'Недостаточно средств. Доступно: {sender.balance} {sender.currency}.'
            )
 
        else:
            # Двигаем деньги
            sender.balance   -= amount
            receiver.balance += amount
            sender.save()
            receiver.save()
 
            # Сохраняем запись о транзакции
            Transaction.objects.create(
                sender_account=sender,
                receiver_account=receiver,
                amount=amount,
                transaction_type=Transaction.TransactionType.TRANSFER,
                status=Transaction.Status.COMPLETED,
                description=description or f'Перевод на счёт {receiver_number}',
            )
 
            # Уведомляем отправителя
            Notification.objects.create(
                user=sender.user,
                title='Перевод выполнен',
                message=(
                    f'Перевод {amount} {sender.currency} '
                    f'на счёт {receiver_number} выполнен успешно.'
                ),
                notification_type=Notification.NotificationType.TRANSACTION,
            )
 
            # Уведомляем получателя
            Notification.objects.create(
                user=receiver.user,
                title='Входящий перевод',
                message=(
                    f'Получен перевод {amount} {sender.currency} '
                    f'от {sender.user.get_full_name() or sender.user.username}.'
                ),
                notification_type=Notification.NotificationType.TRANSACTION,
            )
 
            messages.success(
                request,
                f'Перевод {amount} {sender.currency} выполнен!'
            )
            return redirect('banking:transfer')
 
    return render(request, 'banking/transfer.html', {
        'form':          form,
        'user_accounts': user_accounts,
    })
 
