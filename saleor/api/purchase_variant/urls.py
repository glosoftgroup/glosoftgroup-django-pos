from django.conf.urls import url

from .views import (
    PurchaseCreateAPIView
    )


urlpatterns = [
   url(r'^/create/$', PurchaseCreateAPIView.as_view(), name='create-variant-purchase'),

]

