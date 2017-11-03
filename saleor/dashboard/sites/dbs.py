import sys, os
import datetime
from django.core.management import call_command
from django.http import HttpResponse
import json
from StringIO import StringIO

from django.conf import settings
from django.core.files.storage import FileSystemStorage

def import_db(request):
	db = request.FILES['db']
	fs = FileSystemStorage()
	filename = fs.save(db.name, db)
	uploaded_file_url = fs.url(filename)

	out = StringIO()
	try:
		call_command('flush', interactive=False, load_initial_data=False)
		call_command('loaddata', 'media/'+str(filename), stdout=out)
		d = out.getvalue()
		print d
		if 'Installed' in d:
			print uploaded_file_url
			file_path = os.path.join(settings.MEDIA_ROOT, str(filename))
			os.unlink(file_path)
			return HttpResponse('success')
		else:
			return HttpResponse('error')
	except Exception as e:
		print e
		return HttpResponse('error')


def export_db(request):
	daily = request.GET.get('daily')
	try:
		v = os.path.expanduser('~/Documents')
		if daily:
			backfolder = str(v)+'/Backup/'
		else:
			backfolder = str(v)+'/Backup/Random'
		if not os.path.exists(backfolder):
			os.makedirs(backfolder)

		day = datetime.datetime.now().strftime("%c")
		d = day.replace(' ','@').replace(':','.').replace('/','_')

		sysout = sys.stdout
		i = 0
		while os.path.exists(backfolder+"/"+d+"_db%s.json" % i,):
			i += 1
		sys.stdout = open(backfolder+"/"+d+"_db%s.json" % i, "w")
		call_command('dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes')
		sys.stdout = sysout
		return HttpResponse('Database Backup Successful')
	except Exception as e:
		return HttpResponse(e)