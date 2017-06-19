from django.template.response import TemplateResponse
from django.http import HttpResponse

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

def login(request):
	if request.is_ajax():
		email = request.GET.get('email')
		password = request.GET.get('password')

		return HttpResponse('email is '+str(email)+' and password is '+str(password))


@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'styleguide.html')
