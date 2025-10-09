from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Ley, SubArticulo, TipoDocumento, Documento, LogAcceso, PerfilUsuario


@admin.register(Ley)
class LeyAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'orden']
    list_editable = ['activa', 'orden']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']


@admin.register(SubArticulo)
class SubArticuloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ley', 'periodicidad', 'activo', 'orden']
    list_filter = ['ley', 'periodicidad', 'activo']
    list_editable = ['activo', 'orden']
    search_fields = ['nombre', 'descripcion']
    ordering = ['ley', 'orden', 'nombre']


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'subarticulo', 'get_ley', 'activo', 'orden']
    list_filter = ['subarticulo__ley', 'subarticulo', 'activo']
    list_editable = ['activo', 'orden']
    search_fields = ['nombre', 'descripcion']
    ordering = ['subarticulo__ley', 'subarticulo', 'orden', 'nombre']
    
    def get_ley(self, obj):
        return obj.subarticulo.ley.nombre
    get_ley.short_description = 'Ley'


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['get_documento_info', 'año', 'trimestre', 'get_archivo_info', 'fecha_subida', 'activo']
    list_filter = ['tipo_documento__subarticulo__ley', 'tipo_documento__subarticulo', 'año', 'trimestre', 'activo']
    search_fields = ['tipo_documento__nombre', 'titulo_personalizado', 'descripcion']
    readonly_fields = ['tamaño_archivo', 'fecha_subida', 'fecha_modificacion']
    ordering = ['-año', '-trimestre', 'tipo_documento__subarticulo__ley', 'tipo_documento']
    
    fieldsets = (
        ('Información del Documento', {
            'fields': ('tipo_documento', 'año', 'trimestre', 'archivo')
        }),
        ('Metadatos', {
            'fields': ('titulo_personalizado', 'descripcion', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('tamaño_archivo', 'fecha_subida', 'fecha_modificacion', 'usuario_subida'),
            'classes': ('collapse',)
        }),
    )
    
    def get_documento_info(self, obj):
        return f"{obj.tipo_documento.nombre}"
    get_documento_info.short_description = 'Tipo de Documento'
    
    def get_archivo_info(self, obj):
        if obj.archivo:
            return format_html(
                '<a href="{}" target="_blank">{}</a><br><small>{}</small>',
                obj.archivo.url,
                obj.get_nombre_archivo(),
                obj.get_tamaño_legible()
            )
        return "Sin archivo"
    get_archivo_info.short_description = 'Archivo'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.usuario_subida = request.user
        super().save_model(request, obj, form, change)


@admin.register(LogAcceso)
class LogAccesoAdmin(admin.ModelAdmin):
    list_display = ['documento', 'tipo_acceso', 'ip_address', 'fecha_acceso']
    list_filter = ['tipo_acceso', 'fecha_acceso']
    readonly_fields = ['documento', 'ip_address', 'user_agent', 'fecha_acceso', 'tipo_acceso']
    ordering = ['-fecha_acceso']
    
    def has_add_permission(self, request):
        return False  # No permitir agregar logs manualmente
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar logs


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'tipo_usuario', 'activo', 'fecha_creacion']
    list_filter = ['tipo_usuario', 'activo']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering = ['user__username']


# Inline para mostrar perfil en el admin de usuarios
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'


# Extender el UserAdmin para incluir el perfil
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)