import random
import string
from datetime import date, timedelta
 
from dateutil.relativedelta import relativedelta
 
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone
 
from banking.models import Account, Card
from notifications.models import Notification
from .forms import LoginForm, RegisterForm, TwoFactorForm
from .models import LoginHistory


User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('landing')  # TODO: заменить на 'banking:dashboard'

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()

        # Создаём счёт и карту автоматически
        account = Account.objects.create(
            user=user,
            account_type=Account.AccountType.CHECKING,
            currency=Account.Currency.TJS,
        )
        Card.objects.create(
            account=account,
            expiry_date=date.today() + relativedelta(years=3),
            card_type=Card.CardType.VIRTUAL,
        )

        # Приветственное уведомление
        Notification.objects.create(
            user=user,
            title='Добро пожаловать в ZarinPay!',
            message='Ваш счёт и виртуальная карта успешно созданы.',
            notification_type=Notification.NotificationType.SYSTEM,
        )

        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.first_name}!')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('landing')  # TODO: заменить на 'banking:dashboard'

    # Получаем IP пользователя
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()

    # Ключи для кэша
    attempts_key = f'login_attempts_{ip}'
    lockout_key  = f'login_lockout_{ip}'

    # Проверяем блокировку
    locked_until = cache.get(lockout_key)
    if locked_until:
        remaining_seconds = (locked_until - timezone.now()).total_seconds()
        if remaining_seconds > 0:
            minutes = int(remaining_seconds // 60) + 1
            return render(request, 'accounts/login.html', {
                'form': LoginForm(),
                'lockout_minutes': minutes,
            })
        else:
            # Время блокировки вышло — сбрасываем
            cache.delete(lockout_key)
            cache.delete(attempts_key)

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email    = form.cleaned_data['email']
        password = form.cleaned_data['password']

        # Ищем пользователя по email, так как authenticate работает по username
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            cache.delete(attempts_key)
            cache.delete(lockout_key)

            LoginHistory.objects.create(
                user=user,
                ip_address=ip,
                browser=request.META.get('HTTP_USER_AGENT', '')[:200],
                device='Web',
                is_successful=True,
            )

            Notification.objects.create(
                user=user,
                title='Новый вход в аккаунт',
                message=f'Вход выполнен с IP {ip}.',
                notification_type=Notification.NotificationType.SECURITY,
            )

            login(request, user)
            next_url = request.GET.get('next') or 'landing'  # TODO: 'banking:dashboard'
            return redirect(next_url)

        else:
            attempts = cache.get(attempts_key, 0) + 1
            cache.set(attempts_key, attempts, 15 * 60)

            try:
                failed_user = User.objects.get(email=email)
                LoginHistory.objects.create(
                    user=failed_user,
                    ip_address=ip,
                    browser=request.META.get('HTTP_USER_AGENT', '')[:200],
                    device='Web',
                    is_successful=False,
                )
            except User.DoesNotExist:
                pass

            # Блокируем после 5 неудачных попыток
            if attempts >= 5:
                cache.set(lockout_key, timezone.now() + timedelta(minutes=15), 15 * 60)
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'lockout_minutes': 15,
                })

            remaining = 5 - attempts
            form.add_error(None, f'Неверный email или пароль. Осталось попыток: {remaining}.')

    return render(request, 'accounts/login.html', {'form': form})



def verify_2fa_view(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
 
    user_id = cache.get(f'2fa_user_id_{ip}')
    if not user_id:
        messages.error(request, 'Сессия истекла. Войдите снова.')
        return redirect('accounts:login')
 
    resend_key      = f'2fa_resend_wait_{user_id}'
    resend_wait     = cache.get(resend_key)  # timestamp когда можно переотправить
    can_resend_in   = 0
    if resend_wait:
        seconds_left = (resend_wait - timezone.now()).total_seconds()
        can_resend_in = max(0, int(seconds_left))
 
    form = TwoFactorForm(request.POST or None)
 
    if request.method == 'POST' and form.is_valid():
        entered_code = form.cleaned_data['code']
        saved_code   = cache.get(f'2fa_code_{user_id}')
 
        if saved_code is None:
            return render(request, 'accounts/verify_2fa.html', {
                'form': form,
                'expired': True,
                'can_resend_in': 0,
            })
 
        if entered_code == saved_code:
            cache.delete(f'2fa_code_{user_id}')
            cache.delete(f'2fa_user_id_{ip}')
            cache.delete(resend_key)
 
            user = User.objects.get(id=user_id)
            login(request, user)
 
            LoginHistory.objects.create(
                user=user,
                ip_address=ip,
                browser=request.META.get('HTTP_USER_AGENT', '')[:200],
                device='Web',
                is_successful=True,
            )
            Notification.objects.create(
                user=user,
                title='Новый вход в аккаунт',
                message=f'Выполнен вход с IP {ip}.',
                notification_type=Notification.NotificationType.SECURITY,
            )
 
            return redirect('landing')  # TODO: заменить на 'banking:dashboard'
 
        else:
            form.add_error('code', 'Неверный код. Попробуйте ещё раз.')
 
    return render(request, 'accounts/verify_2fa.html', {
        'form': form,
        'can_resend_in': can_resend_in,
    })
 
 
def resend_2fa_view(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
 
    user_id = cache.get(f'2fa_user_id_{ip}')
    if not user_id:
        messages.error(request, 'Сессия истекла. Войдите снова.')
        return redirect('accounts:login')
 
    resend_key  = f'2fa_resend_wait_{user_id}'
    resend_wait = cache.get(resend_key)
 
    if resend_wait:
        seconds_left = int((resend_wait - timezone.now()).total_seconds())
        if seconds_left > 0:
            minutes = seconds_left // 60 + 1
            messages.warning(
                request,
                f'Повторно запросить код можно через {minutes} мин.'
            )
            return redirect('accounts:verify_2fa')
 
    # Можно переотправить — отправляем и ставим ожидание 3 минуты
    user = User.objects.get(id=user_id)
    _send_2fa_code(user, ip)
    messages.success(request, 'Новый код отправлен на ваш email.')
    return redirect('accounts:verify_2fa')
 
 

 
def _send_2fa_code(user, ip):
    code = ''.join(random.choices(string.digits, k=6))
 
    cache.set(f'2fa_code_{user.id}',    code,    5 * 60)
    cache.set(f'2fa_user_id_{ip}', user.id, 5 * 60)
    cache.set(f'2fa_resend_wait_{user.id}', timezone.now() + timedelta(minutes=3), 3 * 60)
 
    send_mail(
        subject='ZarinPay — код подтверждения',
        message=f'Ваш код для входа: {code}\n\nКод действителен 5 минут.',
        from_email='noreply@zarinpay.tj',
        recipient_list=[user.email],
        fail_silently=False,
    )
 


def logout_view(request):
    logout(request)
    return redirect('landing')