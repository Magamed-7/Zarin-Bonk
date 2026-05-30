from django.contrib import messages
from django.shortcuts import redirect


def client_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'client':
            messages.error(request, 'Доступ только для клиентов.')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role not in ('manager', 'admin'):
            messages.error(request, 'Доступ только для менеджеров.')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'admin':
            messages.error(request, 'Доступ только для администраторов.')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper