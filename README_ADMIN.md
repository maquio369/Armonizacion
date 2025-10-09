# Panel Administrativo - Sistema de Transparencia

## Configuración Inicial

### 1. Crear Usuario Administrador
```bash
python manage.py crear_admin --username admin --email admin@chiapas.gob.mx --password admin123
```

### 2. Acceso al Panel
- URL: `http://localhost:8000/admin-panel/`
- Usuario: `admin`
- Contraseña: `admin123`

## Funcionalidades del Panel

### Dashboard
- Estadísticas de documentos activos
- Total de descargas y visualizaciones
- Documentos recientes y más descargados
- Distribución por ley

### Gestión de Documentos
- **Crear**: Subir nuevos documentos PDF
- **Editar**: Modificar información de documentos existentes
- **Eliminar**: Remover documentos del sistema
- **Filtros**: Por ley, año, estado

### Validaciones Automáticas
- Solo archivos PDF (máximo 50MB)
- Documentos anuales: sin trimestre
- Documentos trimestrales: trimestre obligatorio
- No duplicados por tipo/año/trimestre

### URLs Principales
- `/admin-panel/` - Dashboard
- `/admin-panel/documentos/` - Lista de documentos
- `/admin-panel/documentos/nuevo/` - Crear documento
- `/admin-panel/estadisticas/` - Reportes detallados

## Estructura de Archivos
Los documentos se organizan automáticamente:
```
media/documentos/
├── Ley_General_de_Contabilidad/
│   ├── Clasificador_por_Objeto_del_Gasto/
│   │   ├── 2024/
│   │   │   ├── T1/documento.pdf
│   │   │   └── T2/documento.pdf
│   │   └── 2025/
│   └── Plan_de_Cuentas/
└── Ley_de_Disciplina_Financiera/
```

## Seguridad
- Autenticación requerida para todas las funciones
- Validación de tipos de archivo
- Logs de acceso y descargas
- Protección CSRF en formularios