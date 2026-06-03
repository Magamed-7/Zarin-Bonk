from datetime import date, timedelta
import json

from dateutil.relativedelta import relativedelta
 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views import generic
from decimal import Decimal
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
 
from transactions.models import Transaction
from .models import Account, Card
from .forms import TopUpForm
from .currency_service import (
    get_latest_rates,
    get_rates_last_7_days,
    get_rate_change,
    check_and_update_rates
)
from .forms import CurrencyConvertForm
from django.http import JsonResponse
from .forms import TransferForm
import requests
from notifications.models import Notification


@login_required
def dashboard_view(request):
    account = Account.objects.filter(user=request.user, is_active=True, is_deleted=False).first()

    card = None
    if account:
        card = Card.objects.filter(account=account, is_deleted=False).first()

    recent_transactions = []
    if account:
        recent_transactions = Transaction.objects.filter(
            sender_account=account, is_deleted=False
        ) | Transaction.objects.filter(
            receiver_account=account, is_deleted=False
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
                is_deleted=False,
            ).aggregate(total=Sum('amount'))['total'] or 0
        else:
            spent = 0

        week_data.append(float(spent))

    return render(request, 'banking/dashboard.html', {
        'account':             account,
        'card':                card,
        'recent_transactions': recent_transactions,
        'week_labels':         json.dumps(week_labels),
        'week_data':           json.dumps(week_data),
    })



class AccountsListView(LoginRequiredMixin, generic.ListView):
    model = Account
    template_name = 'banking/accounts.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_deleted=False).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = self.get_queryset()
        total_balance = accounts.filter(
            currency=Account.Currency.TJS
        ).aggregate(total=Sum('balance'))['total'] or 0
        context['total_balance'] = total_balance
        return context


 

class CreateAccountView(LoginRequiredMixin, generic.CreateView):
    model = Account
    template_name = 'banking/create_account.html'
    fields = ['account_type', 'currency']
    
    def form_valid(self, form):
        account = form.save(commit=False)
        account.user = self.request.user
        account.save()
        
        Card.objects.create(
            account=account,
            expiry_date=date.today() + relativedelta(years=3),
            card_type=Card.CardType.VIRTUAL,
        )
        
        messages.success(self.request, f'Счёт {account.account_number} успешно создан.')
        return redirect('banking:accounts')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account_types'] = Account.AccountType.choices
        context['currencies'] = Account.Currency.choices
        return context




@login_required
def account_detail_view(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user, is_deleted=False)
 
    cards = Card.objects.filter(account=account, is_deleted=False)
 
    sent     = Transaction.objects.filter(sender_account=account, is_deleted=False)
    received = Transaction.objects.filter(receiver_account=account, is_deleted=False)
    transactions = (sent | received).order_by('-created_at')[:10]
 
    today      = timezone.now().date()
    start_date = today - timedelta(days=29)
 
    sent_30     = Transaction.objects.filter(
        sender_account=account,
        status=Transaction.Status.COMPLETED,
        created_at__date__gte=start_date,
        is_deleted=False,
    )
    received_30 = Transaction.objects.filter(
        receiver_account=account,
        status=Transaction.Status.COMPLETED,
        created_at__date__gte=start_date,
        is_deleted=False,
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
    check_and_update_rates()
    converted = None
    rate = None
    latest_rates = get_latest_rates()

    form = CurrencyConvertForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            amount = form.cleaned_data['amount']
            source = form.cleaned_data['from_currency']
            target = form.cleaned_data['to_currency']

            # Calculate rate
            if source == target:
                rate = 1.0
            else:
                usd_to_source = Decimal(str(latest_rates.get(source, 1.0))) if source != 'USD' else Decimal('1.0')
                usd_to_target = Decimal(str(latest_rates.get(target, 1.0))) if target != 'USD' else Decimal('1.0')
                rate = (usd_to_target / usd_to_source).quantize(Decimal('0.0004'))

            converted = convert_currency(amount, source, target, latest_rates)

    context = {
        'form': form,
        'converted': converted,
        'rate': rate,
    }

    return render(request, 'banking/currency.html', context)




@login_required
def delete_card_view(request, card_id):
    card = get_object_or_404(Card, id=card_id, account__user=request.user, is_deleted=False)
    card.delete()
    messages.success(request, f'Карта {card.masked_number} удалена.')
    return redirect('banking:account_detail', account_id=card.account.id)


@login_required
def delete_account_view(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user, is_deleted=False)
    
    if account.balance < 0:
        messages.error(request, 'Нельзя удалить счёт с отрицательным балансом.')
        return redirect('banking:account_detail', account_id=account.id)
    
    
    
    account.delete()
    messages.success(request, f'Счёт {account.account_number} удалён. Все средства на счёте обнулены.')
    return redirect('banking:accounts')


@login_required
def rates_view(request):
    check_and_update_rates()
    latest_rates = get_latest_rates()
    currency_info = [
        ('USD', '🇺🇸'),
        ('EUR', '🇪🇺'),
        ('RUB', '🇷🇺'),
        ('TJS', '🇹🇯'),
        ('GBP', '🇬🇧'),
        ('CNY', '🇨🇳'),
        ('JPY', '🇯🇵'),
        ('AUD', '🇦🇺'),
        ('CAD', '🇨🇦'),
        ('CHF', '🇨🇭'),
        ('TRY', '🇹🇷'),
        ('BRL', '🇧🇷'),
        ('INR', '🇮🇳'),
        ('KRW', '🇰🇷'),
    ]
    
    rates_data = []
    rates_for_js = {}
    for currency_code, flag in currency_info:
        if currency_code in latest_rates:
            rate_data = latest_rates[currency_code]
            change, _ = get_rate_change(currency_code)
            labels, chart_data = get_rates_last_7_days(currency_code)
            rates_data.append({
                'code': currency_code,
                'flag': flag,
                'rate': rate_data['rate'],
                'updated_at': rate_data['updated_at'],
                'change': change,
                'chart_labels': json.dumps(labels),
                'chart_data': json.dumps(chart_data),
            })
            rates_for_js[currency_code] = rate_data['rate']
    # Add USD as 1.0 for JS
    rates_for_js['USD'] = 1.0
    
    return render(
        request,
        'banking/rates.html',
        {
            'rates_data': rates_data,
            'rates_for_js': rates_for_js,
        }
    )


@login_required
def receiver_lookup_view(request):
    number = request.GET.get('number', '').strip()
    account = Account.objects.filter(
        account_number=number,
        is_deleted=False
    ).select_related('user').first()

    if not account:
        return JsonResponse({'found': False})

    return JsonResponse({
        'found':    True,
        'name':     account.user.get_full_name() or account.user.username,
        'currency': account.currency,
    })


def api_rates_view(request):
    check_and_update_rates()
    latest_rates = get_latest_rates()
    rates_dict = {'USD': 1.0}
    for currency_code, data in latest_rates.items():
        rates_dict[currency_code] = data['rate']
    return JsonResponse(rates_dict)


def convert_currency(amount, from_currency, to_currency, rates=None):
    if from_currency == to_currency:
        return amount

    if rates is None:
        rates = get_latest_rates()

    # Get rates relative to USD
    usd_to_from = Decimal(str(rates.get(from_currency, 1.0))) if from_currency != 'USD' else Decimal('1.0')
    usd_to_to = Decimal(str(rates.get(to_currency, 1.0))) if to_currency != 'USD' else Decimal('1.0')

    # Convert amount to USD, then to target
    amount_in_usd = amount / usd_to_from if from_currency != 'USD' else amount
    converted_amount = amount_in_usd * usd_to_to if to_currency != 'USD' else amount_in_usd

    return converted_amount.quantize(Decimal('0.01'))
 
 
 
@login_required
def transfer_money_view(request):
    user_accounts = Account.objects.filter(user=request.user, is_active=True, is_deleted=False)
    initial_data = {}
    if request.method == 'GET':
        initial_data = {
            'sender_account': request.GET.get('sender_account'),
            'receiver_number': request.GET.get('receiver_number'),
            'amount': request.GET.get('amount'),
            'description': request.GET.get('description'),
        }
    form = TransferForm(request.POST or None, initial=initial_data, user=request.user)
 
    if request.method == 'POST' and form.is_valid():
        sender          = form.cleaned_data['sender_account']
        receiver_number = form.cleaned_data['receiver_number']
        amount          = form.cleaned_data['amount']
        description     = form.cleaned_data.get('description', '')
 
        receiver = Account.objects.filter(account_number=receiver_number, is_deleted=False).first()
 
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
            received_amount = convert_currency(
                amount,
                from_currency=sender.currency,
                to_currency=receiver.currency,
            )
 
            
            sender.balance   -= amount           
            receiver.balance += received_amount  
            sender.save()
            receiver.save()
 
            # Сохраняем транзакцию
            Transaction.objects.create(
                sender_account=sender,
                receiver_account=receiver,
                amount=amount,
                transaction_type=Transaction.TransactionType.TRANSFER,
                status=Transaction.Status.COMPLETED,
                description=description or (
                    f'Перевод на счёт {receiver_number}'
                    + (
                        f' (конвертация: {amount} {sender.currency} → '
                        f'{received_amount} {receiver.currency})'
                        if sender.currency != receiver.currency else ''
                    )
                ),
            )
 
            # Уведомляем отправителя
            Notification.objects.create(
                user=sender.user,
                title='Перевод выполнен',
                message=(
                    f'Списано {amount} {sender.currency}. '
                    f'Получатель получил {received_amount} {receiver.currency}.'
                ),
                notification_type=Notification.NotificationType.TRANSACTION,
            )
 
            # Уведомляем получателя
            Notification.objects.create(
                user=receiver.user,
                title='Входящий перевод',
                message=(
                    f'Зачислено {received_amount} {receiver.currency} '
                    f'от {sender.user.get_full_name() or sender.user.username}.'
                ),
                notification_type=Notification.NotificationType.TRANSACTION,
            )
 
            messages.success(
                request,
                f'Перевод выполнен! Списано {amount} {sender.currency}, '
                f'зачислено {received_amount} {receiver.currency}.'
            )
            return redirect('banking:transfer')
 
    return render(request, 'banking/transfer.html', {
        'form':          form,
        'user_accounts': user_accounts,
    })