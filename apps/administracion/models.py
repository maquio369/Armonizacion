from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

# Opciones para los tipos de periodicidad
PERIODICIDAD_CHOICES = [
    ('ANUAL', 'Anual'),
    ('TRIMESTRAL', 'Trimestral'),
]

# Opciones para los trimestres
TRIMESTRE_CHOICES = [
    ('T1', 'Primer Trimestre'),
    ('T2', 'Segundo Trimestre'),
    ('T3', 'Tercer Trimestre'),
    ('T4', 'Cuarto Trimestre'),
]

# Años disponibles
YEAR_CHOICES = [(r, r) for r in range(2024, 2031)]

# Tipos de usuario
TIPO_USUARIO_CHOICES = [
    ('ADMIN', 'Administrador'),
    ('RECURSOS_MATERIALES', 'Recursos Materiales'),
    ('PLANEACION', 'Planeación'),
]


class PerfilUsuario(models.Model):
    """Perfil extendido para usuarios con permisos específicos"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='ADMIN')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"
    
    def puede_subir_documento(self, tipo_documento):
        """Verifica si el usuario puede subir un tipo específico de documento"""
        if self.tipo_usuario == 'ADMIN':
            return True
        elif self.tipo_usuario == 'RECURSOS_MATERIALES':
            # Solo puede subir documentos del subarticulo "Inventario Físico de Bienes"
            return 'inventario' in tipo_documento.subarticulo.nombre.lower() and 'físico' in tipo_documento.subarticulo.nombre.lower()
        elif self.tipo_usuario == 'PLANEACION':
            # Puede subir todo EXCEPTO documentos del subarticulo "Inventario Físico de Bienes"
            return not ('inventario' in tipo_documento.subarticulo.nombre.lower() and 'físico' in tipo_documento.subarticulo.nombre.lower())
        return False


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)


class Ley(models.Model):
    """Modelo para las leyes principales"""
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Ley"
        verbose_name_plural = "Leyes"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class SubArticulo(models.Model):
    """Modelo para los sub-artículos de cada ley"""
    ley = models.ForeignKey(Ley, on_delete=models.CASCADE, related_name='subarticulos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    periodicidad = models.CharField(max_length=15, choices=PERIODICIDAD_CHOICES)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Sub-Artículo"
        verbose_name_plural = "Sub-Artículos"
        ordering = ['orden', 'nombre']
        unique_together = ['ley', 'nombre']
    
    def __str__(self):
        return f"{self.ley.nombre} - {self.nombre}"


class TipoDocumento(models.Model):
    """Modelo para los tipos específicos de documentos"""
    subarticulo = models.ForeignKey(SubArticulo, on_delete=models.CASCADE, related_name='tipos_documento')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        ordering = ['orden', 'nombre']
        unique_together = ['subarticulo', 'nombre']
    
    def __str__(self):
        return f"{self.subarticulo.nombre} - {self.nombre}"


def documento_upload_path(instance, filename):
    """Función para generar la ruta de subida de archivos"""
    # Crear estructura: documentos/ley/subarticulo/año/trimestre/filename
    ley_nombre = instance.tipo_documento.subarticulo.ley.nombre.replace(' ', '_')
    subarticulo_nombre = instance.tipo_documento.subarticulo.nombre.replace(' ', '_')
    
    if instance.trimestre:
        return f'documentos/{ley_nombre}/{subarticulo_nombre}/{instance.año}/{instance.trimestre}/{filename}'
    else:
        return f'documentos/{ley_nombre}/{subarticulo_nombre}/{instance.año}/{filename}'


class Documento(models.Model):
    """Modelo principal para los documentos PDF"""
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, related_name='documentos')
    año = models.IntegerField(choices=YEAR_CHOICES)
    trimestre = models.CharField(max_length=2, choices=TRIMESTRE_CHOICES, blank=True, null=True)
    
    # Archivo PDF
    archivo = models.FileField(
        upload_to=documento_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Solo se permiten archivos PDF"
    )
    
    # Metadatos
    titulo_personalizado = models.CharField(max_length=300, blank=True, null=True, 
                                          help_text="Título personalizado para el documento")
    descripcion = models.TextField(blank=True, null=True)
    tamaño_archivo = models.IntegerField(blank=True, null=True, help_text="Tamaño en bytes")
    
    # Campos de auditoría
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario_subida = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-año', '-trimestre', 'tipo_documento__orden']
        unique_together = ['tipo_documento', 'año', 'trimestre']
    
    def __str__(self):
        if self.trimestre:
            return f"{self.tipo_documento.nombre} - {self.año} - {self.trimestre}"
        else:
            return f"{self.tipo_documento.nombre} - {self.año}"
    
    def save(self, *args, **kwargs):
        # Calcular tamaño del archivo automáticamente
        if self.archivo:
            self.tamaño_archivo = self.archivo.size
        
        # Validar trimestre según periodicidad
        periodicidad = self.tipo_documento.subarticulo.periodicidad
        if periodicidad == 'ANUAL':
            self.trimestre = None
        elif periodicidad == 'TRIMESTRAL' and not self.trimestre:
            raise ValueError("Los documentos trimestrales requieren especificar el trimestre")
        
        super().save(*args, **kwargs)
    
    def get_nombre_archivo(self):
        """Obtiene solo el nombre del archivo sin la ruta"""
        if self.archivo:
            return os.path.basename(self.archivo.name)
        return None
    
    def get_tamaño_legible(self):
        """Convierte el tamaño en bytes a formato legible"""
        if not self.tamaño_archivo:
            return "Desconocido"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.tamaño_archivo < 1024.0:
                return f"{self.tamaño_archivo:.1f} {unit}"
            self.tamaño_archivo /= 1024.0
        return f"{self.tamaño_archivo:.1f} TB"
    
    def get_fecha_mas_reciente(self):
        """Obtiene la fecha más reciente entre subida y modificación"""
        return max(self.fecha_subida, self.fecha_modificacion)


class LogAcceso(models.Model):
    """Modelo para registrar accesos y descargas"""
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='logs_acceso')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    fecha_acceso = models.DateTimeField(auto_now_add=True)
    tipo_acceso = models.CharField(max_length=20, choices=[
        ('VISUALIZACION', 'Visualización'),
        ('DESCARGA', 'Descarga'),
    ])
    
    class Meta:
        verbose_name = "Log de Acceso"
        verbose_name_plural = "Logs de Acceso"
        ordering = ['-fecha_acceso']
    
    def __str__(self):
        return f"{self.documento} - {self.tipo_acceso} - {self.fecha_acceso.strftime('%d/%m/%Y %H:%M')}"