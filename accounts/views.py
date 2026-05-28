from datetime import date
from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from banking.models import Account, Card
from .forms import RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('landing')  # TODO: заменить на 'banking:dashboard'

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()

            # Автоматически создаём расчётный счёт
            account = Account.objects.create(
                user=user,
                account_type=Account.AccountType.CHECKING,
                currency=Account.Currency.TJS,
            )

            # Автоматически создаём виртуальную карту (срок — 3 года)
            Card.objects.create(
                account=account,
                expiry_date=date.today() + relativedelta(years=3),
                card_type=Card.CardType.VIRTUAL,
            )

            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('landing')  # TODO: заменить на 'accounts:login'

    return render(request, 'accounts/register.html', {'form': form})