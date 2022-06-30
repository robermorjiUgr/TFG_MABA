from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def space_underscore(value):
    return value.replace(" ","_")

@register.filter
def lower(value):
    return value.lower()

@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))