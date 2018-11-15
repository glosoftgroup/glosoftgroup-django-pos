from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .api.views import *
from .models import CounterTransfer as Table


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="countertransfer/list.html"), name="index"),
    url(r'^api/create/$', CreateAPIView.as_view(), name='api-create'),
    url(r'^api/delete/(?P<pk>[0-9]+)/$', DestroyView.as_view(), name='api-delete'),
    url(r'^api/delete/item/(?P<pk>[0-9]+)/$', DestroyItemView.as_view(), name='api-delete-item'),
    url(r'^api/list/$', ListAPIView.as_view(), name='api-list'),
    url(r'^api/list/items/(?P<pk>[0-9]+)/$', ListItemsAPIView.as_view(), name='api-list-items'),
    url(r'^api/list/stock/$', ListStockAPIView.as_view(), name='api-list-all-stock'),
    url(r'^api/list/stock/(?P<pk>[0-9]+)/$', ListStockAPIView.as_view(), name='api-list-stock'),
    url(r'^api/list/category/(?P<pk>[0-9]+)/$', ListCategoryAPIView.as_view(), name='api-list-category'),
    url(r'^api/update/(?P<pk>[0-9]+)/$', UpdateAPIView.as_view(), name='api-update'),
    url(r'^api/update/item/(?P<pk>[0-9]+)/$', UpdateItemAPIView.as_view(), name='api-update-item'),
    url(r'^api/close/item/(?P<pk>[0-9]+)/$', CloseItemAPIView.as_view(), name='api-update-item'),
    url(r'^add/$', TemplateView.as_view(template_name="countertransfer/form.html"), name='add'),
    url(r'^close/$', TemplateView.as_view(template_name="countertransfer/close.html"), name='close'),
    url(r'^update/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name="countertransfer/items.html", model=Table, fields=['id', 'name']),
        name='update'),
    url(r'^update/view/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name="countertransfer/item_view.html", model=Table, fields=['id', 'name']),
        name='update-view'),
    url(r'^close/item/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name="countertransfer/item_closing.html", model=Table, fields=['id', 'name']),
        name='close-item'),
    url(r'^close/item/view/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name="countertransfer/item_closing_view.html", model=Table, fields=['id', 'name']),
        name='close-item-view'),
]

