#!/bin/bash

echo "Configurando sistema de usuarios con permisos específicos..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Entorno virtual activado"
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
    echo "Entorno virtual activado"
else
    echo "No se encontró entorno virtual. Asegúrate de tener Django instalado."
fi

# Crear migraciones
echo "Creando migraciones..."
python manage.py makemigrations administracion

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate

# Configurar usuarios y permisos
echo "Configurando usuarios y permisos..."
python manage.py configurar_usuarios

echo "¡Configuración completada!"
echo ""
echo "Usuarios creados:"
echo "- recursos_materiales (password: recursos123) - Solo inventarios físicos"
echo "- planeacion (password: planeacion123) - Todo excepto inventarios físicos"
echo ""
echo "Puedes acceder al admin en: http://localhost:8000/admin/"