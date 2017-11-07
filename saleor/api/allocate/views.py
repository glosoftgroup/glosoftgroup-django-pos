from django.db.models import Q
from .pagination import PostLimitOffsetPagination
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                    )
from rest_framework.response import Response
from rest_framework.request import Request
from ...product.models import (
    Product,
    ProductVariant,
    Stock,
    )
from ...allocate.models import Allocate
from ...sale.models import (
                            Sales, SoldItem,
                            Terminal, 
                            TerminalHistoryEntry,
                            DrawerCash
                            )
from ...customer.models import Customer
from .serializers import (
    AllocateListSerializer,
    CreateAllocateSerializer,
    AllocateUpdateSerializer,
     )
from rest_framework import generics
from ...decorators import user_trail
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
        if instance.status == 'fully-paid':
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


class AllocateAgentListAPIView(generics.ListAPIView):
    """
        list agents allocated products items
        @:param q is order status
        @:param pk sale point id
        @:param order_pk order start query

        GET /api/order/sale-point/2/47?q=pending-payment
        payload Json: /payload/getnewerorders.json
    """
    serializer_class = AllocateListSerializer
    queryset = Allocate.objects.all()

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        queryset = self.get_queryset().filter(
            Q(agent__pk=pk)
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
        send_to_sale(instance)
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
        item = SoldItem.objects.create(
                        sales=sale,
                        sku=item.sku,
                        quantity=item.quantity,
                        product_name=item.product_name,
                        total_cost=item.total_cost,
                        unit_cost=item.unit_cost,
                        product_category=item.product_category
                        )
        print item
