import emailit.api
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from ..views import staff_member_required
from ...decorators import permission_decorator, user_trail
import logging
from django.http import JsonResponse
import json


debug_logger = logging.getLogger('debug_logger')
info_logger  = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

from django.contrib.auth import get_user_model
from ...userprofile.models import User
from ...supplier.models import Supplier
from ...customer.models import Customer
from ...smessages.signals import sms as notify
from ...smessages.models import SMessage as Notification

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
        to_customers = request.POST.get('toCustomer',0)
        to_suppliers = request.POST.get('toSupplier',0)
        email_list = json.loads(request.POST.get('emailList'))
        body = request.POST.get('body')
        # for email in email_list:
        # 	user = User.objects.get(email=email['email'])
        # 	notify.send(request.user, recipient=user, verb=subject,description=body)

        # send notification/emails
        for email in email_list:
            user = User.objects.get(email=email['email'])
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


    ctx = {'users':User.objects.all().order_by('-id')}
    return TemplateResponse(request,
                            'dashboard/messages/write.html',
                            ctx)


def contacts(request):
    users = User.objects.all().exclude(mobile=None)
    contact = {}
    for user in users:
        # {"text": "Afghanistan", "value": "AF"},
        contact['text']= user.name
        contact['value'] = user.mobile
    return JsonResponse(contact)