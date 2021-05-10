from django import template

register = template.Library()


@register.filter(name="sub")
def subtract(value, arg):
    return value - arg


@register.filter(name="per")
def divide(value, arg):
    return 100000.0 * value / arg
