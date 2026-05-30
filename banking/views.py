from datetime import date, timedelta
 
from dateutil.relativedelta import relativedelta
 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
 
from transactions.models import Transaction
from .models import Account, Card


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