from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum
from django.core import serializers
from django.template.defaultfilters import date
import datetime

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales



@staff_member_required
# @permission_required('userprofile.view_user', raise_exception=True)
def sales_reports(request):
	users = User.objects.all().order_by('id')
	return TemplateResponse(request, 'dashboard/reports/sales.html', {'users':users})

def product_reports(request):
	users = User.objects.all().order_by('id')
	return TemplateResponse(request, 'dashboard/reports/products.html', {'users':users})

def purchases_reports(request):
	users = User.objects.all().order_by('id')
	return TemplateResponse(request, 'dashboard/reports/purchases.html', {'users':users})

def balancesheet_reports(request):
	users = User.objects.all().order_by('id')
	return TemplateResponse(request, 'dashboard/reports/balancesheet.html', {'users':users})

def get_dashboard_data(request):
	label = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
	default = [12, 19, 3, 5, 2, 3]
	total_sales = Sales.objects.all()
	# total_sales = 
	today = datetime.date.today()
	todays_sales = Sales.objects.filter(created=today).annotate(Sum('total_net'))

	''' get highest product '''
	
	''' get lowest product '''
	data = {
		 "label":label,
		 "default":default,
		 "users":10,
		 "net":serializers.serialize('json', total_sales),
		 "todays_sales": serializers.serialize('json', todays_sales),
	}
	return JsonResponse(data)


#####
##  search using ajax and filter many filds
####

# questions = Help.objects.all()
# filters = {}
# if 'question' in ajax_data:
#     filters['question'] = ajax_data.get('question')
# if 'description' in ajax_data:
#     filters['description'] = ajax_data.get('description')
# if 'status' in ajax_data:
#     filters['status'] = ajax_data.get('status')
# if 'created' in ajax_data:
#     filters['created'] = ajax_data.get('created')
# if 'modified' in ajax_data:
#     filters['modified'] = ajax_data.get('modified')
# questions = questions.filter(**filters).values('id','question','description','status','created','modified').order_by('-id')
