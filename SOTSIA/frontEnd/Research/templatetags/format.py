from django import template

register = template.Library()

@register.filter
def space_underscore(value):
    return value.replace(" ","_")

@register.filter
def lower(value):
    return value.lower()