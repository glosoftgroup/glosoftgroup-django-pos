from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponse
from ..views import staff_member_required
from ...credit.models import Credit
from datetime import date
from ...utils import render_to_pdf, default_logo


@staff_member_required
def pdf(request):

	if request.is_ajax():
		q = request.GET.get( 'q' )
		gid = request.GET.get('gid')

		

		group = None
		if q is not None:
			users = Credit.objects.filter(
			Q( customer_name__icontains = q ) | Q( customer__email__icontains = q )).order_by('-id')

			if gid:
				users = users.filter(created__icontains=gid)

		elif gid:
			users = Credit.objects.all().filter(created__icontains=gid)
		else:
			users = Credit.objects.distinct('customer').order_by('customer')
		img = default_logo()
		data = {
			'today': date.today(),
			'users': users,
			'puller': request.user,
			'image': img
		}
		pdf = render_to_pdf('dashboard/customer/credit/pdf/pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')

@staff_member_required
def details(request, pk=None):

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
		img = default_logo()
		data = {
			'today': date.today(),
			'users': users,
			'puller': request.user,
			'image': img,
			'group':group
		}
		pdf = render_to_pdf('dashboard/customer/credit/pdf/detail.html', data)
		return HttpResponse(pdf, content_type='application/pdf')
