#!/usr/bin/env python3
"""
Script para revertir los cambios temporales del formulario masivo
Ejecutar cuando ya no se necesite la funcionalidad de subida masiva
"""

import os
import shutil

def revertir_cambios():
    """Revierte todos los cambios temporales"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🔄 Revirtiendo cambios temporales...")
    
    # 1. Eliminar template de subida masiva
    bulk_template = os.path.join(base_dir, 'templates/admin/documento_form_bulk.html')
    if os.path.exists(bulk_template):
        os.remove(bulk_template)
        print("✅ Eliminado: documento_form_bulk.html")
    
    # 2. Restaurar template original (si existe respaldo)
    original_backup = os.path.join(base_dir, 'templates/admin/documento_form_original.html')
    current_template = os.path.join(base_dir, 'templates/admin/documento_form.html')
    
    if os.path.exists(original_backup):
        shutil.copy2(original_backup, current_template)
        os.remove(original_backup)
        print("✅ Restaurado: documento_form.html")
    
    # 3. Mostrar instrucciones para cambios manuales
    print("\n📝 CAMBIOS MANUALES REQUERIDOS:")
    print("1. En apps/administracion/urls.py:")
    print("   - Eliminar la línea: path('documentos/nuevo-masivo/', views.DocumentoBulkCreateView.as_view(), name='documento_bulk_create'),")
    
    print("\n2. En apps/administracion/views.py:")
    print("   - Eliminar la clase: DocumentoBulkCreateView")
    
    print("\n3. En templates/admin/documento_list.html:")
    print("   - Eliminar el botón 'Subida Masiva' del toolbar")
    
    print("\n4. Eliminar este script:")
    print(f"   rm {__file__}")
    
    print("\n✅ Cambios temporales revertidos exitosamente!")
    print("💡 No olvides hacer los cambios manuales listados arriba.")

if __name__ == "__main__":
    revertir_cambios()