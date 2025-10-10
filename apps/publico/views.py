from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView, View
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.template.loader import render_to_string
from apps.administracion.models import Ley, SubArticulo, TipoDocumento, Documento, LogAcceso
from datetime import datetime
import os


class HomeView(TemplateView):
    """Vista principal que muestra todas las leyes disponibles"""
    template_name = 'publico/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cargar leyes con sus sub-artículos
        context['leyes'] = Ley.objects.filter(activa=True).prefetch_related(
            'subarticulos'
        ).order_by('orden')
        
        # Estadísticas generales
        context['total_documentos'] = Documento.objects.filter(activo=True).count()
        context['total_descargas'] = LogAcceso.objects.filter(tipo_acceso='DESCARGA').count()
        
        return context


class LeyDetailView(DetailView):
    """Vista detalle de una ley específica con sus sub-artículos"""
    model = Ley
    template_name = 'publico/ley_detail.html'
    context_object_name = 'ley'
    pk_url_kwarg = 'ley_id'
    
    def get_queryset(self):
        return Ley.objects.filter(activa=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subarticulos'] = self.object.subarticulos.filter(activo=True).order_by('orden')
        return context


class SubArticuloDetailView(DetailView):
    """Vista detalle de un sub-artículo con sus documentos"""
    model = SubArticulo
    template_name = 'publico/subarticulo_detail.html'
    context_object_name = 'subarticulo'
    pk_url_kwarg = 'subarticulo_id'
    
    def get_queryset(self):
        return SubArticulo.objects.filter(activo=True)
    
    def get(self, request, *args, **kwargs):
        # Si no hay parámetro de año, redirigir al año actual
        if 'año' not in request.GET:
            año_actual = datetime.now().year
            return redirect(f'{request.path}?año={año_actual}')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leyes'] = Ley.objects.filter(activa=True).order_by('orden')
        
        # Obtener tipos de documento del sub-artículo
        tipos_documento = self.object.tipos_documento.filter(activo=True).order_by('orden')
        
        # Obtener años disponibles
        años_disponibles = Documento.objects.filter(
            tipo_documento__subarticulo=self.object,
            activo=True
        ).values_list('año', flat=True).distinct().order_by('-año')
        
        # Agrupar documentos por año y tipo
        documentos_agrupados = {}
        for año in años_disponibles:
            documentos_agrupados[año] = {}
            
            for tipo_doc in tipos_documento:
                if self.object.periodicidad == 'ANUAL':
                    # Para documentos anuales
                    documento = Documento.objects.filter(
                        tipo_documento=tipo_doc,
                        año=año,
                        activo=True
                    ).first()
                    documentos_agrupados[año][tipo_doc] = {
                        'ANUAL': documento
                    }
                else:
                    # Para documentos trimestrales
                    trimestres = ['T1', 'T2', 'T3', 'T4']
                    documentos_agrupados[año][tipo_doc] = {}
                    
                    for trimestre in trimestres:
                        documento = Documento.objects.filter(
                            tipo_documento=tipo_doc,
                            año=año,
                            trimestre=trimestre,
                            activo=True
                        ).first()
                        documentos_agrupados[año][tipo_doc][trimestre] = documento
        
        context['tipos_documento'] = tipos_documento
        context['años_disponibles'] = años_disponibles
        context['documentos_agrupados'] = documentos_agrupados
        context['trimestres'] = ['T1', 'T2', 'T3', 'T4']
        context['current_year'] = datetime.now().year
        
        # Obtener fecha de última actualización para el año seleccionado
        año_seleccionado = int(self.request.GET.get('año', datetime.now().year))
        documentos_año = Documento.objects.filter(
            tipo_documento__subarticulo=self.object,
            año=año_seleccionado,
            activo=True
        )
        
        # Obtener la fecha más reciente entre subida y modificación
        ultima_fecha = None
        for doc in documentos_año:
            fecha_mas_reciente = max(doc.fecha_subida, doc.fecha_modificacion)
            if not ultima_fecha or fecha_mas_reciente > ultima_fecha:
                ultima_fecha = fecha_mas_reciente
        
        context['ultima_actualizacion'] = ultima_fecha
        
        return context


class DescargarDocumentoView(View):
    """Vista para descargar documentos PDF"""
    
    def get(self, request, documento_id):
        documento = get_object_or_404(Documento, id=documento_id, activo=True)
        
        # Verificar que el archivo existe
        if not documento.archivo or not os.path.exists(documento.archivo.path):
            messages.error(request, 'El archivo solicitado no está disponible.')
            raise Http404("Archivo no encontrado")
        
        # Registrar el acceso
        self._registrar_acceso(request, documento, 'DESCARGA')
        
        # Servir el archivo
        try:
            with open(documento.archivo.path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{documento.get_nombre_archivo()}"'
                return response
        except Exception as e:
            messages.error(request, 'Error al descargar el archivo.')
            raise Http404("Error al acceder al archivo")
    
    def _registrar_acceso(self, request, documento, tipo_acceso):
        """Registra el acceso al documento"""
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        LogAcceso.objects.create(
            documento=documento,
            ip_address=ip_address,
            user_agent=user_agent,
            tipo_acceso=tipo_acceso
        )
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class VisualizarDocumentoView(View):
    """Vista para visualizar documentos PDF en el navegador"""
    
    def get(self, request, documento_id):
        documento = get_object_or_404(Documento, id=documento_id, activo=True)
        
        # Verificar que el archivo existe
        if not documento.archivo or not os.path.exists(documento.archivo.path):
            messages.error(request, 'El archivo solicitado no está disponible.')
            raise Http404("Archivo no encontrado")
        
        # Registrar el acceso
        self._registrar_acceso(request, documento, 'VISUALIZACION')
        
        # Servir el archivo para visualización
        try:
            with open(documento.archivo.path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{documento.get_nombre_archivo()}"'
                return response
        except Exception as e:
            messages.error(request, 'Error al visualizar el archivo.')
            raise Http404("Error al acceder al archivo")
    
    def _registrar_acceso(self, request, documento, tipo_acceso):
        """Registra el acceso al documento"""
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        LogAcceso.objects.create(
            documento=documento,
            ip_address=ip_address,
            user_agent=user_agent,
            tipo_acceso=tipo_acceso
        )
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DocumentosAPIView(View):
    """API para obtener documentos de forma dinámica (para filtros AJAX)"""
    
    def get(self, request):
        ley_id = request.GET.get('ley_id')
        subarticulo_id = request.GET.get('subarticulo_id')
        año = request.GET.get('año')
        
        documentos = Documento.objects.filter(activo=True)
        
        if ley_id:
            documentos = documentos.filter(tipo_documento__subarticulo__ley_id=ley_id)
        
        if subarticulo_id:
            documentos = documentos.filter(tipo_documento__subarticulo_id=subarticulo_id)
        
        if año:
            documentos = documentos.filter(año=año)
        
        # Formatear respuesta
        data = []
        for doc in documentos:
            data.append({
                'id': doc.id,
                'tipo_documento': doc.tipo_documento.nombre,
                'año': doc.año,
                'trimestre': doc.trimestre,
                'titulo': doc.titulo_personalizado or doc.tipo_documento.nombre,
                'url_descarga': f'/documento/{doc.id}/descargar/',
                'tamaño': doc.get_tamaño_legible(),
                'fecha_subida': doc.fecha_subida.strftime('%d/%m/%Y')
            })
        
        return JsonResponse({'documentos': data})


# ⚠️ CORRECCIÓN: Estas clases deben estar al mismo nivel, no dentro de DocumentosAPIView
class LeyContentAPIView(View):
    """API para cargar contenido de una ley específica"""
    
    def get(self, request, ley_id):
        try:
            ley = get_object_or_404(Ley, id=ley_id, activa=True)
            subarticulos = ley.subarticulos.filter(activo=True).order_by('orden')
            
            # Renderizar template parcial
            html_content = render_to_string('publico/partials/ley_content.html', {
                'ley': ley,
                'subarticulos': subarticulos
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'title': ley.nombre,
                'content': html_content,
                'breadcrumb': {
                    'ley': ley.nombre,
                    'subarticulo': None
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class SubArticuloContentAPIView(View):
    """API para cargar contenido de un sub-artículo específico"""
    
    def get(self, request, subarticulo_id):
        try:
            subarticulo = get_object_or_404(SubArticulo, id=subarticulo_id, activo=True)
            
            # Obtener tipos de documento del sub-artículo
            tipos_documento = subarticulo.tipos_documento.filter(activo=True).order_by('orden')
            
            # Obtener años disponibles
            años_disponibles = Documento.objects.filter(
                tipo_documento__subarticulo=subarticulo,
                activo=True
            ).values_list('año', flat=True).distinct().order_by('-año')
            
            # Filtro por año si se especifica
            año_filtro = request.GET.get('año')
            
            # Agrupar documentos por año y tipo
            documentos_agrupados = {}
            años_a_mostrar = [int(año_filtro)] if año_filtro else años_disponibles
            
            for año in años_a_mostrar:
                documentos_agrupados[año] = {}
                
                for tipo_doc in tipos_documento:
                    if subarticulo.periodicidad == 'ANUAL':
                        documento = Documento.objects.filter(
                            tipo_documento=tipo_doc,
                            año=año,
                            activo=True
                        ).first()
                        documentos_agrupados[año][tipo_doc] = {
                            'ANUAL': documento
                        }
                    else:
                        trimestres = ['T1', 'T2', 'T3', 'T4']
                        documentos_agrupados[año][tipo_doc] = {}
                        
                        for trimestre in trimestres:
                            documento = Documento.objects.filter(
                                tipo_documento=tipo_doc,
                                año=año,
                                trimestre=trimestre,
                                activo=True
                            ).first()
                            documentos_agrupados[año][tipo_doc][trimestre] = documento
            
            # Obtener fecha de última actualización
            ultima_fecha = None
            for año in años_a_mostrar:
                documentos_año = Documento.objects.filter(
                    tipo_documento__subarticulo=subarticulo,
                    año=año,
                    activo=True
                )
                for doc in documentos_año:
                    fecha_mas_reciente = max(doc.fecha_subida, doc.fecha_modificacion)
                    if not ultima_fecha or fecha_mas_reciente > ultima_fecha:
                        ultima_fecha = fecha_mas_reciente
            
            # Renderizar template parcial
            html_content = render_to_string('publico/partials/subarticulo_content.html', {
                'subarticulo': subarticulo,
                'tipos_documento': tipos_documento,
                'años_disponibles': años_disponibles,
                'documentos_agrupados': documentos_agrupados,
                'trimestres': ['T1', 'T2', 'T3', 'T4'],
                'año_actual': año_filtro,
                'ultima_actualizacion': ultima_fecha
            }, request=request)
            
            return JsonResponse({
                'success': True,
                'title': subarticulo.nombre,
                'content': html_content,
                'breadcrumb': {
                    'ley': subarticulo.ley.nombre,
                    'subarticulo': subarticulo.nombre
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)