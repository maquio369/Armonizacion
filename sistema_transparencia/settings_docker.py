import os
from .settings import *

# Configuración para producción con Docker
DEBUG = False
ALLOWED_HOSTS = ['172.16.35.75', 'localhost', '127.0.0.1']

# Base de datos externa
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'armonizacion'),
        'USER': os.environ.get('DB_USER', 'maquio'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'maquio92?'),
        'HOST': os.environ.get('DB_HOST', '172.16.35.75'),
        'PORT': os.environ.get('DB_PORT', '32768'),
    }
}

# Configuración de archivos estáticos para producción
STATIC_ROOT = '/app/staticfiles'
MEDIA_ROOT = '/app/media'

# Configuración de seguridad
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False