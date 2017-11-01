from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        # terminal urls
        url(r'^$', permission_required('sale.view_terminal', login_url='account_login')
            (views.terminals), name='terminals'),
        url(r'^add/$', permission_required('sale.add_terminal', login_url='account_login')
            (views.terminal_add), name='terminal-add'),
        url(r'^terminal_process/$', views.terminal_process, name='terminal_process'),
        url(r'^edit/(?P<pk>[0-9]+)/$', permission_required('sale.change_terminal', login_url='account_login')
            (views.terminal_edit), name='terminal-edit'),
        url(r'^terminal/history/(?P<pk>[0-9]+)/$', views.terminal_history, name='terminal-history'),
        url(r'^terminal_update(?P<pk>[0-9]+)/$', views.terminal_update, name='terminal-update'),
        url(r'^detail/(?P<pk>[0-9]+)/$', views.terminal_detail, name='terminal-detail'),
        url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('sale.delete_terminal', login_url='account_login')
            (views.terminal_delete), name='terminal-delete'),
        url(r'^terminal/paginate/$', views.terminal_pagination, name='terminal-paginate'),
        url(r'^terminal/search/$', views.terminal_search, name='terminal-search'),
        # cashmovement urls
        url(r'^transations/$', permission_required('sale.view_drawercash', login_url='account_login')
            (views.transactions), name='transactions'),
        url(r'^transaction/paginate/$', views.transaction_pagination, name='transaction-paginate'),
        url(r'^transaction/search/$', views.transaction_search, name='transaction-search'),
        ]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)