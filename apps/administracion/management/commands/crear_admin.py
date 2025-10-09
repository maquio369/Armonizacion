from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crear usuario administrador para el panel administrativo'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nombre de usuario', default='admin')
        parser.add_argument('--email', type=str, help='Email del administrador', default='admin@chiapas.gob.mx')
        parser.add_argument('--password', type=str, help='Contraseña', default='admin123')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario "{username}" ya existe.')
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Administrador',
            last_name='Sistema'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Usuario administrador "{username}" creado exitosamente.')
        )
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Contraseña: {password}')
        self.stdout.write(
            self.style.WARNING('¡IMPORTANTE: Cambie la contraseña después del primer acceso!')
        )