/**
 * Send messages script
 *
 * @package Glosoft Point of sale
 * Author: Paul K.
 * http://www.glosoftgroup.com
 */
$(function() {
    var pageUrls   = $('.pageUrls');
	var url = pageUrls.data('contacts');
	var composeUrl = pageUrls.data('compose');
    var redirectUrl = pageUrls.data('redirecturl');
	var sendSms = $('#sendSms');
	var getCustomer = $('.getCustomer');
	var getSupplier = $('.getSupplier');
	var userContacts = $('.contacts');
	var subject = $('#subject');
	var body = $('#body');
	var customerCount = $('#customerCount');
	var supplierCount = $('#supplierCount');

// customer contacts
getCustomer.tokenize2({
    placeholder: 'Select customer(s)',
    dataSource: function(search, object){
        $.ajax(url, {
            data: { search: search, start: 1,group:'customers' },
            dataType: 'json',
            success: function(data){
                var $items = [];
                $.each(data, function(k, v){
                    $items.push(v);
                });
                object.trigger('tokenize:dropdown:fill', [$items]);
            }
        });
    }
});
// supplier contacts
getSupplier.tokenize2({
    placeholder: 'Select supplier(s)',
    dataSource: function(search, object){
        $.ajax(url, {
            data: { search: search, start: 1,group:'suppliers' },
            dataType: 'json',
            success: function(data){
                var $items = [];
                $.each(data, function(k, v){
                    $items.push(v);
                });
                object.trigger('tokenize:dropdown:fill', [$items]);
            }
        });
    }
});

// user contacts
// userContacts.tokenize2({
//     placeholder: 'Select user(s)',
//     sortable: true,
//     dataSource: 'select'
// });

// tokenize events
$('#customerModal').on('hidden.bs.modal', function () {
    customerCount.text(getCustomer.val().length);
});
$('#supplierModal').on('hidden.bs.modal', function () {
    supplierCount.text(getSupplier.val().length);
});


function alertUser(msg,status,header='Well done!')
{
    $.jGrowl(msg, 
    {header: header,theme: status});
}

// ajax
function sendNotification(userContacts,subject,body,toCustomers,toSuppliers,single) {
    var dynamicData = {}; 
    dynamicData["single"]  = single;
    dynamicData["userContacts"] = JSON.stringify(userContacts);
    dynamicData["subject"] = subject;
    dynamicData["body"] = body;
    dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
    dynamicData['toCustomers']= JSON.stringify(toCustomers);
    dynamicData['toSuppliers']= JSON.stringify(toSuppliers);
    return $.ajax({
      url: composeUrl,
      type: "post",
      data: dynamicData
    });
  }
  // ./ end sendSms functions
// listen to sendsms click
sendSms.on('click',function(){   
    var ucontacts = userContacts.val();
    var scontacts = getSupplier.val();
    var ccontacts = getCustomer.val(); 
    var single = $('#single').val();
    var what = body.val();
    var verb = subject.val();
    if(!verb)
    { 
        alertUser('Message Subject required','bg-danger','Error!');
        return false;
        subject.focus();
    }
    if(!what){ alertUser('Message Body required','bg-danger','Empty Body!'); return false;}
    if(!ccontacts){ ccontacts = false; }
    if(!scontacts){ scontacts = false; } 
    if(!scontacts && !ccontacts && !ucontacts && !single)
    {
        alertUser('Enter at least one contacts!','bg-danger','Error!');
        return false;
    }
    sendNotification(ucontacts,verb,what,ccontacts,scontacts,single).done(function(data) {
        $.jGrowl('Notification sent successfully', 
        {header: 'Well done!',theme: 'bg-success'});
        window.location.href = redirectUrl;
    });
});
// ./ event click send button
});