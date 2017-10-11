import logging
import base64
import json
from datetime import datetime, timedelta
import hashlib
from ast import literal_eval
from django.utils.translation import get_language
from django_countries.fields import Country

from . import analytics
from ..discount.models import Sale
from ..site.models import Files
from .utils import get_client_ip, get_country_by_ip, get_currency_for_country
from django.conf import settings
from django.template.response import TemplateResponse
from django.urls import reverse
from django.http import QueryDict, HttpResponse
from saleor.dashboard.sites.views import add_sitekeys
from ..core.encryptor import Encryptor
from ..core.readmac import FetchMac
from ..core.utils import replace_last

logger = logging.getLogger(__name__)
info_logger = logging.getLogger('info_logger')

class GoogleAnalytics(object):
    def process_request(self, request):
        client_id = analytics.get_client_id(request)
        path = request.path
        language = get_language()
        headers = request.META
        # FIXME: on production you might want to run this in background
        try:
            analytics.report_view(client_id, path=path, language=language,
                                  headers=headers)
        except Exception:
            logger.exception('Unable to update analytics')


class DiscountMiddleware(object):
    def process_request(self, request):
        discounts = Sale.objects.all()
        discounts = discounts.prefetch_related('products', 'categories')
        request.discounts = discounts


class CountryMiddleware(object):

    def process_request(self, request):
        client_ip = get_client_ip(request)
        if client_ip:
            request.country = get_country_by_ip(client_ip)
        if not request.country:
            request.country = Country(settings.DEFAULT_COUNTRY)


class CurrencyMiddleware(object):

    def process_request(self, request):
        if hasattr(request, 'country') and request.country is not None:
            request.currency = get_currency_for_country(request.country)
        else:
            request.currency = settings.DEFAULT_CURRENCY


class SettingsMiddleware(object):

    def process_request(self, request):
        excluded_path = reverse('dashboard:addsitekeys')

        en = Encryptor()

        fm = FetchMac()

        number = fm.getnumber()

        if request.path.startswith(excluded_path):
            return None

        try:
            ufile = Files.objects.all()[:1][0]
        except IndexError:
            return TemplateResponse(request, 'lockdown/form.html', {'days': "unknown", 'machine': number})

        filecontent  = ufile.file
        filename = ufile.check

        #  check hashlib
        h = hashlib.sha256()
        h.update(filecontent)
        hex = h.hexdigest()

        secretkey = number

        if filename != hex:
            return TemplateResponse(request, 'lockdown/form.html', {'days': 'unknown', 'machine': number})

        if self.is_not_empty(filecontent):
            jsonvalue = en.decrptcode(filecontent, number)

            if self.is_json(jsonvalue):
                data = json.loads(jsonvalue)
                version = data["Version"]
                dateobj = datetime.strptime(version, '%Y-%m-%d')
                exp = dateobj - datetime.utcnow()
                info_logger.info('expiry date: ' + str(exp))

                if exp < timedelta(seconds=0):
                    return TemplateResponse(request, 'lockdown/form.html', {'days': exp, 'machine': number})
                else:
                    info_logger.info('No issue on expiry date')
                    return None
            else:
                return TemplateResponse(request, 'lockdown/form.html', {'days':'unknown', 'machine': number})


    def is_json(self, myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError, e:
            return False
        return True

    def is_not_empty(self, s):
        return bool(s and s.strip())


