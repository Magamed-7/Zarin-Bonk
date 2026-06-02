from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from django.urls import reverse_lazy
from .models import Budget, BudgetCategory


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
        
        chart_labels = []
        chart_data = []
        chart_colors = []
        
        for budget in budgets:
            if budget.current_amount > 0:
                chart_labels.append(budget.category.name)
                chart_data.append(float(budget.current_amount))
                chart_colors.append(budget.category.color)
        
        context['chart_labels'] = chart_labels
        context['chart_data'] = chart_data
        context['chart_colors'] = chart_colors
      
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
