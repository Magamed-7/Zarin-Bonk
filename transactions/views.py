from decimal import Decimal
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from banking.models import Account
from notifications.models import Notification
from budget.models import Budget, BudgetCategory
from .models import Transaction, PaymentTemplate
import datetime

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4, A6
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



TRANSACTION_CATEGORY_TO_BUDGET_CATEGORY = {
    'internet': 'Интернет',
    'phone': 'Связь',
    'utilities': 'ЖКХ',
    'shopping': 'Покупки',
    'food': 'Еда',
    'transport': 'Транспорт',
}


def update_budget(user, transaction_category_id, amount):
    if transaction_category_id not in TRANSACTION_CATEGORY_TO_BUDGET_CATEGORY:
        return
    
    budget_category_name = TRANSACTION_CATEGORY_TO_BUDGET_CATEGORY[transaction_category_id]
    
    try:
        budget_category = BudgetCategory.objects.get(name=budget_category_name)
    except BudgetCategory.DoesNotExist:
        return
    
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    budget = Budget.objects.filter(
        user=user,
        category=budget_category,
        month=current_month,
        year=current_year,
        is_deleted=False
    ).first()
    
    if budget:
        budget.current_amount += amount
        budget.save(update_fields=['current_amount'])


PROVIDERS = {
    'internet': [
        {'id': 'babilon_t', 'name': 'Babilon-T'},
        {'id': 'tojiktelecom', 'name': 'Tojiktelecom'},
        {'id': 'satn', 'name': 'Satn'},
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
    ],
    'shopping': [
        {'id': 'internet_shop', 'name': 'Интернет-магазин'},
        {'id': 'supermarket', 'name': 'Супермаркет'},
        {'id': 'electronics', 'name': 'Электроника'},
    ],
    'food': [
        {'id': 'restaurant', 'name': 'Ресторан'},
        {'id': 'cafe', 'name': 'Кафе'},
        {'id': 'delivery', 'name': 'Доставка еды'},
    ],
    'transport': [
        {'id': 'taxi', 'name': 'Такси'},
        {'id': 'metro', 'name': 'Метро'},
        {'id': 'bus', 'name': 'Автобус'},
    ],
}

CATEGORIES = {
    'internet': {'name': 'Интернет', 'icon': '🌐', 'requisite_label': 'Логин / Номер договора', 'placeholder': 'Введите ваш логин'},
    'phone': {'name': 'Мобильная связь', 'icon': '📱', 'requisite_label': 'Номер телефона', 'placeholder': '+992 9XXXXXXXX'},
    'utilities': {'name': 'ЖКХ', 'icon': '⚡', 'requisite_label': 'Лицевой счет', 'placeholder': 'Введите номер счета ЖКХ'},
    'shopping': {'name': 'Покупки', 'icon': '🛒', 'requisite_label': 'Номер заказа / Магазин', 'placeholder': 'Введите номер заказа'},
    'food': {'name': 'Еда', 'icon': '🍔', 'requisite_label': 'Ресторан / Кафе', 'placeholder': 'Введите название'},
    'transport': {'name': 'Транспорт', 'icon': '🚕', 'requisite_label': 'Номер поездки / Маршрут', 'placeholder': 'Введите детали'},
}

CATEGORIES_LIST = [
    {'id': 'internet', 'name': 'Интернет', 'icon': '🌐'},
    {'id': 'phone', 'name': 'Мобильная связь', 'icon': '📱'},
    {'id': 'utilities', 'name': 'ЖКХ', 'icon': '⚡'},
    {'id': 'shopping', 'name': 'Покупки', 'icon': '🛒'},
    {'id': 'food', 'name': 'Еда', 'icon': '🍔'},
    {'id': 'transport', 'name': 'Транспорт', 'icon': '🚕'},
]

# Helper function to register Cyrillic font
def get_pdf_font_name():
    font_name = 'Helvetica'
    # Windows system Arial font path
    font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arial.ttf')
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Arial', font_path))
            font_name = 'Arial'
        except Exception:
            pass
    return font_name

class ServicesView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'transactions/services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Account.objects.filter(user=self.request.user, is_active=True, is_deleted=False)
        context['templates'] = PaymentTemplate.objects.filter(user=self.request.user, is_deleted=False)
        context['categories'] = CATEGORIES_LIST
        return context

@login_required
def category_services_view(request, category_id):
    if category_id not in CATEGORIES:
        messages.error(request, 'Неверная категория услуг.')
        return redirect('transactions:services')
        
    user_accounts = Account.objects.filter(user=request.user, is_active=True, is_deleted=False)
    category_data = CATEGORIES[category_id]
    providers_list = PROVIDERS[category_id]
    
    initial_provider = request.GET.get('provider', '')
    initial_requisite = request.GET.get('requisite', '')
    initial_amount = request.GET.get('amount', '')
    
    return render(request, 'transactions/pay_service.html', {
        'accounts': user_accounts,
        'category_id': category_id,
        'category': category_data,
        'providers': providers_list,
        'initial_provider': initial_provider,
        'initial_requisite': initial_requisite,
        'initial_amount': initial_amount,
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

    provider_name = provider_id
    if category in PROVIDERS:
        for prov in PROVIDERS[category]:
            if prov['id'] == provider_id:
                provider_name = prov['name']
                break

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

    update_budget(request.user, category, amount)

    # Send Notification
    Notification.objects.create(
        user=request.user,
        title='Услуга оплачена',
        message=f'Списано {amount} {account.currency} за услугу {provider_name} (реквизит: {requisite}).',
        notification_type=Notification.NotificationType.TRANSACTION,
    )

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
    template = get_object_or_404(PaymentTemplate, id=template_id, user=request.user, is_deleted=False)
    account = Account.objects.filter(user=request.user, is_active=True, is_deleted=False).first()

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

    
    update_budget(request.user, template.category, template.amount)

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
    template = get_object_or_404(PaymentTemplate, id=template_id, user=request.user, is_deleted=False)
    name = template.name
    template.delete()
    messages.success(request, f'Шаблон "{name}" удален.')
    return redirect('transactions:services')

@login_required
def transaction_detail_view(request, transaction_id):
    tx = get_object_or_404(
        Transaction.objects.select_related('sender_account', 'receiver_account'),
        id=transaction_id,
        is_deleted=False
    )
    # Security check: User must be sender or receiver
    user_accounts = request.user.accounts.values_list('id', flat=True)
    is_sender = tx.sender_account_id in user_accounts if tx.sender_account else False
    is_receiver = tx.receiver_account_id in user_accounts if tx.receiver_account else False
    
    if not (is_sender or is_receiver or request.user.is_staff):
        messages.error(request, 'Доступ запрещен.')
        return redirect('banking:dashboard')
        
    return render(request, 'transactions/detail.html', {
        'tx': tx,
        'is_sender': is_sender,
        'is_receiver': is_receiver,
    })

@login_required
def repeat_transaction_view(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id)
    
    if tx.transaction_type == Transaction.TransactionType.TRANSFER:
        url = f"/banking/transfer/?sender_account={tx.sender_account_id if tx.sender_account else ''}&receiver_number={tx.receiver_account.account_number if tx.receiver_account else ''}&amount={tx.amount}&description={tx.description}"
        return redirect(url)
        
    elif tx.transaction_type == Transaction.TransactionType.PAYMENT:
        provider_name = ""
        requisite = ""
        desc = tx.description
        if "Реквизит:" in desc:
            parts = desc.split("Реквизит:")
            requisite = parts[1].replace(")", "").strip()
            provider_part = parts[0]
            if "Оплата услуги:" in provider_part:
                provider_name = provider_part.split("Оплата услуги:")[1].strip()
            elif "Быстрая оплата:" in provider_part:
                provider_name = provider_part.split("Быстрая оплата:")[1].strip()
                
        provider_id = provider_name.lower().replace(" ", "_")
        url = f"/transactions/services/{tx.category}/?provider={provider_id}&requisite={requisite}&amount={tx.amount}"
        return redirect(url)
        
    messages.error(request, 'Повторить операцию данного типа невозможно.')
    return redirect('banking:dashboard')

@login_required
def transaction_pdf_view(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id, is_deleted=False)
    
    # Check permissions
    user_accounts = request.user.accounts.values_list('id', flat=True)
    is_sender = tx.sender_account_id in user_accounts if tx.sender_account else False
    is_receiver = tx.receiver_account_id in user_accounts if tx.receiver_account else False
    if not (is_sender or is_receiver or request.user.is_staff):
        return HttpResponse("Доступ запрещен", status=403)
        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{tx.id}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A6, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    font_name = get_pdf_font_name()
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor('#ffd700'),
        alignment=1,
        spaceAfter=15
    )
    
    label_style = ParagraphStyle(
        'ReceiptLabel',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        textColor=colors.HexColor('#8a99ad')
    )
    
    value_style = ParagraphStyle(
        'ReceiptValue',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.black
    )
    
    story.append(Paragraph("ZarinPay Receipt", title_style))
    story.append(Spacer(1, 5))
    
    currency = tx.sender_account.currency if tx.sender_account else 'TJS'
    
    data = [
        [Paragraph("ID Операции:", label_style), Paragraph(str(tx.id), value_style)],
        [Paragraph("Дата и время:", label_style), Paragraph(tx.created_at.strftime('%d.%m.%Y %H:%M'), value_style)],
        [Paragraph("Тип операции:", label_style), Paragraph(tx.get_transaction_type_display(), value_style)],
        [Paragraph("Статус:", label_style), Paragraph(tx.get_status_display(), value_style)],
        [Paragraph("Счет отправителя:", label_style), Paragraph(tx.sender_account.account_number if tx.sender_account else "Внешний источник", value_style)],
        [Paragraph("Счет получателя:", label_style), Paragraph(tx.receiver_account.account_number if tx.receiver_account else "Внешний получатель", value_style)],
        [Paragraph("Описание:", label_style), Paragraph(tx.description or "-", value_style)],
        [Paragraph("Сумма:", label_style), Paragraph(f"{tx.amount:.2f} {currency}", value_style)],
    ]
    
    t = Table(data, colWidths=[100, 150])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#eeeeee')),
    ]))
    
    story.append(t)
    doc.build(story)
    return response

@login_required
def export_statement_pdf_view(request):
    account_id = request.GET.get('account_id')
    start_str = request.GET.get('start_date')
    end_str = request.GET.get('end_date')
    
    if not all([account_id, start_str, end_str]):
        messages.error(request, 'Укажите все параметры для выписки.')
        return redirect('banking:accounts')
        
    account = get_object_or_404(Account, id=account_id, user=request.user)
    
    try:
        start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Некорректный формат дат.')
        return redirect('banking:account_detail', account_id=account.id)
        
    sent = Transaction.objects.filter(sender_account=account, created_at__date__gte=start_date, created_at__date__lte=end_date, is_deleted=False)
    received = Transaction.objects.filter(receiver_account=account, created_at__date__gte=start_date, created_at__date__lte=end_date, is_deleted=False)
    transactions = (sent | received).order_by('created_at')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="statement_{account.account_number}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    font_name = get_pdf_font_name()
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        textColor=colors.HexColor('#ffd700'),
        alignment=0,
        spaceAfter=5
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=15
    )
    
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        fontWeight='bold',
        textColor=colors.white
    )
    
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.black
    )
    
    story.append(Paragraph("Выписка по счету ZarinPay", title_style))
    story.append(Paragraph(f"Счет: {account.account_number} ({account.get_account_type_display()})<br/>"
                           f"Период: {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}<br/>"
                           f"Владелец: {request.user.get_full_name() or request.user.username}", meta_style))
    
    table_data = [[
        Paragraph("Дата", th_style),
        Paragraph("Тип", th_style),
        Paragraph("Описание", th_style),
        Paragraph("Сумма", th_style),
        Paragraph("Статус", th_style)
    ]]
    
    for tx in transactions:
        is_out = tx.sender_account == account
        amount_sign = f"-{tx.amount:.2f}" if is_out else f"+{tx.amount:.2f}"
        table_data.append([
            Paragraph(tx.created_at.strftime('%d.%m.%Y %H:%M'), td_style),
            Paragraph(tx.get_transaction_type_display(), td_style),
            Paragraph(tx.description or "-", td_style),
            Paragraph(f"{amount_sign} {account.currency}", td_style),
            Paragraph(tx.get_status_display(), td_style)
        ])
        
    t = Table(table_data, colWidths=[90, 80, 200, 90, 70])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b1020')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    
    story.append(t)
    doc.build(story)
    return response
