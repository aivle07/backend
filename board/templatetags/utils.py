import datetime 
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="iso_to_date",is_safe=True)
@stringfilter
def iso_to_date(value):
    return datetime.datetime.fromisoformat(value)