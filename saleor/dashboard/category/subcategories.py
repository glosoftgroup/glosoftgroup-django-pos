from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy

from ...product.models import ( Category,
                                Product,
                                ProductClass)
from ..views import staff_member_required
from .forms import CategoryForm, ProductForm
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ...decorators import permission_decorator, user_trail
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def view(request, pk):
	try:
		cat = Category.objects.get(pk=pk)
		queryset_list = ProductClass.objects.filter(products__categories__pk=cat.pk).prefetch_related(
			'product_attributes', 'variant_attributes').order_by('-id').distinct()
		page = request.GET.get('page', 1)
		paginator = Paginator(queryset_list, 10)
		try:
			queryset_list = paginator.page(page)
		except PageNotAnInteger:
			queryset_list = paginator.page(1)
		except InvalidPage:
			queryset_list = paginator.page(1)
		except EmptyPage:
			queryset_list = paginator.page(paginator.num_pages)
		product_results = queryset_list
		user_trail(request.user.name, 'accessed the categories page','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the categories page page')
		product_results.object_list = [
			(pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
			 pc.variant_attributes.all())
			for pc in product_results.object_list]

		data = {
			'product_classes': product_results,
			'totalp':paginator.num_pages,
			'subcategory_name':cat.name,
			'cat_pk':cat.pk,
		}
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/category/subcategories/view.html', data)
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse(e)

def paginate(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')
	pk = int(request.GET.get('cat_pk'))

	try:
		cat = Category.objects.get(pk=pk)
		queryset_list =ProductClass.objects.filter(products__categories__pk=cat.pk).prefetch_related(
			'product_attributes', 'variant_attributes').order_by('-id').distinct()
		
		if list_sz:
			paginator = Paginator(queryset_list, int(list_sz))
			queryset_list = paginator.page(page)
			product_results = queryset_list
			product_results.object_list = [
				(pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
				 pc.variant_attributes.all())
				for pc in product_results.object_list]
			data = {
				'product_classes': product_results,
				'pn': paginator.num_pages,
				'sz': list_sz,
				'gid': 0,
				'cat_pk': cat.pk,
			}
			return TemplateResponse(request, 'dashboard/category/subcategories/p2.html', data)
		else:
			paginator = Paginator(queryset_list, 10)
			if p2_sz:
				paginator = Paginator(queryset_list, int(p2_sz))
			queryset_list = paginator.page(page)
			product_results = queryset_list
			product_results.object_list = [
				(pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
				 pc.variant_attributes.all())
				for pc in product_results.object_list]
			data = {
				'product_classes': product_results,
				'product_pk': pk,
			}
			return TemplateResponse(request, 'dashboard/category/subcategories/paginate.html', data)

		try:
			queryset_list = paginator.page(page)
		except PageNotAnInteger:
			queryset_list = paginator.page(1)
		except InvalidPage:
			queryset_list = paginator.page(1)
		except EmptyPage:
			queryset_list = paginator.page(paginator.num_pages)
		product_results = queryset_list
		product_results.object_list = [
			(pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
			 pc.variant_attributes.all())
			for pc in product_results.object_list]
		data = {
			'product_classes': product_results,
			'cat_pk': cat.pk,
		}
		return TemplateResponse(request, 'dashboard/category/subcategories/paginate.html', data)
	except Exception, e:
		return  HttpResponse()

@staff_member_required
def search(request):
	if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		pk = int(request.GET.get('cat_pk'))

		if list_sz is None:
			sz = 10
		else:
			sz = list_sz

        if q is not None:
			cat = Category.objects.get(pk=pk)			
			subcats = ProductClass.objects.filter(products__categories__pk=cat.pk).order_by('-id').distinct()
			queryset_list = subcats.filter(
				Q(name__icontains=q)|
				Q(product_attributes__name__icontains=q)
			).prefetch_related(
				'product_attributes', 'variant_attributes').order_by('-id')

			paginator = Paginator(queryset_list, 10)

			try:
				queryset_list = paginator.page(page)
			except PageNotAnInteger:
				queryset_list = paginator.page(1)
			except InvalidPage:
				queryset_list = paginator.page(1)
			except EmptyPage:
				queryset_list = paginator.page(paginator.num_pages)
			product_results = queryset_list
			product_results.object_list = [
				(pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
				 pc.variant_attributes.all())
				for pc in product_results.object_list]

			if p2_sz:
				queryset_list = paginator.page(page)
				product_results = queryset_list
				product_results.object_list = [
					(pc.pk, pc.name, pc.has_variants, pc.product_attributes.all(),
					 pc.variant_attributes.all())
					for pc in product_results.object_list]
				return TemplateResponse(request, 'dashboard/category/subcategories/paginate.html', {'product_classes': product_results, 'cat_pk':cat.pk})

			return TemplateResponse(request, 'dashboard/category/subcategories/search.html',
									{'product_classes':product_results, 'pn': paginator.num_pages, 'sz': sz, 'q': q, 'cat_pk':cat.pk})