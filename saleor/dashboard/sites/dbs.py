import sys, os
from datetime import *
from django.core.management import call_command
from django.http import HttpResponse
from StringIO import StringIO

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from saleor.site.models import SiteSettings

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
			try:
				ct = SiteSettings.objects.all().first().closing_time
			except:
				ct = time(21, 00)
			nw = datetime.now()
			export_time = datetime.combine(date.today(), ct) - timedelta(minutes=10)
			if nw.hour != export_time.hour and nw.minute != export_time.minute or \
									nw.hour == export_time.hour and nw.minute != export_time.minute:
				raise Exception()
			day = datetime.now()
			d = str(day.day) + '.' + str(day.month) + '.' + str(day.year)

		else:
			backfolder = str(v)+'/Backup/Random'
			day = datetime.now()
			d = str(day.day) + '.' + str(day.month) + '.' + str(day.year)+'@'+str(day.hour)+'.'+\
				str(day.minute)+'.'+str(day.second)

		if not os.path.exists(backfolder):
			os.makedirs(backfolder)



		sysout = sys.stdout
		if daily:
			sys.stdout = open(backfolder+"/"+d+"_db.json", "w")
		else:
			i = 0
			while os.path.exists(backfolder+"/"+d+"_db%s.json" % i,):
				i += 1
			sys.stdout = open(backfolder+"/"+d+"_db%s.json" % i, "w")
		call_command('dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes')
		sys.stdout = sysout
		return HttpResponse('Database Backup Successful')
	except Exception as e:
		return HttpResponse(e)