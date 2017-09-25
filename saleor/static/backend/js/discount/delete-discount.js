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
var loader = `
<div class="modal-content">
 <div  class='col-md-8' id="myloader">
            <div class="cs-loader mt-15">
              <div class="cs-loader-inner text-primary">
                <label> ●</label>
                <label> ●</label>
                <label> ●</label>
                <label> ●</label>
                <label> ●</label>
                <label> ●</label>
              </div>
            </div>
          </div>
        </div>
`;
$(function() {
	var deleteBtn = $('.delete-discount');
	var deleteUrl = '#';
	var modalId = $('#modal_instance');
	var modalContent = $('.results');	

	deleteBtn.on('click',function(){
		//modalContent.html(loader);
    	deleteUrl = $(this).data('href');    	
    	$('.modal-title').html($(this).data('title'));    	
    	modalId.modal();
    	dynamicData = {};
    	sendDiscountData(dynamicData,deleteUrl,'get')
		 .done(function(data){		 	
		 	modalContent.html(data);
		 })
		 .fail(function(){		 	
		 });
    });


});