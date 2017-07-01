# from io import BytesIO
# import StringIO
# from django.http import HttpResponse
# from django.template.loader import get_template
# import os

# from xhtml2pdf import pisa

# def render_to_pdf(template_src, context_dict={}):

# 	template = get_template(template_src)
# 	html  = template.render(context_dict)
# 	# result = BytesIO()
# 	# pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)# result = StringIO.StringIO()
# 	if not pdf.err:
# 		return HttpResponse(result.getvalue(), content_type='application/pdf')
# 	return None

# def fetch_resources(uri, rel):
# 	path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))

# 	return path

# def link_callback(uri, rel):
#     sUrl = settings.STATIC_URL      # Typically /static/
#     sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
#     mUrl = settings.MEDIA_URL       # Typically /static/media/
#     mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

#     if uri.startswith(mUrl):
#         path = os.path.join(mRoot, uri.replace(mUrl, ""))

#     elif uri.startswith(sUrl):
#         path = os.path.join(sRoot, uri.replace(sUrl, ""))
#     else:
#         return uri.encode("urf-8")  # handle absolute uri (ie: http://some.tld/foo.png)

#     if not os.path.isfile(path):
#             raise Exception(
#                 'media URI must start with %s or %s' % (sUrl, mUrl)
#             )
#     return path

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
import cStringIO as StringIO
import cgi
import os

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = StringIO.StringIO()
	pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources )
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))

def fetch_resources(uri, rel):
	path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))

	return path

# Utility function
def convert_html_to_pdf(source_html, output_filename):
	# open output file for writing (truncated binary)
	result_file = open(output_filename, "w+b")

	# convert HTML to PDF
	pisa_status = pisa.CreatePDF(source_html, dest=result_file)           # file handle to recieve result

	# close output file
	result_file.close()                 # close output file

	# return True on success and False on errors
	return pisa_status.err