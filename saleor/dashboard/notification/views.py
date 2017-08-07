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


def notification_list(request,status=None):
    # read users notifications
    if status == 'trash':
        notifications = request.user.notifications.deleted()
    elif status == 'unread':
        notifications = request.user.notifications.unread()
    elif status == 'read':
        notifications = request.user.notifications.read()
    elif status == 'sent':
        notifications = request.user.notifications.filter(actor_object_id=request.user.id)
    else:
        notifications = request.user.notifications.active()
    print notifications
    users = User.objects.all().order_by('-id')
    ctx = {
        'deleted':len(request.user.notifications.deleted()),
        'notifications':notifications,
        'total_notifications': len(notifications),
        'users':User.objects.all()}
    return TemplateResponse(request,
                            'dashboard/notification/list.html',
                            ctx)

def unread_count(request):
    notification = request.user.notifications.unread()
    return HttpResponse(len(notification))


def delete(request,pk=None):
    if pk:
        notification = get_object_or_404(Notification, pk=pk)        
        notification.deleted = True
        notification.save()
        return HttpResponse('Added to spam box')
    else:
        return HttpResponse('Error deleting notification')
    return HttpResponse('error')
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
def write(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        emailList = json.loads(request.POST.get('emailList'))
        body = request.POST.get('body')
        for email in emailList:
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
