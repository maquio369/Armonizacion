from django import forms
from .models import Documento, TipoDocumento, SubArticulo


class DocumentoForm(forms.ModelForm):
    """Formulario para crear/editar documentos"""
    
    class Meta:
        model = Documento
        fields = [
            'tipo_documento', 'año', 'trimestre', 'archivo', 
            'titulo_personalizado', 'descripcion', 'activo'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_documento'
            }),
            'año': forms.Select(attrs={'class': 'form-select'}),
            'trimestre': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_trimestre'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'titulo_personalizado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título personalizado (opcional)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del documento (opcional)'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'año': 'Año',
            'trimestre': 'Trimestre',
            'archivo': 'Archivo PDF',
            'titulo_personalizado': 'Título Personalizado',
            'descripcion': 'Descripción',
            'activo': 'Documento Activo'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar el queryset de tipo_documento para mostrarlo organizado
        self.fields['tipo_documento'].queryset = TipoDocumento.objects.select_related(
            'subarticulo__ley'
        ).filter(activo=True).order_by(
            'subarticulo__ley__orden', 'subarticulo__orden', 'orden'
        )
        
        # Personalizar las opciones de año
        from django.utils import timezone
        año_actual = timezone.now().year
        años = [(año, año) for año in range(2024, año_actual + 7)]
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