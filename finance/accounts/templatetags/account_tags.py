from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def repeat(value, arg):
    return value * int(arg)
