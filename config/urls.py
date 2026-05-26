from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    path('admin/', admin.site.urls),
]

if not settings.DEBUG:
    urlpatterns += [
        re_path(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': settings.STATICFILES_DIRS[0]},
        ),
    ]
