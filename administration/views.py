from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib import messages
import json

from accounts.models import User
from accounts.decorators import admin_required
from banking.models import Account, BankSettings, ExchangeRate
from transactions.models import Transaction
from loans.models import Loan, LoanProgram
from .forms import BankSettingsForm, ExchangeRateForm, LoanProgramForm


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class AdminDashboardView(generic.View):
    template_name = 'administration/dashboard.html'

    def get(self, request, *args, **kwargs):
        # Calculate statistics
        total_users = User.objects.filter(is_deleted=False).count()
        total_transactions = Transaction.objects.filter(is_deleted=False).count()
        total_loans = Loan.objects.count()

        # Calculate monthly growth data for charts (last 12 months)
        today = timezone.now()
        months = []
        user_counts = []
        transaction_counts = []
        loan_counts = []

        for i in range(11, -1, -1):
            month_date = today - relativedelta(months=i)
            month_label = month_date.strftime("%b %Y")
            months.append(month_label)

            # Users registered in this month
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + relativedelta(months=1)) - relativedelta(seconds=1)

            user_count = User.objects.filter(is_deleted=False, date_joined__gte=month_start, date_joined__lte=month_end).count()
            user_counts.append(user_count)

            # Transactions in this month
            trans_count = Transaction.objects.filter(is_deleted=False, created_at__gte=month_start, created_at__lte=month_end).count()
            transaction_counts.append(trans_count)

            # Loans in this month
            loan_count = Loan.objects.filter(created_at__gte=month_start, created_at__lte=month_end).count()
            loan_counts.append(loan_count)

        context = {
            'total_users': total_users,
            'total_transactions': total_transactions,
            'total_loans': total_loans,
            'months': json.dumps(months),
            'user_counts': json.dumps(user_counts),
            'transaction_counts': json.dumps(transaction_counts),
            'loan_counts': json.dumps(loan_counts),
        }

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserListView(generic.ListView):
    model = User
    template_name = 'administration/user_list.html'
    context_object_name = 'users'
    ordering = ['-date_joined']
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.filter(is_deleted=False)
        role_filter = self.request.GET.get('role', '')
        search_query = self.request.GET.get('search', '')
        
        if role_filter:
            queryset = queryset.filter(role=role_filter)
            
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_filter'] = self.request.GET.get('role', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserDetailView(generic.DetailView):
    model = User
    template_name = 'administration/user_detail.html'
    context_object_name = 'user_profile'
    pk_url_kwarg = 'user_id'

    def get_queryset(self):
        return User.objects.filter(is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        context['accounts'] = Account.objects.filter(user=user_profile, is_deleted=False)
        context['loans'] = Loan.objects.filter(user=user_profile)
        context['transactions'] = Transaction.objects.filter(
            Q(sender_account__user=user_profile) | Q(receiver_account__user=user_profile)
        ).order_by('-created_at')[:20]
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ChangeRoleView(generic.View):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id, is_deleted=False)
        
        if user == request.user:
            messages.error(request, 'Вы не можете изменить свою роль!')
            return redirect('administration:user_detail', user_id=user.id)
        
        new_role = request.POST.get('role')
        if new_role in [choice[0] for choice in User.Role.choices]:
            old_role = user.get_role_display()
            user.role = new_role
            user.save()
            messages.success(request, f'Роль пользователя {user.username} изменена с {old_role} на {user.get_role_display()}')
        
        return redirect('administration:user_detail', user_id=user.id)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ToggleBlockView(generic.View):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id, is_deleted=False)
        
        if user == request.user:
            messages.error(request, 'Вы не можете заблокировать самого себя!')
            return redirect('administration:user_detail', user_id=user.id)
        
        user.is_active = not user.is_active
        user.save()
        
        if user.is_active:
            messages.success(request, f'Пользователь {user.username} разблокирован')
        else:
            messages.success(request, f'Пользователь {user.username} заблокирован')
        
        return redirect('administration:user_detail', user_id=user.id)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class TransactionListView(generic.ListView):
    model = Transaction
    template_name = 'administration/transactions.html'
    context_object_name = 'transactions'
    ordering = ['-created_at']
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(is_deleted=False).select_related(
            'sender_account', 'receiver_account',
            'sender_account__user', 'receiver_account__user'
        )
        # Фильтры
        type_filter = self.request.GET.get('type', '')
        search_query = self.request.GET.get('search', '')
        
        if type_filter:
            queryset = queryset.filter(transaction_type=type_filter)
        
        if search_query:
            queryset = queryset.filter(
                Q(sender_account__user__username__icontains=search_query) |
                Q(receiver_account__user__username__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Общая статистика
        total_turnover = Transaction.objects.filter(
            is_deleted=False, transaction_type='transfer'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_deposits = Transaction.objects.filter(
            is_deleted=False, transaction_type='deposit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_withdrawals = Transaction.objects.filter(
            is_deleted=False, transaction_type='withdrawal'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context['total_turnover'] = total_turnover
        context['total_deposits'] = total_deposits
        context['total_withdrawals'] = total_withdrawals
        context['type_filter'] = self.request.GET.get('type', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class BankSettingsView(generic.UpdateView):
    model = BankSettings
    template_name = 'administration/settings.html'
    form_class = BankSettingsForm
    context_object_name = 'settings'

    def get_object(self, queryset=None):
        return BankSettings.get_settings()

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, 'Настройки банка успешно обновлены!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ExchangeRateListView(generic.ListView):
    model = ExchangeRate
    template_name = 'administration/exchange_rates.html'
    context_object_name = 'rates'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ExchangeRateCreateView(generic.CreateView):
    model = ExchangeRate
    template_name = 'administration/exchange_rate_form.html'
    form_class = ExchangeRateForm
    success_url = '/administration/exchange-rates/'

    def form_valid(self, form):
        messages.success(self.request, 'Курс валют успешно добавлен!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ExchangeRateUpdateView(generic.UpdateView):
    model = ExchangeRate
    template_name = 'administration/exchange_rate_form.html'
    form_class = ExchangeRateForm
    pk_url_kwarg = 'rate_id'
    success_url = '/administration/exchange-rates/'

    def form_valid(self, form):
        messages.success(self.request, 'Курс валют успешно обновлен!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class ExchangeRateDeleteView(generic.DeleteView):
    model = ExchangeRate
    pk_url_kwarg = 'rate_id'
    success_url = '/administration/exchange-rates/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Курс валют успешно удалён!')
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class LoanProgramListView(generic.ListView):
    model = LoanProgram
    template_name = 'administration/loan_programs.html'
    context_object_name = 'programs'


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class LoanProgramCreateView(generic.CreateView):
    model = LoanProgram
    template_name = 'administration/loan_program_form.html'
    form_class = LoanProgramForm
    success_url = '/administration/loan-programs/'

    def form_valid(self, form):
        messages.success(self.request, 'Кредитная программа успешно добавлена!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class LoanProgramUpdateView(generic.UpdateView):
    model = LoanProgram
    template_name = 'administration/loan_program_form.html'
    form_class = LoanProgramForm
    pk_url_kwarg = 'program_id'
    success_url = '/administration/loan-programs/'

    def form_valid(self, form):
        messages.success(self.request, 'Кредитная программа успешно обновлена!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class LoanProgramDeleteView(generic.DeleteView):
    model = LoanProgram
    pk_url_kwarg = 'program_id'
    success_url = '/administration/loan-programs/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Кредитная программа успешно удалена!')
        return super().delete(request, *args, **kwargs)

