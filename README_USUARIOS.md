# Sistema de Usuarios con Permisos Específicos

## Tipos de Usuario

### 1. Administrador (ADMIN)
- **Permisos**: Acceso completo a todos los documentos
- **Puede subir**: Cualquier tipo de documento
- **Puede ver**: Todos los documentos del sistema

### 2. Recursos Materiales (RECURSOS_MATERIALES)
- **Permisos**: Solo inventarios físicos de bienes
- **Puede subir**: Únicamente documentos que contengan "inventario" y "físico" en el nombre
- **Puede ver**: Solo los documentos de inventarios físicos de bienes

### 3. Planeación (PLANEACION)
- **Permisos**: Todos los documentos EXCEPTO inventarios físicos de bienes
- **Puede subir**: Cualquier documento excepto los que contengan "inventario" y "físico"
- **Puede ver**: Todos los documentos excepto inventarios físicos de bienes

## Configuración Inicial

### Paso 1: Ejecutar el script de configuración
```bash
./configurar_usuarios.sh
```

### Paso 2: Usuarios creados automáticamente
- **recursos_materiales** (password: recursos123)
- **planeacion** (password: planeacion123)

### Paso 3: Acceso al sistema
- URL: http://localhost:8000/admin/
- Panel administrativo: http://localhost:8000/admin-panel/

## Funcionalidades

### Dashboard Personalizado
- Cada usuario ve estadísticas solo de los documentos que puede gestionar
- El tipo de usuario se muestra en el dashboard

### Formularios Filtrados
- Los formularios de creación/edición solo muestran los tipos de documento permitidos
- Validación automática de permisos al guardar

### Lista de Documentos
- Cada usuario ve solo los documentos que puede gestionar
- Filtros automáticos según el tipo de usuario

## Administración

### Crear Nuevos Usuarios
1. Ir al admin de Django: `/admin/`
2. Crear usuario en "Users"
3. El perfil se crea automáticamente
4. Editar el perfil para cambiar el tipo de usuario

### Modificar Permisos
1. Ir a "Perfiles de Usuario" en el admin
2. Cambiar el tipo de usuario según sea necesario
3. Los permisos se aplican inmediatamente

## Seguridad

- Validación en el backend para todos los permisos
- No se puede subir documentos sin permisos
- Filtrado automático en todas las vistas
- Logs de acceso para auditoría

## Personalización

Para agregar nuevos tipos de usuario:

1. Modificar `TIPO_USUARIO_CHOICES` en `models.py`
2. Actualizar el método `puede_subir_documento()` en `PerfilUsuario`
3. Modificar los filtros en las vistas según sea necesario
4. Ejecutar migraciones si es necesario