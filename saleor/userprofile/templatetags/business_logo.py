from django.template import Library, Node
from django.shortcuts import get_object_or_404, redirect
from ...site.models import SiteSettings
from ...utils import image64

register = Library()

@register.simple_tag
def business_logo():
	try:
		site = get_object_or_404(SiteSettings, pk=1)
		image = site.image.url
	except:
		image = image64()
	return image