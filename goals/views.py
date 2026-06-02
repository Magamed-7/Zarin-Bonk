from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from .models import Goal


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
