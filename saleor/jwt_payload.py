from .api.product.serializers import UserSerializer

# Override to return a custom response such as including 
# the serialized representation of the User.
def jwt_response_payload_handler(token, user=None, request=None):
     return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
            }