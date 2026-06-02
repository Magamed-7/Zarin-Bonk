import random
import string
from datetime import date, timedelta
import os 
import uuid

from dateutil.relativedelta import relativedelta
 
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone
 
from banking.models import Account, Card
from notifications.models import Notification
from .forms import LoginForm, RegisterForm, TwoFactorForm
from .models import LoginHistory
from .decorators import client_required, manager_required, admin_required


User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('banking:dashboard') 

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()

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

        Notification.objects.create(
            user=user,
            title='Добро пожаловать в ZarinPay!',
            message='Ваш счёт и виртуальная карта успешно созданы.',
            notification_type=Notification.NotificationType.SYSTEM,
        )

        login(request, user)
        send_verification_email(user, request)
        messages.success(request, f'Добро пожаловать, {user.first_name}!')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html', {'form': form})




def send_verification_email(user, request):
    token = str(uuid.uuid4())
    cache.set(f'email_verify_{token}', user.id, 24 * 60 * 60) 

    verify_url = request.build_absolute_uri(
        f'/accounts/verify-email/{token}/'
    )

    send_mail(
        subject='ZarinPay — подтвердите email',
        message=(
            f'Здравствуйте, {user.first_name}!\n\n'
            f'Для подтверждения email перейдите по ссылке:\n{verify_url}\n\n'
            'Ссылка действительна 24 часа.'
        ),
        from_email='noreply@zarinpay.tj',
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_email_view(request, token):
    user_id = cache.get(f'email_verify_{token}')

    if not user_id:
        return render(request, 'accounts/verify_email.html', {'invalid': True})

    user = User.objects.filter(id=user_id).first()
    if not user:
        return render(request, 'accounts/verify_email.html', {'invalid': True})

    if user.is_verified:
        return render(request, 'accounts/verify_email.html', {'already': True})

    user.is_verified = True
    user.save()
    cache.delete(f'email_verify_{token}')

    Notification.objects.create(
        user=user,
        title='Email подтверждён',
        message='Ваш email успешно подтверждён.',
        notification_type=Notification.NotificationType.SYSTEM,
    )

    return render(request, 'accounts/verify_email.html', {'success': True})


def resend_verification_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.user.is_verified:
        messages.info(request, 'Ваш email уже подтверждён.')
        return redirect('accounts:profile')

    send_verification_email(request.user, request)
    messages.success(request, 'Письмо отправлено повторно. Проверьте почту.')
    return redirect('accounts:profile')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('banking:dashboard') 

    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()


    attempts_key = f'login_attempts_{ip}'
    lockout_key  = f'login_lockout_{ip}'

   
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
            
            cache.delete(lockout_key)
            cache.delete(attempts_key)

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email    = form.cleaned_data['email']
        password = form.cleaned_data['password']

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
            next_url = request.GET.get('next') or 'banking:dashboard' 
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
    resend_wait     = cache.get(resend_key)  
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
 
            return redirect('banking:dashboard') 
 
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




def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
 
        if not email:
            messages.error(request, 'Введите email.')
        else:
            user = User.objects.filter(email=email).first()
 
            if user is None:
                messages.success(request, 'Если email зарегистрирован — код отправлен.')
            else:
                code = ''.join(random.choices(string.digits, k=6))
                cache.set(f'reset_code_{user.id}',  code,    10 * 60)  # 10 минут
                cache.set(f'reset_user_{email}', user.id, 10 * 60)
 
                send_mail(
                    subject='ZarinPay — восстановление пароля',
                    message=f'Ваш код для сброса пароля: {code}\n\nКод действителен 10 минут.',
                    from_email='noreply@zarinpay.tj',
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Если email зарегистрирован — код отправлен.')
 
            request.session['reset_email'] = email
            return redirect('accounts:password_reset_verify')
 
    return render(request, 'accounts/forgot_password.html')
 
 
def password_reset_verify_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('accounts:forgot_password')
 
    user = User.objects.filter(email=email).first()
 
    if request.method == 'POST':
        entered_code = request.POST.get('code', '').strip()
 
        if user is None:
            messages.error(request, 'Неверный или просроченный код.')
        else:
            saved_code = cache.get(f'reset_code_{user.id}')
 
            if saved_code and entered_code == saved_code:
                cache.delete(f'reset_code_{user.id}')
                request.session['reset_verified_user_id'] = user.id
                return redirect('accounts:password_reset_new')
            else:
                messages.error(request, 'Неверный или просроченный код.')
 
    return render(request, 'accounts/password_reset_verify.html', {'email': email})
 
 
def password_reset_new_view(request):
    user_id = request.session.get('reset_verified_user_id')
    if not user_id:
        return redirect('accounts:forgot_password')
 
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return redirect('accounts:forgot_password')
 
    if request.method == 'POST':
        password         = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
 
        if len(password) < 8:
            messages.error(request, 'Пароль должен быть не менее 8 символов.')
        elif password != password_confirm:
            messages.error(request, 'Пароли не совпадают.')
        else:
            user.set_password(password)
            user.save()
 
            # Чистим сессию
            request.session.pop('reset_email', None)
            request.session.pop('reset_verified_user_id', None)
 
            Notification.objects.create(
                user=user,
                title='Пароль изменён',
                message='Ваш пароль был успешно изменён.',
                notification_type=Notification.NotificationType.SECURITY,
            )
 
            messages.success(request, 'Пароль успешно изменён! Войдите с новым паролем.')
            return redirect('accounts:login')
 
    return render(request, 'accounts/password_reset_new.html')




@login_required
def profile_view(request):
    user = request.user
    login_history = LoginHistory.objects.filter(user=user)[:10]
 
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        
        
        if avatar and not 'first_name' in request.POST:
            if user.avatar and os.path.isfile(user.avatar.path):
                os.remove(user.avatar.path)
            user.avatar = avatar
            user.save()
            messages.success(request, 'Фото профиля успешно обновлено.')
            return redirect('accounts:profile')
            
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        address    = request.POST.get('address', '').strip()
 
        if not first_name or not last_name:
            messages.error(request, 'Имя и фамилия обязательны.')
        else:
            user.first_name = first_name
            user.last_name  = last_name
            user.phone      = phone
            user.address    = address
 
            if avatar:
                if user.avatar and os.path.isfile(user.avatar.path):
                    os.remove(user.avatar.path)
                user.avatar = avatar
 
            user.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('accounts:profile')
 
    return render(request, 'accounts/profile.html', {
        'user': user,
        'login_history': login_history,
    })
 
 


@login_required
def delete_account_view(request):
    user = request.user
    
    if request.method == 'POST':
        user.delete()
        logout(request)
        messages.success(request, 'Ваш аккаунт успешно удалён.')
        return redirect('landing')
    
    return render(request, 'accounts/delete_account.html', {'user': user})


@login_required
def change_password_view(request):
    user = request.user
 
    if request.method == 'POST':
        old_password     = request.POST.get('old_password', '')
        new_password     = request.POST.get('new_password', '')
        password_confirm = request.POST.get('password_confirm', '')
 
        if not user.check_password(old_password):
            messages.error(request, 'Старый пароль введён неверно.')
 
        elif len(new_password) < 8:
            messages.error(request, 'Новый пароль должен быть не менее 8 символов.')
 
        elif new_password == old_password:
            messages.error(request, 'Новый пароль совпадает со старым.')
 
        elif new_password != password_confirm:
            messages.error(request, 'Пароли не совпадают.')
 
        else:
            user.set_password(new_password)
            user.save()
 
            login(request, user)
 
            Notification.objects.create(
                user=user,
                title='Пароль изменён',
                message='Ваш пароль был успешно изменён. Если это были не вы — обратитесь в поддержку.',
                notification_type=Notification.NotificationType.SECURITY,
            )
 
            send_mail(
                subject='ZarinPay — пароль изменён',
                message=(
                    f'Здравствуйте, {user.first_name}!\n\n'
                    'Ваш пароль в ZarinPay был успешно изменён.\n\n'
                    'Если это были не вы — немедленно обратитесь в службу поддержки.'
                ),
                from_email='noreply@zarinpay.tj',
                recipient_list=[user.email],
                fail_silently=False,
            )
 
            messages.success(request, 'Пароль успешно изменён!')
            return redirect('accounts:change_password')
 
    return render(request, 'accounts/change_password.html')