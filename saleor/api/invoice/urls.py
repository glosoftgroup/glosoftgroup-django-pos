from django.conf.urls import url

from .views import (    
    InvoiceCreateAPIView,
    InvoiceListAPIView
    )


urlpatterns = [
    url(r'^$', InvoiceListAPIView.as_view(), name='list-invoices'),
    url(r'^create-invoice/$', InvoiceCreateAPIView.as_view(), name='create-invoice'),
    

]

