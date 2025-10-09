from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.administracion.models import PerfilUsuario, Documento


class Command(BaseCommand):
    help = 'Configura grupos de usuarios y permisos iniciales'

    def handle(self, *args, **options):
        self.stdout.write('Configurando grupos y permisos...')
        
        # Crear grupos
        grupo_admin, created = Group.objects.get_or_create(name='Administradores')
        grupo_recursos, created = Group.objects.get_or_create(name='Recursos Materiales')
        grupo_planeacion, created = Group.objects.get_or_create(name='Planeación')
        
        # Obtener permisos de documentos
        content_type = ContentType.objects.get_for_model(Documento)
        permisos_documento = Permission.objects.filter(content_type=content_type)
        
        # Asignar permisos a grupos
        grupo_admin.permissions.set(permisos_documento)
        grupo_recursos.permissions.set(permisos_documento)
        grupo_planeacion.permissions.set(permisos_documento)
        
        self.stdout.write(self.style.SUCCESS('Grupos configurados exitosamente'))
        
        # Crear usuarios de ejemplo si no existen
        if not User.objects.filter(username='recursos_materiales').exists():
            user_recursos = User.objects.create_user(
                username='recursos_materiales',
                password='recursos123',
                first_name='Usuario',
                last_name='Recursos Materiales',
                email='recursos@gobierno.mx'
            )
            user_recursos.groups.add(grupo_recursos)
            PerfilUsuario.objects.update_or_create(
                user=user_recursos,
                defaults={'tipo_usuario': 'RECURSOS_MATERIALES'}
            )
            self.stdout.write(f'Usuario recursos_materiales creado')
        
        if not User.objects.filter(username='planeacion').exists():
            user_planeacion = User.objects.create_user(
                username='planeacion',
                password='planeacion123',
                first_name='Usuario',
                last_name='Planeación',
                email='planeacion@gobierno.mx'
            )
            user_planeacion.groups.add(grupo_planeacion)
            PerfilUsuario.objects.update_or_create(
                user=user_planeacion,
                defaults={'tipo_usuario': 'PLANEACION'}
            )
            self.stdout.write(f'Usuario planeacion creado')
        
        # Asegurar que el superusuario tenga perfil de admin
        for user in User.objects.filter(is_superuser=True):
            PerfilUsuario.objects.update_or_create(
                user=user,
                defaults={'tipo_usuario': 'ADMIN'}
            )
            user.groups.add(grupo_admin)
        
        self.stdout.write(self.style.SUCCESS('Configuración completada'))