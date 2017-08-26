from __future__ import unicode_literals

import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import MpesaPayment
from ..sale.models import PaymentOption

def payments_list(request):	
    try:
        options = PaymentOption.objects.all().order_by('-id')
        #expense_types = ExpenseType.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(options, 10)
        try:
            options = paginator.page(page)
        except PageNotAnInteger:
            options = paginator.page(1)
        except InvalidPage:
            options = paginator.page(1)
        except EmptyPage:
            options = paginator.page(paginator.num_pages)
        data = {
            "expenses": options,            
            "pn": paginator.num_pages
        }
        user_trail(request.user.name, 'accessed expenses', 'views')
        info_logger.info('User: ' + str(request.user.name) + 'accessed expenses page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/paymentoptions/expenses/list.html', data)
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing expenses')

@csrf_exempt
def index(request): 
    #try:
	content = request.read()
	root = ET.fromstring(content)
	responseVl = ''
	for child in root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
		if child.tag == '{http://cps.huawei.com/cpsinterface/c2bpayment}C2BPaymentValidationRequest':
			refNumber = child.find('BillRefNumber').text
			transID = child.find('TransID').text
			phnNumber = child.find('MSISDN').text
			responseVl= '+'+phnNumber+'+'+transID
		elif child.tag == '{http://cps.huawei.com/cpsinterface/c2bpayment}C2BPaymentConfirmationRequest':   
			for childVl in root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
				ref_number = childVl.find('BillRefNumber').text
				amount = childVl.find('TransAmount').text
				transaction_type = childVl.find('TransactionType').text
				trans_id = childVl.find('TransID').text
				trans_time = childVl.find('TransTime').text
				business_shortcode = childVl.find('BusinessShortCode').text
				bill_refNumber = childVl.find('BillRefNumber').text
				invoice_number = childVl.find('InvoiceNumber').text
				phone = childVl.find('MSISDN').text				
				fname, mname, lname = '','',''
				names = childVl.find('KYCInfo')
				detail = []
				for name in root.iter('KYCInfo'):
					detail.append(name.find('KYCName').text)					
				first_name, middle_name, last_name = detail[0],detail[1],detail[2]
				responseVl = last_name 
				mpesa = MpesaPayment.objects.create(
						ref_number=ref_number,
						amount=amount,
						transaction_type=transaction_type,
						trans_id=trans_id,
						trans_time=trans_time,
						business_shortcode=business_shortcode,
						bill_refNumber=bill_refNumber,
						invoice_number=invoice_number,
						phone=phone,
						first_name=first_name,
						last_name=last_name,
						middle_name=middle_name,
					)
				latest = MpesaPayment.objects.latest('id')
	return HttpResponse(latest.phone)
	#except:
	#return HttpResponse('Invalid request')
    