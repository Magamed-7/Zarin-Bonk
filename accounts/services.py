from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import FinancialScore


def get_level(score):
    if score <= 25:
        return FinancialScore.Level.BRONZE
    elif score <= 50:
        return FinancialScore.Level.SILVER
    elif score <= 75:
        return FinancialScore.Level.GOLD
    else:
        return FinancialScore.Level.PLATINUM


def calculate_score(user):
    score = 0
    details = {}

    # Критерий 1: Регулярные пополнения счёта (проверим есть ли счёт и хотя бы 2 транзакции за последние 3 месяца)
    try:
        from banking.models import Account
        from transactions.models import Transaction
        accounts = Account.objects.filter(user=user, is_deleted=False)
        if accounts.exists():
            three_months_ago = timezone.now() - relativedelta(months=3)
            recent_deposits = Transaction.objects.filter(
                receiver_account__in=accounts,
                transaction_type=Transaction.TransactionType.DEPOSIT,
                status=Transaction.Status.COMPLETED,
                created_at__gte=three_months_ago
            ).count()
            if recent_deposits >= 2:
                score += 20
                details['regular_deposits'] = {'points': 20, 'achieved': True}
            else:
                details['regular_deposits'] = {'points': 0, 'achieved': False, 'reason': 'Недостаточно пополнений за последние 3 месяца'}
        else:
            details['regular_deposits'] = {'points': 0, 'achieved': False, 'reason': 'Нет активных счетов'}
    except Exception as e:
        details['regular_deposits'] = {'points': 0, 'achieved': False, 'reason': str(e)}

    # Критерий 2: Нет просрочек по кредитам
    try:
        from loans.models import LoanPayment
        overdue_payments = LoanPayment.objects.filter(
            loan__user=user,
            is_overdue=True,
            is_paid=False
        ).count()
        if overdue_payments == 0:
            score += 25
            details['no_overdue_loans'] = {'points': 25, 'achieved': True}
        else:
            details['no_overdue_loans'] = {'points': 0, 'achieved': False, 'reason': f'Есть {overdue_payments} просроченных платежей'}
    except Exception as e:
        details['no_overdue_loans'] = {'points': 0, 'achieved': False, 'reason': str(e)}

    # Критерий 3: Активный сберегательный счёт (вместо депозитов, т.к. приложение deposits не существует)
    try:
        from banking.models import Account
        active_saving_accounts = Account.objects.filter(
            user=user,
            is_deleted=False,
            is_active=True,
            account_type=Account.AccountType.SAVING
        ).count()
        if active_saving_accounts > 0:
            score += 20
            details['active_saving_account'] = {'points': 20, 'achieved': True}
        else:
            details['active_saving_account'] = {'points': 0, 'achieved': False, 'reason': 'Нет активных сберегательных счетов'}
    except Exception as e:
        details['active_saving_account'] = {'points': 0, 'achieved': False, 'reason': str(e)}

    # Критерий 4: Использует бюджет и цели
    try:
        from budget.models import Budget
        from goals.models import Goal
        has_budget = Budget.objects.filter(user=user, is_deleted=False).exists()
        has_goal = Goal.objects.filter(user=user, is_deleted=False).exists()
        if has_budget and has_goal:
            score += 15
            details['budget_and_goals'] = {'points': 15, 'achieved': True}
        else:
            details['budget_and_goals'] = {'points': 0, 'achieved': False, 'reason': 'Нет бюджета или целей'}
    except Exception as e:
        details['budget_and_goals'] = {'points': 0, 'achieved': False, 'reason': str(e)}

    # Критерий 5: Давно зарегистрирован (больше 3 месяцев)
    try:
        three_months_ago = timezone.now() - relativedelta(months=3)
        if user.date_joined <= three_months_ago:
            score += 20
            details['long_registration'] = {'points': 20, 'achieved': True}
        else:
            details['long_registration'] = {'points': 0, 'achieved': False, 'reason': 'Зарегистрирован менее 3 месяцев назад'}
    except Exception as e:
        details['long_registration'] = {'points': 0, 'achieved': False, 'reason': str(e)}

    level = get_level(score)

    # Обновляем или создаём FinancialScore
    financial_score, created = FinancialScore.objects.update_or_create(
        user=user,
        defaults={
            'score': score,
            'level': level,
            'score_details': details
        }
    )

    return score, level, details
