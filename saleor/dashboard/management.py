from django.db.models.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from ..sale.models import PaymentOption, Terminal
from ..product.models import StockLocation

def add_stock_location(sender,**kwargs):
    try:
        store = StockLocation.objects.filter(name='default')
        if not store.exists():
            StockLocation.objects.create(name="default")
    except Exception as e:
        print e

def add_terminal(sender,**kwargs):
    try:
        terminal = Terminal.objects.all()
        if not terminal.exists():
            Terminal.objects.create(terminal_name="Till-001",terminal_number=1)
    except Exception as e:
        print e

def add_payment_options(sender, **kwargs):
    try:
        cash = PaymentOption.objects.filter(name='Cash')
        if not cash.exists():
            PaymentOption.objects.create(name="Cash")
        visa = PaymentOption.objects.filter(name='Visa')
        if not visa.exists():
            PaymentOption.objects.create(name="Visa")
        mpesa = PaymentOption.objects.filter(name='Mpesa')
        if not mpesa.exists():
            PaymentOption.objects.create(name="Mpesa")
        points = PaymentOption.objects.filter(name='Loyalty Points')
        if not points.exists():
            PaymentOption.objects.create(name="Loyalty Points")
    except:
        print('Error creating payment options')

def add_view_permissions(sender, **kwargs):
    """
    This syncdb hooks takes care of adding a view permission too all our 
    content types.
    """
    # for each of our content types
    for content_type in ContentType.objects.all():
        # build our permission slug
        codename = "view_%s" % content_type.model

        # if it doesn't exist..
        if not Permission.objects.filter(content_type=content_type, codename=codename):
            # add it
            Permission.objects.create(content_type=content_type,
                                      codename=codename,
                                      name="Can view %s" % content_type.name)
            print "Added view permission for %s" % content_type.name
    
    """ Make a sale permission"""
    if not ContentType.objects.filter(model='unused') \
            and not Permission.objects.filter(codename='make_sale') \
            and not Permission.objects.filter(codename='make_invoice'):
        url_content_type = ContentType.objects.create(app_label='sales', model='unused')
        Permission.objects.create(name='can make sales', content_type=url_content_type,codename='make_sale')
        Permission.objects.create(name='can generate invoice', content_type=url_content_type, codename='make_invoice')

    if not ContentType.objects.filter(model='reports') \
            and not Permission.objects.filter(codename='view_sale_reports') \
            and not Permission.objects.filter(codename='view_products_reports') \
            and not Permission.objects.filter(codename='view_purchase_reports'):
        url_content_type = ContentType.objects.create(app_label='reports', model='reports')
        Permission.objects.create(name='view sales reports', content_type=url_content_type,codename='view_sale_reports')
        Permission.objects.create(name='view products reports', content_type=url_content_type, codename='view_products_reports')
        Permission.objects.create(name='view purchase reports', content_type=url_content_type, codename='view_purchase_reports')
        Permission.objects.create(name='view balancesheet', content_type=url_content_type, codename='view_balancesheet')

    view_unused = Permission.objects.filter(codename='view_unused')
    view_unused.delete()

    view_reports = Permission.objects.filter(codename='view_reports')
    view_reports.delete()

    add_usertrail = Permission.objects.filter(codename='add_usertrail')
    delete_usertrail = Permission.objects.filter(codename='delete_usertrail')
    change_usertrail = Permission.objects.filter(codename='change_usertrail')
    add_usertrail.delete()
    delete_usertrail.delete()
    change_usertrail.delete()



# check for all our view permissions after a syncdb
post_migrate.connect(add_view_permissions)
post_migrate.connect(add_payment_options)
post_migrate.connect(add_terminal)
post_migrate.connect(add_stock_location)