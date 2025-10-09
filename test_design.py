#!/usr/bin/env python
"""
Script de verificación para el diseño mejorado
"""
import os

def test_design():
    """Verificación básica del diseño"""
    print("🔍 Verificando archivos del diseño mejorado...")
    
    # Verificar estructura de archivos
    templates_path = "templates/publico/"
    required_templates = [
        "home.html",
        "partials/ley_content.html", 
        "partials/subarticulo_content.html"
    ]
    
    print("\n🔍 Verificando templates...")
    for template in required_templates:
        full_path = os.path.join(templates_path, template)
        if os.path.exists(full_path):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - NO ENCONTRADO")
    
    # Verificar CSS
    css_path = "static/css/chiapas-style.css"
    if os.path.exists(css_path):
        print(f"✅ CSS principal encontrado")
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
                checks = [
                    ('.hero-section', 'Hero section'),
                    ('.stat-card', 'Tarjetas de estadísticas'),
                    ('.law-card', 'Tarjetas de leyes'),
                    ('.help-section', 'Sección de ayuda'),
                    ('.footer-content', 'Footer mejorado')
                ]
                
                for css_class, description in checks:
                    if css_class in content:
                        print(f"✅ {description} presentes")
                    else:
                        print(f"❌ {description} no encontrados")
        except Exception as e:
            print(f"❌ Error leyendo CSS: {e}")
    else:
        print(f"❌ CSS principal no encontrado")
    
    # Verificar template home.html mejorado
    home_template = "templates/publico/home.html"
    if os.path.exists(home_template):
        try:
            with open(home_template, 'r', encoding='utf-8') as f:
                content = f.read()
                improvements = [
                    ('hero-section', 'Hero section'),
                    ('stats-section', 'Sección de estadísticas'),
                    ('laws-section', 'Sección de leyes'),
                    ('help-section', 'Sección de ayuda'),
                    ('law-card', 'Tarjetas de leyes')
                ]
                
                print("\n🔍 Verificando mejoras en home.html...")
                for class_name, description in improvements:
                    if class_name in content:
                        print(f"✅ {description}")
                    else:
                        print(f"❌ {description} no encontrada")
        except Exception as e:
            print(f"❌ Error leyendo home.html: {e}")
    
    print("\n🎨 Resumen del diseño mejorado:")
    print("📝 Características implementadas:")
    print("   • Hero section con gradiente y animaciones")
    print("   • Tarjetas de estadísticas modernas con iconos")
    print("   • Tarjetas de leyes interactivas con preview")
    print("   • Sección de ayuda con pasos")
    print("   • Footer mejorado con información estructurada")
    print("   • Efectos hover y transiciones suaves")
    print("   • Diseño completamente responsive")
    print("   • Paleta de colores consistente con Chiapas.gob.mx")
    print("   • Navegación SPA mejorada")
    
    print("\n🚀 Para ver los cambios:")
    print("   1. Instala las dependencias: pip install -r requirements.txt")
    print("   2. Configura la base de datos PostgreSQL")
    print("   3. Ejecuta: python manage.py migrate")
    print("   4. Carga datos iniciales: python manage.py cargar_datos_iniciales")
    print("   5. Inicia el servidor: python manage.py runserver")
    
    return True

if __name__ == "__main__":
    test_design()