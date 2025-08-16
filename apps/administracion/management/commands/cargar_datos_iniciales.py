from django.core.management.base import BaseCommand
from apps.administracion.models import Ley, SubArticulo, TipoDocumento


class Command(BaseCommand):
    help = 'Carga los datos iniciales de leyes, sub-artículos y tipos de documento'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de datos iniciales...')
        
        # Crear Ley General de Contabilidad Gubernamental
        ley_contabilidad, created = Ley.objects.get_or_create(
            nombre="Ley General de Contabilidad Gubernamental",
            defaults={
                'descripcion': 'Ley que establece los criterios generales que regirán la contabilidad gubernamental y la emisión de información financiera de los entes públicos.',
                'orden': 1
            }
        )
        if created:
            self.stdout.write(f'✓ Creada: {ley_contabilidad.nombre}')
        
        # Crear Ley de Disciplina Financiera
        ley_disciplina, created = Ley.objects.get_or_create(
            nombre="Ley de Disciplina Financiera",
            defaults={
                'descripcion': 'Ley que establece los criterios generales de responsabilidad hacendaria y financiera.',
                'orden': 2
            }
        )
        if created:
            self.stdout.write(f'✓ Creada: {ley_disciplina.nombre}')

        # Sub-artículos de Ley General de Contabilidad Gubernamental
        subarticulos_contabilidad = [
            {
                'nombre': 'Presupuesto de Egresos',
                'periodicidad': 'ANUAL',
                'orden': 1,
                'tipos_documento': [
                    'Presupuesto de Egresos Calendarizado'
                ]
            },
            {
                'nombre': 'Información Contable',
                'periodicidad': 'TRIMESTRAL',
                'orden': 2,
                'tipos_documento': [
                    'Estado de Actividades',
                    'Estado de Situación Financiera',
                    'Estado de Variación en la Hacienda Pública',
                    'Estado de Cambios en la Situación Financiera',
                    'Estado de Flujos de Efectivo',
                    'Informe sobre Pasivos Contingentes',
                    'Notas a los Estados Financieros',
                    'Estado Analítico del Activo',
                    'Estado Analítico de la Deuda y Otros Pasivos'
                ]
            },
            {
                'nombre': 'Información Presupuestaria',
                'periodicidad': 'TRIMESTRAL',
                'orden': 3,
                'tipos_documento': [
                    'Estado Analítico de Ingresos',
                    'Estado Analítico del Ejercicio del Presupuesto de Egresos con base en la Clasificación Administrativa',
                    'Estado Analítico del Ejercicio del Presupuesto de Egresos con base en la Clasificación Económica por Tipo de Gasto',
                    'Estado Analítico del Ejercicio del Presupuesto de Egresos con base en la Clasificación por Objeto del Gasto',
                    'Estado Analítico del Ejercicio del Presupuesto de Egresos con base en la Clasificación Funcional',
                    'Endeudamiento Neto',
                    'Intereses de la Deuda'
                ]
            },
            {
                'nombre': 'Información Programática',
                'periodicidad': 'TRIMESTRAL',
                'orden': 4,
                'tipos_documento': [
                    'Gasto por Categoría Programática',
                    'Indicadores de Resultados',
                    'Programas y Proyectos de Inversión'
                ]
            },
            {
                'nombre': 'Ayudas y Subsidios',
                'periodicidad': 'TRIMESTRAL',
                'orden': 5,
                'tipos_documento': [
                    'Montos Pagados por Ayudas y Subsidios'
                ]
            },
            {
                'nombre': 'Cuenta Pública',
                'periodicidad': 'TRIMESTRAL',
                'orden': 6,
                'tipos_documento': [
                    'Información Contable',
                    'Información Presupuestal'
                ]
            },
            {
                'nombre': 'Información Cualitativa',
                'periodicidad': 'TRIMESTRAL',
                'orden': 7,
                'tipos_documento': [
                    'Avances de Metas, Objetivos e Indicadores'
                ]
            },
            {
                'nombre': 'Inventario Físico de Bienes',
                'periodicidad': 'ANUAL',
                'orden': 8,
                'tipos_documento': [
                    'Inventario Físico de Bienes',
                    'Reporte General de Vehículos'
                ]
            }
        ]

        # Sub-artículos de Ley de Disciplina Financiera
        subarticulos_disciplina = [
            {
                'nombre': 'Información de la Ley de Disciplina Financiera',
                'periodicidad': 'TRIMESTRAL',
                'orden': 1,
                'tipos_documento': [
                    'Estado de Situación Financiera Detallado (LDF-1)',
                    'Informe Analítico de la Deuda y Otros Pasivos (LDF-2)',
                    'Informe Analítico de Obligaciones Diferentes de Financiamientos (LDF-3)',
                    'Balance Presupuestario (LDF-4)',
                    'Estado Analítico de Ingresos Detallado (LDF-5)',
                    'Clasificación por Objeto del Gasto (LDF-6a)',
                    'Clasificación Administrativa (LDF-6b)',
                    'Clasificación Funcional (LDF-6c)',
                    'Clasificación de Servicios Personales por Categoría (LDF-6d)'
                ]
            },
            {
                'nombre': 'Anexos de la Ley de Disciplina Financiera',
                'periodicidad': 'TRIMESTRAL',
                'orden': 2,
                'tipos_documento': [
                    'Información Detallada sobre la Contratación de Deuda Pública u Obligaciones (LDF-Art. 25)',
                    'Obligaciones de Corto Plazo (LDF-Art. 31)',
                    'Información del Cumplimiento de Obligaciones de Responsabilidad Hacendaria (LDF-Art. 40)'
                ]
            }
        ]

        # Crear sub-artículos y tipos de documento para Ley de Contabilidad
        self._crear_subarticulos_y_tipos(ley_contabilidad, subarticulos_contabilidad)
        
        # Crear sub-artículos y tipos de documento para Ley de Disciplina
        self._crear_subarticulos_y_tipos(ley_disciplina, subarticulos_disciplina)

        self.stdout.write(self.style.SUCCESS('¡Datos iniciales cargados exitosamente!'))

    def _crear_subarticulos_y_tipos(self, ley, subarticulos_data):
        for subarticulo_data in subarticulos_data:
            # Crear sub-artículo
            subarticulo, created = SubArticulo.objects.get_or_create(
                ley=ley,
                nombre=subarticulo_data['nombre'],
                defaults={
                    'periodicidad': subarticulo_data['periodicidad'],
                    'orden': subarticulo_data['orden']
                }
            )
            if created:
                self.stdout.write(f'  ✓ Sub-artículo: {subarticulo.nombre}')

            # Crear tipos de documento
            for orden, tipo_nombre in enumerate(subarticulo_data['tipos_documento'], 1):
                tipo_doc, created = TipoDocumento.objects.get_or_create(
                    subarticulo=subarticulo,
                    nombre=tipo_nombre,
                    defaults={'orden': orden}
                )
                if created:
                    self.stdout.write(f'    ✓ Tipo: {tipo_doc.nombre}')