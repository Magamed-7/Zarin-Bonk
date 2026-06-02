from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic
from django.shortcuts import render
from django.db.models import Count, Sum
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import json

from accounts.models import User
from accounts.decorators import admin_required
from banking.models import Account
from transactions.models import Transaction
from loans.models import Loan


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

