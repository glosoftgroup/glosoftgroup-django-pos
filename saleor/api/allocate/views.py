from django.db.models import Q
from .pagination import PostLimitOffsetPagination
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                    )
from django.contrib.auth import get_user_model
User = get_user_model()
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
    #credit = Credit.objects.get(invoice_number=invoice_number)
    sale = Sales.objects.create(
                         user=credit.user,
                         invoice_number=credit.invoice_number,
                         total_net=credit.total_net,
                         sub_total=credit.sub_total,
                         balance=credit.balance,
                         terminal=credit.terminal,
                         amount_paid=credit.amount_paid,
                         status=credit.status,
                         total_tax=credit.total_tax,
                         mobile=credit.mobile,
                         customer_name=credit.customer_name
                         )
    for item in credit.items():
        item = SoldItem.objects.create(sales=sale,
                        sku=item.sku,
                        quantity=item.quantity,
                        product_name=item.product_name,
                        total_cost=item.total_cost,
                        unit_cost=item.unit_cost,
                        product_category=item.product_category
                        )
        print item
