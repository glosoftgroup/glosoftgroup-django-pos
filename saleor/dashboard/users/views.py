from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User, UserTrail
from ...decorators import permission_decorator, user_trail
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
# @permission_decorator('userprofile.view_user')
def users(request):
	try:
		users = User.objects.all().order_by('id')
		page = request.GET.get('page', 1)
		paginator = Paginator(users, 10)
		try:
			users = paginator.page(page)
		except PageNotAnInteger:
			users = paginator.page(1)
		except EmptyPage:
			users = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed users list page')
		info_logger.info('User: '+str(request.user.name)+' accessed the view users page')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/users/users.html', {'users':users})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')

def user_paginate(request):
	users = User.objects.all().order_by('id')
	page = request.GET.get('page', 1)
	list_sz = request.GET.get('size')
	select_sz = request.GET.get('select_size')
	if list_sz:
		paginator = Paginator(users, int(list_sz))
	else:
		paginator = Paginator(users, 10)
	if select_sz and list_sz:
		paginator = Paginator(users, int(list_sz))
		return HttpResponse(paginator.num_pages)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	np = users.paginator.num_pages
	return TemplateResponse(request,'dashboard/users/paginate.html',{'users':users})

@staff_member_required
@permission_decorator('userprofile.add_user')
def user_add(request):
	try:
		permissions = Permission.objects.all()
		groups = Group.objects.all()
		user_trail(request.user.name, 'accessed add users page')
		info_logger.info('User: '+str(request.user.name)+' accessed user create page')
		return TemplateResponse(request, 'dashboard/users/add_user.html',{'permissions':permissions, 'groups':groups})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing add users page')

@staff_member_required
@csrf_exempt
def user_process(request):
	user = User.objects.all()
	if request.method == 'POST':
		name = request.POST.get('name')
		email = request.POST.get('email')
		password = request.POST.get('password')
		encr_password = make_password(password)
		nid = request.POST.get('nid')
		mobile = request.POST.get('mobile')
		image= request.FILES.get('image')
		groups = request.POST.getlist('groups[]')
		new_user = User(
			name = name,
			email = email,
			password = encr_password,
			nid = nid,
			mobile = mobile,
			image = image
		)
		try:
			new_user.save()
		except:
			error_logger.info('Error when saving ')
		last_id = User.objects.latest('id')
		if groups:
			permissions = Permission.objects.filter(group__name__in=groups)
			last_id.user_permissions.add(*permissions)
			gps = Group.objects.filter(name__in=groups)
			last_id.groups.add(*gps)
			last_id.save()
		user_trail(request.user.name, 'created user: '+str(name))
		info_logger.info('User: '+str(request.user.name)+' created user:'+str(name))
		return HttpResponse(last_id.id)

def user_detail(request, pk):
	user = get_object_or_404(User, pk=pk)
	permissions = Permission.objects.filter(user=user)
	groups = user.groups.all()
	if request.user == user:
		user_trail(request.user.name, 'viewed self profile ')
		info_logger.info('User: '+str(request.user)+' viewed self profile')
	else:
		user_trail(request.user.name, 'viewed '+str(user.name)+ '`s profile')
		info_logger.info('User: '+str(request.user.name)+' viewed '+str(user.name)+'`s profile')
	return TemplateResponse(request, 'dashboard/users/detail.html', {'user':user,'permissions':permissions,'groups':groups})

def user_delete(request, pk):
	user = get_object_or_404(User, pk=pk)
	if request.method == 'POST':
		user.delete()
		user_trail(request.user.name, 'deleted user: '+ str(user.name))
		return HttpResponse('success')
def user_edit(request, pk):
	user = get_object_or_404(User, pk=pk)
	permissions = Permission.objects.all()
	user_permissions = Permission.objects.filter(user=user)
	ctx = {'user': user,'permissions':permissions, 'user_permissions':user_permissions}
	user_trail(request.user.name, 'accessed edit page for user '+ str(user.name))
	info_logger.info('User: '+str(request.user.name)+' accessed edit page for user: '+str(user.name))
	return TemplateResponse(request, 'dashboard/users/edit_user.html', ctx)

def user_update(request, pk):
	user = get_object_or_404(User, pk=pk)
	if request.method == 'POST':
		name = request.POST.get('name')
		email = request.POST.get('email')
		password = request.POST.get('password')
		nid = request.POST.get('nid')
		mobile = request.POST.get('mobile')
		image= request.FILES.get('image')
		if password == user.password:
			encr_password = user.password
		else:
			encr_password = make_password(password)
		if image :
			user.name = name
			user.email = email
			user.password = encr_password
			user.nid = nid
			user.mobile = mobile
			user.image = image
			user.save()
			user_trail(request.user.name, 'updated user: '+ str(user.name))
			info_logger.info('User: '+str(request.user.name)+' updated user: '+str(user.name))
			return HttpResponse("success with image")
		else:
			user.name = name
			user.email = email
			user.password = encr_password
			user.nid = nid
			user.mobile = mobile
			user.save()
			user_trail(request.user.name, 'updated user: '+ str(user.name))
			info_logger.info('User: '+str(request.user.name)+' updated user: '+str(user.name))
			return HttpResponse("success without image")

@csrf_exempt
def user_assign_permission(request):
	if request.method == 'POST':
		user_id = request.POST.get('user_id')
		user = get_object_or_404(User, pk=user_id)
		user_has_permissions = Permission.objects.filter(user=user)
		login_status = request.POST.get('check_login')
		permission_list = request.POST.getlist('checklist[]')
		if login_status == 'inactive':
			user.is_staff = False
			user.is_active = False
			user.user_permissions.remove(*user_has_permissions)
			user.save()
			user_trail(request.user.name, 'deactivated and removed all permissions for user: '+ str(user.name))
			info_logger.info('User: '+str(request.user.name)+' deactivated and removed all permissions for user: '+str(user.name))
			return HttpResponse('deactivated')
		else:
			if user_has_permissions in permission_list:
				not_in_user_permissions = list(set(permission_list) - set(user_has_permissions))
				user.is_staff = True
				user.is_active = True
				user.user_permissions.add(*not_in_user_permissions)
				user.save()
				user_trail(request.user.name, 'assigned permissions for user: '+ str(user.name))
				info_logger.info('User: '+str(request.user)+' assigned permissions for user: '+str(user.name))
				return HttpResponse('permissions added')
			else:
				not_in_user_permissions = list(set(permission_list) - set(user_has_permissions))
				user.is_staff = True
				user.is_active = True
				user.user_permissions.remove(*user_has_permissions)
				user.user_permissions.add(*not_in_user_permissions)
				user.save()
				user_trail(request.user.name, 'assigned permissions for user: '+ str(user.name))
				info_logger.info('User: '+str(request.user.name)+' assigned permissions for user: '+str(user.name))
				return HttpResponse('permissions updated')

def user_trails(request):
	users = UserTrail.objects.all().order_by('id')
	user_trail(request.user.name, 'accessed user trail page')
	info_logger.info('User: '+str(request.user.name)+' accessed the user trail page')
	return TemplateResponse(request, 'dashboard/users/trail.html', {'users':users})

def user_search( request ):

    if request.is_ajax():
        q = request.GET.get( 'q' )
        if q is not None:            
            users = User.objects.filter( 
                Q( name__contains = q ) |
                Q( email__contains = q ) | Q( mobile__contains = q ) ).order_by( 'id' )

            return TemplateResponse(request, 'dashboard/users/search.html', {'users':users})




		