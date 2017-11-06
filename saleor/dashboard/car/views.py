from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q

from ..views import staff_member_required
from ...car.models import Car as Table
from ...decorators import user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


@staff_member_required
def list(request):
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
            "table_name": 'Cars',
            "options": options,            
            "pn": paginator.num_pages
        }
        user_trail(request.user.name, 'accessed Cars List', 'views')
        info_logger.info('User: ' + str(request.user.name) + 'accessed Cars List Page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/car/list.html', data)
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing payment options')


@staff_member_required
def add(request):
    if request.method == 'POST':
        if request.POST.get('name'):
            option = Table()
            option.name = request.POST.get('name')
            if request.POST.get('number'):
                option.number = request.POST.get('number')
            option.save()
            data = {'name': option.name}
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps({'message': 'Invalid method'}))


@staff_member_required
def delete(request, pk=None):
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            if option.name == "Loyalty Points":
                pass
            else:
                option.delete()
                user_trail(request.user.name, 'deleted payment option : '+ str(option.name),'delete')
                info_logger.info('deleted payment option: '+ str(option.name))
                return HttpResponse('success')
            return HttpResponse(json.dumps({'error':"Object is not deletable"}),content_type='application/json')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def edit(request, pk=None):
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            if request.POST.get('name'):
                option.name = request.POST.get('name')
                if request.POST.get('number'):
                    option.number = request.POST.get('number')
                option.save()
                user_trail(request.user.name, 'updated car : '+ str(option.name),'delete')
                info_logger.info('updated car : '+ str(option.name))
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
            option = get_object_or_404(Table, pk=pk)
            ctx = {'option': option}
            user_trail(request.user.name, 'access Car details of: ' + str(option.name)+' ','view')
            info_logger.info('access car details of: ' + str(option.name)+'  ')
            return TemplateResponse(request, 'dashboard/car/detail.html', ctx)
        except Exception, e:
            error_logger.error(e)
            return TemplateResponse(request, 'dashboard/car/detail.html', {'error': e})


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
            options = Table.objects.filter(
                Q(name__icontains=q)
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
                return TemplateResponse(request, 'dashboard/car/paginate.html', {'options': options,'sz':sz})
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': sz,
                    'q': q}
            return TemplateResponse(request, 'dashboard/car/search.html', data)


@staff_member_required
def paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        options = Table.objects.filter(name=type.name)
        if p2_sz:
            paginator = Paginator(options, int(p2_sz))
            options = paginator.page(page)
            return TemplateResponse(request,'dashboard/car/paginate.html',{'options':options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': request.GET.get('gid')}
            return TemplateResponse(request, 'dashboard/car/p2.html',data)

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        data = {'options': options,
                'pn': paginator.num_pages,
                'sz': 10,
                'gid': request.GET.get('gid')}
        return TemplateResponse(request,'dashboard/car/p2.html', data)
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
                return TemplateResponse(request, 'dashboard/car/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "options": options
                }
                return TemplateResponse(request, 'dashboard/car/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/car/paginate.html', {"options": options})
        except Exception, e:
            return HttpResponse()