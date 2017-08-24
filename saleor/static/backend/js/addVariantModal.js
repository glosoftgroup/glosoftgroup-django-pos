$(function() {
  
  var pageUrls = $('.pageUrls');
  var modalBtnD = $('#add-new-classd');
  var addClassBtnD = $('#addClassBtnD');
  var modalIdD  = $('#daddProductClass');
  var url      = pageUrls.data('attributes');
  var addClassUrl = pageUrls.data('addclassurlb');
  var addAttrUrl = pageUrls.data('addattrurl');
  var addAnotherAttr = $('#add-another-attr');
  var valueBox = $('#add_value32D');
  // select selectors
  var getAttributesD = $('.getAttributesD');
  var getAttributesTwoD = $('.getAttributesTwoD');

  // open modal
  modalBtnD.on('click',function(){
  	$('#daddProductClass').modal();
  });
  // alertUser
  function alertUser(msg,status='bg-success',header='Well done!')
	{
	    $.jGrowl(msg, 
	    {header: header,theme: status});
	}

  // add New Class
  // ajax
  function addNewClassD(name,attributes,variants) {
    var dynamicData = {};    
    dynamicData["attributes"] = JSON.stringify(attributes);
    dynamicData["name"] = name;
    dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
    dynamicData['variants']= JSON.stringify(variants);
    return $.ajax({
      url: addClassUrl,
      type: "post",
      data: dynamicData
    });
   }
  // // ./add new class  ajax function
  // function addItemD(newitemnum, newitemdesc) {
  //  var selector = $('#id_product_class');
  //  selector.append('<option value="'+newitemnum+'">'+newitemdesc+'</option>');
  //  selector.selectpicker('refresh'); 
  //  selector.selectpicker('val', newitemdesc); 
  // }

  addClassBtnD.on('click',function(){
  	var cname = $('#id_product_class').val();
  	var attributes = getAttributesD.val();
  	var variants = getAttributesTwoD.val();
    if(!attributes && !variants){
      alertUser('Add attributes or variants!','bg-danger','Error!');
      return false;
    }
  	if(!cname){
  		alertUser('Sub category name required!','bg-danger','Error!');
  		return false;
  	}
  	addNewClassD(cname,variants,attributes).done(function(data){
  		alertUser('Sub category name required!');  		
  		refreshAttributes();
      $('#daddProductClass').modal('hide');
  	}).fail(function(){
      alertUser('Variant already added. Please add a unique variant','bg-danger','Error!');
    });



  });
  
  getAttributesD.on('tokenize:select', function(container){
	$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
   });
  // get getAttributes
  getAttributesD.tokenize2({
    placeholder: 'Select variant(s) (eg. Weight)',
    displayNoResultsMessage:true,
    //searchMinLength:3,
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

  getAttributesTwoD.on('tokenize:select', function(container){
	$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
   });
  getAttributesTwoD.tokenize2({
    placeholder: 'Select Attributes(s) (eg. Box Size, Bottle size, Book cover, weight)',
    displayNoResultsMessage:true,
    //searchMinLength:3,
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
  // sdfj

  // add attributes
  var attrNameBtnD = $('#attr-nameD');
  var newValueBtnD = $('#newvalueD');
  var Aurl = addAttrUrl;
  function alertUser(msg,status='bg-success',header='Well done!')
  {
	    $.jGrowl(msg, 
	    {header: header,theme: status});
  }	
    // ajax
	function addAttributeD(myUrl,attName) 
	{
	   var dynamicData = {};
	   dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
	   dynamicData['name'] = attName;
	   return $.ajax({
	      url: myUrl,
	      type: "post",
	      data: dynamicData
	    });
	}

	// ajax
	function addNValueD(myUrl,attName) 
	{
	   var dynamicData = {};
	   dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
	   dynamicData['value'] = attName;
	   return $.ajax({
	      url: myUrl,
	      type: "post",
	      data: dynamicData
	    });
	}

  newValueBtnD.on('click',function(){
    var value = $('#value32D').val();
    //alert(Aurl);
    if(!value){ 
	  	alertUser('Attribute Value required!','bg-danger','Error');
	  	return false;	  	
     }
     addNValueD(Aurl,value).done(function(data){
	     alertUser('Attribute added successful');
	     $('#add_value32D').empty().html(data);
	     $('#value32D').val('');
	  }).fail(function(){
      alertUser('Value already added. Please enter a unique name','bg-danger','Error!');
    });
  });

  attrNameBtnD.on('click',function(){  
    var atname = $('#attribute_name32D').val();
    if(!atname){ 
	  	alertUser('Attribute Name required!','bg-danger','Error');
	  	return false;
     }
    addAttributeD(Aurl,atname).done(function(data){
	   alertUser('Attribute added successful');
	   Aurl = addAttrUrl+data+'/';
	   $('#attribute_name32D').attr('disabled','disabled');
	   attrNameBtnD.addClass('hidden');
	   $('#value-inputD').removeClass('hidden');
	   $('#newvalueD').removeClass('hidden');	
     addAnotherAttr.removeClass('hidden');
	});
});

  addAnotherAttr.on('click',function(){
     $('#attribute_name32D').removeAttr('disabled');
     attrNameBtnD.removeClass('hidden');
     $('#value-inputD').addClass('hidden');
     $('#newvalueD').addClass('hidden'); 
     addAnotherAttr.addClass('hidden');
     valueBox.html('');
     Aurl = addAttrUrl;
  });
  // ./add attributes



});