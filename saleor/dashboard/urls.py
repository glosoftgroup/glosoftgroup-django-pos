from django.conf.urls import url, include

from . import views as core_views
from .allocate.urls import urlpatterns as allocate_urls
from .banking.urls import urlpatterns as banking_urls
from .car.urls import urlpatterns as car_urls
from .category.urls import urlpatterns as category_urls
from .credit.urls import urlpatterns as credit_urls
from .customer.urls import urlpatterns as customer_urls
from .drawercash.urls import urlpatterns as drawercash_urls
from .discount.urls import urlpatterns as discount_urls
from .hr.urls import urlpatterns as hr_urls
from .messages.urls import urlpatterns as messages_urls
from .notification.urls import urlpatterns as notification_urls
from .order.urls import urlpatterns as order_urls
from .payment.urls import urlpatterns as payment_urls
from .permgroups.urls import urlpatterns as group_urls
from .product.urls import urlpatterns as product_urls
from .purchase.urls import urlpatterns as purchase_urls
from .variants.urls import urlpatterns as variants_urls
from .reports.urls import urlpatterns as reports_urls

from .search.urls import urlpatterns as search_urls
from .sites.urls import urlpatterns as site_urls
from .shipping.urls import urlpatterns as shipping_urls
from .supplier.urls import urlpatterns as supplier_urls
from .users.urls import urlpatterns as users_urls

urlpatterns = [
    url(r'^$', core_views.index, name='index'),
    url(r'^allocate/', include(allocate_urls)),
    url(r'^banking/', include(banking_urls)),
    url(r'^car/', include(car_urls)),
    url(r'^categories/', include(category_urls)),
    url(r'^customers/', include(customer_urls)),
    url(r'^credit/', include(credit_urls)),
    url(r'^discounts/', include(discount_urls)),
    url(r'^drawercash/', include(drawercash_urls)),
    url(r'^hr/', include(hr_urls)), 
    url(r'^landing-page/', core_views.landing_page, name='landing-page'),
    url(r'^orders/', include(order_urls)),
    url(r'^payments/', include(payment_urls)),
    url(r'^products/', include(product_urls)),
    url(r'^variants/', include(variants_urls)),
    url(r'^messages/', include(messages_urls)),
    url(r'^notification/',include(notification_urls)),    
    url(r'^perms/', include(group_urls)),
    url(r'^purchase/', include(purchase_urls)),
    url(r'^reports/', include(reports_urls)),
    url(r'^search/', include(search_urls)),
    url(r'^settings/', include(site_urls)),
    url(r'^shipping/', include(shipping_urls)),
    url(r'^style-guide/', core_views.styleguide, name='styleguide'),
    url(r'^supplier/', include(supplier_urls)),
    url(r'^users/', include(users_urls)),
]