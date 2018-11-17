from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .api.views import *
from saleor.countertransfer.models import CounterTransfer as Table

global module
module = 'counter_transfer_report'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name=module+"/list.html"), name="index"),
    url(r'^api/list/$', ListAPIView.as_view(), name='api-list'),
    url(r'^api/graph/$', SnippetList.as_view(), name='api-list-high'),
    url(r'^api/graph/pie/$', HighchartPieList.as_view(), name='api-high-pie'),
    url(r'^api/graph/counter/$', HighchartCounterList.as_view(), name='api-high-pie'),
    url(r'^api/graph/top/$', TopProducts.as_view(), name='api-top-products'),
    url(r'^api/graph/recharts/$', RechartsList.as_view(), name='api-rechart'),
    url(r'^api/graph/recharts/total/$', RechartsListTotal.as_view(), name='api-rechart-total'),
    url(r'^api/list/items/(?P<pk>[0-9]+)/$', ListItemsAPIView.as_view(), name='api-list-items'),
    url(r'^api/list/stock/$', ListStockAPIView.as_view(), name='api-list-all-stock'),
    url(r'^api/list/stock/(?P<pk>[0-9]+)/$', ListStockAPIView.as_view(), name='api-list-stock'),
    url(r'^api/list/category/(?P<pk>[0-9]+)/$', ListCategoryAPIView.as_view(), name='api-list-category'),
    url(r'^api/update/(?P<pk>[0-9]+)/$', UpdateAPIView.as_view(), name='api-update'),
    url(r'^api/update/item/(?P<pk>[0-9]+)/$', UpdateItemAPIView.as_view(), name='api-update-item'),
    url(r'^add/$', TemplateView.as_view(template_name=module+"/form.html"), name='add'),
    url(r'^report/$', TemplateView.as_view(template_name=module+"/list_report.html"), name='add'),
    url(r'^update/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name=module+"/items.html", model=Table, fields=['id', 'name']),
        name='update'),
    url(r'^update/view/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name=module+"/item_view.html", model=Table, fields=['id', 'name']),
        name='update-view'),
]

