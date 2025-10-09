from django.urls import path
from . import views

app_name = 'publico'

urlpatterns = [
    # Página principal
    path('', views.HomeView.as_view(), name='home'),
    
    # Navegación por leyes (mantener para URLs directas)
    path('ley/<int:ley_id>/', views.LeyDetailView.as_view(), name='ley_detail'),
    path('subarticulo/<int:subarticulo_id>/', views.SubArticuloDetailView.as_view(), name='subarticulo_detail'),
    
    # Nuevas APIs para navegación dinámica
    path('api/ley/<int:ley_id>/content/', views.LeyContentAPIView.as_view(), name='api_ley_content'),
    path('api/subarticulo/<int:subarticulo_id>/content/', views.SubArticuloContentAPIView.as_view(), name='api_subarticulo_content'),
    
    # Descarga y visualización de documentos
    path('documento/<int:documento_id>/descargar/', views.DescargarDocumentoView.as_view(), name='descargar_documento'),
    path('documento/<int:documento_id>/ver/', views.VisualizarDocumentoView.as_view(), name='visualizar_documento'),
]