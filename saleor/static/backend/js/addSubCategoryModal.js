$(function() {
  
  var pageUrls = $('.pageUrls');
  var modalBtn = $('#add-new-class');
  var addClassBtn = $('#addClassBtn');
  var modalId  = $('#addProductClass');
  var withVariants = $('#withVariants');
  var url      = pageUrls.data('attributes');
  var addClassUrl = pageUrls.data('addclassurl');
  var addAttrUrl = pageUrls.data('addattrurl');
  // select selectors
  var getAttributes = $('.getAttributes');
  var getAttributesTwo = $('.getAttributesTwo');

  // open modal
  modalBtn.on('click',function(){
  	modalId.modal();
  });
  // alertUser
  function alertUser(msg,status='bg-success',header='Well done!')
	{
	    $.jGrowl(msg, 
	    {header: header,theme: status});
	}

  // add New Class
  // ajax
  function addNewClass(name,attributes,variants,has_variants=1) {
    var dynamicData = {};    
    dynamicData["attributes"] = JSON.stringify(attributes);
    dynamicData["name"] = name;
    dynamicData['has_variants'] = has_variants;
    dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
    dynamicData['variants']= JSON.stringify(variants);
    return $.ajax({
      url: addClassUrl,
      type: "post",
      data: dynamicData
    });
   }
  // ./add new class  ajax function
  function addItem(newitemnum, newitemdesc) {
   var selector = $('#id_product_class');
   selector.append('<option value="'+newitemnum+'">'+newitemdesc+'</option>');
   selector.selectpicker('refresh'); 
   selector.selectpicker('val', newitemnum);
  }

  addClassBtn.on('click',function(){
  	var cname = $('#newClassName').val();
  	var attributes = getAttributes.val();
  	var variants = getAttributesTwo.val();
    var has_variants = 1;
    if(withVariants.is(":checked"))
    { has_variants = 1; }else{ has_variants = 0;}
    //console.log(has_variants);
  	if(!cname){
  		alertUser('Sub category name required!','bg-danger','Error!');
  		return false;
  	}
  	addNewClass(cname,attributes,variants,has_variants).done(function(data){
  		alertUser('Sub category name required!');  		
  		addItem(parseInt(data['value']),data['text']);
  		$('#newClassName').val('');
  		$('#addProductClass').modal('hide');
      refreshAttributes();
  	}).fail(function(){
      alertUser('Sub-category already added. Please enter a unique name','bg-danger','Error!');
    });



  });
  
  getAttributes.on('tokenize:select', function(container){
	$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
   });
  // get getAttributes
  getAttributes.tokenize2({
    placeholder: 'Select Attributes(s) (eg. Brand)',
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

  getAttributesTwo.on('tokenize:select', function(container){
	$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
   });
  getAttributesTwo.tokenize2({
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
  var attrNameBtn = $('#attr-name');
  var newValueBtn = $('#newvalue');
  var Aurl = addAttrUrl;
  function alertUser(msg,status='bg-success',header='Well done!')
  {
	    $.jGrowl(msg, 
	    {header: header,theme: status});
  }	
    // ajax
	function addAttribute(myUrl,attName) 
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
	function addNValue(myUrl,attName) 
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

  newValueBtn.on('click',function(){
    var value = $('#value32b').val();
    //alert(Aurl);
    if(!value){ 
	  	alertUser('Attribute Value required!','bg-danger','Error');
	  	return false;	  	
     }
     addNValue(Aurl,value).done(function(data){
	     alertUser('Attribute added successful');
	     $('#add_value32b').empty().html(data);
	     $('#value32b').val('');
	  }).fail(function(){
      alertUser('Value already added. Please enter a unique name','bg-danger','Error!');
    });
  });

  attrNameBtn.on('click',function(){  
    var atname = $('#attribute_name32b').val();
    if(!atname){ 
	  	alertUser('Attribute Name required!','bg-danger','Error');
	  	return false;
     }
    addAttribute(Aurl,atname).done(function(data){
	   alertUser('Attribute added successful');
	   Aurl = addAttrUrl+data+'/';
	   $('#attribute_name32b').attr('disabled','disabled');
	   attrNameBtn.remove();
	   $('#value-input').removeClass('hidden');
	   $('#newvalue').removeClass('hidden');	   
	});
});
  // ./add attributes


});