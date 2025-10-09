from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.administracion.models import PerfilUsuario


class Command(BaseCommand):
    help = 'Arregla perfiles de usuario duplicados o faltantes'

    def handle(self, *args, **options):
        self.stdout.write('Arreglando perfiles de usuario...')
        
        # Crear perfiles faltantes
        usuarios_sin_perfil = User.objects.filter(perfil__isnull=True)
        for user in usuarios_sin_perfil:
            PerfilUsuario.objects.get_or_create(user=user)
            self.stdout.write(f'Perfil creado para: {user.username}')
        
        # Verificar que todos los usuarios tengan perfil
        total_usuarios = User.objects.count()
        total_perfiles = PerfilUsuario.objects.count()
        
        self.stdout.write(f'Usuarios: {total_usuarios}')
        self.stdout.write(f'Perfiles: {total_perfiles}')
        
        if total_usuarios == total_perfiles:
            self.stdout.write(self.style.SUCCESS('✅ Todos los usuarios tienen perfil'))
        else:
            self.stdout.write(self.style.ERROR('❌ Hay inconsistencias'))