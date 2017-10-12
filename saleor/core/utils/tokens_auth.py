import requests
from django.conf import settings
from rest_framework import status as http_status
from structlog import get_logger
import logging
import json


class MpesaApiAuthorization(object):
    def __init__(self):
        self.logger = logging.getLogger('info_logger')
        self.token_url = settings.SAFARICOM_KE_AUTH_TOKEN_API_URL
        self.consumer_key = settings.SAFARICOM_KE_CONSUMER_KEY
        self.consumer_secret = settings.SAFARICOM_KE_CONSUMER_SECRET

    def get_authorization_token(self):
        """
        Generates token
        :return: False or dict of tokens
        """

        params = {
            "grant_type": "client_credentials"
        }
        headers = {
            'Accept': 'application/json;charset=UTF-8'
        }

        try:
            # Configure connect and read timeouts respectively
            self.logger.info(
                    'token_api_request',
                    url=self.token_url,
                    params=params,
            )
            response = requests.get(
                    self.token_url,
                    headers=headers,
                    auth=(self.consumer_key, self.consumer_secret),
                    params=params,
                    timeout=5
            )

            # Convert response to actual json - Default is unicode
            self.logger.info(
                    'token_api_response',
                    status_code=response.status_code,
                    content=response.text
            )
            result = response.json()
            self.logger.info('token_response', result=result, status_code=response.status_code)

        except Exception as e:
            self.logger.exception(
                    'mpesa_auth_token_request_failure',
                    exception=str(e)
            )
            result = {}
        return result

    def get_mpesa_headers(self, headers={}):
        """
        Receives request headers in a dict form.
        Appends the token to the header

        :param headers:
        :return: Dict containing headers
        """
        # Ensure content-type is json as per doc
        headers['Content-Type'] = 'application/json'

        self.logger.info('current_headers', headers=headers)
        try:
            token = self.get_authorization_token()
            access_token = token.get("access_token", False)

            if access_token:
                # When access token is available.
                # Expected header "Bearer xxxxxxx"

                headers['Authorization'] = "Bearer {access_token}".format(
                        access_token=access_token
                )
                self.logger.debug('token_appending_success', headers=headers)
            else:
                # When access token is not available
                self.logger.info('token_appending_failure', headers=headers)

        except Exception as e:
            self.logger.exception('token_appending_error',
                                  exception=str(e))

        return headers

    def register_url(self, validation_url, confirmation_url, response_type, short_code):
        """
        Registers end points MPESA is going to use to reach our apps.
        Recommended that it is done once on app start up.
        Token is used to enforce token generation and appending
        :param validation_url:
        :param confirmation_url:
        :param response_type:
        :param short_code:
        :return: Boolean
        """
        self.registration_url = settings.SAFARICOM_KE_C2B_MPESA_REGISTER_URL
        headers = self.get_mpesa_headers()

        # Create registration payload
        payload = {
            "ShortCode": short_code,
            "ResponseType": response_type,
            "ConfirmationURL": confirmation_url,
            "ValidationURL": validation_url
        }

        try:
            self.logger.info('register_url_request', url=self.registration_url, payload=payload)
            # Configure connect and read timeouts respectively
            response = requests.post(self.registration_url, json=payload,
                                     headers=headers, timeout=5)

            self.logger.info(
                'register_url_response',
                response=response.text,
                status_code=response.status_code
            )
            result = response.json()

            if response.status_code == http_status.HTTP_200_OK:
                # Convert response to actual json - Default is unicode

                if result.get('ResponseDescription') == 'success':
                    self.logger.info(
                        'register_url_success',
                        result=result,
                        status_code=response.status_code
                    )
                    return True
                else:
                    self.logger.exception(
                        'register_url_failure',
                        result=result,
                        status_code=response.status_code
                    )
                    return False
            else:
                self.logger.exception(
                    'register_url_failure',
                    result=result,
                    status_code=response.status_code
                )
                return False

        except Exception as error:
            self.logger.exception(
                'register_url_error',
                exception=str(error),
            )
            return False

    def get_password(self, timestamp):
        """
        This method return the password to be sent
        in the lipa na mpesa online request
        password = base64.encode(Shortcode:Passkey:Timestamp)
        """
        passkey = settings.SAFARICOM_KE_LIPA_NA_MPESA_ONLINE_PASSKEY
        short_code = settings.SAFARICOM_KE_LIPA_NA_MPESA_ONLINE_SHORTCODE

        password = short_code + passkey + timestamp
        password = password.encode('base64')

        return password

    def register_mpesa_c2b_urls(self):

        short_code = settings.SAFARICOM_KE_SHORTCODE_1
        response_type = "Completed"

        self.register_url(
            settings.SAFARICOM_KE_C2B_VALIDATION_URL,
            settings.SAFARICOM_KE_C2B_CONFIRMATION_URL,
            response_type,
            short_code
        )
