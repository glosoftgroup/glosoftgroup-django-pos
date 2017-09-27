from rest_framework_jwt.views import obtain_jwt_token
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.views import serve
from django.views.i18n import javascript_catalog
from graphene_django.views import GraphQLView

from .accounts.urls import urlpatterns as accounts_urls
from .api.cash.urls import urlpatterns as api_cash_urls
from .api.customer.urls import urlpatterns as api_customer_urls
from .api.discount.urls import urlpatterns as api_discount_urls
from .api.invoice.urls import urlpatterns as api_invoice_urls
from .api.credit.urls import urlpatterns as api_credit_urls
from .api.payment.urls import urlpatterns as api_payment_urls
from .api.product.urls import urlpatterns as api_urls
from .api.sms.urls import urlpatterns as api_sms_urls
from .api.terminal.urls import urlpatterns as api_terminal_urls
from .cart.urls import urlpatterns as cart_urls
from .checkout.urls import urlpatterns as checkout_urls
from .core.sitemaps import sitemaps
from .core.urls import urlpatterns as core_urls
from .dashboard.urls import urlpatterns as dashboard_urls
from .data_feeds.urls import urlpatterns as feed_urls
from .order.urls import urlpatterns as order_urls
from .payment.urls import urlpatterns as payment_urls
from .product.urls import urlpatterns as product_urls
from .registration.urls import urlpatterns as registration_urls
from .search.urls import urlpatterns as search_urls
from .userprofile.urls import urlpatterns as userprofile_urls
import notifications.urls
from .api.product import views as api_views
from .api.login import ObtainJSONWebToken
from . import decorators


urlpatterns = [    
    url(r'^', include(core_urls)),
    url(r'^account/', include(registration_urls)),
    url(r'^accounts/', include(accounts_urls, namespace='accounts')),
    url(r'^api/cash/', include(api_cash_urls, namespace='cash-api')),
    url(r'^api/customer/', include(api_customer_urls, namespace='customer-api')),
    url(r'^api/discount/', include(api_discount_urls, namespace='discount-api')),
    url(r'^api/invoice/', include(api_invoice_urls, namespace='invoice-api')),
    url(r'^api/credit/', include(api_credit_urls, namespace='credit-api')),
    url(r'^api/products/', include(api_urls, namespace='product-api')),
    url(r'^api/payment/', include(api_payment_urls, namespace='payment-api')),    
    url(r'^api/sms/', include(api_sms_urls, namespace='terminal-api')),
    url(r'^api/terminal/', include(api_terminal_urls, namespace='terminal-api')),
    url(r'^cart/', include(cart_urls, namespace='cart')),
    url(r'^checkout/', include(checkout_urls, namespace='checkout')),
    url(r'^dashboard/', include(dashboard_urls, namespace='dashboard')),
    url(r'^graphql', GraphQLView.as_view(graphiql=settings.DEBUG)),
    url(r'^jsi18n/$', javascript_catalog, name='javascript-catalog'),
    url(r'^notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^order/', include(order_urls, namespace='order')),
    url(r'^payment/', include(payment_urls, namespace='payment')),
    url(r'^products/', include(product_urls, namespace='product')),
    url(r'^profile/', include(userprofile_urls, namespace='profile')),
    url(r'^search/', include(search_urls, namespace='search')),
    url(r'^feeds/', include(feed_urls, namespace='data_feeds')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'', include('payments.urls')),
    url('', include('social_django.urls', namespace='social')),
    #jwt post token code url
    # url(r'^api/auth/token/', obtain_jwt_token),
    url(r'^api/auth/token/', ObtainJSONWebToken.as_view()),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve)
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
