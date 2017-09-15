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

$(function() {
	var pageUrls = $('.pageUrls');
	var getVariants = $('#variants');
	var url   = pageUrls.data('variants');
	var redirectUrl = pageUrls.data('redirect');
	var name  = $('#id_name');
	var value = $('#id_value');
	var type  = $('#id_type');
	var id_start_date = $('#id_start_date');
	var id_end_date = $('#id_end_date');
	var createDiscountBtn = $('#createDiscountBtn');

	// take care of variants
	getVariants.on('tokenize:select', function(container){
		$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
	   });	 
	getVariants.tokenize2({
	    placeholder: 'Select Product Variants',
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
      if(id_start_date.val()){
        dynamicData['start_date'] = id_start_date.val();
      } 
      if(id_end_date.val()){
        dynamicData['end_date'] = id_end_date.val();
      }  

	 sendDiscountData(dynamicData,createUrl,'post')
	 .done(function(){
	 	alertUser('Discount Added successfully');
	 	window.location.href = redirectUrl;
	 })
	 .fail(function(){
	 	alertUser('Error adding discount','bg-danger','Oops!');
	 });
	});
});