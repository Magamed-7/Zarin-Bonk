from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db.models import Q, Count, Sum

from accounts.decorators import manager_required
from loans.models import Loan, LoanPayment
from banking.models import Account
from transactions.models import Transaction
from notifications.models import Notification
from accounts.models import User
from support.models import SupportTicket, SupportMessage


@method_decorator(manager_required, name='dispatch')
class ManagerDashboardView(generic.TemplateView):
    template_name = 'manager/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clients'] = User.objects.filter(role=User.Role.CLIENT, is_deleted=False).count()
        context['pending_loans'] = Loan.objects.filter(status=Loan.Status.PENDING).count()
        context['active_loans'] = Loan.objects.filter(status=Loan.Status.ACTIVE).count()
        context['open_tickets'] = SupportTicket.objects.filter(status=SupportTicket.Status.OPEN).count()
        context['recent_transactions'] = Transaction.objects.select_related('sender_account', 'receiver_account').order_by('-created_at')[:10]
        return context


@method_decorator(manager_required, name='dispatch')
class LoanRequestsListView(generic.ListView):
    model = Loan
    template_name = 'manager/loan_requests.html'
    context_object_name = 'loans'
    ordering = ['-created_at']
    def get_queryset(self):
        return Loan.objects.select_related('user')


@method_decorator(manager_required, name='dispatch')
class LoanRequestDetailView(generic.DetailView):
    model = Loan
    template_name = 'manager/loan_request_detail.html'
    context_object_name = 'loan'
    pk_url_kwarg = 'loan_id'
    
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


@method_decorator(manager_required, name='dispatch')
class ClientListView(generic.ListView):
    model = User
    template_name = 'manager/client_list.html'
    context_object_name = 'clients'
    ordering = ['-date_joined']
    
    def get_queryset(self):
        queryset = User.objects.filter(role=User.Role.CLIENT, is_deleted=False).select_related()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator(manager_required, name='dispatch')
class ClientDetailView(generic.DetailView):
    model = User
    template_name = 'manager/client_detail.html'
    context_object_name = 'client'
    pk_url_kwarg = 'user_id'
    
    def get_queryset(self):
        return User.objects.filter(role=User.Role.CLIENT, is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        context['accounts'] = Account.objects.filter(user=client, is_deleted=False)
        context['loans'] = Loan.objects.filter(user=client)
        context['transactions'] = Transaction.objects.filter(
            Q(sender_account__user=client) | Q(receiver_account__user=client)
        ).order_by('-created_at')[:20]
        context['tickets'] = SupportTicket.objects.filter(user=client).order_by('-created_at')
        return context


@method_decorator(manager_required, name='dispatch')
class TicketListView(generic.ListView):
    model = SupportTicket
    template_name = 'manager/ticket_list.html'
    context_object_name = 'tickets'
    ordering = ['-created_at']
    
    def get_queryset(self):
        return SupportTicket.objects.select_related('user', 'manager')


@method_decorator(manager_required, name='dispatch')
class TicketDetailView(generic.DetailView):
    model = SupportTicket
    template_name = 'manager/ticket_detail.html'
    context_object_name = 'ticket'
    pk_url_kwarg = 'ticket_id'
    
    def get_queryset(self):
        return SupportTicket.objects.select_related('user', 'manager')
    
    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        action = request.POST.get('action')
        
        if action == 'close':
            ticket.status = SupportTicket.Status.CLOSED
            ticket.save()
            messages.success(request, 'Тикет закрыт')
        elif action == 'send_message':
            message_text = request.POST.get('message', '')
            if message_text:
                SupportMessage.objects.create(
                    ticket=ticket,
                    sender=request.user,
                    message=message_text
                )
                messages.success(request, 'Сообщение отправлено')
        
        return redirect('manager:ticket_detail', ticket_id=ticket.pk)
