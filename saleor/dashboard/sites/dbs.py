import sys
from django.core.management import call_command
from django.http import HttpResponse


def import_db(request):
	data = request.FILES['db'].read()
	print request.FILES['db']
	# data = request.FILES['db']
	# call_command('loaddata', 'media/dbb.json')
	try:
		call_command('loaddata', data)
		return HttpResponse('success')
	except Exception as e:
		return HttpResponse(e)


def export_db(request):
	# if not os.path.exists(thisMonthDirectory):
	# 	os.makedirs(thisMonthDirectory)
	sysout = sys.stdout
	sys.stdout = open('media/dbb.json', 'w')
	call_command('dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes')
	sys.stdout = sysout