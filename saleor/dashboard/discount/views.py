from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy

from ...discount.models import Sale, Voucher
from ...decorators import permission_decorator, user_trail
from . import forms
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def sale_list(request):
    sales = Sale.objects.prefetch_related('products')
    ctx = {'sales': sales}
    user_trail(request.user.name, 'accessed discount page', 'view')
    info_logger.info('User: ' + str(request.user.name) + 'accessed discount page')
    return TemplateResponse(request, 'dashboard/discount/sale_list.html', ctx)

@staff_member_required
def discount_detail(request,pk=None):
    if request.method == 'GET':
        if pk:
            instance = get_object_or_404(Sale, pk=pk)
            products = instance.products.all()
            ctx = {'product_results':products,'discount':instance}
            user_trail(request.user.name, 'accessed discount detail page for '+str(instance.name), 'view')
            info_logger.info('User: ' + str(request.user.name) + 'accessed discount detail page for '+str(instance.name))
            return TemplateResponse(request, 'dashboard/discount/discount_detail.html', ctx)

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
