/**
 * Send messages script
 *
 * @package Glosoft Point of sale
 * Author: Paul K.
 * http://www.glosoftgroup.com
 */
$(function() {
    var pageUrls   = $('.pageUrls');
	var url        = pageUrls.data('contacts');
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
    var sendspinnerId = $('#sendspinner');

// customer contacts
getCustomer.on('tokenize:select', function(container){
  $(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
});

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
getSupplier.on('tokenize:select', function(container){
  $(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
});

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
userContacts.on('tokenize:select', function(container){
  $(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
});
userContacts.tokenize2({
    placeholder: 'Select user(s)',
    sortable: true,
    dataSource: function(search, object){
        $.ajax(url, {
            data: { search: search, start: 1, group:'users' },
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
function sendNotification(dynamicData) {    
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
    var what = body.val();
    var verb = subject.val();
    var dynamicData = {}; 
    if(!verb)
    { 
        alertUser('Message Subject required','bg-danger','Error!');
        return false;
        subject.focus();
    }
    if(!what){ alertUser('Message Body required','bg-danger','Empty Body!'); return false;}
    if(ccontacts){ 
     dynamicData['toCustomers']= JSON.stringify(ccontacts);
    }
    if(scontacts){
     dynamicData['toSuppliers']= JSON.stringify(scontacts);
    } 
    if(!scontacts && !ccontacts && !ucontacts)
    {
        alertUser('Enter at least one contacts!','bg-danger','Error!');
        return false;
    }

    sendspinnerId.removeClass('icon-checkmark3');
    sendspinnerId.addClass('icon-spinner').addClass('spinner');       
    dynamicData["userContacts"] = JSON.stringify(ucontacts);
    dynamicData["subject"] = verb;
    dynamicData["body"] = what;
    dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();    
    
    sendNotification(dynamicData)
    .done(function(data) {
        $.jGrowl('Notification sent successfully', 
        {header: 'Well done!',theme: 'bg-success'});
        window.location.href = redirectUrl;
    })
    .fail(function(){
    sendspinnerId.addClass('icon-checkmark3');
    sendspinnerId.removeClass('icon-spinner').removeClass('spinner');
    });
    
});
// ./ event click send button




});