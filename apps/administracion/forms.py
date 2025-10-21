from django import forms
from django.db.models import Q
from .models import Documento, TipoDocumento, SubArticulo, PerfilUsuario


class DocumentoForm(forms.ModelForm):
    """Formulario para crear/editar documentos"""
    
    class Meta:
        model = Documento
        fields = [
            'tipo_documento', 'año', 'trimestre', 'archivo', 'activo'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_documento'
            }),
            'año': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Seleccione el año'
            }),
            'trimestre': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_trimestre',
                'placeholder': 'Seleccione el trimestre'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),

            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'año': 'Año',
            'trimestre': 'Periodicidad (opcional)',
            'archivo': 'Archivo PDF',

            'activo': 'Documento Activo'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Personalizar el queryset de tipo_documento según el tipo de usuario
        queryset = TipoDocumento.objects.select_related(
            'subarticulo__ley'
        ).filter(activo=True).order_by(
            'subarticulo__ley__orden', 'subarticulo__orden', 'orden'
        )
        
        # Filtrar según el tipo de usuario
        if self.user and hasattr(self.user, 'perfil'):
            perfil = self.user.perfil
            if perfil.tipo_usuario == 'RECURSOS_MATERIALES':
                # Solo documentos del subarticulo inventarios físicos de bienes
                queryset = queryset.filter(
                    subarticulo__nombre__icontains='inventario'
                ).filter(subarticulo__nombre__icontains='físico')
            elif perfil.tipo_usuario == 'PLANEACION':
                # Todo excepto documentos del subarticulo inventarios físicos de bienes
                queryset = queryset.exclude(
                    Q(subarticulo__nombre__icontains='inventario') & 
                    Q(subarticulo__nombre__icontains='físico')
                )
        
        self.fields['tipo_documento'].queryset = queryset
        
        # Personalizar las opciones de año
        from django.utils import timezone
        año_actual = timezone.now().year
        años = [(año, año) for año in range(2019, año_actual + 7)]
        self.fields['año'].choices = años
        
        # Inicialmente deshabilitar trimestre
        self.fields['trimestre'].required = False
        
        # Si estamos editando un documento existente
        if self.instance.pk:
            # Verificar si el tipo de documento requiere trimestre
            if self.instance.tipo_documento and self.instance.tipo_documento.subarticulo.periodicidad == 'ANUAL':
                self.fields['trimestre'].widget.attrs['disabled'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get('tipo_documento')
        trimestre = cleaned_data.get('trimestre')
        año = cleaned_data.get('año')
        
        if tipo_documento:
            periodicidad = tipo_documento.subarticulo.periodicidad
            
            # Validar trimestre según periodicidad
            if periodicidad == 'ANUAL' and trimestre:
                raise forms.ValidationError("Los documentos anuales no requieren trimestre.")
            elif periodicidad == 'TRIMESTRAL' and not trimestre:
                raise forms.ValidationError("Los documentos trimestrales requieren especificar el trimestre.")
            
            # Verificar duplicados
            existing_doc = Documento.objects.filter(
                tipo_documento=tipo_documento,
                año=año,
                trimestre=trimestre if periodicidad == 'TRIMESTRAL' else None
            )
            
            # Si estamos editando, excluir el documento actual
            if self.instance.pk:
                existing_doc = existing_doc.exclude(pk=self.instance.pk)
            
            if existing_doc.exists():
                if periodicidad == 'ANUAL':
                    raise forms.ValidationError(f"Ya existe un documento de este tipo para el año {año}.")
                else:
                    raise forms.ValidationError(f"Ya existe un documento de este tipo para {trimestre} de {año}.")
        
        return cleaned_data
    
    class Media:
        js = ('js/documento_form.js',)