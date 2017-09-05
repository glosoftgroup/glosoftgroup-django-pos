import emailit.api
from django.conf import settings
from africastalking.AfricasTalkingGateway import (
        AfricasTalkingGateway, 
        AfricasTalkingGatewayException)
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
from ...product.models import Product
from ...site.models import SiteSettings


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
        temp = SmsTemplate(name=t_name,content=t_content)
        temp.save()
        return HttpResponse(temp.pk)
    return HttpResponse('Post request expected')

@staff_member_required
def list_messages(request,status=None):
    # read users messages
    mark_read = True
    title = 'Inbox'
    delete_permanently = False
    if status == 'trash':
        delete_permanently = True
        title = 'Trashed'
        messages = Notification.objects.deleted()
    elif status == 'unread':
        title = 'Unread '
        messages = Notification.objects.unread()
    elif status == 'read':
        title = 'Read'
        messages = Notification.objects.read()
    elif status == 'sent_to_sms':
        title = 'Sent'
        mark_read = False
        print request.user.mobile
        messages = Notification.objects.filter(from_number=str(request.user.mobile),sent=True)
    elif status == 'pending':
        title = 'Pending'
        mark_read = False
        messages = Notification.objects.filter(from_number=str(request.user.mobile),sent=False)
    
    elif status == 'sent':
        mark_read = False
        messages = Notification.objects.filter(actor_object_id=request.user.id)
    elif status == 'fetch':
        title = 'Fetch From SMS Gateway'
        fetch = fetch_messages()
        mark_read = False
        messages = {}
        if fetch:
            messages = messages
    else:
        messages = Notification.objects.filter(to='user',to_number=str(request.user.mobile))
    ctx = {
        'title':title,
        'delete_permanently': delete_permanently,
        'mark_read': mark_read,
        'status': status,
        'deleted': len(Notification.objects.deleted()),
        'notifications': messages,
        'total_notifications': len(messages),
        'users': User.objects.all()}
    return TemplateResponse(request,
                            'dashboard/messages/list.html',
                            ctx)


@staff_member_required
def unread_count(request):
    messages = Notification.objects.unread()
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
                            'dashboard/messages/read.html',
                            ctx)
    else:
        messages = request.user.notifications.unread()
        ctx = {
        'deleted':len(messages.deleted()),
        'notifications':messages,
        'total_notifications': len(messages),
        'users':User.objects.all()}
    return TemplateResponse(request,
                            'dashboard/messages/list.html',
                            ctx)

@staff_member_required
def resend(request, pk=None):
    if request.method == 'POST':
        if pk:
            message = get_object_or_404(Notification, pk=pk)
            #message.mark_as_read()
            sms_response = sendSms(message.to_number,message.description,message.verb,actor=request.user,message_id=message.pk)
            
            if not sms_response:                
                return HttpResponse(json.dumps({'message':message.status}), content_type='application/json')
            return HttpResponse(json.dumps({'message':'Success'}), content_type='application/json')
        else:
            return HttpResponse('message id required')
    return HttpResponse('Invalid method GET')


@staff_member_required
def write(request):
    if request.method == 'POST':
        # get form data        
        subject = request.POST.get('subject')
        if request.POST.get('toCustomers'):
            to_customers = json.loads(request.POST.get('toCustomers'))
        else:
            to_customers = None
        if request.POST.get('toSuppliers'):
            to_suppliers = json.loads(request.POST.get('toSuppliers'))
        else:
            to_suppliers = None
        if request.POST.get('userContacts'):
            user_contacts = json.loads(request.POST.get('userContacts'))
        else:
            user_contacts = None            
        body = request.POST.get('body')

        if request.POST.get('single'):
            single = request.POST.get('single')
            print('to single')
            user = Supplier.objects(mobile=single)
            if user:
                notif = Notification(to='supplier', actor=request.user, recipient=request.user, sent_to=user.id, verb=subject, description=body)
                notif.save()
            else:
                notif = Notification(to='anonymous', actor=request.user, recipient=request.user, sent_to=single, verb=subject, description=body)
                notif.save()
        
        if user_contacts and user_contacts is not 'null':            
            to = []
            for mobile in user_contacts:
                to.append(mobile.replace('(','').replace(')','').replace('-',''))
            to_csv = ",".join(to)                                               
            sms_response = sendSms(to_csv,body,subject,actor=request.user,tag='user')                    
            print sms_response
        if  to_customers:
            print('to customers')
            to = []
            for mobile in to_customers:
                to.append(mobile.replace('(','').replace(')','').replace('-',''))
            to_csv = ",".join(to)                                               
            sms_response = sendSms(to_csv,body,subject,actor=request.user,tag='customer')                    
            
        if to_suppliers:
            print('to suppliers')
            to = []
            for mobile in to_suppliers:
                to.append(mobile.replace('(','').replace(')','').replace('-',''))
            to_csv = ",".join(to)                                               
            sms_response = sendSms(to_csv,body,subject,actor=request.user,tag='supplier')                    
            print sms_response
    ctx = {'users':User.objects.all().order_by('-id'),
           'templates':SmsTemplate.objects.all().order_by('-id')}
    
    if request.GET.get('pk'):
            product = get_object_or_404(Product, pk=int(request.GET.get('pk')))
            ctx = {'product':product, 'users':User.objects.all().order_by('-id'),
           'templates':SmsTemplate.objects.all().order_by('-id')}
            return TemplateResponse(request,
                            'dashboard/messages/write_single.html',
                            ctx)
    return TemplateResponse(request,
                            'dashboard/messages/write.html',
                            ctx)

@staff_member_required
def write_single(request):
    if request.method == 'POST':
        # get form data
        single = request.POST.get('single');
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        if single:
            sms_response = sendSms(str(single),body,subject,actor=request.user,tag='supplier')                       
        
    ctx = {'users':User.objects.all().order_by('-id'),
           'templates':SmsTemplate.objects.all().order_by('-id')}
    
    if request.GET.get('pk'):
            product = get_object_or_404(Product, pk=int(request.GET.get('pk')))
            ctx = {'product':product, 'users':User.objects.all().order_by('-id'),
           'templates':SmsTemplate.objects.all().order_by('-id')}
            return TemplateResponse(request,
                            'dashboard/messages/write_single.html',
                            ctx)
    return TemplateResponse(request,
                            'dashboard/messages/write.html',
                            ctx)

@staff_member_required
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

def sendSms(to,message,subject,actor,tag='user',message_id=None):
    # Specify your login credentials
    site = SiteSettings.objects.get(pk=1)
    username = site.sms_gateway_username 
    apikey   = site.sms_gateway_apikey 
        
    gateway = AfricasTalkingGateway(username, str(apikey), "sandbox")
    report = []
    try:
        # Thats it, hit send and we'll take care of the rest.        
        results = gateway.sendMessage(to, message)        
        for recipient in results:
            # status is either "Success" or "error message"
            report.append({
                'number':recipient['number'],
                'status':recipient['status']
                })
            print 'number=%s;status=%s;messageId=%s;cost=%s' % (recipient['number'],
                                                                recipient['status'],
                                                                recipient['messageId'],
                                                                recipient['cost'])

            
            if not message_id:
                send_notification(recipient['number'],actor,tag,message,subject,recipient['status'])
            else:
                update_message(message_id,recipient['status'])
    except AfricasTalkingGatewayException, e:
        print 'Encountered an error while sending: %s' % str(e)
        return None

#from django.test.client import RequestFactory
def fetch_messages():
    site = SiteSettings.objects.get(pk=1)
    username = site.sms_gateway_username 
    apikey   = site.sms_gateway_apikey
    # rf = RequestFactory()
    # post_request = rf.post('/submit/', {'username': username})        
    # username = post_request.POST.get('username')
    gateway = AfricasTalkingGateway(username, str(apikey), "sandbox")   
    try:
        # Our gateway will return 10 messages at a time back to you, starting with
        # what you currently believe is the lastReceivedId. Specify 0 for the first
        # time you access the gateway, and the ID of the last message we sent you
        # on subsequent results
        lastReceivedId = 0;
        
        while True:
            messages = gateway.fetchMessages(lastReceivedId)
            
            for message in messages:
                print 'from=%s;to=%s;date=%s;text=%s;linkId=%s;' % (message['from'],
                                                                    message['to'],
                                                                    message['date'],
                                                                    message['text'],
                                                                    message['linKId']
                                                                   )
                lastReceivedId = message['id']
        if len(messages) == 0:
            return False
        else:
            return message
                
    except AfricasTalkingGatewayException, e:
        print 'Encountered an error while fetching messages: %s' % str(e)
        #return False


def update_message(message_id,status):
    message = Notification.objects.get(pk=message_id)
    if status == 'Success':
        message.status
        message.sent=True
        message.save()
        return True
    return False

def send_notification(number=None,actor=None,tag='user',body=None,subject=None,status=None):
    if not number or not actor or not body or not subject:
        return False
    user = None
    if tag == 'user':
        user = User.objects.get(mobile=number.decode('utf-8'))
    if tag == 'customer':
        print number
        user = Customer.objects.get(mobile=number.decode('utf-8'))
    if tag == 'supplier':
        user = Supplier.objects.get(mobile=number.decode('utf-8'))
    if status == 'Success':
        notif = Notification.objects.create(
                            to=tag, 
                            actor=actor, 
                            recipient=actor, 
                            sent_to=user.id,  
                            verb=subject,
                            from_number=actor.mobile,
                            to_number=user.mobile,
                            sent=True, 
                            description=body,
                            status=status)
        print notif.status                    
    else:
        notif = Notification.objects.create(
                            to=tag, 
                            actor=actor,
                            recipient=actor,
                            sent_to=user.id, 
                            from_number=actor.mobile,
                            to_number=user.mobile,
                            verb=subject, 
                            description=body,
                            status=status)
        print notif.status
    print 'message saved on db'
    #print status
        