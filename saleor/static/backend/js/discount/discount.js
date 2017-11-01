/* ------------------------------------------------------------------------------
*
*  # Discount js scripts
*
*  Specific JS code additions for G-POS backend pages
*
*  Version: 1.0
*  Latest update: Sep 8, 2017
*
* ---------------------------------------------------------------------------- */
// alertUser
function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }
//add productDetails
function sendDiscountData(dynamicData,url,method){
  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
  return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });
}

function refreshTable(){
	var rUrl = $('.pageUrls').data('refreshtable');
	$.ajax({ url:rUrl, type: 'GET',data: {page:1, q:''},success: function(data){
          $('#pagination-div').html(data);
   }});
}

$(function(){    
    // validate
    $('#sale-details').validate({
    rules:{
        name: {
          required:true,
          minlength:3
        },
        start_date: {
          required:true,         
        }, 
        end_date: {
          required:true,          
        },     

    },
    messages:{
      name:{
        required: "Provide a name",
        minlength: "at least 3 characters long"
      },      
    },
    
  });
    // end validate
  
});

$(function() {
	var pageUrls = $('.pageUrls');
	var getVariants = $('#variants');
	var getCustomers = $('#customers');
	var url   = pageUrls.data('variants');
	var curl  = pageUrls.data('curl');
	var redirectUrl = pageUrls.data('redirect');
	var name  = $('#id_name');
	var value = $('#id_value');
	var type  = $('#id_type');
	var id_start_date = $('#id_start_date');
	var id_end_date = $('#id_end_date');
	var deleteBtn = $('.delete-discount');
	var deleteUrl = '#';
	var modalId = $('#modal_instance');
	var toggleDiv = $('#toggle-div');
	var modalContent = $('.results');
	var createDiscountBtn = $('#createDiscountBtn');

	// take care of variants
	getVariants.on('tokenize:select', function(container){
		$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
	   });	 
	getVariants.tokenize2({
	    placeholder: 'Select Product',
	    displayNoResultsMessage:true,	    
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
	// take care customer
	getCustomers.on('tokenize:select', function(container){
		$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
	   });	 
	getCustomers.tokenize2({
	    placeholder: 'Select customer',
	    displayNoResultsMessage:true,	    
	    sortable: true,
	    dataSource: function(search, object){
	        $.ajax(curl, {
	            data: { search: search, start: 1, group:'customers',returnId:'true' },
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
	// end tokenization

	// validate and create Discouont
	createDiscountBtn.on('click',function(){
	  var createUrl = $(this).data('createurl');
      var dynamicData = {};
      if(!name.val()){
      	alertUser('Discount name required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['name'] = name.val();
      }
      if(!value.val()){
      	alertUser('Discount Value field required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['value'] = value.val();
      }
      if(!type.val()){
      	alertUser('Discount Type field required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['type'] = type.val();
      }
      if(getVariants.val()){
        dynamicData['variants'] = JSON.stringify(getVariants.val());
      }
      if(getCustomers.val()){
        dynamicData['customers'] = JSON.stringify(getCustomers.val());
      } 
      if(id_start_date.val()){
        dynamicData['start_date'] = id_start_date.val();
      } 
      if(id_end_date.val()){
        dynamicData['end_date'] = id_end_date.val();
      }  

	 sendDiscountData(dynamicData,createUrl,'post')
	 .done(function(){
	 	alertUser('Discount Added successfully');
	 	toggleDiv.slideUp('slow');
	 	refreshTable();
	 	//window.location.href = redirectUrl;
	 })
	 .fail(function(){
	 	alertUser('Error adding discount','bg-danger','Oops!');
	 });
	});

	// Basic select
    $('.bootstrap-select').selectpicker();
     // Default initialization
    

    $('.pickadate-selectors').pickadate({
        format: 'yyyy-mm-dd',
        editable: true,  
        selectYears: true,
        selectMonths: true,
        formatSubmit: 'yyyy-mm-dd',

    });

    deleteBtn.on('click',function(){
    	deleteUrl = $(this).data('href');    	
    	$('.modal-title').html($(this).data('title'));    	
    	modalId.modal();
    	dynamicData = {};
    	sendDiscountData(dynamicData,deleteUrl,'get')
		 .done(function(data){
		 	//alertUser('Delete content loaded');
		 	modalContent.html(data);
		 })
		 .fail(function(){
		 	//alertUser('Error loading form','bg-danger','Oops!');
		 });
    });
});