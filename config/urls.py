from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf.urls.static import static
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("<html><body style='background:#0a0a1a;color:#ffd700;font-size:3rem;text-align:center;padding:2rem;'><h1>TEST PAGE WORKS!</h1><p>ZarinPay server is up!</p><a href='/' style='color:white;'>Go to landing page</a></body></html>")

def robots_txt_view(request):
    from django.template.loader import render_to_string
    content = render_to_string('robots.txt', request=request)
    return HttpResponse(content, content_type='text/plain')

urlpatterns = [
    path('test/', test_view, name='test'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contacts/', TemplateView.as_view(template_name='contacts.html'), name='contacts'),
    path('licenses/', TemplateView.as_view(template_name='licenses.html'), name='licenses'),
    path('policy/', TemplateView.as_view(template_name='policy.html'), name='policy'),
    path('security/', TemplateView.as_view(template_name='security.html'), name='security'),
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
