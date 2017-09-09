from django.template import Library, Node
from ...utils import image64

register = Library()

@register.simple_tag
def default_user_image():
	img = image64()
	return img
