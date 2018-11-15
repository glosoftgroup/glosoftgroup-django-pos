from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphene
from saleor.graphql.utils import get_paginator
from .models import CounterTransfer as Transfer
from .models import CounterTransferItems as Items
from saleor.counter.models import Counter


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class TransferNode(DjangoObjectType):
    class Meta:
        model = Transfer
        filter_fields = ['name', 'date']
        interfaces = (relay.Node, )


class ItemNode(DjangoObjectType):
    class Meta:
        model = Items
        # Allow for some more advanced filtering here
        filter_fields = {
            'id': ['exact', 'icontains', 'istartswith'],
            'sku': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class CounterNode(DjangoObjectType):
    class Meta:
        model = Counter
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


# Now we create a corresponding PaginatedType for that object type:
class ItemPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(ItemNode)


class Query(object):
    counter_transfer = relay.Node.Field(TransferNode)
    all_counter_transfer = DjangoFilterConnectionField(TransferNode)

    transfer_items = relay.Node.Field(ItemNode)
    all_items = DjangoFilterConnectionField(ItemNode)

    # def resolve_all_items(self, info, **kwargs):
    #     qs = Items.objects.all()
    #     # page = 1
    #     # page_size = 10
    #     # return get_paginator(qs, page_size, page, ItemPaginatedType)

    counter = relay.Node.Field(CounterNode)
    all_counters = DjangoFilterConnectionField(CounterNode)
