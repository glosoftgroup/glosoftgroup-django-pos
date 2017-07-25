from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User, UserTrail
from ...customer.models import Customer
from ...sale.models import Terminal, DrawerCash, TerminalHistoryEntry
from ...decorators import permission_decorator, user_trail
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def transactions(request):
	transactions = DrawerCash.objects.all().order_by('-id')
	user_trail(request.user.name, 'accessed transaction', 'view')
	info_logger.info('User: ' + str(request.user.name) + 'accessed transaction:')
	return TemplateResponse(request, 
							'dashboard/cashmovement/transactions.html', 
							{'transactions':transactions})

@staff_member_required
# @permission_decorator('userprofile.view_user')
def terminals(request):
	try:
		users = Terminal.objects.all().order_by('-id')
		user_trail(request.user.name, 'accessed Terminals', 'view')
		info_logger.info('User: ' + str(request.user.name) + ' accessed terminals')
		return TemplateResponse(request, 'dashboard/terminal/terminals.html', {'users':users})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')

@staff_member_required
@permission_decorator('userprofile.add_terminal')
def terminal_add(request):
	try:
		user_trail(request.user.name, 'accessed add terminal page', 'view')
		info_logger.info('User: ' + str(request.user.name) + 'accessed terminal add page')
		return TemplateResponse(request, 'dashboard/terminal/add_terminal.html',{})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing add terminal page')

@staff_member_required
@csrf_exempt
def terminal_process(request):
	user = Terminal.objects.all()
	if request.method == 'POST':
		terminal_name = request.POST.get('name')		
		terminal_number = request.POST.get('nid')		
		new_user = Terminal.objects.create(
			terminal_name = terminal_name,						
			terminal_number = terminal_number,			
		)
		try:
			new_user.save()
			user_trail(request.user.name, 'created Terminal: ' + str(terminal_name), 'add')
			info_logger.info('User: ' + str(request.user.name) + ' created terminal:' + str(terminal_name))
		except Exception as e:
			error_logger.info(e)
		last_id = Terminal.objects.latest('id')
		return HttpResponse(last_id.id)

def terminal_detail(request, pk):
	user = get_object_or_404(Terminal, pk=pk)
	user_trail(request.user.name, 'accessed terminal: ' + str(user.terminal_name), 'view')
	info_logger.info('User: ' + str(request.user.name) + ' accessed terminal:' + str(user.terminal_name))
	return TemplateResponse(request, 'dashboard/terminal/detail.html', {'user':user})

def terminal_delete(request, pk):
	terminal = get_object_or_404(Terminal, pk=pk)
	if request.method == 'POST':
		terminal.delete()
		user_trail(request.user.name, 'deleted terminal: '+ str(terminal.terminal_name), 'delete')
		info_logger.info('User: ' + str(request.user.name) + ' deleted terminal:' + str(terminal.terminal_name))
		return HttpResponse('success')
def terminal_edit(request, pk):
	terminal = get_object_or_404(Terminal, pk=pk)		
	ctx = {'user': terminal}
	user_trail(request.user.name, 'accessed edit page for user '+ str(terminal.terminal_name),'update')
	info_logger.info('User: '+str(request.user.name)+' accessed edit page for user: '+str(terminal.terminal_name))
	return TemplateResponse(request, 'dashboard/terminal/terminal_edit.html', ctx)

def terminal_update(request, pk):
	terminal = get_object_or_404(Terminal, pk=pk)
	if request.method == 'POST':
		name = request.POST.get('name')
		nid = request.POST.get('nid')		
		terminal.terminal_name = name				
		terminal.terminal_number = nid		
		terminal.save()
		user_trail(request.user.name, 'updated terminal: '+ str(terminal.terminal_name))
		info_logger.info('User: '+str(request.user.name)+' updated terminal: '+str(terminal.terminal_name))
		return HttpResponse("success")

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

@staff_member_required
def terminal_history(request,pk=None):
	if request.method == 'GET':
		if pk:
			instance = get_object_or_404(Terminal, pk=pk)
			terminal_history = TerminalHistoryEntry.objects.filter(terminal=instance).order_by('-id')
			ctx = {'terminal_history':terminal_history}
			user_trail(request.user.name, 'accessed terminal history for terminal: ' + str(instance.terminal_name), 'view')
			info_logger.info('User: ' + str(request.user.name) + 'accessed terminal history for terminal for:' + str(user.terminal_name))
			return TemplateResponse(request, 'dashboard/includes/_terminal_history.html', ctx)
			

def user_trails(request):
	users = UserTrail.objects.all().order_by('id')
	user_trail(request.user.name, 'accessed user trail page')
	info_logger.info('User: '+str(request.user.name)+' accessed the user trail page')
	return TemplateResponse(request, 'dashboard/users/trail.html', {'users':users})




		