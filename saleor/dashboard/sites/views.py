from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import FieldError
from django.db import DatabaseError
from django.views.decorators.csrf import csrf_exempt, csrf_protect, requires_csrf_token

from .forms import AuthorizationKeyFormSet, SiteSettingForm
from ..views import staff_member_required
from ...site.models import AuthorizationKey, SiteSettings, Files
from ...site.utils import get_site_settings_from_request
# from django.views.decorators.csrf import csrf_protect
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def index(request):
    settings = get_site_settings_from_request(request)
    return redirect('dashboard:site-update', site_id=settings.pk)


@staff_member_required
def update(request, site_id=None):
    site = get_object_or_404(SiteSettings, pk=site_id)
    form = SiteSettingForm(request.POST or None, instance=site)
    authorization_qs = AuthorizationKey.objects.filter(site_settings=site)
    if all([form.is_valid()]):
        site = form.save()
        
        messages.success(request, _('Updated site %s') % site)
        return redirect('dashboard:site-update', site_id=site.id)
    ctx = {'site': site, 'form': form}
    return TemplateResponse(request, 'dashboard/sites/detail.html', ctx)

@staff_member_required
def update_settings(request,site_id=None):
    if request.method == 'POST':
        site = get_object_or_404(SiteSettings, pk=site_id)
        if request.POST.get('sms_username'):
            site.sms_gateway_username = request.POST.get('sms_username')
            print site.sms_gateway_username
        if request.POST.get('sms_api_key'):
            site.sms_gateway_apikey = request.POST.get('sms_api_key')
            print site.sms_gateway_apikey
        site.save()
        return HttpResponse('success')
    return HttpResponse('Invalid method')

@csrf_protect
def add_sitekeys(request):
    if request.method == 'POST':
        keyfile = request.POST.get('lic_key').strip()
        info_logger.info("***************")
        info_logger.info(keyfile)
        info_logger.info("***************")
        check = "sometext"
        if keyfile:
            new_key = Files.objects.create(
                file=keyfile,
                check=check
            )
        else:
            error_logger.info('License Key is empty ')
            return HttpResponse('Empty Key license')

        try:
            new_key.save()
        except DatabaseError, BaseException :
            error_logger.info('Error when saving ')

        if new_key.id:
            return HttpResponse('success')
        return HttpResponse('Error: Not saved')

    return HttpResponse('Invalid request')


def test(request):
    print ('testKeys')
    return HttpResponse('success 123')
