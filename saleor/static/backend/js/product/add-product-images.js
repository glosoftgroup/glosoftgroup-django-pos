(function($, window, document) {   
   $(function() {
   	var pageUrls = $("#pageUrls");
   	var url = pageUrls.data('iscreditable');
    var addImageBtn = $('#images-bt');
   	var creditabale = $("[name='switch-size']");
    var dynamicData = {};
    
    // local function

   });

  // global function
  function addImageFun(dynamicData,url,method){
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