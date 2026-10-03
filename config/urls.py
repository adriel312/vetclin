from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('produtos/', include('apps.produtos.urls')),
    path('servicos/', include('apps.servicos.urls')),
    path('exames/', include('apps.exames.urls')),
    path('contato/', include('apps.contato.urls')),
]

# Em produção, /static/ e /media/ são servidos diretamente pelo Nginx.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
