from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q
from django.http import HttpResponse
import json

from ...discount.models import Sale, Voucher
from ...product.models import ProductVariant
from ...decorators import permission_decorator, user_trail
from . import forms
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def sale_list(request):
    try:
        sales = Sale.objects.prefetch_related('products').order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(sales, 10)
        try:
            sales = paginator.page(page)
        except PageNotAnInteger:
            sales = paginator.page(1)
        except InvalidPage:
            sales = paginator.page(1)
        except EmptyPage:
            sales = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed discount page', 'view')
        info_logger.info('User: ' + str(request.user.name) + 'accessed discount page')

        return TemplateResponse(request, 'dashboard/discount/sale_list.html',
                                    {'sales': sales, 'pn': paginator.num_pages})
    except TypeError as e:
        error_logger.error(e)
        return TemplateResponse(request, 'dashboard/discount/sale_list.html', {})

def disc_paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    sales = Sale.objects.prefetch_related('products').order_by('-id')
    if list_sz:
        paginator = Paginator(sales, int(list_sz))
        sales = paginator.page(page)
        return TemplateResponse(request, 'dashboard/discount/pagination/p2.html',
                            {'sales':sales, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
    else:
        paginator = Paginator(sales, 10)
    if p2_sz:
        paginator = Paginator(sales, int(p2_sz))
        sales = paginator.page(page)
        return TemplateResponse(request, 'dashboard/discount/pagination/paginate.html', {"sales":sales})

    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except InvalidPage:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'dashboard/discount/pagination/paginate.html', {"sales":sales})

@staff_member_required
def disc_search(request):
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
            discounts = Sale.objects.prefetch_related('products').order_by('-id')
            queryset_list = discounts.filter(
                Q(name__icontains=q) |
                Q(value__icontains=q)
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
            sales = queryset_list
            if p2_sz:
                users = paginator.page(page)
                return TemplateResponse(request, 'dashboard/discount/pagination/paginate.html', {"sales":sales})

            return TemplateResponse(request, 'dashboard/discount/pagination/search.html',
            {"sales":sales, 'pn': paginator.num_pages, 'sz': sz, 'q': q})

@staff_member_required
def discount_detail(request,pk=None):
    if request.method == 'GET':
        if pk:
            try:
                instance = get_object_or_404(Sale, pk=pk)
                products = instance.variant.all()

                page = request.GET.get('page', 1)
                paginator = Paginator(products, 10)
                try:
                    products = paginator.page(page)
                except PageNotAnInteger:
                    products = paginator.page(1)
                except InvalidPage:
                    products = paginator.page(1)
                except EmptyPage:
                    products = paginator.page(paginator.num_pages)
                user_trail(request.user.name, 'accessed discount detail page for ' + str(instance.name), 'view')
                info_logger.info(
                    'User: ' + str(request.user.name) + 'accessed discount detail page for ' + str(instance.name))

                return TemplateResponse(request, 'dashboard/discount/discount_detail.html',
                                        {'product_results':products,'discount':instance, 'pn': paginator.num_pages, 'pk':pk})
            except TypeError as e:
                error_logger.error(e)
                return TemplateResponse(request, 'dashboard/customer/discount_detail.html', {})

def disc_products_paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    pk = request.GET.get('pk')

    instance = get_object_or_404(Sale, pk=pk)
    products = instance.variant.all()
    if list_sz:
        paginator = Paginator(products, int(list_sz))
        products = paginator.page(page)
        return TemplateResponse(request, 'dashboard/discount/detail_pagination/p2.html',
                            {'product_results':products, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0, 'pk':pk})
    else:
        paginator = Paginator(products, 10)
    if p2_sz:
        paginator = Paginator(products, int(p2_sz))
        products = paginator.page(page)
        return TemplateResponse(request, 'dashboard/discount/detail_pagination/paginate.html', {"product_results":products, 'pk':pk})

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except InvalidPage:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'dashboard/discount/detail_pagination/paginate.html', {"product_results":products, 'pk':pk})

@staff_member_required
def disc_products_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        pk = request.GET.get('pk')

        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            instance = get_object_or_404(Sale, pk=pk)
            products = instance.variant.all()

            queryset_list = products.filter(
                Q(name__icontains=q)
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
            sales = queryset_list
            if p2_sz:
                users = paginator.page(page)
                return TemplateResponse(request, 'dashboard/discount/detail_pagination/paginate.html', {"product_results":products, 'pk':pk})

            return TemplateResponse(request, 'dashboard/discount/detail_pagination/search.html',
            {"product_results":products, 'pn': paginator.num_pages, 'sz': sz, 'q': q, 'pk':pk})

@staff_member_required
def sale_edit(request, pk=None):
    if pk:
        instance = get_object_or_404(Sale, pk=pk)
    else:
        instance = Sale()
    form = forms.SaleForm(
        request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()
        msg = pgettext_lazy(
            'Sale (discount) message', 'Updated sale') if pk else pgettext_lazy(
                'Sale (discount) message', 'Added sale')
        messages.success(request, msg)
        user_trail(request.user.name, 'updated discount : ' + str(instance.name), 'update')
        info_logger.info('User: ' + str(request.user.name) + ' updated discount:' + str(instance.name))
        return redirect('dashboard:sale-update', pk=instance.pk)
    ctx = {'sale': instance, 'form': form}
    return TemplateResponse(request, 'dashboard/discount/sale_form.html', ctx)


@staff_member_required
def create_discount(request):
    if request.method == 'POST':
        discount = Sale()
        if request.POST.get('variants'):
            variants = json.loads(request.POST.get('variants'))
        if request.POST.get('customers'):
            customers = json.loads(request.POST.get('customers'))        
        if request.POST.get('type'):
            discount.type = request.POST.get('type')
        if request.POST.get('value'):
            discount.value = request.POST.get('value')
        if request.POST.get('name'):
            discount.name = request.POST.get('name')
        if request.POST.get('start_date'):
            discount.start_date = request.POST.get('start_date')
        if request.POST.get('end_date'):
            discount.end_date = request.POST.get('end_date')
        discount.save()
        for variant in variants:
            discount.variant.add(variant)
        try:
            for customer in customers:
                discount.customers.add(customer)
        except:
            pass
        return HttpResponse(json.dumps({'message':discount.name}))
    else:
        return HttpResponse(json.dumps({'message':'Invalid method'}))
        

@staff_member_required
def sale_delete(request, pk):
    instance = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        instance.delete()
        messages.success(
            request,
            pgettext_lazy('Sale (discount) message', 'Deleted sale %s') % (instance.name,))
        user_trail(request.user.name, 'deleted discount : ' + str(instance.name), 'delete')
        info_logger.info('User: ' + str(request.user.name) + ' deleted discount:' + str(instance.name))
        return redirect('dashboard:sale-list')
    ctx = {'sale': instance}
    return TemplateResponse(
        request, 'dashboard/discount/sale_modal_confirm_delete.html', ctx)


@staff_member_required
def voucher_list(request):
    vouchers = Voucher.objects.select_related('product', 'category')
    ctx = {'vouchers': vouchers}
    return TemplateResponse(
        request, 'dashboard/discount/voucher_list.html', ctx)


@staff_member_required
def voucher_edit(request, pk=None):
    if pk is not None:
        instance = get_object_or_404(Voucher, pk=pk)
    else:
        instance = Voucher()
    voucher_form = forms.VoucherForm(request.POST or None, instance=instance)
    type_base_forms = {
        Voucher.SHIPPING_TYPE: forms.ShippingVoucherForm(
            request.POST or None, instance=instance,
            prefix=Voucher.SHIPPING_TYPE),
        Voucher.VALUE_TYPE: forms.ValueVoucherForm(
            request.POST or None, instance=instance,
            prefix=Voucher.VALUE_TYPE),
        Voucher.PRODUCT_TYPE: forms.ProductVoucherForm(
            request.POST or None, instance=instance,
            prefix=Voucher.PRODUCT_TYPE),
        Voucher.CATEGORY_TYPE: forms.CategoryVoucherForm(
            request.POST or None, instance=instance,
            prefix=Voucher.CATEGORY_TYPE)}
    if voucher_form.is_valid():
        voucher_type = voucher_form.cleaned_data['type']
        form_type = type_base_forms.get(voucher_type)
        if form_type is None:
            instance = voucher_form.save()
        elif form_type.is_valid():
            instance = form_type.save()

        if form_type is None or form_type.is_valid():
            msg = pgettext_lazy(
                'Voucher message', 'Updated voucher') if pk else pgettext_lazy(
                    'Voucher message', 'Added voucher')
            messages.success(request, msg)
            return redirect('dashboard:voucher-update', pk=instance.pk)
    ctx = {
        'voucher': instance, 'default_currency': settings.DEFAULT_CURRENCY,
        'form': voucher_form, 'type_base_forms': type_base_forms}
    return TemplateResponse(
        request, 'dashboard/discount/voucher_form.html', ctx)


@staff_member_required
def voucher_delete(request, pk):
    instance = get_object_or_404(Voucher, pk=pk)
    if request.method == 'POST':
        instance.delete()
        messages.success(
            request,
            pgettext_lazy('Voucher message', 'Deleted voucher %s') % (instance,))
        return redirect('dashboard:voucher-list')
    ctx = {'voucher': instance}
    return TemplateResponse(
        request, 'dashboard/discount/voucher_modal_confirm_delete.html', ctx)

@staff_member_required
def token_variants(request):
    search = request.GET.get('search')
    group = request.GET.get('group')    
    variants = ProductVariant.objects.all().filter(
        Q(name__icontains=search) |
        Q(sku__icontains=search) |
        Q(product__product_class__name__icontains=search) |
        Q(product__name__icontains=search)
    ).order_by('-id')[:10:1]
    l = []
    for variant in variants:        
        l.append({'text':variant.display_product(),'value': variant.pk})
    return HttpResponse(json.dumps(l), content_type='application/json')

