import emailit.api
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from ..views import staff_member_required
from ...decorators import permission_decorator, user_trail
import logging
import json
from django.db.models import Q


debug_logger = logging.getLogger('debug_logger')
info_logger  = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

from django.contrib.auth import get_user_model
from ...userprofile.models import User
from ...supplier.models import Supplier
from ...customer.models import Customer
from ...smessages.signals import sms as notify
from ...smessages.models import SMessage as Notification, SmsTemplate

@staff_member_required
def get_template(request,pk=None):
    if request.method == 'GET':
        if request.is_ajax():
            if request.GET.get('pk'):
                stemplate = get_object_or_404(SmsTemplate,pk=(int(request.GET.get('pk'))))
                ctx = {'template':stemplate}
                if request.GET.get('template'):                
                    template = request.GET.get('template')
                    return TemplateResponse(request, 'dashboard/messages/includes/'+template+'.html', ctx)
                
                return TemplateResponse(request, 'dashboard/messages/includes/single-template.html', ctx)
        sms_templates = SmsTemplate.objects.all().order_by('-id')
        ctx = {'sms_templates':sms_templates}
        return TemplateResponse(request, 'dashboard/messages/includes/templates.html', ctx)

@staff_member_required
def add_template(request):
    if request.method == 'POST':
        t_name = request.POST.get('tname')
        t_content = request.POST.get('tcontent','')
        # print template_content
        # print template_name
        temp = SmsTemplate(name=t_name,content=t_content)
        temp.save()
        return HttpResponse(temp.pk)
    return HttpResponse('Post request expected')
@staff_member_required
def list_messages(request,status=None):
    # read users messages
    mark_read = True
    delete_permanently = False
    if status == 'trash':
        delete_permanently = True
        messages = request.user.notifications.deleted()
    elif status == 'unread':
        messages = request.user.notifications.unread()
    elif status == 'read':
        messages = request.user.notifications.read()
    elif status == 'emailed':
        mark_read = False
        messages = Notification.objects.filter(actor_object_id=request.user.id,emailed=True)
    elif status == 'sent':
        mark_read = False
        messages = Notification.objects.filter(actor_object_id=request.user.id)
    else:
        messages = request.user.notifications.active()
    ctx = {
        'delete_permanently': delete_permanently,
        'mark_read': mark_read,
        'status': status,
        'deleted': len(request.user.notifications.deleted()),
        'notifications': messages,
        'total_notifications': len(messages),
        'users': User.objects.all()}
    return TemplateResponse(request,
                            'dashboard/messages/list.html',
                            ctx)


@staff_member_required
def unread_count(request):
    messages = request.user.notifications.unread()
    return HttpResponse(len(messages))


@staff_member_required
def delete_template(request,pk=None):
    if pk:
        template = get_object_or_404(SmsTemplate,pk=pk)
        template.delete()
        return HttpResponse('Template Deleted successfully')
    return HttpResponse('Select template id')


@staff_member_required
def delete_permanently(request, pk=None):
    if pk:
        message = get_object_or_404(Notification, pk=pk)
        message.delete()
        return HttpResponse(str(message.verb)+' Deleted successfully')
    else:
        return HttpResponse('Provide a correct Notification')


@staff_member_required
def delete(request, pk=None):
    if pk:
        message = get_object_or_404(Notification, pk=pk)
        message.deleted = True
        message.save()
        return HttpResponse('Added to spam box')
    else:
        return HttpResponse('Error deleting notification')
    return HttpResponse('error')


@staff_member_required
def read(request, pk=None):
    if pk:
        message = get_object_or_404(Notification, pk=pk)
        message.mark_as_read()
        ctx = {
              'notification':message,
              'actor':message.actor.email[0]}
        return TemplateResponse(request,
                            'dashboard/notification/read.html',
                            ctx)
    else:
        messages = request.user.notifications.unread()
        ctx = {
        'deleted':len(messages.deleted()),
        'notifications':messages,
        'total_notifications': len(messages),
        'users':User.objects.all()}
    return TemplateResponse(request,
                            'dashboard/notification/list.html',
                            ctx)


@staff_member_required
def write(request):
    if request.method == 'POST':
        # get form data
        subject = request.POST.get('subject')
        to_customers = request.POST.get('toCustomers',0)
        to_suppliers = request.POST.get('toSuppliers',0)
        user_contacts = json.loads(request.POST.get('userContacts'))
        body = request.POST.get('body')
        print user_contacts
        print type(to_customers)
        print to_suppliers
        if user_contacts and user_contacts is not 'null':
            for mobile in user_contacts:
                user = User.objects.get(mobile=mobile)
                #notify.send(request.user, sent_to=user, verb=subject, description=body)
                notif = Notification(to='user', actor=request.user, recipient=request.user, sent_to=user.id, verb=subject, description=body)
                notif.save()
        if not to_customers:
            for mobile in to_customers:
                user = Customer.objects.get(mobile=mobile)
                #notify.send(request.user, sent_to=user.id, verb=subject, description=body)
                notif = Notification(to='customer', actor=request.user, recipient=request.user, sent_to=user.id, verb=subject, description=body)
                notif.save()

    ctx = {'users':User.objects.all().order_by('-id'),
           'templates':SmsTemplate.objects.all().order_by('-id')}
    return TemplateResponse(request,
                            'dashboard/messages/write.html',
                            ctx)


def contacts(request):
    search = request.GET.get('search')
    group = request.GET.get('group')
    if 'users' == str(group):
        users = User.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(mobile=None)
    elif 'suppliers' == str(group):
        users = Supplier.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(mobile=None)
    elif 'customers' == str(group):
        users = Customer.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(mobile=None)
    else:
        users = User.objects.all().filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        ).exclude(mobile=None)

    contact = {}
    l = []
    for user in users:
        # {"text": "Afghanistan", "value": "AF"},
        contact={'text':user.name,'value': user.mobile}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')