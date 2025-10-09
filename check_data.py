#!/usr/bin/env python
"""
Script para verificar datos en la base de datos
"""
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_transparencia.settings')

try:
    import django
    django.setup()
    
    from apps.administracion.models import Ley, SubArticulo, TipoDocumento, Documento
    
    print("🔍 Verificando datos en la base de datos...")
    
    # Verificar leyes
    leyes = Ley.objects.filter(activa=True).order_by('orden')
    print(f"\n📋 Leyes activas: {leyes.count()}")
    
    for ley in leyes:
        subarticulos = ley.subarticulos.filter(activo=True)
        print(f"   • {ley.nombre}")
        print(f"     Sub-artículos: {subarticulos.count()}")
        
        for sub in subarticulos[:3]:  # Mostrar solo los primeros 3
            tipos = sub.tipos_documento.filter(activo=True).count()
            docs = Documento.objects.filter(tipo_documento__subarticulo=sub, activo=True).count()
            print(f"       - {sub.nombre} ({tipos} tipos, {docs} docs)")
    
    if leyes.count() == 0:
        print("\n❌ No hay leyes en la base de datos")
        print("💡 Ejecuta: python manage.py cargar_datos_iniciales")
    
except ImportError:
    print("❌ Django no está instalado")
    print("💡 Ejecuta: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Verifica la configuración de la base de datos")