from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import generic
from django.db.models import Q

from .models import Notification


class NotificationListView(LoginRequiredMixin, generic.ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


@login_required
def mark_as_read(request, pk):
    if request.method == 'POST':
        notification = Notification.objects.filter(user=request.user, pk=pk).first()
        if notification:
            notification.is_read = True
            notification.save()
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            return JsonResponse({
                'success': True,
                'unread_count': unread_count
            })
        return redirect('notifications:notification_list')
    return redirect('notifications:notification_list')


@login_required
def mark_all_as_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'unread_count': 0})
        return redirect('notifications:notification_list')
    return redirect('notifications:notification_list')
