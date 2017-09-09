from django.template import Library, Node
from django.shortcuts import get_object_or_404, redirect
from ...site.models import SiteSettings

register = Library()

@register.simple_tag
def business_name():
	try:
		site = get_object_or_404(SiteSettings, pk=1)
		name = (site.name).upper()
	except:
		name ="POS"
	return name