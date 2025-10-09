#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_transparencia.settings')
django.setup()

from django.contrib.auth.models import User
from apps.administracion.models import PerfilUsuario, TipoDocumento

print("=== SISTEMA DE USUARIOS CON PERMISOS ESPECÍFICOS ===\n")

# Verificar usuarios creados
usuarios = User.objects.all()
print("Usuarios en el sistema:")
for user in usuarios:
    if hasattr(user, 'perfil'):
        print(f"- {user.username}: {user.perfil.get_tipo_usuario_display()}")
    else:
        print(f"- {user.username}: Sin perfil")

print("\n" + "="*50)

# Verificar tipos de documento disponibles
tipos = TipoDocumento.objects.filter(activo=True)
print(f"\nTipos de documento disponibles ({tipos.count()}):")
for tipo in tipos[:5]:  # Solo mostrar los primeros 5
    print(f"- {tipo.nombre}")

print("\n" + "="*50)

# Probar permisos
print("\nPrueba de permisos:")
try:
    user_recursos = User.objects.get(username='recursos_materiales')
    user_planeacion = User.objects.get(username='planeacion')
    
    # Buscar un tipo de documento que contenga "inventario"
    tipo_inventario = tipos.filter(nombre__icontains='inventario').first()
    tipo_otro = tipos.exclude(nombre__icontains='inventario').first()
    
    if tipo_inventario:
        print(f"\nTipo: {tipo_inventario.nombre}")
        print(f"- Recursos Materiales puede subir: {user_recursos.perfil.puede_subir_documento(tipo_inventario)}")
        print(f"- Planeación puede subir: {user_planeacion.perfil.puede_subir_documento(tipo_inventario)}")
    
    if tipo_otro:
        print(f"\nTipo: {tipo_otro.nombre}")
        print(f"- Recursos Materiales puede subir: {user_recursos.perfil.puede_subir_documento(tipo_otro)}")
        print(f"- Planeación puede subir: {user_planeacion.perfil.puede_subir_documento(tipo_otro)}")
        
except User.DoesNotExist:
    print("Error: No se encontraron los usuarios de prueba")

print("\n" + "="*50)
print("\n✅ Sistema configurado correctamente!")
print("🌐 Accede al admin: http://localhost:8000/admin/")
print("📊 Panel administrativo: http://localhost:8000/admin-panel/")
print("\n📝 Credenciales:")
print("   - recursos_materiales / recursos123")
print("   - planeacion / planeacion123")