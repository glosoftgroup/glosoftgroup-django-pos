from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q

from ..views import staff_member_required
from ...banking.models import Bank, Account
from ...decorators import user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


@staff_member_required
def list(request):
    try:
        options = Account.objects.all().order_by('-id')
        banks = Bank.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(options, 10)
        try:
            options = paginator.page(page)
        except PageNotAnInteger:
            options = paginator.page(1)
        except InvalidPage:
            options = paginator.page(1)
        except EmptyPage:
            options = paginator.page(paginator.num_pages)
        data = {
            "accounts": options,
            "pn": paginator.num_pages,
            "banks":banks
        }
        user_trail(request.user.name, 'accessed bank accounts', 'views')
        info_logger.info('User: ' + str(request.user.name) + 'accessed bank accounts page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/banking/accounts/list.html', data)
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing bank accounts')


@staff_member_required
def add(request):
    if request.method == 'POST':
        print request.POST.get('bank')
        print request.POST.get('name')
        print request.POST.get('number')
        print request.POST.get('amount')

        account = Account()
        account.name = request.POST.get('name')
        bank = Bank.objects.get(name=request.POST.get('bank'))
        account.bank = bank
        account.number = request.POST.get('number')
        account.balance = request.POST.get('amount')
        try:
            account.save()
            data = {'name': account.name}
            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            return HttpResponse(json.dumps({'message': 'Error Saving'}))


@staff_member_required
def delete(request, pk=None):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        try:
            account.delete()
            user_trail(request.user.name, 'deleted bank account : '+ str(account.name),'delete')
            info_logger.info('deleted bank account: '+ str(account.name))
            return HttpResponse('success')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def edit(request, pk=None):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        account.name = request.POST.get('name')
        account.bank = request.POST.get('bank')
        account.number = request.POST.get('number')
        account.balance = request.POST.get('balance')
        try:
            account.save()
            user_trail(request.user.name, 'updated bank account : '+ str(account.name),'update')
            info_logger.info('updated bank account: '+ str(account.name))
            return HttpResponse('success')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def detail(request, pk=None):
    if request.method == 'GET':
        try:
            account = get_object_or_404(Account, pk=pk)
            ctx = {'option': account}
            user_trail(request.user.name, 'access bank account details of: ' + str(account.name)+' ','view')
            info_logger.info('access banking account details of: ' + str(account.name)+'  ')
            return TemplateResponse(request, 'dashboard/banking/accounts/detail.html', ctx)
        except Exception, e:
            error_logger.error(e)
            return TemplateResponse(request, 'dashboard/banking/accounts/detail.html', {'error': e})


def searchs(request):
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
            options = Account.objects.filter(
                Q(name__icontains=q) |
                Q(number__icontains=q) |
                Q(bank__name__icontains=q)
            ).order_by('-id')
            paginator = Paginator(options, 10)
            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            if p2_sz:
                options = paginator.page(page)
                return TemplateResponse(request, 'dashboard/banking/accounts/paginate.html', {'options': options,'sz':sz})
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': sz,
                    'q': q}
            return TemplateResponse(request, 'dashboard/banking/accounts/search.html', data)


@staff_member_required
def paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        options = Account.objects.all()
        if p2_sz:
            paginator = Paginator(options, int(p2_sz))
            options = paginator.page(page)
            return TemplateResponse(request,'dashboard/banking/accounts/paginate.html',{'accounts':options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            data = {'accounts': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': request.GET.get('gid')}
            return TemplateResponse(request, 'dashboard/banking/accounts/p2.html',data)

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        data = {'accounts': options,
                'pn': paginator.num_pages,
                'sz': 10,
                'gid': request.GET.get('gid')}
        return TemplateResponse(request,'dashboard/banking/accounts/p2.html', data)
    else:
        try:
            options = Account.objects.all().order_by('-id')
            if list_sz:
                paginator = Paginator(options, int(list_sz))
                options = paginator.page(page)
                data = {
                    'accounts': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': 0
                }
                return TemplateResponse(request, 'dashboard/banking/accounts/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "accounts": options
                }
                return TemplateResponse(request, 'dashboard/banking/accounts/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/banking/accounts/paginate.html', {"accounts": options})
        except Exception, e:
            return HttpResponse()