from rest_framework import pagination
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import generics

from ...decorators import user_trail
from ...credit.models import Credit
from ...sale.models import (
    Sales, SoldItem,
    Terminal,
    TerminalHistoryEntry,
    DrawerCash,
    PaymentOption
)
from .pagination import PostLimitOffsetPagination
from .serializers import (
    CreditListSerializer,
    CreateCreditSerializer,
    CreditUpdateSerializer,
    DistinctTableListSerializer,
    TableListSerializer
)

from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()


class CreditDetailAPIView(generics.RetrieveAPIView):
    queryset = Credit.objects.all()
    serializer_class = CreditListSerializer


class CreditCreateAPIView(generics.CreateAPIView):
    queryset = Credit.objects.all()
    serializer_class = CreateCreditSerializer

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        if instance.status == 'fully-paid':
            send_to_sale(instance)


class CreditListAPIView(generics.ListAPIView):
    serializer_class = CreditListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Credit.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query)
            ).distinct()
        return queryset_list


class CreditorsListAPIView(generics.ListAPIView):
    serializer_class = CreditListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Credit.objects.filter(status='payment-pending')
        query = self.request.GET.get('q')
        try:
            if query:
                queryset_list = queryset_list.filter(status='payment-pending').filter(
                    Q(invoice_number__icontains=query) |
                    Q(customer__name__icontains=query) |
                    Q(created__icontains=query) |
                    Q(customer__mobile__icontains=query)).distinct()
        except:
            print('nothing found')
        return queryset_list


class CreditUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Credit.objects.all()
    serializer_class = CreditUpdateSerializer

    def perform_update(self, serializer):
        instance = serializer.save(user=self.request.user)
        if instance.status == 'fully-paid':
            send_to_sale(instance)
        user_trail(self.request.user.name,
                   'made a credit sale:#' + str(serializer.data['invoice_number']) + ' credit sale worth: ' + str(
                       serializer.data['total_net']), 'add')
        logger.info(
            'User: ' + str(self.request.user) + ' made a credit sale:' + str(serializer.data['invoice_number']))
        terminal = Terminal.objects.get(pk=int(serializer.data['terminal']))
        trail = 'User: ' + str(self.request.user) + \
                ' updated a credited sale :' + str(serializer.data['invoice_number']) + \
                ' Net#: ' + str(serializer.data['total_net']) + \
                ' Amount paid#:' + str(serializer.data['amount_paid'])

        TerminalHistoryEntry.objects.create(
            terminal=terminal,
            comment=trail,
            crud='deposit',
            user=self.request.user
        )
        drawer = DrawerCash.objects.create(manager=self.request.user,
                                           user=self.request.user,
                                           terminal=terminal,
                                           amount=serializer.data['amount_paid'],
                                           trans_type='credit paid')


def send_to_sale(credit):
    sale = Sales.objects.create(
        user=credit.user,
        invoice_number=credit.invoice_number,
        total_net=credit.total_net,
        sub_total=credit.sub_total,
        balance=credit.balance,
        terminal=credit.terminal,
        amount_paid=credit.amount_paid,
        customer=credit.customer,
        status=credit.status,
        total_tax=credit.total_tax,
        mobile=credit.mobile,
        customer_name=credit.customer_name,
        payment_data=credit.payment_data
    )
    payment_data = sale.payment_data
    if payment_data:
        for option in payment_data:
            pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
            sale.payment_options.add(pay_opt)
        sale.save()

    for item in credit.items():
        credit_item = SoldItem.objects.create(sales=sale,
                                       sku=item.sku,
                                       quantity=item.quantity,
                                       product_name=item.product_name,
                                       total_cost=item.total_cost,
                                       unit_cost=item.unit_cost,
                                       product_category=item.product_category,
                                       attributes=item.attributes,
                                       unit_purchase=item.unit_purchase,
                                       total_purchase=item.total_purchase
                                       )
        if item.stock_id and item.transfer_id and item.counter:
            credit_item.stock_id = item.stock_id
            credit_item.transfer_id = item.transfer_id
            credit_item.counter = item.counter
            credit_item.save()


# on
class CustomerCreditListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                pk = Credit.objects.get(pk=self.kwargs['pk']).customer.pk
                queryset_list = Credit.objects.filter(customer__pk=pk).select_related()
            else:
                queryset_list = Credit.objects.all().order_by('-id').select_related()
        except Exception as e:
            queryset_list = Credit.objects.all().select_related()
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
                Q(customer__name__icontains=query)
            ).distinct()
        return queryset_list.order_by('-id')


class CustomerDistinctListAPIView(generics.ListAPIView):
    serializer_class = DistinctTableListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = Credit.objects.filter(customer__pk=self.kwargs['pk']).order_by('car').distinct(
                    'car').select_related()
            else:
                queryset_list = Credit.objects.all.select_related()
        except Exception as e:
            queryset_list = Credit.objects.distinct('customer')
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
                Q(customer__name__icontains=query)
            ).distinct('customer')
        return queryset_list.order_by('customer')
