from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from . import api
from . import views, products, subcategory_products


urlpatterns = [
    
    url(r'^$',permission_required('product.view_product', login_url='not_found')
    (products.view), name='product-list'),
    url(r'^list-paginate/$', products.paginate, name='product-list-paginate'),
    url(r'^list/search/$', products.search, name='product-list-search'),
    url(r'^(?P<pk>[0-9]+)/update/$', permission_required('product.change_product', login_url='not_found')
        (views.product_edit), name='product-update'),
    url(r'^(?P<pk>[0-9]+)/update/(?P<name>[\w\-]+)$', permission_required('product.change_product', login_url='not_found')
        (views.product_edit), name='product-update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', permission_required('product.delete_product', login_url='not_found')
        (views.product_delete), name='product-delete'),
    url(r'^add/(?P<class_pk>[0-9]+)/$', permission_required('product.add_product', login_url='not_found')
        (views.product_create), name='product-add'),
    url(r'^add/$', permission_required('product.add_product', login_url='not_found')
    (views.product_create), name='product-add'),
    url(r'^product/data/$', permission_required('product.add_product', login_url='not_found')
    (views.product_data), name='product-data'),
    url(r'^fetch_variants/$', permission_required('product.view_product', login_url='not_found')
        (views.fetch_variants), name='fetch-variants'),
    url(r'^fetch_variants/real/$', permission_required('product.view_product', login_url='not_found')
        (views.fetch_variants32), name='fetch-variants32'),
    # tax routes
    url(r'^tax/$', permission_required('product.view_producttax', login_url='not_found')
        (views.tax_list), name='tax-list'),
    url(r'^tax/add$', permission_required('product.add_producttax', login_url='not_found')
        (views.tax_add), name='tax-add'),
    url(r'^tax/add/ajax$',
        views.tax_add_ajax, name='tax-add-ajax'),    
    url(r'^tax/delete/(?P<pk>[0-9]+)/$', permission_required('product.delete_producttax', login_url='not_found')
        (views.tax_delete), name='tax-delete'),
    url(r'^tax/edit(?P<pk>[0-9]+)/$', permission_required('product.change_producttax', login_url='not_found')
        (views.tax_edit), name='tax-update'),
    # end tax
    # purchase routes
    url(r'^purchase/$', permission_required('product.view_stock', login_url='not_found')
        (views.stocks), name='purchase-list'),
    # end purchase routes
    # search routes
    url(r'^search_ajax/$',
        views.search_product, name='search-product'),
    url(r'^search_sku/$',
        views.search_sku, name='search-sku'),
    url(r'^search_productclass/$',
        views.search_productclass, name='search-type'),
    # pagination
    url(r'^stocks/$', permission_required('product.view_stock', login_url='not_found')
        (views.stocks), name='stocks'),
    url(r'^stock_paginate/$', views.stock_paginate, name='stock_paginate'),
    url(r'^stock_pages/$', permission_required('product.view_stock', login_url='not_found')
    (views.stock_pages), name='stock_pages'),
    url( r'^stock_search/$', views.stock_search, name = 'stock_search' ),
    url(r'^stock_filter/$',
        views.stock_filter, name='stock_filter'),
     
     url(r'^product_pages/$',
        views.stock_pages, name='product_pages'),
     url(r'^product_filter/$',
        views.product_filter, name='product_filter'),
    # end search routes
    # url(r'^classes/$', permission_required('product.view_productclass', login_url='not_found')
    #     (views.product_class_list), name='product-class-list'),
    url(r'^classes/$', permission_required('product.view_productclass', login_url='not_found')
            (views.class_list_view), name='product-class-list'),
    url(r'^classes/paginate/$', permission_required('product.view_productclass', login_url='not_found')
            (views.paginate_class_list), name='paginate-class-list'),
    url(r'^classes/search/$', permission_required('product.view_productclass', login_url='not_found')
            (views.search_class_list), name='search-class-list'),
    url(r'^classes/add/$', permission_required('product.add_productclass', login_url='not_found')
        (views.product_class_create), name='product-class-add'),
    url(r'^classes/refresh/$',
        views.refresh_producttype, name='refresh_producttype'),    
    
    url(r'^classes/add/new_window/(\d+)/$', permission_required('product.add_productclass', login_url='not_found')
        (views.product_class_create), name='product-class-add-new'),
    url(r'^classes/add/form32b/$', permission_required('product.add_productclass', login_url='not_found')
        (views.product_class_form32b), name='product-class-form32b'),
    
    url(r'^classes/(?P<pk>[0-9]+)/update/$', permission_required('product.change_productclass', login_url='not_found')
        (views.product_class_edit), name='product-class-update'),
    url(r'^classes/(?P<pk>[0-9]+)/delete/$', permission_required('product.delete_productclass', login_url='not_found')
        (views.product_class_delete), name='product-class-delete'),

    url(r'^subcategory/(?P<pk>[0-9]+)/$', permission_required('product.view_productclass', login_url='not_found')
        (subcategory_products.view), name='subcategory-products'),
    url(r'^subcategory/products/paginate/$', subcategory_products.paginate, name='subcategory-products-paginate'),
    url(r'^subcategory/products/search/$', subcategory_products.search, name='subcategory-products-search'),

    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/$', permission_required('product.change_productvariant', login_url='not_found')
        (views.variant_edit), name='variant-update'),
    url(r'^have-variants/$', views.have_variants, name='have-variants'),
    url(r'^(?P<product_pk>[0-9]+)/variants/add/$', permission_required('product.add_productvariant', login_url='not_found')
        (views.variant_edit), name='variant-add'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/delete/$', permission_required('product.delete_productvariant', login_url='not_found')
        (views.variant_delete), name='variant-delete'),
    url(r'^(?P<product_pk>[0-9]+)/single/variants/(?P<variant_pk>[0-9]+)/delete/$', permission_required('product.delete_productvariant', login_url='not_found')
        (views.single_variant_delete), name='single-variant-delete'),
    
    url(r'^(?P<product_pk>[0-9]+)/variants/bulk_delete/', permission_required('product.delete_productvariant', login_url='not_found')
        (views.variants_bulk_delete), name='variant-bulk-delete'),
    url(r'^products_pdf/$', products.products_pdf, name='products_pdf'),
    url(r'^products_export_csv/$', products.products_export_csv, name='products_export_csv'),
    url(r'^(?P<product_pk>[0-9]+)/stock/(?P<stock_pk>[0-9]+)/$', permission_required('product.change_stock', login_url='not_found')
        (views.stock_edit), name='product-stock-update'),
    url(r'^stock/(?P<stock_pk>[0-9]+)/history$', permission_required('product.view_stock', login_url='not_found')
        (views.stock_history), name='stock-history'),
    url(r'^(?P<product_pk>[0-9]+)/stock/add/$', permission_required('product.add_stock', login_url='not_found')
        (views.stock_edit), name='product-stock-add'),
    url(r'^(?P<product_pk>[0-9]+)/product-stock/add/form/$', permission_required('product.add_stock', login_url='not_found')
        (views.stock_form), name='product-stock-add-form'),
    url(r'^(?P<product_pk>[0-9]+)/stock/add/$', permission_required('product.add_stock', login_url='not_found')
        (views.stock_edit), name='product-stock-add'),
    url(r'^(?P<product_pk>[0-9]+)/stock/add/refresh$', permission_required('product.add_stock', login_url='not_found')
        (views.stock_fresh), name='refresh-stock-table'),    
    url(r'^(?P<product_pk>[0-9]+)/stock/(?P<stock_pk>[0-9]+)/delete/$', permission_required('product.delete_stock', login_url='not_found')
        (views.stock_delete), name='product-stock-delete'),
    url(r'^(?P<product_pk>[0-9]+)/stock/bulk_delete/', permission_required('product.delete_stock', login_url='not_found')
        (views.stock_bulk_delete), name='stock-bulk-delete'),
    url(r'^add_stock_ajax/$',
        views.add_stock_ajax,name='add_stock_ajax'),
    url(r'^(?P<product_pk>[0-9]+)/delete/single/stock/(?P<stock_pk>[0-9]+)/delete/$', permission_required('product.delete_productvariant', login_url='not_found')
        (views.single_stock_delete), name='single-stock-delete'),
    url(r'^re_order/$',
        views.re_order,name='re_order'),
    url(r'^re_order/pagination/$',
        views.reorder_pagination,name='reorder_pagination'),
    url(r'^re_order/search/$',
        views.reorder_search,name='reorder_search'),
    url(r'^re_order/form/(?P<pk>[0-9]+)$',
        views.re_order_form,name='re_order_form'),
    url(r'^re_order/form/item/(?P<pk>[0-9]+)$',
        views.add_reorder_stock,name='reorder_stock'),
    url(r'^re_order/request/$',
        views.request_order,name='request_order'),  
           

    url(r'^(?P<product_pk>[0-9]+)/images/(?P<img_pk>[0-9]+)/$', permission_required('product.change_productimage', login_url='not_found')
        (views.product_image_edit), name='product-image-update'),
    url(r'^(?P<product_pk>[0-9]+)/images/add/$', permission_required('product.add_productimage', login_url='not_found')
        (views.product_image_edit), name='product-image-add'),
    url(r'^(?P<product_pk>[0-9]+)/images/(?P<img_pk>[0-9]+)/delete/$', permission_required('product.delete_productimage', login_url='not_found')
        (views.product_image_delete), name='product-image-delete'),
    url('^(?P<product_pk>[0-9]+)/images/reorder/$', permission_required('product.change_productimage', login_url='not_found')
        (api.reorder_product_images), name='product-images-reorder'),
    url('^(?P<product_pk>[0-9]+)/images/upload/$', permission_required('product.add_productimage', login_url='not_found')
        (api.upload_image), name='product-images-upload'),

    # url(r'attributes/$', permission_required('product.view_productattribute', login_url='not_found')
    #     (views.attribute_list), name='product-attributes'),
    url(r'attributes/$', permission_required('product.view_productattribute', login_url='not_found')
        (views.view_attr), name='product-attributes'),
    url(r'attributes/paginate/$', permission_required('product.view_productattribute', login_url='not_found')
        (views.paginate_attr), name='attr_paginate'),
    url(r'new-attribute/$', views.new_attribute,name='new-attribute'),
    url(r'attributes/search$',
        views.search_attribute, name='search-attribute'),
    url(r'attributes/add/new/$',
        views.add_new_attribute, name='add-new-attribute'),
    url(r'attributes/(?P<pk>[0-9]+)/add/ney/$',
        views.add_new_attribute, name='edit-new-attribute'),
    
    url(r'attributes/(?P<pk>[0-9]+)/$', permission_required('product.change_productattribute', login_url='not_found')
        (views.attribute_edit), name='product-attribute-update'),
    url(r'attributes/add/$', permission_required('product.add_productattribute', login_url='not_found')
        (views.attribute_edit), name='product-attribute-add'),
    url(r'attributes/add/modal/$', permission_required('product.add_productattribute', login_url='not_found')
    (views.attribute_add_modal), name='product-attribute-add-modal'),
    url(r'attributes/(?P<pk>[0-9]+)/delete/$', permission_required('product.delete_productattribute', login_url='not_found')
        (views.attribute_delete), name='product-attribute-delete'),
    url(r'attr_list/$',views.attr_list,name="attr_list"),
    url(r'attr_list/form32b/$',views.attr_list_f32b,name="attr_list_f32b"),
    url(r'attr_list/form32d/$',views.attr_list_f32d,name="attr_list_f32d"),
    url(r'add-attributes/ajax/$', views.add_attributes,name="add-attributes"),

    url(r'attributes/ajax_add/$',
        views.attribute_add, name='product-attr-add'),
    url(r'attributes/ajax_add/(\d+)/$',
        views.attribute_add, name='product-attr-add-value'),
    

    url(r'stocklocations/$', permission_required('product.view_stocklocation', login_url='not_found')
        (views.stock_location_list), name='product-stock-location-list'),
    url(r'stocklocations/pagiante/$', views.stock_location_pagination, name='product-stock-location-paginate'),
    url(r'stocklocations/search/$', views.stock_location_search, name='product-stock-location-search'),
    url(r'stocklocations/add/$', permission_required('product.add_stocklocation', login_url='not_found')
        (views.stock_location_edit), name='product-stock-location-add'),
    url(r'stocklocations/(?P<location_pk>[0-9]+)/$', permission_required('product.change_stocklocation', login_url='not_found')
    (views.stock_location_edit), name='product-stock-location-edit'),
    url(r'stocklocations/(?P<location_pk>[0-9]+)/delete/$', permission_required('product.delete_stocklocation', login_url='not_found')
        (views.stock_location_delete), name='product-stock-location-delete'),
    url(r'update/stock/data/$', permission_required('product.view_stock', login_url='not_found')
        (views.purchase_data), name='update-stock-purchase-data'),
]
