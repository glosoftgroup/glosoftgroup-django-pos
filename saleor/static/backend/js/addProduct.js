/* ------------------------------------------------------------------------------
*
*  # addproduct js scripts
*
*  Specific JS code additions for G-POS backend pages
*
*  Version: 1.0
*  Latest update: Aug 19, 2017
*
* ---------------------------------------------------------------------------- */
// alertUser
function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }
//add productDetails
function addProductDetails(dynamicData,url,method){
  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
  return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });

}

$(function() {  
 
 // pricing variables
 var tax_id = $('#id_product_tax');
 var updatePricing = $('#updatePricing');
 var newPrice = $('#tabprice');
 var wholesaleId = $('#id_wholesale_price');
 var tax = 0;

 // stock variables
 var thresholdId = $('#id_low_stock_threshold');
 var supplierId  = $('#id_product_supplier');
 var skuId       = $('#id_variant-sku');
 var updateStockBtn = $('#updatestock'); 
 skuId.attr('disabled','disabled');
 
 $('.disablesku').find('input[name=variant-sku]')
 .removeAttr('required').attr('disabled','disabled');

 // alertUser
  function alertUser(msg,status='bg-success',header='Well done!')
  { $.jGrowl(msg,{header: header,theme: status}); }


 //add productDetails
 function addProductDetails(dynamicData,url,method){
 	dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
 	return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });

 }

 updateStockBtn.on('click', function(){ 	
 	var sku = skuId.val();
 	var supplier = supplierId.val();
 	var threshold = thresholdId.val();
 	url = $(this).data('stockurl');
    pk  = $(this).data('productpk');

 	// if(!sku){
 	//   alertUser('Stock keeping unit required','bg-danger','SKU missing!');
 	//   return false; 	  
 	// }
 	dynamicData = {};
    dynamicData['sku'] = sku;
    dynamicData['pk'] = pk;
    if(supplier){
    dynamicData['supplier'] = supplier;
    }
    if(threshold){
    dynamicData['threshold'] = threshold;
    }     
    dynamicData['track'] = 'add stock details';
    
    method = 'post';
    addProductDetails(dynamicData,url,method)
    .done(function(data){
      alertUser('Data sent successfully');      
    }).fail(function(){
      alertUser('Error adding stock details','bg-danger','Error!');
    });

 });
 updatePricing.on('click',function(){
    tax = tax_id.val();
    price = newPrice.val();
    wholesalePrice = wholesaleId.val();
    url = $(this).data('priceurl');
    pk  = $(this).data('productpk');
    dynamicData = {};
    dynamicData['pk'] = pk;
    dynamicData['price'] = price;
    if(tax){
    dynamicData['tax'] = tax;
    }
    if(wholesalePrice){
    dynamicData['wholesale_price'] =wholesalePrice;	
    }
    
    dynamicData['track'] = 'add pricing';
    method = 'post';
    addProductDetails(dynamicData,url,method)
    .done(function(data){
      alertUser('Data sent successfully');
      $('#id_price').val(price);      
    }).fail(function(){
      alertUser('Error occured','bg-danger','Error!');
    });
 });
});
/* ------------------------------------------------------------------------------
*
*  # adding varaints
**
* ---------------------------------------------------------------------------- */
$(function() {
  var addvariantBtn = $('#addvariantBtn');
  var retailPriceId = $('#rprice');
  var wholePriceId  = $('#wprice');
  var dynamicVariants = $('.dynamicvxx');
  var newSkuId = $('#new-sku-td');
  var refreshVaraintsContent = $('#refreshvaraintscontent');
  var json = [];
  addvariantBtn.on('click',function(){    
    // map each varaint
    dynamicVariants.map(function() { 
      //console.log($(this).data('pk'));
      var id = $(this).data('pk');      
      var value = $(this).val(); 
      if(id && value){
        json.push({'id':id,'value':value});
      }
      return $(this).data('pk');
    }).get();  
    // ./mapping    
    
    wholePrice  = wholePriceId.val();
    retailPrice = retailPriceId.val();
    newSku      = newSkuId.val();
    if(!retailPrice || !newSku){
      alertUser('Retail Price & SKU required','bg-danger','Fill required fields!');
      return false;
    }
    dynamicData = {};
    if(wholePrice){
      dynamicData['wholesale'] = wholePrice;
    }
    if ( json.length < 1) {
      //alertUser(json.length);
      alertUser('Please Select variants','bg-danger','Varaints Required!');
      return false;
    }  
    
    dynamicData['price'] = retailPrice;
    dynamicData['sku'] = newSku;
    dynamicData['attributes'] = JSON.stringify(json);
    dynamicData['track'] = 'adding variants';
    dynamicData['pk'] = $(this).data('productpk');
    var method = 'post';
    var url = $(this).data('attrurl');
    addProductDetails(dynamicData,url,method)
    .done(function(data){
      alertUser('data sent successfully');
      json = [];
      refreshVaraintsContent.html(data);
    })
    .fail(function(){
      alertUser('Error adding attributes','bg-danger','Error!');
      json = [];
    });
  });


});

$(function() {
  
  var pageUrls = $('.pageUrls');
  var modalBtnD = $('#addNewvaraints');
  var addClassBtnD = $('#xaddClassBtnD');
  var modalIdD  = $('#xProductClass');
  var url      = pageUrls.data('attributes');
  var addClassUrl = pageUrls.data('addclassurlb');
  var addAttrUrl = pageUrls.data('addattrurl');
  var getDetailUrl = pageUrls.data('variantdetail');
  var addAnotherAttr = $('#add-another-attr');
  var valueBox = $('#add_value32D');
  // select selectors
  var getAttributesD = $('.xgetAttributesD');
  //var getAttributesTwoD = $('.xgetAttributesTwoD');
  
  // get product class getDetailUrl
  function getDetail(class_pk,getDetailUrl)
  {
    var dynamicData = {};
    dynamicData["name"] = name;
    dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
    dynamicData['class_pk'] = class_pk;
    return $.ajax({
      url: getDetailUrl,
      type: "post",
      data: dynamicData
    });
  }
  // ./ porduct class detail

  // open modal
  modalBtnD.on('click',function(){
    getDetail(getProductClass(),getDetailUrl).done(function(data){
      if(data['name'] == 'None' ){
        alertUser('Change Sub category and try again!','bg-danger','You cannot add attributes!');
      }else{
        modalIdD.modal();
      }
    });
    
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
    //dynamicData["attributes"] = JSON.stringify(attributes);
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
    //var variants = getAttributesTwoD.val();
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
      //refreshAttributes();
      window.location.href = $('#xaddClassBtnD').data('refreshme');
      $('#daddProductClass').modal('hide');
    }).fail(function(){
      alertUser('Variant already added. Please add a unique variant name','bg-danger','Error!');
    });



  });
  
  getAttributesD.on('tokenize:select', function(container){
  $(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
   });
  // get getAttributes
  getAttributesD.tokenize2({
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
  }).fail(function(){
      alertUser('Attribute name already added. Please add a unique name','bg-danger','Error!');
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