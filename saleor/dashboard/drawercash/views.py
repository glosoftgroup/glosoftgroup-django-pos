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
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q

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
	try:
		transactions = DrawerCash.objects.all().order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(transactions, 10)
		try:
			transactions = paginator.page(page)
		except PageNotAnInteger:
			transactions = paginator.page(1)
		except InvalidPage:
			transactions = paginator.page(1)
		except EmptyPage:
			transactions = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed transaction', 'view')
		info_logger.info('User: ' + str(request.user.name) + 'accessed transaction:')
		return TemplateResponse(request, 'dashboard/cashmovement/transactions.html',{'transactions':transactions, 'pn': paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return TemplateResponse(request, 'dashboard/cashmovement/transactions.html', {'transactions':transactions, 'pn': paginator.num_pages})

def transaction_pagination(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	transactions = DrawerCash.objects.all().order_by('-id')
	if list_sz:
		paginator = Paginator(transactions, int(list_sz))
		transactions = paginator.page(page)
		return TemplateResponse(request, 'dashboard/cashmovement/pagination/p2.html',
								{'transactions':transactions, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
	else:
		paginator = Paginator(transactions, 10)
	if p2_sz:
		paginator = Paginator(transactions, int(p2_sz))
		transactions = paginator.page(page)
		return TemplateResponse(request, 'dashboard/cashmovement/pagination/paginate.html', {"transactions":transactions})
	try:
		transactions = paginator.page(page)
	except PageNotAnInteger:
		transactions = paginator.page(1)
	except InvalidPage:
		transactions = paginator.page(1)
	except EmptyPage:
		transactions = paginator.page(paginator.num_pages)
	return TemplateResponse(request, 'dashboard/cashmovement/pagination/paginate.html', {"transactions":transactions})

@staff_member_required
def transaction_search(request):
	if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		if list_sz is None:
			sz = 10
		else:
			sz = list_sz

		if q is not None:
			queryset_list = DrawerCash.objects.filter(
				Q(user__name__icontains=q) |
				Q(user__email__icontains=q) |
				Q(terminal__terminal_name__icontains=q) |
				Q(trans_type__icontains=q) |
				Q(manager__name__icontains=q) |
				Q(manager__email__icontains=q)
			).order_by('-id')
			paginator = Paginator(queryset_list, 10)

			try:
				queryset_list = paginator.page(page)
			except PageNotAnInteger:
				queryset_list = paginator.page(1)
			except InvalidPage:
				queryset_list = paginator.page(1)
			except EmptyPage:
				queryset_list = paginator.page(paginator.num_pages)
			transactions = queryset_list
			if p2_sz:
				transactions = paginator.page(page)
				return TemplateResponse(request, 'dashboard/cashmovement/pagination/paginate.html', {"transactions":transactions})

			return TemplateResponse(request, 'dashboard/cashmovement/pagination/search.html',
			{"transactions":transactions, 'pn': paginator.num_pages, 'sz': sz, 'q': q})

@staff_member_required
@permission_decorator('sale.view_terminal')
def terminals(request):
	try:
		users = Terminal.objects.all().order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(users, 10)
		try:
			users = paginator.page(page)
		except PageNotAnInteger:
			users = paginator.page(1)
		except InvalidPage:
			users = paginator.page(1)
		except EmptyPage:
			users = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed Terminals', 'view')
		info_logger.info('User: ' + str(request.user.name) + ' accessed terminals')
		return TemplateResponse(request, 'dashboard/terminal/terminals.html',{'users': users, 'pn': paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return TemplateResponse(request, 'dashboard/terminal/terminals.html', {'users': users, 'pn': paginator.num_pages})

def terminal_pagination(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	users = Terminal.objects.all().order_by('-id')
	if list_sz:
		paginator = Paginator(users, int(list_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/terminal/pagination/p2.html',
								{'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
	else:
		paginator = Paginator(users, 10)
	if p2_sz:
		paginator = Paginator(users, int(p2_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/terminal/pagination/paginate.html', {"users":users})

	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except InvalidPage:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	return TemplateResponse(request, 'dashboard/terminal/pagination/paginate.html', {"users":users})

@staff_member_required
def terminal_search(request):
	if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		if list_sz is None:
			sz = 10
		else:
			sz = list_sz

		if q is not None:
			queryset_list = Terminal.objects.filter(
				Q(terminal_name__icontains=q)|
				Q(terminal_number__icontains=q)
			).order_by('-id')
			paginator = Paginator(queryset_list, 10)

			try:
				queryset_list = paginator.page(page)
			except PageNotAnInteger:
				queryset_list = paginator.page(1)
			except InvalidPage:
				queryset_list = paginator.page(1)
			except EmptyPage:
				queryset_list = paginator.page(paginator.num_pages)
			users = queryset_list
			if p2_sz:
				users = paginator.page(page)
				return TemplateResponse(request, 'dashboard/terminal/pagination/paginate.html', {"users":users})

			return TemplateResponse(request, 'dashboard/terminal/pagination/search.html',
			{"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
@permission_decorator('sale.add_terminal')
def terminal_add(request):
	try:
		user_trail(request.user.name, 'accessed add terminal page', 'view')
		info_logger.info('User: ' + str(request.user.name) + 'accessed terminal add page')
		return TemplateResponse(request, 'dashboard/terminal/add_terminal.html',{})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing add terminal page')

@staff_member_required
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



@staff_member_required
def terminal_history(request,pk=None):
	if request.method == 'GET':
		if pk:
			instance = get_object_or_404(Terminal, pk=pk)
			terminal_history = TerminalHistoryEntry.objects.filter(terminal=instance).order_by('-id')
			ctx = {'terminal_history':terminal_history}
			#user_trail(request.user.name, 'accessed terminal history for terminal: ' + str(instance.terminal_name), 'view')
			#info_logger.info('User: ' + str(request.user.name) + 'accessed terminal history for terminal for:' + str(user.terminal_name))
			return TemplateResponse(request, 'dashboard/includes/_terminal_history.html', ctx)
			

def user_trails(request):
	users = UserTrail.objects.all().order_by('id')
	user_trail(request.user.name, 'accessed user trail page')
	info_logger.info('User: '+str(request.user.name)+' accessed the user trail page')
	return TemplateResponse(request, 'dashboard/users/trail.html', {'users':users})




		