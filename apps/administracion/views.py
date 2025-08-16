from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import Documento, Ley, SubArticulo, TipoDocumento, LogAcceso
from .forms import DocumentoForm


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal para administradores"""
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_documentos'] = Documento.objects.filter(activo=True).count()
        context['total_descargas'] = LogAcceso.objects.filter(tipo_acceso='DESCARGA').count()
        context['total_visualizaciones'] = LogAcceso.objects.filter(tipo_acceso='VISUALIZACION').count()
        context['documentos_pendientes'] = Documento.objects.filter(activo=False).count()
        
        # Documentos recientes
        context['documentos_recientes'] = Documento.objects.filter(
            activo=True
        ).order_by('-fecha_subida')[:5]
        
        # Documentos más descargados
        documentos_populares = Documento.objects.filter(
            activo=True
        ).annotate(
            num_descargas=Count('logs_acceso', filter=Q(logs_acceso__tipo_acceso='DESCARGA'))
        ).order_by('-num_descargas')[:5]
        context['documentos_populares'] = documentos_populares
        
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
        
        # Filtros
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
    
    def form_valid(self, form):
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
    
    def form_valid(self, form):
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