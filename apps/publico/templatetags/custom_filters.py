from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Filtro para acceder a valores de diccionario en templates"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None