from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contacts/', TemplateView.as_view(template_name='contacts.html'), name='contacts'),
    path('admin/', admin.site.urls),
    path('administration/', include('administration.urls')),
    path('accounts/', include('accounts.urls')),
    path('banking/', include('banking.urls')),
    path('transactions/', include('transactions.urls')),
    path('budget/', include('budget.urls')),
    path('goals/', include('goals.urls')),
    path('loans/', include('loans.urls')),
    path('notifications/', include('notifications.urls')),
    path('support/', include('support.urls')),
    path('manager/', include('manager.urls')),
    path('ai-assistant/', include('ai_assistant.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': settings.STATICFILES_DIRS[0]},
        ),
    ]
