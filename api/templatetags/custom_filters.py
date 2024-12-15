from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Django template filter to retrieve a value from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, '')
