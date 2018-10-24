from django.conf import settings
from django import template
from saleor.site.models import SiteSettings

register = template.Library()


@register.filter
def model_settings(value):
    value = eval('SiteSettings.objects.get(pk=1).'+str(value))
    return value