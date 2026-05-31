from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from notifications.models import Notification
from .models import Loan

LOAN_PROGRAMS = {
    'consumer': {
        'id': 'consumer',
        'name': 'Потребительский кредит',
        'rate': 15.0,
        'min_amount': 1000,
        'max_amount': 50000,
        'min_term': 3,
        'max_term': 36,
        'icon': '🛍️'
    },
    'auto': {
        'id': 'auto',
        'name': 'Автокредит',
        'rate': 12.0,
        'min_amount': 10000,
        'max_amount': 150000,
        'min_term': 12,
        'max_term': 60,
        'icon': '🚗'
    },
    'mortgage': {
        'id': 'mortgage',
        'name': 'Ипотека',
        'rate': 8.0,
        'min_amount': 50000,
        'max_amount': 500000,
        'min_term': 24,
        'max_term': 240,
        'icon': '🏠'
    },
}

@login_required
def loans_view(request):
    if request.method == 'POST':
        program_id = request.POST.get('program')
        amount_str = request.POST.get('amount')
        term_str = request.POST.get('term')
        purpose = request.POST.get('purpose', '').strip()

        if program_id not in LOAN_PROGRAMS:
            messages.error(request, 'Некорректная кредитная программа.')
            return redirect('loans:loans_page')

        program = LOAN_PROGRAMS[program_id]

        try:
            amount = Decimal(amount_str)
            term = int(term_str)
        except (ValueError, TypeError):
            messages.error(request, 'Некорректные параметры кредита.')
            return redirect('loans:loans_page')

        if not (program['min_amount'] <= amount <= program['max_amount']):
            messages.error(request, f"Сумма для программы {program['name']} должна быть в пределах от {program['min_amount']} до {program['max_amount']} TJS.")
            return redirect('loans:loans_page')

        if not (program['min_term'] <= term <= program['max_term']):
            messages.error(request, f"Срок для программы {program['name']} должен быть в пределах от {program['min_term']} до {program['max_term']} месяцев.")
            return redirect('loans:loans_page')

        # Create Loan Application (status is pending by default)
        loan = Loan.objects.create(
            user=request.user,
            amount=amount,
            term_months=term,
            interest_rate=Decimal(str(program['rate'])),
            status=Loan.Status.PENDING,
            manager_comment=f"Программа: {program['name']}. Цель кредита: {purpose}"
        )

        # Notify the user
        Notification.objects.create(
            user=request.user,
            title='Заявка на кредит принята',
            message=f"Ваша заявка на кредит '{program['name']}' на сумму {amount} TJS на срок {term} мес. находится на рассмотрении.",
            notification_type=Notification.NotificationType.LOAN,
        )

        messages.success(request, 'Заявка на кредит успешно отправлена на рассмотрение менеджеру!')
        return redirect('loans:loans_page')

    user_loans = Loan.objects.filter(user=request.user)
    return render(request, 'loans/loans.html', {
        'programs': LOAN_PROGRAMS.values(),
        'loans': user_loans,
    })
