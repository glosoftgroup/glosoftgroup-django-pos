from django.db.models import Q, Count, Avg

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import pagination

from .pagination import PostLimitOffsetPagination
from ...allocate.models import Allocate
from ...sale.models import (
                            Sales, SoldItem,
                            Terminal, 
                            TerminalHistoryEntry,
                            DrawerCash
                            )

from .serializers import (
    AllocateListSerializer,
    CreateAllocateSerializer,
    AllocateUpdateSerializer,
    CarAllocateListSerializer
     )
from rest_framework import generics
from ...decorators import user_trail
from ...site.models import SiteSettings
import logging
from django.contrib.auth import get_user_model

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class AllocateDetailAPIView(generics.RetrieveAPIView):
    queryset = Allocate.objects.all()
    serializer_class = AllocateListSerializer


class AllocateCreateAPIView(generics.CreateAPIView):
    """ allocate products to a agent """
    queryset = Allocate.objects.all()
    serializer_class = CreateAllocateSerializer

    def perform_create(self, serializer):              
        instance = serializer.save(user=self.request.user)
        # show tranfer in sale
        show_transfer = SiteSettings.objects.get(pk=1).show_transfer
        if instance.status == 'fully-paid':
            if show_transfer:
                send_to_sale(instance)


class AllocateListAPIView(generics.ListAPIView):
    serializer_class = AllocateListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Allocate.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query)
                ).distinct()
        return queryset_list


class CarTransferListAPIView(generics.ListAPIView):
    serializer_class = AllocateListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                car_pk = Allocate.objects.get(pk=self.kwargs['pk']).car.pk
                queryset_list = Allocate.objects.filter(car__pk=car_pk).select_related()
            else:
                queryset_list = Allocate.objects.all().order_by('-id').select_related()
        except Exception as e:
            queryset_list = Allocate.objects.all().select_related()
        query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if self.request.GET.get('status') == 'True':
                queryset_list = queryset_list.filter(active=True)
            if self.request.GET.get('status') == 'False':
                queryset_list = queryset_list.filter(active=False)
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(created__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query) |
                Q(car__number__icontains=query) |
                Q(car__name__icontains=query)
                ).distinct()
        return queryset_list.order_by('-id')


class CarListAPIView(generics.ListAPIView):
    serializer_class = CarAllocateListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = Allocate.objects.filter(customer__pk=self.kwargs['pk']).order_by('car').distinct('car').select_related()
            else:
                queryset_list = Allocate.objects.all.select_related()
        except Exception as e:
            queryset_list = Allocate.objects.distinct('car')
            query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if self.request.GET.get('status') == 'True':
                queryset_list = queryset_list.filter(active=True)
            if self.request.GET.get('status') == 'False':
                queryset_list = queryset_list.filter(active=False)
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(created__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query) |
                Q(car__number__icontains=query) |
                Q(agent__name__icontains=query) |
                Q(car__name__icontains=query)
                ).distinct('car')
        return queryset_list.order_by('car')


class AllocateAgentListAPIView(generics.ListAPIView):
    """
        list agents pending allocated products items
        @:param pk agent id
        GET api/allocate/agent/6/
        payload Json: /payload/agents_allocations.json
    """
    serializer_class = AllocateListSerializer
    queryset = Allocate.objects.all()

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        queryset = self.get_queryset().filter(
            Q(agent__pk=pk) and
            Q(status='payment-pending')
        )
        serializer = AllocateListSerializer(queryset, many=True, context=serializer_context)
        return Response(serializer.data)

    def get_queryset(self, *args, **kwargs):
        queryset_list = Allocate.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query)               
                ).distinct()
        return queryset_list


class AllocateListAPIView2(generics.ListAPIView):
    serializer_class = AllocateListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Allocate.objects.filter(status='payment-pending')
        query = self.request.GET.get('q')
        try:
            if query:
                queryset_list = queryset_list.filter(status='payment-pending').filter(
                    Q(invoice_number__icontains=query)|
                    Q(customer__name__icontains=query)|
                    Q(customer__mobile__icontains=query)).distinct()
        except:
            print('nothing found')
        return queryset_list


class AllocateUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
        update allocated products
        :param quantity: amount sold by agent
        :return updated allocate instance
        :operation subtracts allocated_quantity quantity result added back to stock
        sold quantities are sent to sale model.
        :payload - /payload/update-allocate.json
    """
    queryset = Allocate.objects.all()
    serializer_class = AllocateUpdateSerializer

    def perform_update(self, serializer):
        instance = serializer.save(user=self.request.user)
        show_transfer = SiteSettings.objects.get(pk=1).show_transfer
        if instance.amount_paid != 0.00:
            if show_transfer:
                send_to_sale(instance)
        else:
            print('amount paid cannot be zero')
        user_trail(self.request.user.name,'made a allocated sale:#'+str(serializer.data['invoice_number'])+' credit sale worth: '+str(serializer.data['total_net']),'add')
        info_logger.info('User: '+str(self.request.user)+' made a allocated sale:'+str(serializer.data['invoice_number']))
        terminal = Terminal.objects.get(pk=int(serializer.data['terminal']))
        trail = 'User: '+str(self.request.user)+\
                ' updated a allocated sale :'+str(serializer.data['invoice_number'])+\
                ' Net#: '+str(serializer.data['total_net'])+\
                ' Amount paid#:'+str(serializer.data['amount_paid'])

        TerminalHistoryEntry.objects.create(
                            terminal=terminal,
                            comment=trail,
                            crud='deposit',
                            user=self.request.user
                        )
        drawer = DrawerCash.objects.create(manager=self.request.user,                                        
                                           user = self.request.user,
                                           terminal=terminal,
                                           amount=serializer.data['amount_paid'],
                                           trans_type='allocated sale paid')
        

def send_to_sale(credit):
    sale = Sales()
    sale.user = credit.user
    sale.transfer = True
    sale.total_net = credit.amount_paid
    sale.sub_total = credit.sub_total
    sale.balance = credit.balance
    sale.terminal = credit.terminal
    sale.amount_paid = credit.amount_paid
    sale.status = credit.status
    sale.total_tax = credit.total_tax
    sale.mobile = credit.mobile
    sale.customer_name = credit.customer_name
    try:
        sale.invoice_number = credit.invoice_number
        sale.save()
    except Exception as e:
        invoice_number = Sales.objects.latest('id')
        invoice_number = str(invoice_number.id) + str(credit.invoice_number)
        sale.invoice_number = invoice_number
        sale.save()
        print(e)

    for item in credit.items():
        if item.quantity:
            new = SoldItem()
            new.sales = sale
            new.sku = item.sku
            new.quantity = item.quantity
            new.product_name = item.product_name
            new.total_cost = item.total_cost
            new.unit_cost = item.unit_cost
            new.product_category=item.product_category
            new.save()
