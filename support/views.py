from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SupportTicket, SupportMessage


class SupportTicketListView(LoginRequiredMixin, generic.ListView):
    model = SupportTicket
    template_name = 'support/ticket_list.html'
    context_object_name = 'tickets'
    ordering = ['-created_at']

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)


class SupportTicketCreateView(LoginRequiredMixin, generic.CreateView):
    model = SupportTicket
    template_name = 'support/ticket_form.html'
    fields = ['subject']
    success_url = '/support/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        ticket = form.save()
        
        # Create initial message if provided
        initial_message = self.request.POST.get('message', '')
        if initial_message:
            SupportMessage.objects.create(
                ticket=ticket,
                sender=self.request.user,
                message=initial_message
            )
        
        messages.success(self.request, 'Тикет создан!')
        return super().form_valid(form)


class SupportTicketDetailView(LoginRequiredMixin, generic.DetailView):
    model = SupportTicket
    template_name = 'support/ticket_detail.html'
    context_object_name = 'ticket'
    pk_url_kwarg = 'ticket_id'

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if ticket.status == 'open':
            message_text = request.POST.get('message', '')
            if message_text:
                SupportMessage.objects.create(
                    ticket=ticket,
                    sender=request.user,
                    message=message_text
                )
                messages.success(request, 'Сообщение отправлено!')
        return redirect('support:ticket_detail', ticket_id=ticket.pk)
