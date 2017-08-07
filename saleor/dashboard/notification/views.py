from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from ..views import staff_member_required

from ...decorators import permission_decorator, user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger  = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

from django.contrib.auth import get_user_model
from ...userprofile.models import User
from notifications.signals import notify
from notifications.models import Notification

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
        subject = request.POST.get('subject')
        email_list = json.loads(request.POST.get('emailList'))
        body = request.POST.get('body')
        for email in email_list:
        	user = User.objects.filter(email=email['email'])
        	print('--------')
        	print('sending email to ')
        	print(user)
        	print '--------'
        	notify.send(request.user, recipient=user, verb=subject,description=body)

        HttpResponse(emailList)


    ctx = {'users':User.objects.all().order_by('-id')}
    return TemplateResponse(request,
                            'dashboard/notification/write.html',
                            ctx)
