from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import Goal
from ai_assistant.ai_service import AIService
from banking.models import Account
from transactions.models import Transaction


class GoalListView(LoginRequiredMixin, generic.ListView):
    model = Goal
    template_name = 'goals/goal_list.html'
    context_object_name = 'goals'

    def get_queryset(self):
        return Goal.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_goals'] = Goal.objects.filter(
            user=self.request.user,
            is_deleted=False,
            is_completed=True
        ).order_by('-created_at')
        return context


class GoalCreateView(LoginRequiredMixin, generic.View):
    template_name = 'goals/goal_form.html'
    
    def get(self, request, *args, **kwargs):
        from django import forms
        
        class GoalForm(forms.Form):
            title = forms.CharField(
                label='Название цели',
                max_length=200,
                widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Новый автомобиль'})
            )
            target_amount = forms.DecimalField(
                label='Целевая сумма (TJS)',
                widget=forms.NumberInput(attrs={
                    'class': 'form-input',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': '10000.00'
                })
            )
            deadline = forms.DateField(
                label='Дедлайн',
                required=False,
                widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
            )
            description = forms.CharField(
                label='Описание',
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Опишите вашу цель...'})
            )
            icon = forms.ChoiceField(
                label='Иконка',
                choices=[
                    ('🎯', '🎯 Цель'),
                    ('🚗', '🚗 Автомобиль'),
                    ('🏠', '🏠 Дом'),
                    ('✈️', '✈️ Путешествие'),
                    ('💻', '💻 Техника'),
                    ('📱', '📱 Гаджет'),
                    ('💰', '💰 Накопления'),
                    ('🎓', '🎓 Образование'),
                    ('💍', '💍 Подарок'),
                    ('🏥', '🏥 Здоровье'),
                    ('🎮', '🎮 Развлечения'),
                    ('📚', '📚 Книги'),
                ],
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        
        form = GoalForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        from django import forms
        
        class GoalForm(forms.Form):
            title = forms.CharField(
                label='Название цели',
                max_length=200,
                widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Новый автомобиль'})
            )
            target_amount = forms.DecimalField(
                label='Целевая сумма (TJS)',
                widget=forms.NumberInput(attrs={
                    'class': 'form-input',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': '10000.00'
                })
            )
            deadline = forms.DateField(
                label='Дедлайн',
                required=False,
                widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
            )
            description = forms.CharField(
                label='Описание',
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Опишите вашу цель...'})
            )
            icon = forms.ChoiceField(
                label='Иконка',
                choices=[
                    ('🎯', '🎯 Цель'),
                    ('🚗', '🚗 Автомобиль'),
                    ('🏠', '🏠 Дом'),
                    ('✈️', '✈️ Путешествие'),
                    ('💻', '💻 Техника'),
                    ('📱', '📱 Гаджет'),
                    ('💰', '💰 Накопления'),
                    ('🎓', '🎓 Образование'),
                    ('💍', '💍 Подарок'),
                    ('🏥', '🏥 Здоровье'),
                    ('🎮', '🎮 Развлечения'),
                    ('📚', '📚 Книги'),
                ],
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        
        form = GoalForm(request.POST)
        
        if form.is_valid():
            goal = Goal.objects.create(
                user=request.user,
                title=form.cleaned_data['title'],
                target_amount=form.cleaned_data['target_amount'],
                current_amount=Decimal('0.00'),
                deadline=form.cleaned_data.get('deadline'),
                description=form.cleaned_data.get('description', ''),
                icon=form.cleaned_data['icon']
            )
            messages.success(request, f'Цель "{goal.title}" создана.')
            return redirect('goals:goal_list')
        
        return render(request, self.template_name, {'form': form})


class GoalUpdateView(LoginRequiredMixin, generic.View):
    template_name = 'goals/goal_form.html'

    def get(self, request, *args, **kwargs):
        from django import forms
        goal = get_object_or_404(Goal, slug=kwargs['slug'], user=request.user, is_deleted=False)
        
        class GoalForm(forms.Form):
            title = forms.CharField(
                label='Название цели',
                max_length=200,
                initial=goal.title,
                widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Новый автомобиль'})
            )
            target_amount = forms.DecimalField(
                label='Целевая сумма (TJS)',
                initial=goal.target_amount,
                widget=forms.NumberInput(attrs={
                    'class': 'form-input',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': '10000.00'
                })
            )
            deadline = forms.DateField(
                label='Дедлайн',
                required=False,
                initial=goal.deadline,
                widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
            )
            description = forms.CharField(
                label='Описание',
                required=False,
                initial=goal.description,
                widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Опишите вашу цель...'})
            )
            icon = forms.ChoiceField(
                label='Иконка',
                choices=[
                    ('🎯', '🎯 Цель'),
                    ('🚗', '🚗 Автомобиль'),
                    ('🏠', '🏠 Дом'),
                    ('✈️', '✈️ Путешествие'),
                    ('💻', '💻 Техника'),
                    ('📱', '📱 Гаджет'),
                    ('💰', '💰 Накопления'),
                    ('🎓', '🎓 Образование'),
                    ('💍', '💍 Подарок'),
                    ('🏥', '🏥 Здоровье'),
                    ('🎮', '🎮 Развлечения'),
                    ('📚', '📚 Книги'),
                ],
                initial=goal.icon,
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        
        form = GoalForm()
        return render(request, self.template_name, {'form': form, 'is_update': True})

    def post(self, request, *args, **kwargs):
        from django import forms
        goal = get_object_or_404(Goal, slug=kwargs['slug'], user=request.user, is_deleted=False)
        
        class GoalForm(forms.Form):
            title = forms.CharField(
                label='Название цели',
                max_length=200,
                widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Новый автомобиль'})
            )
            target_amount = forms.DecimalField(
                label='Целевая сумма (TJS)',
                widget=forms.NumberInput(attrs={
                    'class': 'form-input',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': '10000.00'
                })
            )
            deadline = forms.DateField(
                label='Дедлайн',
                required=False,
                widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
            )
            description = forms.CharField(
                label='Описание',
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Опишите вашу цель...'})
            )
            icon = forms.ChoiceField(
                label='Иконка',
                choices=[
                    ('🎯', '🎯 Цель'),
                    ('🚗', '🚗 Автомобиль'),
                    ('🏠', '🏠 Дом'),
                    ('✈️', '✈️ Путешествие'),
                    ('💻', '💻 Техника'),
                    ('📱', '📱 Гаджет'),
                    ('💰', '💰 Накопления'),
                    ('🎓', '🎓 Образование'),
                    ('💍', '💍 Подарок'),
                    ('🏥', '🏥 Здоровье'),
                    ('🎮', '🎮 Развлечения'),
                    ('📚', '📚 Книги'),
                ],
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        
        form = GoalForm(request.POST)
        
        if form.is_valid():
            goal.title = form.cleaned_data['title']
            goal.target_amount = form.cleaned_data['target_amount']
            goal.deadline = form.cleaned_data.get('deadline')
            goal.description = form.cleaned_data.get('description', '')
            goal.icon = form.cleaned_data['icon']
            goal.save()
            
            messages.success(request, f'Цель "{goal.title}" обновлена.')
            return redirect('goals:goal_list')
        
        return render(request, self.template_name, {'form': form, 'is_update': True})


class GoalDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Goal
    template_name = 'goals/goal_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('goals:goal_list')

    def get_queryset(self):
        return Goal.objects.filter(
            user=self.request.user,
            is_deleted=False
        )

    def delete(self, request, *args, **kwargs):
        goal = self.get_object()
        messages.success(request, f'Цель "{goal.title}" удалена.')
        return super().delete(request, *args, **kwargs)


class GoalDepositView(LoginRequiredMixin, generic.View):
    template_name = 'goals/goal_deposit.html'
    
    def get(self, request, *args, **kwargs):
        from django import forms
        from .models import Goal
        
        goal = get_object_or_404(Goal, slug=kwargs['slug'], user=request.user, is_deleted=False)
        
        class DepositForm(forms.Form):
            amount = forms.DecimalField(
                label='Сумма пополнения (TJS)',
                widget=forms.NumberInput(attrs={
                    'class': 'form-input',
                    'step': '0.01',
                    'min': '0.01',
                    'placeholder': '100.00'
                })
            )
        
        form = DepositForm()
        return render(request, self.template_name, {'form': form, 'goal': goal})
    
    def post(self, request, *args, **kwargs):
        from django import forms
        from django.shortcuts import get_object_or_404
        from .models import Goal
        
        goal = get_object_or_404(Goal, slug=kwargs['slug'], user=request.user, is_deleted=False)
        
        class DepositForm(forms.Form):
            amount = forms.DecimalField(
                label='Сумма пополнения (TJS)',
                widget=forms.NumberInput(attrs={
                    'class': 'form-input',
                    'step': '0.01',
                    'min': '0.01',
                    'placeholder': '100.00'
                })
            )
        
        form = DepositForm(request.POST)
        
        if form.is_valid():
            amount = form.cleaned_data['amount']
            goal.current_amount += amount
            goal.save()
            
            if goal.is_completed:
                messages.success(request, f'🎉 Поздравляем! Вы достигли цели "{goal.title}"!')
            else:
                messages.success(request, f'Цель "{goal.title}" пополнена на {amount} TJS.')
            
            return redirect('goals:goal_list')
        
        return render(request, self.template_name, {'form': form, 'goal': goal})


class AIFinancialPlannerView(LoginRequiredMixin, generic.View):
    template_name = 'goals/ai_planner.html'
    
    def get(self, request, *args, **kwargs):
        from django import forms
        
        class PlannerForm(forms.Form):
            goal_title = forms.CharField(
                label='Название цели',
                max_length=200,
                widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Новый телефон'})
            )
            target_amount = forms.DecimalField(
                label='Целевая сумма (TJS)',
                widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'placeholder': '15000.00'})
            )
            deadline_months = forms.IntegerField(
                label='Срок достижения (в месяцах)',
                min_value=1,
                max_value=60,
                widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '12'})
            )
            description = forms.CharField(
                label='Дополнительная информация',
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Опишите вашу финансовую ситуацию, доходы и расходы...'})
            )
        
        form = PlannerForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        from django import forms
        
        class PlannerForm(forms.Form):
            goal_title = forms.CharField(
                label='Название цели',
                max_length=200,
                widget=forms.TextInput(attrs={'class': 'form-input'})
            )
            target_amount = forms.DecimalField(
                label='Целевая сумма (TJS)',
                widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'})
            )
            deadline_months = forms.IntegerField(
                label='Срок достижения (в месяцах)',
                min_value=1,
                max_value=60,
                widget=forms.NumberInput(attrs={'class': 'form-input'})
            )
            description = forms.CharField(
                label='Дополнительная информация',
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3})
            )
        
        form = PlannerForm(request.POST)
        ai_plan = None
        plan_data = None
        
        if form.is_valid():
            goal_title = form.cleaned_data['goal_title']
            target_amount = form.cleaned_data['target_amount']
            deadline_months = form.cleaned_data['deadline_months']
            description = form.cleaned_data.get('description', '')
            
            # Calculate deadline date
            deadline_date = timezone.now().date() + relativedelta(months=+deadline_months)
            
            # Prepare financial context for AI
            user_accounts = Account.objects.filter(user=request.user, is_deleted=False)
            total_balance = sum(acc.balance for acc in user_accounts)
            
            # Get recent transactions
            now = timezone.now()
            month_ago = now - relativedelta(months=1)
            recent_transactions = Transaction.objects.filter(
                (Q(sender_account__in=user_accounts) | Q(receiver_account__in=user_accounts)),
                is_deleted=False,
                created_at__gte=month_ago
            ).order_by('-created_at')[:50]
            
            total_income = sum(tx.amount for tx in recent_transactions if tx.receiver_account in user_accounts)
            total_expense = sum(tx.amount for tx in recent_transactions if tx.sender_account in user_accounts)
            
            # Prepare context prompt for AI
            system_prompt = """Вы — финансовый советник банка ZarinPay. Пользователь хочет достичь финансовой цели. 
Создайте ПОШАГОВЫЙ ПЛАН НАКОПЛЕНИЙ, используя следующий формат (строго соблюдайте!):

### ШАГ за шагом:
1. [Краткий шаг 1]|[Пояснение шага 1]
2. [Краткий шаг 2]|[Пояснение шага 2]
3. [Краткий шаг 3]|[Пояснение шага 3]
... (5-8 шагов)

### Важные рекомендации:
- • Рекомендация 1
- • Рекомендация 2
- • Рекомендация 3

Отвечайте на русском языке, будьте дружелюбны и реалистичны!"""
            
            user_context = f"""
Цель пользователя: {goal_title}
Целевая сумма: {target_amount} TJS
Срок достижения: {deadline_months} месяцев
Дедлайн: {deadline_date.strftime('%d.%m.%Y')}
Текущий баланс: {total_balance} TJS
Доходы за месяц: {total_income} TJS
Расходы за месяц: {total_expense} TJS
Дополнительно: {description}
"""
            
            try:
                # Call AI service
                ai_service = AIService()
                ai_response = ai_service.get_ai_response(
                    "Создай пошаговый финансовый план",
                    user_context + "\n\n" + system_prompt
                )
                
                # Parse the AI response
                ai_plan = ai_response
                plan_data = {
                    'title': goal_title,
                    'target_amount': target_amount,
                    'deadline_months': deadline_months,
                    'deadline_date': deadline_date,
                    'monthly_payment': (target_amount / Decimal(str(deadline_months))).quantize(Decimal('0.01'))
                }
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"AI planner error: {e}")
                ai_plan = "Произошла ошибка при генерации плана. Попробуйте позже."
                plan_data = {
                    'title': goal_title,
                    'target_amount': target_amount,
                    'deadline_months': deadline_months,
                    'deadline_date': deadline_date,
                    'monthly_payment': (target_amount / Decimal(str(deadline_months))).quantize(Decimal('0.01'))
                }
        
        return render(request, self.template_name, {
            'form': form,
            'ai_plan': ai_plan,
            'plan_data': plan_data
        })


class CreateGoalFromPlanView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        from django import forms
        
        class PlanForm(forms.Form):
            title = forms.CharField(max_length=200)
            target_amount = forms.DecimalField()
            deadline_date = forms.DateField()
        
        form = PlanForm(request.POST)
        
        if form.is_valid():
            goal = Goal.objects.create(
                user=request.user,
                title=form.cleaned_data['title'],
                target_amount=form.cleaned_data['target_amount'],
                current_amount=Decimal('0.00'),
                deadline=form.cleaned_data['deadline_date'],
                description='Цель создана с помощью ИИ финансового планера',
                icon='🎯'
            )
            messages.success(request, f'Цель "{goal.title}" создана по плану ИИ!')
        
        return redirect('goals:goal_list')
