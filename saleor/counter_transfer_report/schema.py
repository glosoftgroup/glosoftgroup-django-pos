import graphene

from graphene_django.types import DjangoObjectType

from saleor.graphql.utils import get_paginator

from .models import CounterTransfer as Transfer
from .models import CounterTransferItems as Items
from saleor.counter.models import Counter


class TransferType(DjangoObjectType):
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
    objects = graphene.List(ItemType)


class TransferPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    total = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(TransferType)


class CounterPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    total = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(CounterType)


class Query(object):
    """ Counter """
    all_counters = graphene.Field(CounterPaginatedType, page=graphene.Int())

    def resolve_all_counters(self, info, page, **kwargs):
        page_size = 10
        page = page
        qs = Counter.objects.all()
        return get_paginator(qs, page_size, page, CounterPaginatedType)

    """ Counter Transfer """
    all_counter_transfer = graphene.Field(TransferPaginatedType, page=graphene.Int())

    def resolve_all_counter_transfer(self, info, page, **kwargs):
        page_size = 10
        page = page
        qs = Transfer.objects.all()
        return get_paginator(qs, page_size, page, TransferPaginatedType)

    """ Transferred Items"""
    all_items = graphene.Field(ItemsPaginatedType, page=graphene.Int())

    def resolve_all_items(self, info, page, **kwargs):
        page_size = 10
        page = page
        qs = Items.objects.all()
        return get_paginator(qs, page_size, page, ItemsPaginatedType)
