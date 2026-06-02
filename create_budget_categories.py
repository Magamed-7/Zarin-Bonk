import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from budget.models import BudgetCategory

categories = [
    {'name': 'Покупки', 'icon': '🛒', 'color': '#FF6384'},
    {'name': 'Еда', 'icon': '🍔', 'color': '#36A2EB'},
    {'name': 'Транспорт', 'icon': '🚕', 'color': '#FFCE56'},
    {'name': 'Интернет', 'icon': '🌐', 'color': '#4BC0C0'},
    {'name': 'Связь', 'icon': '📱', 'color': '#9966FF'},
    {'name': 'ЖКХ', 'icon': '⚡', 'color': '#FF9F40'},
    {'name': 'Прочее', 'icon': '📄', 'color': '#C9CBCF'},
]

for cat in categories:
    BudgetCategory.objects.get_or_create(
        name=cat['name'],
        defaults={'icon': cat['icon'], 'color': cat['color']}
    )
    print(f"Создана категория: {cat['icon']} {cat['name']}")

print("\nВсе категории созданы успешно!")
