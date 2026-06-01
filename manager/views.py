from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from accounts.decorators import manager_required
from loans.models import Loan, LoanPayment
from banking.models import Account
from transactions.models import Transaction
from notifications.models import Notification


@method_decorator(manager_required, name='dispatch')
class LoanRequestsListView(generic.ListView):
    model = Loan
    template_name = 'manager/loan_requests.html'
    context_object_name = 'loans'
    ordering = ['-created_at']


@method_decorator(manager_required, name='dispatch')
class LoanRequestDetailView(generic.DetailView):
    model = Loan
    template_name = 'manager/loan_request_detail.html'
    context_object_name = 'loan'
    
    def post(self, request, *args, **kwargs):
        loan = self.get_object()
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            loan.status = Loan.Status.ACTIVE
            loan.manager_comment = comment
            loan.save()
            
            monthly_payment = loan.calculate_monthly_payment()
            start_date = timezone.now().date()
            
            for i in range(1, loan.term_months + 1):
                due_date = start_date + relativedelta(months=i)
                LoanPayment.objects.create(
                    loan=loan,
                    amount=monthly_payment,
                    due_date=due_date,
                    is_paid=False
                )
            
            account = Account.objects.filter(user=loan.user, is_active=True).first()
            if account:
                account.balance += loan.amount
                account.save()
                
                Transaction.objects.create(
                    sender_account=None,
                    receiver_account=account,
                    amount=loan.amount,
                    transaction_type=Transaction.TransactionType.DEPOSIT,
                    status=Transaction.Status.COMPLETED,
                    description=f"Зачисление кредитных средств (кредит #{loan.id})"
                )
            
            Notification.objects.create(
                user=loan.user,
                title='Кредит одобрен',
                message=f'Ваш кредит на сумму {loan.amount} TJS одобрен и зачислен на счёт.',
                notification_type=Notification.NotificationType.LOAN,
            )
            
            messages.success(request, f'Кредит #{loan.id} одобрен и выдан')
            
        elif action == 'reject':
            loan.status = Loan.Status.REJECTED
            loan.manager_comment = comment
            loan.save()
            
            Notification.objects.create(
                user=loan.user,
                title='Кредит отклонён',
                message=f'Ваш запрос на кредит отклонён. Причина: {comment}',
                notification_type=Notification.NotificationType.LOAN,
            )
            
            messages.success(request, f'Кредит #{loan.id} отклонён')
        
        return redirect('manager:loan_requests')
