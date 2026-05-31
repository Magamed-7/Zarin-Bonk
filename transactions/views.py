from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from banking.models import Account
from notifications.models import Notification
from .models import Transaction, PaymentTemplate

PROVIDERS = {
    'internet': [
        {'id': 'babilon_t', 'name': 'Babilon-T'},
        {'id': 'tojiktelecom', 'name': 'Tojiktelecom'},
        {'id': 'satn', 'name': 'Satn'},
        {'id': 'megafon', 'name': 'MegaFon'},
        {'id': 'zet_mobile', 'name': 'ZET-Mobile'},
    ],
    'phone': [
        {'id': 'megafon', 'name': 'MegaFon'},
        {'id': 'tcell', 'name': 'Tcell'},
        {'id': 'babilon_m', 'name': 'Babilon-M'},
        {'id': 'zet_mobile', 'name': 'ZET-Mobile'},
    ],
    'utilities': [
        {'id': 'barki_tojik', 'name': 'Барки Точик (Электроэнергия)'},
        {'id': 'vodokanal', 'name': 'Душанбеводоканал (Вода)'},
        {'id': 'communal', 'name': 'Коммунальные услуги'},
    ]
}

CATEGORIES = {
    'internet': {'name': 'Интернет', 'icon': '🌐', 'requisite_label': 'Логин / Номер договора', 'placeholder': 'Введите ваш логин'},
    'phone': {'name': 'Мобильная связь', 'icon': '📱', 'requisite_label': 'Номер телефона', 'placeholder': '+992 9XXXXXXXX'},
    'utilities': {'name': 'ЖКХ', 'icon': '⚡', 'requisite_label': 'Лицевой счет', 'placeholder': 'Введите номер счета ЖКХ'},
}

CATEGORIES_LIST = [
    {'id': 'internet', 'name': 'Интернет', 'icon': '🌐'},
    {'id': 'phone', 'name': 'Мобильная связь', 'icon': '📱'},
    {'id': 'utilities', 'name': 'ЖКХ', 'icon': '⚡'},
]

@login_required
def services_view(request):
    user_accounts = Account.objects.filter(user=request.user, is_active=True)
    templates = PaymentTemplate.objects.filter(user=request.user)
    
    return render(request, 'transactions/services.html', {
        'accounts': user_accounts,
        'templates': templates,
        'categories': CATEGORIES_LIST,
    })

@login_required
def category_services_view(request, category_id):
    if category_id not in CATEGORIES:
        messages.error(request, 'Неверная категория услуг.')
        return redirect('transactions:services')
        
    user_accounts = Account.objects.filter(user=request.user, is_active=True)
    category_data = CATEGORIES[category_id]
    providers_list = PROVIDERS[category_id]
    
    return render(request, 'transactions/pay_service.html', {
        'accounts': user_accounts,
        'category_id': category_id,
        'category': category_data,
        'providers': providers_list,
    })

@login_required
def pay_service_view(request):
    if request.method != 'POST':
        return redirect('transactions:services')

    account_id = request.POST.get('account')
    category = request.POST.get('category')
    provider_id = request.POST.get('provider')
    requisite = request.POST.get('requisite', '').strip()
    amount_str = request.POST.get('amount', '').strip()
    save_template = request.POST.get('save_template') == 'on'
    template_name = request.POST.get('template_name', '').strip()

    if not all([account_id, category, provider_id, requisite, amount_str]):
        messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
        return redirect('transactions:services')

    account = get_object_or_404(Account, id=account_id, user=request.user, is_active=True)
    
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        messages.error(request, 'Некорректная сумма платежа.')
        return redirect('transactions:services')

    if account.balance < amount:
        messages.error(request, f'Недостаточно средств. На балансе: {account.balance} {account.currency}.')
        return redirect('transactions:services')

    # Find provider display name
    provider_name = provider_id
    if category in PROVIDERS:
        for prov in PROVIDERS[category]:
            if prov['id'] == provider_id:
                provider_name = prov['name']
                break

    # Perform payment
    account.balance -= amount
    account.save()

    # Create Transaction
    Transaction.objects.create(
        sender_account=account,
        receiver_account=None,
        amount=amount,
        transaction_type=Transaction.TransactionType.PAYMENT,
        status=Transaction.Status.COMPLETED,
        category=category,
        description=f"Оплата услуги: {provider_name} (Реквизит: {requisite})"
    )

    # Send Notification
    Notification.objects.create(
        user=request.user,
        title='Услуга оплачена',
        message=f'Списано {amount} {account.currency} за услугу {provider_name} (реквизит: {requisite}).',
        notification_type=Notification.NotificationType.TRANSACTION,
    )

    # Save as template if requested
    if save_template:
        name = template_name if template_name else f"Шаблон {provider_name}"
        PaymentTemplate.objects.create(
            user=request.user,
            name=name,
            category=category,
            service_provider=provider_name,
            requisite=requisite,
            amount=amount
        )
        messages.success(request, f'Шаблон "{name}" успешно сохранен.')

    messages.success(request, f'Платеж на сумму {amount} {account.currency} успешно выполнен!')
    return redirect('transactions:services')

@login_required
def quick_pay_view(request, template_id):
    template = get_object_or_404(PaymentTemplate, id=template_id, user=request.user)
    account = Account.objects.filter(user=request.user, is_active=True).first()

    if not account:
        messages.error(request, 'У вас нет активных счетов для оплаты.')
        return redirect('transactions:services')

    if account.balance < template.amount:
        messages.error(request, f'Недостаточно средств на счете {account.account_number} для оплаты по шаблону.')
        return redirect('transactions:services')

    # Process payment
    account.balance -= template.amount
    account.save()

    # Create Transaction
    Transaction.objects.create(
        sender_account=account,
        receiver_account=None,
        amount=template.amount,
        transaction_type=Transaction.TransactionType.PAYMENT,
        status=Transaction.Status.COMPLETED,
        category=template.category,
        description=f"Быстрая оплата: {template.service_provider} (Реквизит: {template.requisite})"
    )

    # Send Notification
    Notification.objects.create(
        user=request.user,
        title='Быстрая оплата выполнена',
        message=f'Списано {template.amount} {account.currency} за {template.service_provider} по шаблону "{template.name}".',
        notification_type=Notification.NotificationType.TRANSACTION,
    )

    messages.success(request, f'Быстрая оплата по шаблону "{template.name}" выполнена!')
    return redirect('transactions:services')

@login_required
def delete_template_view(request, template_id):
    template = get_object_or_404(PaymentTemplate, id=template_id, user=request.user)
    name = template.name
    template.delete()
    messages.success(request, f'Шаблон "{name}" удален.')
    return redirect('transactions:services')
