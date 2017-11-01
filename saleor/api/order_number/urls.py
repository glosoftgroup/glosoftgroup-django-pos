from django.conf.urls import url

from .views import (
    new_order,
    )


urlpatterns = [
    url(r'^$', new_order, name='api-order_number'),
]

