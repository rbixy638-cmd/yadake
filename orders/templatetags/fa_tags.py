from django import template

from orders.jalali import jdate

register = template.Library()


@register.filter
def jd(value):
    return jdate(value)


@register.filter
def jdt(value):
    return jdate(value, True)
