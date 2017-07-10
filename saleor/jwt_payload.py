from rest_framework.views import exception_handler
from .api.product.serializers import UserSerializer

import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

from .site.models import SiteSettings
from datetime import datetime


def check_work_period():
    """
        compares current time with working period time
        returns true to if current time matches working 
        period
        else false
    """
    settings= SiteSettings.objects.get(pk=1)
    closing_time = settings.closing_time
    opening_time  = settings.opening_time
    #format = '%H:%M %p'
    now = datetime.time(datetime.now())
    print 'now:'+str(now)
    print 'close:'+str(closing_time)
    print 'opening:'+str(opening_time)
    if closing_time == None and opening_time != None:
        print 'closing time not set'
        if now < opening_time:
            return False
    if opening_time == None and closing_time != None:
        print 'opening time not set'
        if now > closing_time:
            return False
    if opening_time != None and closing_time != None:
        if now < opening_time and now > closing_time:
            return False
        else:
            return True

def jwt_response_payload_handler(token, user=None, request=None):
     if not check_work_period():
        return {
               'error': "working period closed"
          }

     # Override to return a custom response such as including 
     # the serialized representation of the User.
     return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
            }

def jwt_get_username_from_payload_handler(payload):
    """
    Override this function if username is formatted differently in payload
    """
    return payload.get('name')

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
        # log errors
       	debug_logger.debug(response.data)
       	error_logger.error(response.data)
    else:
    	info_logger.error(context)
    
    return response

