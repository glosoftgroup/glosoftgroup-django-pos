import graphene
from graphene.types.generic import GenericScalar
from graphene_django.types import DjangoObjectType

from saleor.graphql.utils import get_paginator

from .models import CounterTransfer as Transfer
from .models import CounterTransferItems as Items
from saleor.counter.models import Counter


class TransferGraphType(DjangoObjectType):
    date = graphene.String()
    total_item = graphene.Int()
    series = GenericScalar()

    class Meta:
        model = Transfer


class TransferType(DjangoObjectType):
    total_item = graphene.Int()

    class Meta:
        model = Transfer


class ItemType(DjangoObjectType):
    class Meta:
        model = Items


class CounterType(DjangoObjectType):
    class Meta:
        model = Counter


# PaginatedType for that object type:
class ItemsPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    total = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    results = graphene.List(ItemType)


class TransferPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    total = graphene.Int()
    has_next = graphene.String()
    has_prev = graphene.Boolean()
    results = graphene.List(TransferType)
    # items = graphene.List(ItemType)


class CounterPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    total = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    results = graphene.List(CounterType)


class User(graphene.ObjectType):
    """ Type definition for User """
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()


class Query(object):
    users = graphene.List(User)

    def resolve_users(self, args):
        resp = {'id': 39330, 'username': 'RCraig', "email": 'WRussell@dolor.gov'}
        return resp

    """ Counter """
    all_counters = graphene.Field(CounterPaginatedType, page=graphene.Int())

    def resolve_all_counters(self, info, page, **kwargs):
        page_size = 10
        page = page
        qs = Counter.objects.all()
        return get_paginator(qs, page_size, page, CounterPaginatedType)

    """ Counter Transfer """
    transfer_graph = graphene.Field(
        TransferGraphType,
        page=graphene.Int(),
        start_date=graphene.String(),
        end_date=graphene.String()
    )

    def resolve_transfer_graph(self, info, start_date=None, end_date=None, **kwargs):
        return Transfer.objects.all_items_filter(start_date=start_date, end_date=end_date)
        # return data['series']

    all_counter_transfer = graphene.Field(
        TransferPaginatedType,
        page=graphene.Int(),
        start_date=graphene.String(),
        end_date=graphene.String()
    )

    def resolve_all_counter_transfer(self, info, page, start_date, end_date, **kwargs):
        page_size = 10
        page = page
        qs = Transfer.objects.all_items_filter(start_date=start_date, end_date=end_date)
        # qs = Transfer.objects.all()
        return get_paginator(qs, page_size, page, TransferPaginatedType)

    """ Transferred Items"""
    all_items = graphene.Field(
        ItemsPaginatedType,
        page=graphene.Int(),
        start_date=graphene.String(),
        end_date=graphene.String()
    )

    def resolve_all_items(self, info, page, start_date, end_date, **kwargs):
        page_size = 10
        page = page
        qs = Items.objects.all()  # all_items_filter(start_date=start_date, end_date=end_date)
        return get_paginator(qs, page_size, page, ItemsPaginatedType)
