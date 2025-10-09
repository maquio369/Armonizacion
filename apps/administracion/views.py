from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import Documento, Ley, SubArticulo, TipoDocumento, LogAcceso, PerfilUsuario
from .forms import DocumentoForm
from django.core.exceptions import PermissionDenied


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal para administradores"""
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtrar documentos según el tipo de usuario
        documentos_queryset = Documento.objects.all()
        if hasattr(self.request.user, 'perfil'):
            perfil = self.request.user.perfil
            if perfil.tipo_usuario == 'RECURSOS_MATERIALES':
                documentos_queryset = documentos_queryset.filter(
                    tipo_documento__subarticulo__nombre__icontains='inventario'
                ).filter(tipo_documento__subarticulo__nombre__icontains='físico')
            elif perfil.tipo_usuario == 'PLANEACION':
                documentos_queryset = documentos_queryset.exclude(
                    Q(tipo_documento__subarticulo__nombre__icontains='inventario') & 
                    Q(tipo_documento__subarticulo__nombre__icontains='físico')
                )
        
        # Estadísticas generales
        context['total_documentos'] = documentos_queryset.filter(activo=True).count()
        context['total_visualizaciones'] = LogAcceso.objects.filter(
            tipo_acceso='VISUALIZACION',
            documento__in=documentos_queryset
        ).count()
        context['documentos_pendientes'] = documentos_queryset.filter(activo=False).count()
        
        # Documentos recientes
        context['documentos_recientes'] = documentos_queryset.filter(
            activo=True
        ).order_by('-fecha_subida')[:5]
        
        # Documentos más vistos
        documentos_mas_vistos = documentos_queryset.filter(
            activo=True
        ).annotate(
            num_visualizaciones=Count('logs_acceso', filter=Q(logs_acceso__tipo_acceso='VISUALIZACION'))
        ).order_by('-num_visualizaciones')[:5]
        context['documentos_mas_vistos'] = documentos_mas_vistos
        
        # Distribución por ley
        distribucion_leyes = Ley.objects.annotate(
            num_documentos=Count('subarticulos__tipos_documento__documentos', 
                               filter=Q(subarticulos__tipos_documento__documentos__activo=True))
        ).order_by('-num_documentos')
        context['distribucion_leyes'] = distribucion_leyes
        
        return context


class DocumentoListView(LoginRequiredMixin, ListView):
    """Lista de documentos para administradores"""
    model = Documento
    template_name = 'admin/documento_list.html'
    context_object_name = 'documentos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Documento.objects.all().order_by('-fecha_subida')
        
        # Filtrar según el tipo de usuario
        if hasattr(self.request.user, 'perfil'):
            perfil = self.request.user.perfil
            if perfil.tipo_usuario == 'RECURSOS_MATERIALES':
                # Solo documentos del subarticulo inventarios físicos de bienes
                queryset = queryset.filter(
                    tipo_documento__subarticulo__nombre__icontains='inventario'
                ).filter(tipo_documento__subarticulo__nombre__icontains='físico')
            elif perfil.tipo_usuario == 'PLANEACION':
                # Todo excepto documentos del subarticulo inventarios físicos de bienes
                queryset = queryset.exclude(
                    Q(tipo_documento__subarticulo__nombre__icontains='inventario') & 
                    Q(tipo_documento__subarticulo__nombre__icontains='físico')
                )
        
        # Filtros adicionales
        ley_id = self.request.GET.get('ley')
        subarticulo_id = self.request.GET.get('subarticulo')
        año = self.request.GET.get('año')
        activo = self.request.GET.get('activo')
        
        if ley_id:
            queryset = queryset.filter(tipo_documento__subarticulo__ley_id=ley_id)
        
        if subarticulo_id:
            queryset = queryset.filter(tipo_documento__subarticulo_id=subarticulo_id)
        
        if año:
            queryset = queryset.filter(año=año)
        
        if activo:
            queryset = queryset.filter(activo=activo == 'true')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leyes'] = Ley.objects.filter(activa=True)
        context['años'] = range(2024, 2031)
        return context


class DocumentoCreateView(LoginRequiredMixin, CreateView):
    """Crear nuevo documento"""
    model = Documento
    form_class = DocumentoForm
    template_name = 'admin/documento_form.html'
    success_url = reverse_lazy('administracion:documento_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Verificar permisos antes de guardar
        if hasattr(self.request.user, 'perfil'):
            perfil = self.request.user.perfil
            if not perfil.puede_subir_documento(form.instance.tipo_documento):
                messages.error(self.request, 'No tiene permisos para subir este tipo de documento.')
                return self.form_invalid(form)
        
        form.instance.usuario_subida = self.request.user
        messages.success(self.request, 'Documento creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el documento. Revise los campos.')
        return super().form_invalid(form)


class DocumentoUpdateView(LoginRequiredMixin, UpdateView):
    """Editar documento existente"""
    model = Documento
    form_class = DocumentoForm
    template_name = 'admin/documento_form.html'
    success_url = reverse_lazy('administracion:documento_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Verificar permisos antes de actualizar
        if hasattr(self.request.user, 'perfil'):
            perfil = self.request.user.perfil
            if not perfil.puede_subir_documento(form.instance.tipo_documento):
                messages.error(self.request, 'No tiene permisos para editar este tipo de documento.')
                return self.form_invalid(form)
        
        messages.success(self.request, 'Documento actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el documento. Revise los campos.')
        return super().form_invalid(form)


class DocumentoDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar documento"""
    model = Documento
    template_name = 'admin/documento_confirm_delete.html'
    success_url = reverse_lazy('administracion:documento_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Documento eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class EstadisticasView(LoginRequiredMixin, TemplateView):
    """Vista de estadísticas detalladas"""
    template_name = 'admin/estadisticas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas por mes (últimos 12 meses)
        from django.utils import timezone
        from datetime import timedelta
        import calendar
        
        fecha_inicio = timezone.now() - timedelta(days=365)
        
        # Descargas por mes
        descargas_mensuales = {}
        for i in range(12):
            fecha = timezone.now() - timedelta(days=30*i)
            mes_nombre = calendar.month_name[fecha.month]
            año = fecha.year
            
            descargas = LogAcceso.objects.filter(
                tipo_acceso='DESCARGA',
                fecha_acceso__year=año,
                fecha_acceso__month=fecha.month
            ).count()
            
            descargas_mensuales[f"{mes_nombre} {año}"] = descargas
        
        context['descargas_mensuales'] = descargas_mensuales
        
        # Top 10 documentos más descargados
        top_documentos = Documento.objects.annotate(
            num_descargas=Count('logs_acceso', filter=Q(logs_acceso__tipo_acceso='DESCARGA'))
        ).order_by('-num_descargas')[:10]
        
        context['top_documentos'] = top_documentos
        
        # Estadísticas por IP (para detectar uso intensivo)
        top_ips = LogAcceso.objects.values('ip_address').annotate(
            total_accesos=Count('id')
        ).order_by('-total_accesos')[:10]
        
        context['top_ips'] = top_ips
        
        return context


class TipoDocumentoPeriodicidadAPIView(LoginRequiredMixin, View):
    """API para obtener la periodicidad de un tipo de documento"""
    
    def get(self, request, tipo_id):
        try:
            tipo_documento = get_object_or_404(TipoDocumento, id=tipo_id, activo=True)
            return JsonResponse({
                'periodicidad': tipo_documento.subarticulo.periodicidad,
                'nombre': tipo_documento.nombre,
                'subarticulo': tipo_documento.subarticulo.nombre
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=404)