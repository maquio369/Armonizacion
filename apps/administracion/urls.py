from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'administracion'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Gestión de documentos
    path('documentos/', views.DocumentoListView.as_view(), name='documento_list'),
    path('documentos/nuevo/', views.DocumentoCreateView.as_view(), name='documento_create'),
    path('documentos/<int:pk>/editar/', views.DocumentoUpdateView.as_view(), name='documento_update'),
    path('documentos/<int:pk>/eliminar/', views.DocumentoDeleteView.as_view(), name='documento_delete'),
    
    # API endpoints
    path('api/tipo-documento/<int:tipo_id>/periodicidad/', views.TipoDocumentoPeriodicidadAPIView.as_view(), name='api_tipo_documento_periodicidad'),
    

    
    # Autenticación personalizada
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]