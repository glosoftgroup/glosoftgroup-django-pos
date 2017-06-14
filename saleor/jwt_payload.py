from rest_framework.views import exception_handler
from .api.product.serializers import UserSerializer
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
# Override to return a custom response such as including 
# the serialized representation of the User.
def jwt_response_payload_handler(token, user=None, request=None):
     return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
            }


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

