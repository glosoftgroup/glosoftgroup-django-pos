(function($, window, document) {   
   $(function() {
   	var pageUrls = $("#pageUrls");
   	var url = pageUrls.data('iscreditable');
   	var creditabale = $("[name='switch-size']");
    $.fn.bootstrapSwitch.defaults.size = 'mini';
    $.fn.bootstrapSwitch.defaults.onText = 'Yes';
    $.fn.bootstrapSwitch.defaults.offText = 'No';
    $.fn.bootstrapSwitch.defaults.onColor = 'primary';
    $.fn.bootstrapSwitch.defaults.animate = 'true';
    $.fn.bootstrapSwitch.defaults.labelWidth = 'auto';
    var dynamicData = {};

    creditabale.bootstrapSwitch();
    creditabale.on('switchChange.bootstrapSwitch', function(event, state) {      
      console.log(url);
      var pk  = $(this).data('pk');
      dynamicData = {};
      dynamicData['pk'] = pk;       
      dynamicData['track'] = 'Is customer creditable';
      if(String(state) == 'true'){      	
      	dynamicData['is_creditable'] = 1;
      }else{ 
        dynamicData['is_creditable'] = 0;     	
      }
      isCreditable(dynamicData,url,'post')
      .done(function(){
      	alertUser('Customer data updated');
      })
      .fail(function(){
      	alertUser('Error updating customer data','bg-warning','Error!');
      });
       
    });


   });

   
  function isCreditable(dynamicData,url,method){
	  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
	  return $.ajax({
	      url: url,
	      type: method,
	      data: dynamicData
	    });

	}
  // alertUser
  function alertUser(msg,status='bg-success',header='Well done!')
  { $.jGrowl(msg,{header: header,theme: status}); }


}(window.jQuery, window, document));