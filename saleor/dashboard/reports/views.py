from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Min, Sum, Avg, F, Q
from django.core import serializers
# from django.template.defaultfilters import date
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import datetime
from datetime import date, timedelta
from django.utils.dateformat import DateFormat
import logging

from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf
import csv
import random
from django.utils.encoding import smart_str
from datetime import date

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem, DrawerCash
from ...product.models import Product, ProductVariant, Stock
from ...purchase.models import PurchaseProduct
from ...decorators import permission_decorator, user_trail
from ...dashboard.views import get_low_stock_products

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_list(request):
    try:
        try:
            last_sale = Sales.objects.latest('id')
            last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
        except:
            last_date_of_sales = DateFormat(datetime.datetime.today()).format('Y-m-d')

        all_sales = Sales.objects.filter(created__contains=last_date_of_sales)
        total_sales_amount = all_sales.aggregate(Sum('total_net'))
        total_tax_amount = all_sales.aggregate(Sum('total_tax'))
        total_sales = []
        for sale in all_sales:
            quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Sum('quantity'))
            setattr(sale, 'quantity', quantity['c'])
            total_sales.append(sale)

        page = request.GET.get('page', 1)
        paginator = Paginator(total_sales, 10)
        try:
            total_sales = paginator.page(page)
        except PageNotAnInteger:
            total_sales = paginator.page(1)
        except InvalidPage:
            total_sales = paginator.page(1)
        except EmptyPage:
            total_sales = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed sales reports', 'view')
        info_logger.info('User: ' + str(request.user.name) + ' accessed the view sales report page')
        return TemplateResponse(request, 'dashboard/reports/sales/sales_list.html',{'pn': paginator.num_pages, 'sales': total_sales, "total_sales_amount":total_sales_amount, "total_tax_amount":total_tax_amount,"date":last_date_of_sales})
    except ObjectDoesNotExist as e:
        error_logger.error(e)

@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_detail(request, pk=None):
    try:
        sale = Sales.objects.get(pk=pk)
        items = SoldItem.objects.filter(sales=sale)
        return TemplateResponse(request, 'dashboard/reports/sales/details.html',{'items': items, "sale":sale})
    except ObjectDoesNotExist as e:
        error_logger.error(e)

@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_revert(request, pk=None):
    try:
        sale = Sales.objects.get(pk=pk)
        items = SoldItem.objects.filter(sales=sale)

        for solditem in items:
            try:
                st = Stock.objects.get(pk=solditem.stock_id)
                st.quantity = st.quantity + solditem.quantity
                st.save()
                solditem.delete()
            except Exception as e:
                variant = ProductVariant.objects.get(sku=solditem.sku)
                Stock.objects.create(
                    variant=variant,
                    price_override=solditem.unit_cost,
                    wholesale_override=solditem.wholesale_override,
                    minimum_price=solditem.minimum_price,
                    low_stock_threshold=solditem.low_stock_threshold,
                    cost_price=solditem.unit_purchase,
                    quantity=solditem.quantity)
                solditem.delete()

        sale.delete()

        data = {
            'message': 'success',
            'status': 200
        }
        return JsonResponse(data)
    except ObjectDoesNotExist as e:
        error_logger.error(e)
        data = {
            'message': str("Error Reverting Sale"),
            'status': 400
        }
        return JsonResponse(data)

@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_reports(request):
    try:
        today = datetime.date.today()
        items = SoldItem.objects.all().order_by('-id')
        ts = Sales.objects.filter(created__icontains=today)
        tsum = ts.aggregate(Sum('total_net'))
        total_sales = Sales.objects.aggregate(Sum('total_net'))
        total_tax = Sales.objects.aggregate(Sum('total_tax'))
        page = request.GET.get('page', 1)
        paginator = Paginator(items, 10)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed sales reports','view')
        info_logger.info('User: '+str(request.user.name)+' accessed the view sales report page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/reports/sales/sales.html', {'items':items, 'total_sales':total_sales,'total_tax':total_tax, 'ts':ts, 'tsum':tsum})
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing sales reports')

@staff_member_required
def sales_paginate(request):
    page = int(request.GET.get('page'))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    date = request.GET.get('gid')
    sales = Sales.objects.all().order_by('-id')
    today_formart = DateFormat(datetime.date.today())
    today = today_formart.format('Y-m-d')
    ts = Sales.objects.filter(created__icontains=today)
    tsum = ts.aggregate(Sum('total_net'))
    total_sales = Sales.objects.aggregate(Sum('total_net'))
    total_tax = Sales.objects.aggregate(Sum('total_tax'))


    if date:
        try:
            all_salesd = Sales.objects.filter(created__icontains=date).order_by('-id')
            that_date_sum = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))
            sales = []
            for sale in all_salesd:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Sum('quantity'))
                setattr(sale, 'quantity', quantity['c'])
                sales.append(sale)

            if p2_sz and date:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'sales':sales, 'gid':date})

            paginator = Paginator(sales, 10)
            sales = paginator.page(page)
            return TemplateResponse(request,'dashboard/reports/sales/p2.html',
                {'sales':sales, 'pn':paginator.num_pages,'sz':10,'gid':date,
                'total_sales':total_sales,'total_tax':total_tax,'tsum':tsum,
                'that_date_sum':that_date_sum, 'date':date, 'today':today})

        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/p2.html',{'date': date})

    else:
        try:
            last_sale = Sales.objects.latest('id')
            last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
            all_sales = Sales.objects.filter(created__contains=last_date_of_sales)
            total_sales_amount = all_sales.aggregate(Sum('total_net'))
            total_tax_amount = all_sales.aggregate(Sum('total_tax'))
            sales = []
            for sale in all_sales:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Sum('quantity'))
                setattr(sale, 'quantity', quantity['c'])
                sales.append(sale)

            if list_sz:
                paginator = Paginator(sales, int(list_sz))
                sales = paginator.page(page)
                return TemplateResponse(request,'dashboard/reports/sales/p2.html',{'sales':sales, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0, 'total_sales':total_sales,'total_tax':total_tax, 'tsum':tsum})
            else:
                paginator = Paginator(sales, 10)
            if p2_sz:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'sales':sales})

            try:
                sales = paginator.page(page)
            except PageNotAnInteger:
                sales = paginator.page(1)
            except InvalidPage:
                sales = paginator.page(1)
            except EmptyPage:
                sales = paginator.page(1)
            return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'sales':sales})
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/p2.html', {'date': date})

@staff_member_required
def sales_search(request):
    if request.is_ajax():
        page = int(request.GET.get('page', 1))
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get( 'q' )
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            all_sales = Sales.objects.filter(
                Q( invoice_number__icontains = q ) |
                Q( terminal__terminal_name__icontains = q ) |
                Q(created__icontains=q) |
                Q(customer__name__icontains=q) | Q(customer__mobile__icontains=q) |
                Q(solditems__product_name__icontains=q) |
                Q(user__email__icontains=q) |
                Q(user__name__icontains=q)).order_by( 'id' ).distinct()
            sales = []

            if request.GET.get('gid'):
                csales = all_sales.filter(created__icontains=request.GET.get('gid'))
                for sale in csales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Sum('quantity'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)

                if p2_sz:
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales/paginate.html', {'sales': sales})

                if list_sz:
                    paginator = Paginator(sales, int(list_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales/search.html',
                                            {'sales': sales, 'pn': paginator.num_pages, 'sz': list_sz,
                                             'gid': request.GET.get('gid'), 'q': q})

                paginator = Paginator(sales, 10)
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales/search.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': sz,
                                         'gid': request.GET.get('gid')})

            else:
                for sale in all_sales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Sum('quantity'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)

                if list_sz:
                    print ('lst')
                    paginator = Paginator(sales, int(list_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales/search.html',
                                            {'sales': sales, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                             'q': q})

                if p2_sz:
                    print ('pst')
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales/paginate.html', {'sales': sales})

                paginator = Paginator(sales, 10)
                try:
                    sales = paginator.page(page)
                except PageNotAnInteger:
                    sales = paginator.page(1)
                except InvalidPage:
                    sales = paginator.page(1)
                except EmptyPage:
                    sales = paginator.page(paginator.num_pages)
                if p2_sz:
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales/paginate.html', {'sales': sales})

                return TemplateResponse(request, 'dashboard/reports/sales/search.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': sz, 'q': q})

@staff_member_required
@permission_decorator('reports.view_products_reports')
def product_reports(request):
    try:
        items = Stock.objects.all().order_by('-id')
        total_cost = 0
        for i in items:
            try:
                total_cost+=i.get_total_cost()
            except Exception as e:
                total_cost+=0
        page = request.GET.get('page', 1)
        paginator = Paginator(items, 10)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed products reports','view')
        info_logger.info('User: '+str(request.user.name)+' accessed the view sales report page')
        return TemplateResponse(request, 'dashboard/reports/products/products.html', {'pn':paginator.num_pages,'items':items, 'total_cost':total_cost})
    except TypeError as e:
        error_logger.error(e)
        print (e)
        return HttpResponse('error accessing products reports')


@staff_member_required
def products_paginate(request):
    page = int(request.GET.get('page'))
    list_sz = request.GET.get('size')
    date = request.GET.get('date')
    action = request.GET.get('action')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    gid = request.GET.get('gid')
    items = Stock.objects.all().order_by('-id')
    if request.GET.get('sth'):
        if action:
            try:
                items = Stock.objects.all().order_by('-id')
                if p2_sz and gid:
                    paginator = Paginator(items, int(p2_sz))
                    items = paginator.page(page)
                    return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items, 'gid':action})

                paginator = Paginator(items, 10)
                items = paginator.page(page)
                return TemplateResponse(request,'dashboard/reports/products/p2.html',{'items':items, 'pn':paginator.num_pages,'sz':10,'gid':action})

            except ValueError as e:
                return HttpResponse(e)
    else:

        if list_sz:
            paginator = Paginator(items, int(list_sz))
            items = paginator.page(page)
            return TemplateResponse(request,'dashboard/reports/products/p2.html',{'items':items, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0})
        else:
            paginator = Paginator(items, 10)
        if p2_sz:
            paginator = Paginator(items, int(p2_sz))
            items = paginator.page(page)
            return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items})

        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items})

@staff_member_required
def products_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get( 'q' )
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            items = Stock.objects.filter(
                Q( variant__sku__icontains = q ) |
                Q( variant__product__name__icontains = q ) |
                Q(variant__product__product_class__name__icontains = q) ).order_by( '-id' )

            if p2_sz:
                paginator = Paginator(items, int(p2_sz))
                items = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/products/paginate.html', {'items': items})

            if list_sz:
                paginator = Paginator(items, int(list_sz))
                items = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/products/search.html',
                                        {'items': items, 'pn': paginator.num_pages, 'sz': list_sz,
                                         'gid': request.GET.get('gid'), 'q': q})

            paginator = Paginator(items, 10)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except InvalidPage:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)
            if p2_sz:
                items = paginator.page(page)
                return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items})

            return TemplateResponse(request, 'dashboard/reports/products/search.html', {'items':items, 'pn':paginator.num_pages,'sz':sz,'q':q})

@staff_member_required
def products_reorder_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get( 'q' )
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            products = get_low_stock_products()
            items = products.filter(
                Q(variant__product__name__icontains=q) |
                Q(variant__name__icontains=q)).order_by('-id').distinct()
            paginator = Paginator(items, 10)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except InvalidPage:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)
            if p2_sz:
                items = paginator.page(page)
                return TemplateResponse(request,'dashboard/reports/products/reorder_paginate.html',{'items':items})

            if list_sz:
                paginator = Paginator(items, int(list_sz))
                items = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/products/reorder_search.html',
                                        {'items': items, 'pn': paginator.num_pages, 'sz': list_sz,
                                         'gid': request.GET.get('gid'), 'q': q})

            return TemplateResponse(request, 'dashboard/reports/products/reorder_search.html', {'items':items, 'pn':paginator.num_pages,'sz':sz,'q':q})


@staff_member_required
def sales_list_export_csv(request):
    pdfname = 'sales'+str(random.random())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="'+pdfname+'.csv"'

    try:
        last_sale = Sales.objects.latest('id')
        last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
    except:
        last_date_of_sales = DateFormat(datetime.datetime.today()).format('Y-m-d')

    all_sales = Sales.objects.filter(created__contains=last_date_of_sales)
    total_sales_amount = all_sales.aggregate(Sum('total_net'))
    total_tax_amount = all_sales.aggregate(Sum('total_tax'))
    total_sales = []
    for sale in all_sales:
        quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Sum('quantity'))
        if not sale['customer']:
            sale['customer'] = 'Customer'
        setattr(sale, 'quantity', quantity['c'])
        total_sales.append(sale)

    qs = total_sales
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"Transaction Date"),
        smart_str(u"Receipt No"),
        smart_str(u"Client Name"),
        smart_str(u"Cashier"),
        smart_str(u"Terminal"),
        smart_str(u"Quantity"),
        smart_str(u"Total Sales"),
    ])
    for obj in qs:
        writer.writerow([
            smart_str(obj.created),
            smart_str(obj.invoice_number),
            smart_str(obj.customer),
            smart_str(obj.user.name),
            smart_str(obj.terminal),
            smart_str(obj.quantity),
            smart_str(obj.total_net),
        ])
    return response


@staff_member_required
def products_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        if q is not None:
            items = Stock.objects.filter(
                Q(variant__sku__icontains=q) |
                Q(variant__product__name__icontains=q) |
                Q(variant__product__product_class__name__icontains=q)).order_by('-id')

            data = {
                'today': date.today(),
                'items': items,
                'puller': request.user,
                'gid':gid
            }
            pdf = render_to_pdf('dashboard/reports/products/pdf/pdf.html', data)
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            items = ProductVariant.objects.all().order_by('-id')

            data = {
                'today': date.today(),
                'items': items,
                'puller': request.user,
                'gid': gid
            }
            pdf = render_to_pdf('dashboard/reports/products/pdf/pdf.html', data)
            return HttpResponse(pdf, content_type='application/pdf')

@staff_member_required
def products_export_csv(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        if q is not None:
            items = ProductVariant.objects.filter(
                Q(sku__icontains=q) |
                Q(product__name__icontains=q) |
                Q(product__product_class__name__icontains=q)).order_by('-id')
        else:
            items = ProductVariant.objects.all().order_by('id')

        pdfname = 'products' + str(random.random())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + pdfname + '.csv"'
        qs = items
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
        writer.writerow([
            smart_str(u"sku"),
            smart_str(u"Product Name"),
            smart_str(u"Category"),
            smart_str(u"Sub-Category"),
            smart_str(u"Reorder-level"),
            smart_str(u"Current Quantity"),
            smart_str(u"Unit Cost"),
            smart_str(u"Total Cost"),
        ])
        for obj in qs:
            writer.writerow([
                smart_str(obj.sku),
                smart_str(obj.display_product()),
                smart_str(obj.product.get_first_category()),
                smart_str(obj.product.product_class.name),
                smart_str(obj.product.low_stock_threshold),
                smart_str(obj.get_stock_quantity()),
                smart_str(obj.get_price_per_item().gross),
                smart_str(obj.get_total_price_cost()),
            ])
        return response


@staff_member_required
@permission_decorator('reports.view_balancesheet')
def balancesheet_reports(request):
    get_date = request.GET.get('date')
    if get_date:
        date = get_date
    else:
        try:
            last_sale = Sales.objects.latest('id')
            date = DateFormat(last_sale.created).format('Y-m-d')
        except:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    try:
        """ Debit """
        petty_cash = 30000
        try:
            ds = DrawerCash.objects.latest('id')
            drawer = ds.objects.annotate(c=Count('terminal', distinct=True)).aggregate(total_amount=Sum('amount'))['total_amount']
        except:
            drawer = 0
        # stock = 23000 #from purchases
        items = ProductVariant.objects.all().order_by('-id')
        stock = 0
        for i in items:
            stock += i.get_total_price_cost()

        sales_cash = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))['total_net__sum']
        cash_in_hand = drawer + sales_cash

        debit_total = petty_cash + stock + cash_in_hand

        """ Credit """
        accounts_payable = petty_cash + stock
        notes_payable = drawer
        revenues = sales_cash
        # expenses = 1233
        credit_total = accounts_payable + notes_payable + revenues
        data = {
            "petty_cash":petty_cash,
            "cash_in_hand":cash_in_hand,
            "stock":stock,
            "debit_total":debit_total,

            "accounts_payable":accounts_payable,
            "notes_payable":notes_payable,
            "revenues":revenues,
            "credit_total":credit_total,
            "status":True
        }
        return TemplateResponse(request, 'dashboard/reports/balancesheet/balancesheet.html', data)
    except ObjectDoesNotExist as e:
        error_logger.error(e)
        return TemplateResponse(request, 'dashboard/reports/balancesheet/balancesheet.html')
    except TypeError as e:
        error_logger.error(e)
        return TemplateResponse(request, 'dashboard/reports/balancesheet/balancesheet.html')

@staff_member_required
def get_dashboard_data(request):
    label = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
    default = [12, 19, 3, 5, 2, 3]
    total_sales = Sales.objects.all()
    today = datetime.date.today()
    todays_sales = Sales.objects.filter(created=today).annotate(Sum('total_net'))

    ''' get highest product '''

    ''' get lowest product '''
    data = {
         "label":label,
         "default":default,
         "users":10,
         "net":serializers.serialize('json', total_sales),
         "todays_sales": serializers.serialize('json', todays_sales),
    }
    return JsonResponse(data)

@staff_member_required
@permission_decorator('reports.view_products_reports')
def product_reorder(request):
    try:
        low_stock = get_low_stock_products()
        page = request.GET.get('page', 1)
        paginator = Paginator(low_stock, 10)
        try:
            low_stock = paginator.page(page)
        except PageNotAnInteger:
            low_stock = paginator.page(1)
        except InvalidPage:
            low_stock = paginator.page(1)
        except EmptyPage:
            low_stock = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed products reports','view')
        info_logger.info('User: '+str(request.user.name)+' accessed the view sales report page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/reports/products/reorder.html', {'low_stock':low_stock})
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing products reports')

@staff_member_required
def products_reorder_paginate(request):
    page = int(request.GET.get('page'))
    list_sz = request.GET.get('size')
    date = request.GET.get('date')
    action = request.GET.get('action')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    gid = request.GET.get('gid')
    items = get_low_stock_products()
    if request.GET.get('sth'):
        if action:
            try:
                if p2_sz and gid:
                    paginator = Paginator(items, int(p2_sz))
                    items = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/products/reorder_paginate.html',
                                            {'items': items, 'gid': action})

                paginator = Paginator(items, 10)
                items = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/products/reorder_p2.html',
                                        {'items': items, 'pn': paginator.num_pages, 'sz': 10, 'gid': action})

            except ValueError as e:
                return HttpResponse(e)
    else:

        if list_sz:
            paginator = Paginator(items, int(list_sz))
            items = paginator.page(page)
            return TemplateResponse(request, 'dashboard/reports/products/reorder_p2.html',
                                    {'items': items, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
        else:
            paginator = Paginator(items, 10)
        if p2_sz:
            print ('hello')
            print (page)
            print (p2_sz)
            paginator = Paginator(items, int(p2_sz))
            items = paginator.page(int(page))
            return TemplateResponse(request, 'dashboard/reports/products/reorder_paginate.html', {'items': items})

        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return TemplateResponse(request, 'dashboard/reports/products/reorder_paginate.html', {'items': items})

@staff_member_required
def reorder_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        if q is not None:
            products = items = get_low_stock_products()
            items = products.filter(
                Q(variant__product__name__icontains=q) |
                Q(variant__name__icontains=q)).order_by('id').distinct()

            data = {
                'today': date.today(),
                'items': items,
                'puller': request.user,
                'gid':gid
            }
            pdf = render_to_pdf('dashboard/reports/products/pdf/reorder_pdf.html', data)
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            items = get_low_stock_products()

            data = {
                'today': date.today(),
                'items': items,
                'puller': request.user,
                'gid': gid
            }
            pdf = render_to_pdf('dashboard/reports/products/pdf/reorder_pdf.html', data)
            return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
def reorder_export_csv(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        if q is not None:
            products = items = get_low_stock_products()
            items = products.filter(name__icontains=q).order_by('-id')
        else:
            items = get_low_stock_products()

        pdfname = 'low stock products-'+str(random.random())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="'+pdfname+'.csv"'
        # qs = PurchaseProduct.objects.all().order_by('id')
        qs = items
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
        writer.writerow([
            smart_str(u"Product name"),
            smart_str(u"Stock left"),
            smart_str(u"Low stock Threshold"),
        ])

        for obj in qs:
            writer.writerow([
                smart_str(obj),
                smart_str(obj.total_stock),
                smart_str(obj.low_stock_threshold)
            ])
        return response
