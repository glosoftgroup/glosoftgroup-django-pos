from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, views as django_views
from django.contrib.auth.decorators import login_required
import json

from ..dashboard.views import staff_member_required
from ..product.utils import products_with_availability, products_for_homepage


def home(request):
	products = products_for_homepage()[:8]
	products = products_with_availability(
		products, discounts=request.discounts, local_currency=request.currency)
	return TemplateResponse(request, 'dashboard/login.html')

def lock(request):
	return TemplateResponse(request, 'dashboard/lock.html')

def lock_process(request):
	email = request.POST['email']
	password = request.POST['password']
	next_url = request.POST["next"]
	user = authenticate(username=email, password=password)
	if user is not None:
		if user.is_active:
			# auth.login(request, user)
			# user_trail(request.user,"signed in ", "login")
			# if next_url:
			#     t = HttpResponse(next_url)
			# else:
			#     t = HttpResponse(settings.LOGIN_REDIRECT_URL)
			return HttpResponse(next_url)
		else: 
			return HttpResponse('error login')
	else: 
		return HttpResponse('wrong credentials')


@staff_member_required
def styleguide(request):
	return TemplateResponse(request, 'styleguide.html')

def not_found(request):
	return TemplateResponse(request, '404.html')
