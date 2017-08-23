from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext, Context
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
import os
import base64

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User, UserTrail
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, image64
import csv
import random
from django.utils.encoding import smart_str
import logging
from datetime import date


@staff_member_required
def pdf( request ):

	if request.is_ajax():
		q = request.GET.get( 'q' )
		gid = request.GET.get('gid')

		group = None
		if q is not None:
			users = User.objects.filter(
			Q( name__icontains = q ) | Q( email__icontains = q ) |
			Q( mobile__icontains = q ) | Q(groups__id__icontains=q)).order_by('-id')

			if gid:
				users = users.filter(groups__id=gid)
				group = Group.objects.get(id=gid)

		elif gid:
			users = User.objects.all().filter(groups__id=gid)
			group = Group.objects.get(pk=gid)
			print (group.name)
		else:
			users = User.objects.all()
		img = image64()
		data = {
			'today': date.today(),
			'users': users,
			'puller': request.user,
			'image': img,
			'group':group
		}
		pdf = render_to_pdf('dashboard/users/pdf/users.html', data)
		return HttpResponse(pdf, content_type='application/pdf')
