from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, views as django_views
import json

from ..dashboard.views import staff_member_required
from ..product.utils import products_with_availability, products_for_homepage


def home(request):
	products = products_for_homepage()[:8]
	products = products_with_availability(
		products, discounts=request.discounts, local_currency=request.currency)
	# return TemplateResponse(
	#     request, 'home.html',
	#     {'products': products, 'parent': None})
	return TemplateResponse(request, 'dashboard/login.html')


@staff_member_required
def styleguide(request):
	return TemplateResponse(request, 'styleguide.html')
