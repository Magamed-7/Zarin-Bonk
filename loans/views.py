from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from banking.models import Account
from transactions.models import Transaction
from notifications.models import Notification
from ai_assistant.ai_service import AIService
from .models import Loan, LoanPayment

def run_credit_scoring(loan, user):
    """
    Run AI-powered credit scoring for the loan application
    """
    try:
        # Gather financial history data
        from django.db.models import Q, Sum
        
        user_accounts = Account.objects.filter(user=user, is_deleted=False)
        transactions = Transaction.objects.filter(
            Q(sender_account__in=user_accounts) | Q(receiver_account__in=user_accounts),
            is_deleted=False
        ).order_by('-created_at')[:100]
        
        user_loans = Loan.objects.filter(user=user)
        
        # Prepare context for AI
        context_parts = [
            f"Клиент: {user.first_name} {user.last_name}",
            f"Запрашиваемая сумма кредита: {loan.amount} TJS",
            f"Срок кредита: {loan.term_months} месяцев",
        ]
        
        total_balance = sum(acc.balance for acc in user_accounts)
        context_parts.append(f"Общий баланс на счетах: {total_balance} TJS")
        
        total_income = sum(
            tx.amount for tx in transactions
            if tx.receiver_account and tx.receiver_account in user_accounts
        )
        total_expense = sum(
            tx.amount for tx in transactions
            if tx.sender_account and tx.sender_account in user_accounts
        )
        context_parts.append(f"Общий доход за последние транзакции: {total_income} TJS")
        context_parts.append(f"Общие расходы за последние транзакции: {total_expense} TJS")
        
        # Loan history
        active_loans = user_loans.filter(status__in=['active', 'pending'])
        closed_loans = user_loans.filter(status='closed')
        rejected_loans = user_loans.filter(status='rejected')
        
        context_parts.append(f"Активные кредиты: {active_loans.count()}")
        context_parts.append(f"Закрытые кредиты: {closed_loans.count()}")
        context_parts.append(f"Отклоненные заявки: {rejected_loans.count()}")
        
        overdue_payments = LoanPayment.objects.filter(
            loan__user=user,
            is_paid=False,
            is_overdue=True
        ).count()
        context_parts.append(f"Просроченные платежи: {overdue_payments}")
        
        full_context = "\n".join(context_parts)
        
        system_prompt = """Ты кредитный аналитик банка ZarinPay. Оцени кредитоспособность клиента.
        
Ответь в следующем формате строго:
СКОРИНГ: [число от 0 до 100]
ОБЪЯСНЕНИЕ: [подробное объяснение, почему такой рейтинг]

Пример:
СКОРИНГ: 75
ОБЪЯСНЕНИЕ: У клиента стабильный доход, нет просроченных платежей, хорошая кредитная история. Рекомендуется одобрить заявку."""
        
        # Call AI service
        ai_service = AIService()
        ai_response = ai_service.get_ai_response(
            "Оцени кредитоспособность клиента.",
            full_context + "\n\n" + system_prompt
        )
        
        # Parse AI response
        score = None
        explanation = ""
        
        for line in ai_response.split('\n'):
            line = line.strip()
            if line.startswith('СКОРИНГ:'):
                try:
                    score = int(line.replace('СКОРИНГ:', '').strip())
                    # Clamp score between 0 and 100
                    score = max(0, min(100, score))
                except ValueError:
                    pass
            elif line.startswith('ОБЪЯСНЕНИЕ:'):
                explanation = line.replace('ОБЪЯСНЕНИЕ:', '').strip()
            elif explanation:
                explanation += " " + line
        
        # Fallback if parsing failed
        if score is None:
            score = 50
            explanation = "Не удалось получить точный анализ от ИИ. Средний рейтинг по умолчанию."
        
        # Save to loan
        loan.credit_score = score
        loan.credit_score_explanation = explanation
        loan.save()
        
    except Exception as e:
        # Fallback in case of any error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Credit scoring error: {e}")
        loan.credit_score = 50
        loan.credit_score_explanation = "Ошибка при анализе кредитоспособности. Средний рейтинг по умолчанию."
        loan.save()


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

        # Create Loan with pending status (waiting for manager approval)
        loan = Loan.objects.create(
            user=request.user,
            amount=amount,
            term_months=term,
            interest_rate=Decimal(str(program['rate'])),
            status=Loan.Status.PENDING,
            manager_comment=f"Программа: {program['name']}. Цель кредита: {purpose}"
        )
        
        # Run credit scoring
        run_credit_scoring(loan, request.user)

        # Notify the user
        Notification.objects.create(
            user=request.user,
            title='Заявка на кредит отправлена',
            message=f"Ваша заявка на кредит '{program['name']}' на сумму {amount} TJS отправлена на рассмотрение менеджеру.",
            notification_type=Notification.NotificationType.LOAN,
        )

        messages.success(request, f"Заявка на кредит '{program['name']}' на сумму {amount} TJS отправлена на рассмотрение!")
        return redirect('loans:loans_page')

    # GET request
    user_loans = Loan.objects.filter(user=request.user).prefetch_related('payments')
    
    # Calculate additional fields for template
    processed_loans = []
    for l in user_loans:
        all_payments = l.payments.all()
        total_count = all_payments.count()
        paid_payments = all_payments.filter(is_paid=True)
        paid_count = paid_payments.count()
        
        # Next payment
        next_pay = all_payments.filter(is_paid=False).first()
        
        # Calculate paid amount vs total amount
        total_paid_amount = sum(p.amount for p in paid_payments)
        total_loan_amount = sum(p.amount for p in all_payments)
        
        progress = int((paid_count / total_count * 100)) if total_count > 0 else 0
        
        processed_loans.append({
            'obj': l,
            'progress': progress,
            'next_payment': next_pay,
            'total_paid_amount': total_paid_amount,
            'total_loan_amount': total_loan_amount,
            'payments': all_payments
        })
        
    return render(request, 'loans/loans.html', {
        'programs': LOAN_PROGRAMS.values(),
        'loans': processed_loans,
    })

@login_required
def repay_loan_view(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user, status=Loan.Status.ACTIVE)
    unpaid_payments = loan.payments.filter(is_paid=False)
    
    if not unpaid_payments.exists():
        messages.error(request, 'Кредит уже полностью оплачен.')
        return redirect('loans:loans_page')
        
    total_repayment = sum(p.amount for p in unpaid_payments)
    
    # User's account to deduct balance
    account = Account.objects.filter(user=request.user, is_active=True).first()
    if not account:
        messages.error(request, 'У вас нет активного счета для совершения платежа.')
        return redirect('loans:loans_page')
        
    if account.balance < total_repayment:
        messages.error(request, f'Недостаточно средств на счете {account.account_number} для досрочного погашения ({total_repayment} TJS).')
        return redirect('loans:loans_page')
        
    # Process payment
    account.balance -= total_repayment
    account.save()
    
    # Mark payments as paid
    for payment in unpaid_payments:
        payment.is_paid = True
        payment.paid_date = timezone.now().date()
        payment.save()
        
    # Mark loan as closed
    loan.status = Loan.Status.CLOSED
    loan.save()
    
    # Create transaction
    Transaction.objects.create(
        sender_account=account,
        receiver_account=None,
        amount=total_repayment,
        transaction_type=Transaction.TransactionType.PAYMENT,
        status=Transaction.Status.COMPLETED,
        category='loans',
        description=f"Полное досрочное погашение кредита #{loan.id}"
    )
    
    # Notification
    Notification.objects.create(
        user=request.user,
        title='Кредит погашен досрочно',
        message=f"Кредит #{loan.id} успешно закрыт. Списано {total_repayment} TJS с вашего счета.",
        notification_type=Notification.NotificationType.LOAN,
    )
    
    messages.success(request, f"Кредит #{loan.id} полностью погашен! Списано {total_repayment} TJS.")
    return redirect('loans:loans_page')
