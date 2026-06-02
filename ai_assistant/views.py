from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from .models import AIMessage
from .ai_service import AIService
import json


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
            
            # Сохраняем пользовательское сообщение
            AIMessage.objects.create(
                user=request.user,
                role=AIMessage.Role.USER,
                message=user_message
            )
            
            # Получаем ответ от AI
            ai_service = AIService()
            ai_response = ai_service.get_ai_response(user_message)
            
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
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
