# Cambios Temporales - Subida Masiva de Documentos

## 📋 Descripción
Se implementó una funcionalidad temporal para subir los 4 trimestres de documentos trimestrales de una sola vez, facilitando la carga de archivos históricos.

## 🚀 Cómo usar la funcionalidad

1. **Acceder al formulario masivo:**
   - Ve a: `http://sag.chiapas.gob.mx:3021/admin-panel/documentos/`
   - Haz clic en el botón **"Subida Masiva"** (botón amarillo)

2. **Llenar el formulario:**
   - Selecciona el **Tipo de Documento** (debe ser trimestral)
   - Selecciona el **Año**
   - Aparecerán 4 secciones para subir archivos PDF (T1, T2, T3, T4)
   - Puedes subir solo los trimestres que tengas disponibles

3. **Subir archivos:**
   - Selecciona los archivos PDF para cada trimestre
   - Haz clic en **"Subir Documentos"**
   - El sistema creará automáticamente los documentos individuales

## ⚠️ Limitaciones
- Solo funciona con documentos **trimestrales**
- Para documentos anuales, usa el formulario normal
- No permite duplicados (si ya existe un documento para ese trimestre/año, lo omite)
- Máximo 50MB por archivo PDF

## 📁 Archivos modificados/creados

### Archivos nuevos:
- `templates/admin/documento_form_bulk.html` - Template del formulario masivo
- `revertir_cambios_temporales.py` - Script para revertir cambios
- `CAMBIOS_TEMPORALES.md` - Este archivo de documentación

### Archivos modificados:
- `apps/administracion/views.py` - Agregada clase `DocumentoBulkCreateView`
- `apps/administracion/urls.py` - Agregada URL para formulario masivo
- `templates/admin/documento_list.html` - Agregado botón "Subida Masiva"

### Archivos de respaldo:
- `templates/admin/documento_form_original.html` - Respaldo del template original

## 🔄 Cómo revertir los cambios

### Opción 1: Script automático (parcial)
```bash
python revertir_cambios_temporales.py
```

### Opción 2: Manual (completo)

1. **Eliminar archivos nuevos:**
   ```bash
   rm templates/admin/documento_form_bulk.html
   rm revertir_cambios_temporales.py
   rm CAMBIOS_TEMPORALES.md
   ```

2. **Restaurar template original:**
   ```bash
   mv templates/admin/documento_form_original.html templates/admin/documento_form.html
   ```

3. **Editar `apps/administracion/urls.py`:**
   - Eliminar la línea: `path('documentos/nuevo-masivo/', views.DocumentoBulkCreateView.as_view(), name='documento_bulk_create'),`

4. **Editar `apps/administracion/views.py`:**
   - Eliminar toda la clase `DocumentoBulkCreateView`

5. **Editar `templates/admin/documento_list.html`:**
   - Revertir el botón toolbar a su estado original (solo "Nuevo Documento")

## 🎯 Casos de uso
- Carga inicial de archivos históricos
- Migración de documentos de sistemas anteriores
- Actualización masiva de documentos trimestrales

## 📞 Soporte
Si encuentras algún problema, revisa:
1. Que el tipo de documento sea trimestral
2. Que los archivos sean PDF válidos
3. Que no excedan 50MB por archivo
4. Que no existan duplicados para ese año/trimestre

---
**Nota:** Esta es una funcionalidad temporal diseñada para facilitar la carga inicial de documentos. Una vez completada la migración, se recomienda revertir los cambios para mantener el sistema limpio.