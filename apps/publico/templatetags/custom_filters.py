from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Filtro para acceder a valores de diccionario en templates"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def periodicidad_display(subarticulo):
    """Filtro para mostrar periodicidad personalizada"""
    if 'inventario' in subarticulo.nombre.lower() and 'físico' in subarticulo.nombre.lower():
        return 'Bimestral'
    return subarticulo.get_periodicidad_display()