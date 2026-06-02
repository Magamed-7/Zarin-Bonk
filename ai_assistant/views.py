from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
from .models import AIMessage
from .ai_service import AIService
from banking.models import Account
from transactions.models import Transaction
from loans.models import Loan
import json


def get_bank_context(user):
    """Собирает контекст для ИИ: балансы, транзакции, кредиты"""
    context = []
    
    try:
        # Счета и балансы
        accounts = Account.objects.filter(user=user)
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
        context.append(f"Пользователь: {user.first_name} {user.last_name} (ID: {user.id})")
        context.append(f"Общий баланс всех счетов: {total_balance:.2f} TJS")
        context.append("\nСчета пользователя:")
        for account in accounts:
            context.append(f"  • Счет {account.account_number} ({account.account_type}): {account.balance:.2f} {account.currency}")
        
        # Последние 10 транзакций
        recent_transactions = Transaction.objects.filter(
            Q(sender_account__user=user) | Q(receiver_account__user=user)
        ).order_by('-created_at')[:10]
        if recent_transactions:
            context.append("\nПоследние 10 транзакций:")
            for tx in recent_transactions:
                tx_type = "Расход" if tx.transaction_type in ['withdrawal', 'transfer', 'payment'] else "Доход"
                context.append(f"  • {tx.created_at.strftime('%d.%m.%Y %H:%M')} — {tx_type}: {tx.amount:.2f} {tx.currency}")
        
        # Активные кредиты
        active_loans = Loan.objects.filter(user=user, status__in=['approved', 'active'])
        if active_loans:
            context.append("\nАктивные кредиты:")
            for loan in active_loans:
                context.append(f"  • Кредит на {loan.amount:.2f} {loan.currency}, выплатить до: {loan.due_date.strftime('%d.%m.%Y')}, статус: {loan.status}")
    except Exception as e:
        context.append(f"Пользователь: {user.first_name} {user.last_name}")
        context.append("Финансовая информация временно недоступна")
    
    return "\n".join(context)


@method_decorator(login_required, name='dispatch')
class AIChatView(TemplateView):
    template_name = 'ai_assistant/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = AIMessage.objects.filter(user=self.request.user).order_by('created_at')[:50]
        return context


@method_decorator(login_required, name='dispatch')
class AIChatAPIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'success': False, 'error': 'Сообщение не может быть пустым'}, status=400)
            
            # Собираем контекст банка
            bank_context = get_bank_context(request.user)
            
            # Сохраняем пользовательское сообщение
            AIMessage.objects.create(
                user=request.user,
                role=AIMessage.Role.USER,
                message=user_message
            )
            
            # Получаем ответ от AI с контекстом
            ai_service = AIService()
            ai_response = ai_service.get_ai_response(user_message, bank_context)
            
            # Сохраняем ответ AI
            AIMessage.objects.create(
                user=request.user,
                role=AIMessage.Role.ASSISTANT,
                message=ai_response
            )
            
            return JsonResponse({
                'success': True,
                'message': ai_response
            })
            
        except Exception as e:
            import traceback
            print("ERROR:", str(e))
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
