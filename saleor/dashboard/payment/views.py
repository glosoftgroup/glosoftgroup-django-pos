from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q

from ..views import staff_member_required
from ...sale.models import PaymentOption
from saleor.payment.models import PaymentOption as Table
from ...sale.models import DrawerCash
from ...decorators import user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


@staff_member_required
def payments_list(request): 
    try:
        options = PaymentOption.objects.all().exclude(name='Loyalty Points').order_by('-id')
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
            "options": options,            
            "pn": paginator.num_pages
        }
        user_trail(request.user.name, 'accessed payment option', 'views')
        info_logger.info('User: ' + str(request.user.name) + 'accessed payment option page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/payment/options/list.html', data)
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing payment options')


@staff_member_required
def payment_add(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        if request.POST.get('loyalty_points'):
            loyalty_points = request.POST.get('loyalty_points')        
        else:
            loyalty_points = 0
        if request.POST.get('name'):
            option = PaymentOption.objects.create(
                            name=request.POST.get('name'),
                            description=description,
                            loyalty_point_equiv=loyalty_points)
            l = {'name':option.name}
            return HttpResponse(json.dumps(l), content_type='application/json')
        return HttpResponse(json.dumps({'message': 'Invalid method'}))


@staff_member_required
def payment_stock_add(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        if request.POST.get('loyalty_points'):
            loyalty_points = request.POST.get('loyalty_points')
        else:
            loyalty_points = 0
        if request.POST.get('name'):
            option = Table.objects.create(
                            name=request.POST.get('name'),
                            description=description,
                            loyalty_point_equiv=loyalty_points)
            l = {'name':option.name}
            return HttpResponse(json.dumps(l), content_type='application/json')
        return HttpResponse(json.dumps({'message':'Invalid method'}))


@staff_member_required
def delete(request, pk=None):
    option = get_object_or_404(PaymentOption, pk=pk)
    if request.method == 'POST':
        try:
            if option.name == "Loyalty Points":
                pass
            else:
                option.delete()
                user_trail(request.user.name, 'deleted payment option : '+ str(option.name),'delete')
                info_logger.info('deleted payment option: '+ str(option.name))
                return HttpResponse('success')
            return HttpResponse(json.dumps({'error':"Loyalty Points is not deletable"}),content_type='application/json')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def stock_delete(request, pk=None):
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            if option.name == "Credit":
                pass
            else:
                option.delete()
                user_trail(request.user.name, 'deleted stock payment option : '+ str(option.name),'delete')
                info_logger.info('deleted stock payment option: '+ str(option.name))
                return HttpResponse('success')
            return HttpResponse(json.dumps({'error': "You cannot delete Credit"}),
                                content_type='application/json')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def edit(request, pk=None):
    option = get_object_or_404(PaymentOption, pk=pk)
    if request.method == 'POST':
        try:
            if request.POST.get('name'):
                if request.POST.get('name') != 'Loyalty Points':
                    option.name = request.POST.get('name')
                if request.POST.get('description'):
                    option.description = request.POST.get('description')
                if request.POST.get('loyalty_point_equiv'):
                    option.loyalty_point_equiv = request.POST.get('loyalty_point_equiv')                
                option.save()
                user_trail(request.user.name, 'updated payment option : '+ str(option.name),'delete')
                info_logger.info('updated payment option: '+ str(option.name))
                return HttpResponse('success')
            else:
                return HttpResponse('invalid response')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def detail(request, pk=None):
    if request.method == 'GET':
        try:
            option = get_object_or_404(PaymentOption, pk=pk)
            ctx = {'option':option}
            if option.name == "Loyalty Points":
                ctx['disabled'] = "disabled"
            else:
                ctx['disabled'] = ''
            user_trail(request.user.name, 'access payment option details of: '+ str(option.name)+' ','view')
            info_logger.info('access payment option details of: '+ str(option.name)+'  ')
            return TemplateResponse(request, 'dashboard/payment/options/detail.html', ctx)
        except Exception, e:
            error_logger.error(e)
            return TemplateResponse(request, 'dashboard/payment/options/detail.html', {'error': e})

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
def option_searchs(request):
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
            options = PaymentOption.objects.exclude(name='Loyalty Points').filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)                
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
                return TemplateResponse(request, 'dashboard/payment/options/paginate.html', {'options': options,'sz':sz})

            return TemplateResponse(request, 'dashboard/payment/options/search.html',
{'options': options, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def options_paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        options = PaymentOption.objects.exclude(name='Loyalty Points').filter(expense_type=type.name)
        if p2_sz:
            paginator = Paginator(options, int(p2_sz))
            options = paginator.page(page)
            return TemplateResponse(request,'dashboard/payment/options/paginate.html',{'options':options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            return TemplateResponse(request,'dashboard/payment/options/p2.html',{'options':options, 'pn':paginator.num_pages,'sz':list_sz, 'gid':request.GET.get('gid')})

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        return TemplateResponse(request,'dashboard/payment/options/p2.html',{'options':options, 'pn':paginator.num_pages,'sz':10,'gid':request.GET.get('gid')})
    else:
        try:
            options = PaymentOption.objects.all().exclude(name='Loyalty Points').order_by('-id')
            if list_sz:
                paginator = Paginator(options, int(list_sz))
                options = paginator.page(page)
                data = {
                    'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': 0
                }
                return TemplateResponse(request, 'dashboard/payment/options/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "options": options
                }
                return TemplateResponse(request, 'dashboard/payment/options/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/payment/options/paginate.html', {"options": options})
        except Exception, e:
            return HttpResponse()


# stock payment option
@staff_member_required
def payments_stock_list(request):
    try:
        options = Table.objects.all().order_by('-id')
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
            "options": options,
            "pn": paginator.num_pages
        }
        user_trail(request.user.name, 'accessed stock payment option', 'views')
        info_logger.info('User: ' + str(request.user.name) + 'accessed stock payment option page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/payment/stock/list.html', data)
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing stock payment options')


@staff_member_required
def stock_edit(request, pk=None):
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            if request.POST.get('name'):
                if request.POST.get('name') != 'Credit':
                    option.name = request.POST.get('name')
                if request.POST.get('description'):
                    option.description = request.POST.get('description')
                if request.POST.get('loyalty_point_equiv'):
                    option.loyalty_point_equiv = request.POST.get('loyalty_point_equiv')
                option.save()
                user_trail(request.user.name, 'updated stock payment option : '+ str(option.name),'delete')
                info_logger.info('updated stock payment option: '+ str(option.name))
                return HttpResponse('success')
            else:
                return HttpResponse('invalid response')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def stock_detail(request, pk=None):
    if request.method == 'GET':
        try:
            option = get_object_or_404(Table, pk=pk)
            ctx = {'option': option}
            if option.name == "Credit":
                ctx['disabled'] = "disabled"
            else:
                ctx['disabled'] = ''
            user_trail(request.user.name, 'access payment option details of: '+ str(option.name)+' ','view')
            info_logger.info('access payment option details of: '+ str(option.name)+'  ')
            return TemplateResponse(request, 'dashboard/payment/stock/detail.html', ctx)
        except Exception, e:
            error_logger.error(e)
            return TemplateResponse(request, 'dashboard/payment/stock/detail.html', {'error': e})


@staff_member_required
def options_stock_paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        options = Table.objects.filter(expense_type=type.name)
        if p2_sz:
            paginator = Paginator(options, int(p2_sz))
            options = paginator.page(page)
            return TemplateResponse(request, 'dashboard/payment/stock/paginate.html',{'options':options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            return TemplateResponse(request,'dashboard/payment/stock/p2.html',{'options':options, 'pn':paginator.num_pages,'sz':list_sz, 'gid':request.GET.get('gid')})

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        return TemplateResponse(request, 'dashboard/payment/stock/p2.html',{'options':options, 'pn':paginator.num_pages,'sz':10,'gid':request.GET.get('gid')})
    else:
        try:
            options = Table.objects.all().order_by('-id')
            if list_sz:
                paginator = Paginator(options, int(list_sz))
                options = paginator.page(page)
                data = {
                    'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': 0
                }
                return TemplateResponse(request, 'dashboard/payment/stock/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "options": options
                }
                return TemplateResponse(request, 'dashboard/payment/stock/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/payment/stock/paginate.html', {"options": options})
        except Exception, e:
            return HttpResponse()


@staff_member_required
def option_stock_search(request):
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
            options = Table.objects.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
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
                return TemplateResponse(request, 'dashboard/payment/stock/paginate.html', {'options': options,'sz':sz})

            return TemplateResponse(request, 'dashboard/payment/stock/search.html',
            {'options': options, 'pn': paginator.num_pages, 'sz': sz, 'q': q})
