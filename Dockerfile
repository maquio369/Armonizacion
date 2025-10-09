FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/media

# Verificar que los archivos estáticos existen
RUN ls -la /app/static/

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput --settings=sistema_transparencia.settings_docker

# Verificar archivos recopilados
RUN ls -la /app/staticfiles/

# Script de inicio
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

CMD ["/docker-entrypoint.sh"]