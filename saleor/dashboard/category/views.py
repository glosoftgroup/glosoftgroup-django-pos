from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import HttpResponse
import json
from django.utils.translation import pgettext_lazy

from ...product.models import ( Category, 
                                Product, 
                                ProductClass)
from ..views import staff_member_required
from .forms import CategoryForm, ProductForm
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from ...decorators import permission_decorator, user_trail

@staff_member_required
@permission_decorator('product.view_category')
def category_list(request, root_pk=None):
    root = None
    path = None
    categories = Category.tree.root_nodes().order_by('-id')

    page = request.GET.get('page', 1)
    paginator = Paginator(categories, 10)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except InvalidPage:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    if root_pk:
        root = get_object_or_404(Category, pk=root_pk)
        path = root.get_ancestors(include_self=True) if root else []
        categories = root.get_children().order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(categories, 10)
        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except InvalidPage:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)
        ctx = {'categories': categories, 'path': path, 'root': root, 'totalp': paginator.num_pages}
        return TemplateResponse(request, 'dashboard/category/list_subcategories.html', ctx)

    ctx = {'categories': categories, 'path': path, 'root': root, 'totalp':paginator.num_pages}    
    return TemplateResponse(request, 'dashboard/category/pagination/view.html', ctx)

def paginate_category(request, root_pk=None):
    root = None
    path = None

    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    try:
        if root_pk:
            root = get_object_or_404(Category, pk=root_pk)
            path = root.get_ancestors(include_self=True) if root else []
            categories = root.get_children().order_by('-id')
            paginator = Paginator(categories, 10)
        else:
            categories = Category.tree.root_nodes().order_by('-id')
            paginator = Paginator(categories, 10)

        if list_sz:
            paginator = Paginator(categories, int(list_sz))
            categories = paginator.page(page)
            data = {
                'categories': categories,
                'pn': paginator.num_pages,
                'sz': list_sz,
                'gid': 0,
                'root': root
            }
            return TemplateResponse(request, 'dashboard/category/pagination/p2.html', data)
        else:
            paginator = Paginator(categories, 10)
            if p2_sz:
                paginator = Paginator(categories, int(p2_sz))
            categories = paginator.page(page)
            data = {
                'categories': categories,
                'root': root
            }
            return TemplateResponse(request, 'dashboard/category/pagination/paginate.html', data)

        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except InvalidPage:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)

        return TemplateResponse(request, 'dashboard/category/pagination/paginate.html', {'categories': categories})
    except Exception, e:
        return  HttpResponse()

@staff_member_required
def category_search(request, root_pk=None):
    if request.is_ajax():
        root = None
        path = None
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            if root_pk:
                root = get_object_or_404(Category, pk=root_pk)
                path = root.get_ancestors(include_self=True) if root else []
                categories = root.get_children().filter(name__icontains=q).order_by('-id')
            else:
                categories = Category.tree.root_nodes().filter(name__icontains=q).order_by('-id')

            paginator = Paginator(categories, 10)

            try:
                categories = paginator.page(page)
            except PageNotAnInteger:
                categories = paginator.page(1)
            except InvalidPage:
                categories = paginator.page(1)
            except EmptyPage:
                categoriest = paginator.page(paginator.num_pages)
            if p2_sz:
                categories = paginator.page(page)
                return TemplateResponse(request, 'dashboard/category/pagination/paginate.html', {'categories': categories,'root': root})

            return TemplateResponse(request, 'dashboard/category/pagination/search.html',
                                    {'categories':categories, 'pn': paginator.num_pages, 'sz': sz, 'q': q,'root': root})


@staff_member_required
@permission_decorator('product.add_category')
def category_create32(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = Category() 
        all_cats = Category.objects.all().order_by('-id')       
        description = request.POST.get('description')
        new_category = Category.objects.create(name=name,description=description)
        product = Product()
        class_pk = ProductClass.objects.all().first().pk
        product_class = get_object_or_404(ProductClass, pk=class_pk)
        product.product_class = product_class
        product_form = ProductForm(request.POST or None, instance=product)
        ctx = {'all_cats':all_cats,'category': category, 'product_form': product_form}
        return TemplateResponse(request, 'dashboard/category/_category_add_success.html', ctx)
    else:
        return HttpResponse('Unexpected get method')
@staff_member_required
@permission_decorator('product.add_category')
def category_create(request, root_pk=None):
    category = Category()
    form = CategoryForm(request.POST or None, parent_pk=root_pk)
    if form.is_valid():
        category = form.save()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Added category %s') % category)
        if request.is_ajax():
            product = Product()
            class_pk = ProductClass.objects.all().first().pk
            product_class = get_object_or_404(ProductClass, pk=class_pk)
            product.product_class = product_class
            product_form = ProductForm(request.POST or None, instance=product)
            ctx = {'category': category, 'product_form': product_form}
            return TemplateResponse(request, 'dashboard/category/_category_add_success.html', ctx)    
        if root_pk:
            return redirect('dashboard:category-list', root_pk=root_pk)
        else:
            return redirect('dashboard:category-list')
    ctx = {'category': category, 'form': form}
    if request.is_ajax():        
        return TemplateResponse(request, 'dashboard/category/ajax_modal_detail.html', ctx)    
    return TemplateResponse(request, 'dashboard/category/detail.html', ctx)


@staff_member_required
@permission_decorator('product.change_category')
def category_edit(request, root_pk=None):
    category = get_object_or_404(Category, pk=root_pk)
    form = CategoryForm(request.POST or None, instance=category,
                        parent_pk=category.parent_id)
    status = 200
    if form.is_valid():
        category = form.save()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Updated category %s') % category)
        if root_pk:
            return redirect('dashboard:category-list', root_pk=root_pk)
        else:
            return redirect('dashboard:category-list')
    elif form.errors:
        status = 400
    ctx = {'category': category, 'form': form, 'status': status}
    template = 'dashboard/category/modal_edit.html'
    return TemplateResponse(request, template, ctx, status=status)

@staff_member_required
@permission_decorator('product.delete_category')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Deleted category %s') % category)
        root_pk = None
        if category.parent:
            root_pk = category.parent.pk
        if root_pk:
            if request.is_ajax():
                response = {'redirectUrl': reverse(
                    'dashboard:category-list', kwargs={'root_pk': root_pk})}
                return JsonResponse(response)
            return redirect('dashboard:category-list', root_pk=root_pk)
        else:
            if request.is_ajax():
                response = {'redirectUrl': reverse('dashboard:category-list')}
                return JsonResponse(response)
            return redirect('dashboard:category-list')
    ctx = {'category': category,
           'descendants': list(category.get_descendants()),
           'products_count': len(category.products.all())}
    return TemplateResponse(request,
                            'dashboard/category/modal_delete.html',
                            ctx)
