from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic, View
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum, Q
from django.shortcuts import render
from .models import Budget, BudgetCategory
from transactions.models import Transaction
from loans.models import Loan
from banking.models import Account
from ai_assistant.ai_service import AIService


class BudgetListView(LoginRequiredMixin, generic.ListView):
    model = Budget
    template_name = 'budget/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budgets = self.get_queryset()
        
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        user_accounts = self.request.user.accounts.all()
        
        category_map = {
            'internet': 'Интернет',
            'phone': 'Связь',
            'utilities': 'ЖКХ',
            'shopping': 'Покупки',
            'food': 'Еда',
            'transport': 'Транспорт',
        }
        
        # --- Данные для расходов ---
        expense_transactions = Transaction.objects.filter(
            sender_account__in=user_accounts,
            status=Transaction.Status.COMPLETED,
            is_deleted=False,
            created_at__month=current_month,
            created_at__year=current_year
        )
        
        expense_totals = {}
        total_expense = 0
        
        for tx in expense_transactions:
            tx_category = tx.category or 'Прочее'
            budget_category_name = category_map.get(tx_category, tx_category)
            
            if budget_category_name not in expense_totals:
                expense_totals[budget_category_name] = 0
            expense_totals[budget_category_name] += float(tx.amount)
            total_expense += float(tx.amount)
        
        expense_labels = []
        expense_data = []
        expense_colors = []
        
        budget_categories = {bc.name: bc for bc in BudgetCategory.objects.all()}
        
        for cat_name, total in expense_totals.items():
            if total > 0:
                expense_labels.append(cat_name)
                expense_data.append(total)
                expense_colors.append(budget_categories[cat_name].color if cat_name in budget_categories else '#888888')
        
        income_transactions = Transaction.objects.filter(
            receiver_account__in=user_accounts,
            status=Transaction.Status.COMPLETED,
            is_deleted=False,
            created_at__month=current_month,
            created_at__year=current_year
        )
        
        income_totals = {}
        total_income = 0
        
        for tx in income_transactions:
            tx_type = tx.get_transaction_type_display() or 'Доход'
            
            if tx_type not in income_totals:
                income_totals[tx_type] = 0
            income_totals[tx_type] += float(tx.amount)
            total_income += float(tx.amount)
        
        income_labels = []
        income_data = []
        income_colors = []
        income_color_palette = ['#48c774', '#3298dc', '#209cee', '#10a881', '#059669']
        
        for i, (cat_name, total) in enumerate(income_totals.items()):
            if total > 0:
                income_labels.append(cat_name)
                income_data.append(total)
                income_colors.append(income_color_palette[i % len(income_color_palette)])
        
        context['expense_labels'] = expense_labels
        context['expense_data'] = expense_data
        context['expense_colors'] = expense_colors
        context['total_expense'] = total_expense
        
        context['income_labels'] = income_labels
        context['income_data'] = income_data
        context['income_colors'] = income_colors
        context['total_income'] = total_income
      
        over_limit_budgets = [b for b in budgets if b.is_exceeded]
        context['over_limit_budgets'] = over_limit_budgets
        
        return context



class BudgetCreateView(LoginRequiredMixin, generic.CreateView):
    model = Budget
    template_name = 'budget/budget_form.html'
    fields = ['category', 'limit_amount', 'month', 'year']
    success_url = reverse_lazy('budget:budget_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Бюджет для категории "{form.instance.category.name}" создан.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BudgetCategory.objects.all()
        return context



class BudgetUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Budget
    template_name = 'budget/budget_form.html'
    fields = ['category', 'limit_amount', 'month', 'year']
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('budget:budget_list')

    def get_queryset(self):
        return Budget.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def form_valid(self, form):
        messages.success(self.request, f'Бюджет для категории "{form.instance.category.name}" обновлён.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BudgetCategory.objects.all()
        context['is_update'] = True
        return context



class BudgetDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Budget
    template_name = 'budget/budget_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('budget:budget_list')

    def get_queryset(self):
        return Budget.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def delete(self, request, *args, **kwargs):
        budget = self.get_object()
        messages.success(request, f'Бюджет для категории "{budget.category.name}" удалён.')
        return super().delete(request, *args, **kwargs)


class FinancialAdvisorView(LoginRequiredMixin, View):
    template_name = 'budget/financial_advisor.html'
    
    def get(self, request):
        return self._generate_advice(request)
    
    def post(self, request):
        return self._generate_advice(request)
    
    def _generate_advice(self, request):
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        user_accounts = request.user.accounts.all()
        
        # Сбор транзакций за месяц
        expense_transactions = Transaction.objects.filter(
            sender_account__in=user_accounts,
            status=Transaction.Status.COMPLETED,
            is_deleted=False,
            created_at__month=current_month,
            created_at__year=current_year
        )
        
        income_transactions = Transaction.objects.filter(
            receiver_account__in=user_accounts,
            status=Transaction.Status.COMPLETED,
            is_deleted=False,
            created_at__month=current_month,
            created_at__year=current_year
        )
        
        # Подготовка контекста для ИИ
        context_text = self._prepare_context(request.user, expense_transactions, income_transactions)
        
        # Запрос к ИИ
        ai_service = AIService()
        system_prompt = """Ты финансовый консультант банка ZarinPay. Проанализируй расходы пользователя и дай конкретные, практические советы по экономии. 
        
Ответ дай в таком формате (каждая категория совета на новой строке с иконкой):
🔹 Анализ: (краткий анализ расходов)
💡 Совет 1: (конкретный совет)
💡 Совет 2: (конкретный совет)
💡 Совет 3: (конкретный совет)
💰 Рекомендация: (главная финансовая рекомендация)

Будь дружелюбен и профессионален. Отвечай на русском языке."""
        
        try:
            # Создаем временный контекст
            temp_context = system_prompt + "\n\n" + context_text
            ai_response = ai_service.get_ai_response("Анализируй мои расходы и дай советы по экономии.", temp_context)
        except Exception as e:
            ai_response = self._get_default_advice(expense_transactions, income_transactions)
        
        # Парсим ответ для красивого отображения
        parsed_advice = self._parse_ai_response(ai_response)
        
        total_income = sum(float(tx.amount) for tx in income_transactions)
        total_expense = sum(float(tx.amount) for tx in expense_transactions)
        
        context = {
            'advice': parsed_advice,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'month': now.strftime('%B %Y'),
        }
        
        return render(request, self.template_name, context)
    
    def _prepare_context(self, user, expense_transactions, income_transactions):
        context = []
        context.append(f"Пользователь: {user.first_name} {user.last_name}")
        
        # Подсчет расходов по категориям
        category_map = {
            'internet': 'Интернет',
            'phone': 'Связь',
            'utilities': 'ЖКХ',
            'shopping': 'Покупки',
            'food': 'Еда',
            'transport': 'Транспорт',
        }
        
        expense_totals = {}
        for tx in expense_transactions:
            tx_category = tx.category or 'Прочее'
            budget_category_name = category_map.get(tx_category, tx_category)
            if budget_category_name not in expense_totals:
                expense_totals[budget_category_name] = 0
            expense_totals[budget_category_name] += float(tx.amount)
        
        total_expense = sum(expense_totals.values())
        total_income = sum(float(tx.amount) for tx in income_transactions)
        
        context.append(f"\nОбщий доход за месяц: {total_income:.2f} TJS")
        context.append(f"Общие расходы за месяц: {total_expense:.2f} TJS")
        context.append("\nРасходы по категориям:")
        for cat, amt in expense_totals.items():
            context.append(f"  • {cat}: {amt:.2f} TJS")
        
        return "\n".join(context)
    
    def _parse_ai_response(self, response):
        lines = response.split('\n')
        tips = []
        for line in lines:
            line = line.strip()
            if line.startswith('🔹') or line.startswith('💡') or line.startswith('💰'):
                tips.append(line)
        if not tips:
            tips = [
                '🔹 Анализ: Покажем вам стандартные советы по экономии.',
                '💡 Совет 1: Следите за импульсивными покупками.',
                '💡 Совет 2: Планируйте бюджет заранее.',
                '💡 Совет 3: Сравнивайте цены перед покупкой.',
                '💰 Рекомендация: Создайте подушку безопасности в размере 3-6 месячных расходов.',
            ]
        return tips
    
    def _get_default_advice(self, expense_transactions, income_transactions):
        tips = [
            '🔹 Анализ: Основные расходы - это стандартные категории.',
            '💡 Совет 1: Следите за импульсивными покупками.',
            '💡 Совет 2: Планируйте бюджет заранее.',
            '💡 Совет 3: Сравнивайте цены перед покупкой.',
            '💰 Рекомендация: Создайте подушку безопасности в размере 3-6 месячных расходов.',
        ]
        return '\n'.join(tips)
