from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # Redirección de login
    path('login/', lambda request: redirect('/admin-panel/login/')),
    
    # Favicon
    path('favicon.ico', lambda request: redirect('/static/images/jamach-negro.png')),
    
    # URLs de la aplicación pública
    path('', include('apps.publico.urls')),
    
    # URLs de la aplicación administrativa
    path('admin-panel/', include('apps.administracion.urls')),
]

# Servir archivos media y estáticos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # En producción también servir archivos media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)