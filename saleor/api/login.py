from rest_framework_jwt.views import obtain_jwt_token
import jwt
from calendar import timegm
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.compat import get_username_field, PasswordField
from rest_framework_jwt.views import JSONWebTokenAPIView

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

class CustomJWTSerializer(JSONWebTokenSerializer):
    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            username = username.lower()
            if '@' in username:
                kwargs = {'email': username}
            else:
                kwargs = {'name': username}
            try:
                us = get_user_model().objects.get(**kwargs)
            except ObjectDoesNotExist:
                msg = _('no such user with such credentials.')
                raise serializers.ValidationError(msg)

            user = authenticate(username=us.email, password=attrs.get('password'))

            if user:				
				if not user.is_active:
					msg = _('User account is disabled.')
					raise serializers.ValidationError(msg)

				payload = jwt_payload_handler(user)

				return {
					'token': jwt_encode_handler(payload),
					'user': user,
					'permissions':user.get_all_permissions(),
				}
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)

class ObtainJSONWebToken(JSONWebTokenAPIView):
	"""
	API View that receives a POST with a user's username and password.

	Returns a JSON Web Token that can be used for authenticated requests.
	"""
	# serializer_class = JSONWebTokenSerializer
	serializer_class = CustomJWTSerializer