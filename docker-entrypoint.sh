#!/bin/bash

# Ejecutar migraciones
python manage.py migrate --settings=sistema_transparencia.settings_docker

# Cargar datos iniciales si existen
python manage.py cargar_datos_iniciales --settings=sistema_transparencia.settings_docker || true

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000 --settings=sistema_transparencia.settings_docker