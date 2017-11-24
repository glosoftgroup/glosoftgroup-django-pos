from django import template

register = template.Library()


@register.filter
def payment_status(value, num_decimals=2):
    if value == 'fully-paid':
        return '<span class="text-success  icon-checkmark-circle"><i></i></span>'
    else:
        return '<span class="badge badge-flat border-warning text-warning-600">Pending..</span>'
