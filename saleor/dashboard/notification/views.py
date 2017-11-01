import emailit.api
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from ..views import staff_member_required
from django.db.models import Q
from ...decorators import permission_decorator, user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger  = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

from django.contrib.auth import get_user_model
from ...userprofile.models import User
from ...supplier.models import Supplier
from ...customer.models import Customer
from ...product.models import Product, ProductVariant
from ...smessages.models import EmailTemplate
from notifications.signals import notify
from notifications.models import Notification


@staff_member_required
@staff_member_required
def add_template(request):
    if request.method == 'POST':
        t_name = request.POST.get('tname')
        t_content = request.POST.get('tcontent','')        
        temp = EmailTemplate(name=t_name,content=t_content)
        temp.save()
        return HttpResponse(temp.pk)
    return HttpResponse('Post request expected')


@staff_member_required
def get_template(request, pk=None):
    if request.method == 'GET':
        if request.is_ajax():
            if request.GET.get('pk'):
                stemplate = get_object_or_404(EmailTemplate,pk=(int(request.GET.get('pk'))))
                ctx = {'template': stemplate}
                if request.GET.get('template'):
                    template = request.GET.get('template')
                    return HttpResponse(json.dumps(stemplate.content), content_type='application/json')
                
                return TemplateResponse(request, 'dashboard/notification/includes/single-template.html', ctx)
        sms_templates = EmailTemplate.objects.all().order_by('-id')
        ctx = {'sms_templates':sms_templates}
        return TemplateResponse(request, 'dashboard/notification/includes/templates.html', ctx)


@staff_member_required
def delete_template(request,pk=None):
    if pk:
        template = get_object_or_404(EmailTemplate,pk=pk)
        template.delete()
        return HttpResponse('Template Deleted successfully')
    return HttpResponse('Select template id')


@staff_member_required
def notification_list(request,status=None):
    # read users notifications
    mark_read = True
    delete_permanently = False
    if status == 'trash':
        delete_permanently = True
        notifications = request.user.notifications.deleted()
    elif status == 'unread':
        notifications = request.user.notifications.unread()
    elif status == 'read':
        notifications = request.user.notifications.read()
    elif status == 'emailed':
        mark_read = False
        notifications = Notification.objects.filter(actor_object_id=request.user.id,emailed=True)
    elif status == 'sent':
        mark_read = False
        notifications = Notification.objects.filter(actor_object_id=request.user.id)
    else:
        notifications = request.user.notifications.active()
    ctx = {
        'delete_permanently': delete_permanently,
        'mark_read': mark_read,
        'status': status,
        'deleted': len(request.user.notifications.deleted()),
        'notifications': notifications,
        'total_notifications': len(notifications),
        'users': User.objects.all()}
    return TemplateResponse(request,
                            'dashboard/notification/list.html',
                            ctx)


@staff_member_required
def unread_count(request):
    notification = request.user.notifications.unread()
    return HttpResponse(len(notification))


@staff_member_required
def delete_permanently(request, pk=None):
    if pk:
        notification = get_object_or_404(Notification, pk=pk)
        notification.delete()
        return HttpResponse(str(notification.verb)+' Deleted successfully')
    else:
        return HttpResponse('Provide a correct Notification')


@staff_member_required
def delete(request, pk=None):
    if pk:
        notification = get_object_or_404(Notification, pk=pk)        
        notification.deleted = True
        notification.save()
        return HttpResponse('Added to spam box')
    else:
        return HttpResponse('Error deleting notification')
    return HttpResponse('error')


@staff_member_required
def read(request, pk=None):
    if pk:
        notification = get_object_or_404(Notification, pk=pk)        
        notification.mark_as_read()
        ctx = {
              'notification':notification,
              'actor':notification.actor.email[0]}
        return TemplateResponse(request,
                            'dashboard/notification/read.html',
                            ctx)        
    else:
        notifications = request.user.notifications.unread()
        ctx = {
        'deleted':len(notifications.deleted()),
        'notifications':notifications,
        'total_notifications': len(notifications),
        'users':User.objects.all()}
    return TemplateResponse(request,
                            'dashboard/notification/list.html',
                            ctx)


@staff_member_required
def write(request):
    if request.method == 'POST':
        # get form data
        subject = request.POST.get('subject')
        single = request.POST.get('single');
        to_customers = request.POST.get('toCustomer',0)
        to_suppliers = request.POST.get('toSupplier',0)
        email_list = json.loads(request.POST.get('emailList'))
        body = request.POST.get('body')       

        # send notification/emails
        if single:
            try:
                user = Supplier.objects.get(email=single)
                context = {'user': user.name, 'body': body, 'subject': subject}
                emailit.api.send_mail(user.email,
                                          context,
                                          'notification/emails/notification_email',
                                          from_email=request.user.email)
                notif = Notification(actor=request.user, recipient=request.user, verb=subject, description=body, emailed=True)
                notif.save()
            except:
                #user = Supplier.objects.get(email=single)
                context = {'user': single, 'body': body, 'subject': subject}
                emailit.api.send_mail(single,
                                          context,
                                          'notification/emails/notification_email',
                                          from_email=request.user.email)
                notif = Notification(actor=request.user, recipient=request.user, verb=subject, description=body, emailed=True)
                notif.save()
            return HttpResponse('success')
            
        for email in email_list:
            user = User.objects.get(email=email)
            if user.send_mail:
                context = {'user': user.name, 'body': body, 'subject': subject}
                emailit.api.send_mail(user.email,
                                      context,
                                      'notification/emails/notification_email',
                                      from_email=request.user.email)
                notif = Notification(actor=request.user, recipient=user, verb=subject, description=body, emailed=True)
                notif.save()
            else:
                notify.send(request.user, recipient=user, verb=subject, description=body)

        # check for bulk group mailing/notification
        if 1 == int(to_customers):
            customers = Customer.objects.all()
            for customer in customers:
                context = {'user': customer.name, 'body': body, 'subject': subject}
                emailit.api.send_mail(customer.email,
                                      context,
                                      'notification/emails/notification_email',
                                      from_email=request.user.email)
                notif = Notification(actor=request.user, recipient=customer, verb=subject, description=body, emailed=True)
                notif.save()
        if 1 == int(to_suppliers):
            suppliers = Supplier.objects.all()
            for supplier in suppliers:
                context = {'user': supplier.name, 'body': body, 'subject': subject}
                emailit.api.send_mail(supplier.email,
                                      context,
                                      'notification/emails/notification_email',
                                      from_email=request.user.email)
                notif = Notification(actor=request.user, recipient=supplier, verb=subject, description=body, emailed=True)
                notif.save()

        HttpResponse(email_list)
    ctx = {
            'users':User.objects.all().order_by('-id'),
            'templates':EmailTemplate.objects.all().order_by('-id')
          }
    if request.method == 'GET':
        if request.GET.get('pk'):
            try:
                product = ProductVariant.objects.get(pk=int(request.GET.get('pk')))
                ctx = {
                        'product':product,
                        'users':User.objects.all().order_by('-id'),
                        'templates':EmailTemplate.objects.all().order_by('-id')
                        }
                return TemplateResponse(request,
                                'dashboard/notification/write_single.html',
                                ctx)
            except Exception, e:
                return HttpResponse(e)
    return TemplateResponse(request,
                            'dashboard/notification/write.html',
                            ctx)

@staff_member_required
def emails(request):    
    search = request.GET.get('search')
    group = request.GET.get('group')
    if 'users' == str(group):
        users = User.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(email=None)
    elif 'suppliers' == str(group):
        users = Supplier.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(email=None)
    elif 'customers' == str(group):
        users = Customer.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(email=None)
    else:
        users = User.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(email=None)

    contact = {}
    l = []
    for user in users:
        # {"text": "Afghanistan", "value": "AF"},
        contact={'text':user.email,'value': user.email}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')


def custom_notification(by,body,subject,superusers = True):
    if superusers:
        users = User.objects.filter(is_superuser=True)
        for user in users:
            context = {'user': user.name, 'body': body, 'subject': subject}
            emailit.api.send_mail(user.email,
                                      context,
                                      'notification/emails/notification_email',
                                      from_email=user.email)
            notif = Notification(actor=by, recipient=user, verb=subject, description=body, emailed=True)
            notif.save()
        return True