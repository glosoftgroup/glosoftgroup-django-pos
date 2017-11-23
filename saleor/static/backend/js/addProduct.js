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
var dynamicData = {};

$(function() {  
 
 // pricing variables
 var pageUrls = $('.pageUrls');
 var productUrl = pageUrls.data('productdata');
 var productPk  = pageUrls.data('pk');
 var tax_id = $('#id_product_tax');
 var updatePricing = $('#updatePricing');
 var newPrice = $('#tabprice');
 var minimum_price = $('#id_minimum_price')
 var wholesaleId = $('#id_wholesale_price');
 var tax = 0;
 // stock variables
 var thresholdId = $('#id_variant-low_stock_threshold');
 var supplierId  = $('#id_product_supplier');
 var skuId       = $('#id_variant-sku'); 
 var updateStockBtn = $('#updatestock');
 var id_name = $('#id_name');
 var id_categories = $('#id_categories');
 var update_product_btn = $('#update_product_btn');
 skuId.attr('disabled','disabled');
 
 $('.disablesku').find('input[name=variant-sku]')
 .removeAttr('required').attr('disabled','disabled');

 tax_id.on('change',function(){
   dynamicData = {};
   if(tax_id.val()){
   dynamicData['tax'] = tax_id.val();
   }else{
   dynamicData['tax'] = '0';
   }
   dynamicData['track'] = 'adding tax';
   dynamicData['pk']  = productPk;
   addProductDetails(dynamicData,productUrl,'post')
    .done(function(data){
      alertUser('Data sent successfully');
    }).fail(function(){
      alertUser('Error updating product details','bg-danger','Error!');
    });
 });
 update_product_btn.on('click',function(){
   dynamicData = {};
   dynamicData['pk'] = $(this).data('pk');
   if(!id_name.val())
   { alertUser('Product name required','bg-success','Field Error');
    return false; }else{ dynamicData['name'] = id_name.val();
   }
   if(!id_categories.val())
   { alertUser('Product Categories required','bg-success','Field Error');
    return false;  }else{  dynamicData['categories'] = id_categories.val();
   }
   addProductDetails(dynamicData,$(this).data('href'),'post')
    .done(function(data){
      alertUser('Data sent successfully');
    }).fail(function(){
      alertUser('Error updating product details','bg-danger','Error!');
    });

 });

 updateStockBtn.on('click', function(){ 	
 	var sku = skuId.val();
 	var supplier = supplierId.val();
 	var threshold = thresholdId.val();
 
 	url = $(this).data('stockurl');
    pk  = $(this).data('productpk');

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

    addProductDetails(dynamicData,url,'post')
    .done(function(data){
      alertUser('Data sent successfully');      
    }).fail(function(){
      alertUser('Error adding stock details','bg-danger','Error!');
    });

 });
 updatePricing.on('click',function(){
    console.log('update priceing');
    tax = tax_id.val();
    price = newPrice.val();
    wholesalePrice = wholesaleId.val();
    var threshold = thresholdId.val();
    var sku = skuId.val();
    url = $(this).data('priceurl');
    pk  = $(this).data('productpk');
    if(minimum_price.val()){
       dynamicData['minimum_price'] = minimum_price.val();
    }
    dynamicData = {};
    dynamicData['pk'] = pk;
    dynamicData['price'] = price;
    if(tax){
    dynamicData['tax'] = tax;
    }
    if(threshold){
    dynamicData['threshold'] = threshold;
    }
    if(sku){
    dynamicData['sku'] = sku;
    }
    if(wholesalePrice){
    dynamicData['wholesale_price'] =wholesalePrice;	
    }
    dynamicData['minimum_price'] = $('#id_minimum_price').val();
    dynamicData['track'] = 'add pricing x';
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

function refreshStockVar(dynamicData={},url){    
    return $.ajax({
      url: url,
      type: 'get',
      data: dynamicData
    });
}

$(function() {
  var addvariantBtn = $('#addvariantBtn');
  var retailPriceId = $('#rprice');
  var wholePriceId  = $('#wprice');
  var minimumPrice  = $('#mprice');
  var dynamicVariants = $('.dynamicvxx');
  var newSkuId = $('#new-sku-td');
  var reorder_levelId = $('#reorder_level');
  var refreshVaraintsContent = $('#refreshvaraintscontent');
  var refreshStockVariants = $('#refreshStockVariants');
  var json = [];

  function addItem(newitemnum, newitemdesc) {
   var selector = $('#id_variant');
   console.log('we reresh soth**');
   selector.append('<option value="'+newitemnum+'">'+newitemdesc+'</option>');
   selector.selectpicker('refresh');
   selector.selectpicker('val', newitemnum);
 }
  addvariantBtn.on('click',function(){    
    // map each varaint
    dynamicVariants.map(function() {       
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
    reorder_level = reorder_levelId.val();

    newSkuId.on('focusin',function(){
      $(this).nextAll('.help-block:first').addClass('text-danger').html('');
    });
    if(!newSku){
        newSkuId.nextAll('.help-block:first').addClass('text-danger').html('Sku required');
        return false;
    }
    //validate retail price
    retailPriceId.on('focusin',function(){
      $(this).nextAll('.help-block:first').addClass('text-danger').html('');
    });
    if(!retailPriceId.val()){
        retailPriceId.nextAll('.help-block:first').addClass('text-danger').html('Retail price');
        return false;
    }
    //validate minimum price
    minimumPrice.on('focusin',function(){
      $(this).nextAll('.help-block:first').addClass('text-danger').html('');
    });
    if(!minimumPrice.val()){
        minimumPrice.nextAll('.help-block:first').addClass('text-danger').html('Fill minimum price');
        return false;
    }
    if(!retailPrice || !newSku || !minimumPrice.val()){
      alertUser('Retail Price, Minimum price & SKU required','bg-danger','Fill required fields!');
      return false;
    }
    dynamicData = {};
    if(wholePrice){
      dynamicData['wholesale'] = wholePrice;
    }
    if(reorder_level){
      dynamicData['low_stock_threshold'] = reorder_level;
    }
    
    if ( json.length < 1) {      
      //alertUser('Please Select variants','bg-danger','Varaints Required!');
      //return false;
    }  
    
    dynamicData['price'] = retailPrice;
    dynamicData['minimum_price'] = minimumPrice.val();

    dynamicData['sku'] = newSku;
    dynamicData['attributes'] = JSON.stringify(json);
    dynamicData['track'] = 'adding variants x';
    dynamicData['pk'] = $(this).data('productpk');
    var method = 'post';
    var url = $(this).data('attrurl');
    var refreshvurl = $(this).data('refreshvurl');
    addProductDetails(dynamicData,url,method)
    .done(function(data){
      alertUser('data sent successfully');
      $('#toggleVariant').slideUp();
      json = [];
      refreshVaraintsContent.html(data);
      var dynamic = {}
      dynamic['template'] = 'select_variant';
      dynamic['get'] = 'variants';
      dynamic['track'] = 'refresh stock variant field';
      refreshStockVar(dynamic,refreshvurl)
      .done(function(data){
        addItem(data['id'],data['value']);
      });
    })
    .fail(function(){
      alertUser('Error adding attributes, Add a unique SKU','bg-danger','Error!');
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
  var addAnotherAttr = $('#add-another-attrx');
  var valueBox = $('#add_value32Dx');
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
    addNewClassD(cname,variants,attributes)
    .done(function(data){
      alertUser('Attribute added successfully!');     
      //refreshAttributes();
      window.location.href = $('#xaddClassBtnD').data('refreshme');
      $('#daddProductClass').modal('hide');
    })
    .fail(function(){
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
  var attrNameBtnD = $('#attr-nameDx');
  var newValueBtnD = $('#newvalueDx');
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
    var value = $('#value32Dx').val();
    //alert(Aurl);
    if(!value){ 
      alertUser('Attribute Value required!','bg-danger','Error');
      return false;     
     }
     addNValueD(Aurl,value).done(function(data){
       alertUser('Attribute added successful');
       $('#add_value32Dx').empty().html(data);
       $('#value32Dx').val('');
    }).fail(function(){
      alertUser('Value already added. Please enter a unique name','bg-danger','Error!');
    });
  });

  attrNameBtnD.on('click',function(){  
    var atname = $('#attribute_name32Dx').val();
    if(!atname){ 
      alertUser('Attribute Name required!','bg-danger','Error');
      return false;
     }
    addAttributeD(Aurl,atname).done(function(data){
     alertUser('Attribute added successful');
     Aurl = addAttrUrl+data+'/';
     $('#attribute_name32Dx').attr('disabled','disabled');
     attrNameBtnD.addClass('hidden');
     $('#value-inputDx').removeClass('hidden');
     $('#newvalueDx').removeClass('hidden'); 
     addAnotherAttr.removeClass('hidden');
  }).fail(function(){
      alertUser('Attribute name already added. Please add a unique name','bg-danger','Error!');
    });
});

  addAnotherAttr.on('click',function(){
     $('#attribute_name32Dx').removeAttr('disabled');
     attrNameBtnD.removeClass('hidden');
     $('#value-inputDx').addClass('hidden');
     $('#newvalueDx').addClass('hidden'); 
     addAnotherAttr.addClass('hidden');
     valueBox.html('');
     Aurl = addAttrUrl;
  });
  // ./add attributes



});
/* ------------------------------------------------------------------------------
*
*  # adding form stock
**
* ---------------------------------------------------------------------------- */
function refreshStockDiv(url){
    dynamicData = {};
    return $.ajax({
      url: url,
      type: 'get',
      data: dynamicData
    });
   }
$(function(){
   var stockVariantId  = $('#id_variant');
   var costPriceId     = $('#stockcostprice');
   var stockInvoiceId  = $('#stockInvoiceNumber');
   var stockLocationId = $('#id_location');
   var stockQuantityId = $('#stock_quantity');
   var stockAmountPaid = $('#amount_paid');
   var stockTotalCost  = $('#id_total_cost');
   var stockPaymentOption = $('#payment_option');
   var reorder_levelId = $('#id_low_stock_threshold');
   var stockStatus = $('#status');
   var addnewStockBtn  = $('#addnewStockBtn');

   // remove helper
   stockVariantId.on('change',function(){
    $(this).nextAll('.help-block:first').addClass('text-danger').html('');
    $('#variant-help').addClass('text-danger').html('');
   });
   reorder_levelId.on('change',function(){
    $(this).nextAll('.help-block:first').addClass('text-danger').html('');
   });
   stockQuantityId.on('focusin',function(){
    $(this).nextAll('.help-block:first').addClass('text-danger').html('');
   });
   stockLocationId.on('change',function(){
    $(this).nextAll('.help-block:first').addClass('text-danger').html('');
   });
   stockInvoiceId.on('focusin',function(){
    $(this).nextAll('.help-block:first').addClass('text-danger').html('');
   });
   costPriceId.on('keyup',function(){
    $(this).nextAll('.help-block:first').addClass('text-danger').html('');
   });
   // success
   var refreshDiv = $('#refreshStockitems');   
   addnewStockBtn.on('click',function(){
   console.log('you clicked thi button');
    var dynamicData = {};
    var variant = stockVariantId.val();
    var cost_price = costPriceId.val();
    var location = stockLocationId.val();
    var quantity = stockQuantityId.val();
    var reorder_level = reorder_levelId.val();
    var invoice_number  = stockInvoiceId.val();
    var addStockUrl = $(this).data('contenturl');
    var refreshStockUrl = $(this).data('refreshstockurl');
    // validation
    if(!invoice_number){

      stockInvoiceId.focus();
      stockInvoiceId.prop('autofocus');      
      stockInvoiceId.nextAll('.help-block:first').addClass('text-danger').html('Field required');
      return false;
    }else{
      stockInvoiceId.nextAll('.help-block:first').addClass('text-danger').html('');
    }
    if(!variant){
      stockVariantId.focus();
      stockVariantId.prop('autofocus');      
      $('#variant-help').addClass('text-danger').html('Field required');
      stockVariantId.css("border-color","transparent transparent #D84315;");
      
      return false;
    }else{            
      stockVariantId.nextAll('.help-block:first').addClass('text-danger').html('');     
       
    }
    if(!cost_price){

      costPriceId.focus();
      costPriceId.prop('autofocus');      
      costPriceId.nextAll('.help-block:first').addClass('text-danger').html('Field required');
      costPriceId.css("border-color","transparent transparent #D84315;");
      return false;
    }else{
      costPriceId.nextAll('.help-block:first').addClass('text-danger').html('');
    }
    if(!quantity){
      stockQuantityId.focus();
      stockQuantityId.prop('autofocus');      
      stockQuantityId.nextAll('.help-block:first').addClass('text-danger').html('Field required');
      
      return false;
    }else{
      stockQuantityId.nextAll('.help-block:first').addClass('text-danger').html('');
    }
    
    if(reorder_level){
      dynamicData['low_stock_threshold'] = reorder_level;
    }
    if(stockAmountPaid.val()){
      dynamicData['amount_paid'] = stockAmountPaid.val();
    }
    if(stockPaymentOption.val()){
      dynamicData['payment_options'] = stockPaymentOption.val();
    }
    if(stockTotalCost.val()){
      dynamicData['total_cost'] = stockTotalCost.val();
    }
    
    // ./validation
    dynamicData['status']  = stockStatus.val();
    dynamicData['variant'] = variant;
    dynamicData['quantity'] = quantity;
    dynamicData['cost_price'] = cost_price;
    dynamicData['location'] = location;
    dynamicData['invoice_number'] = invoice_number;
    dynamicData['track'] = 'adding stock details';

    addProductDetails(dynamicData,addStockUrl,'post')
    .done(function(data){        
      if(data.errors){        
        var message = ' ';
        $.each(data, function(i, item) {
           if(item != '__all__'){
            message += item+ ' ';
           }            
        });
        alertUser(message.replace('__all__', ' '),'bg-warning','Error!');
      }else{
        alertUser('Stock information sent successfully');
      }
      
      /* toggle form */
      $('#toggleStock').toggle();
      refreshStockDiv(refreshStockUrl)
      .done(function(data){
        refreshDiv.html(data);
      });
    })
    .fail(function(err){
      var msg = JSON.stringify(err).message;
      console.log(msg);
      alertUser('Stock already exist','bg-danger','Error!');
    });
   });
});

/* ------------------------------------------------------------------------------
*
*  # adding modal stock
*
* ---------------------------------------------------------------------------- */

$(function(){
  var addNewStockBtn = $('#addNewStockBtnjj');
  var modalIds = $('#modal_stocks');  
  var addStockForm = $('.addstockresults');

  addNewStockBtn.on('click',function(){
    dynamicData = {};
    var getStockformUrl = $(this).data('contenturl');    
    addProductDetails(dynamicData,getStockformUrl,'get')
    .done(function(data){     
      addStockForm.html(data);
    });
    modalIds.modal();
  });
});

/* edit variant script */
$(function(){
  var EditRefreshDiv = $('#div-edit-variant');
  var editButton = $('.editVariantBtn');
  var editvariantBtn = $('#editvariantBtn');
  var toggleVariant = $('#toggleVariant');
  var url = '#';  

  editButton.on('click',function(){
    if(toggleVariant.is(':visible')){
        toggleVariant.toggle('slow');
    }
    EditRefreshDiv.html('Processing form ...');
    var pk = $(this).data('pk');
    var url = $(this).data('href');
    dynamicData = {};
    dynamicData['template'] = 'edit_variant';    
    
    $('html, body').animate({
     scrollTop: $('#div-edit-variant').offset().top
    }, 1000);
    addProductDetails(dynamicData,url,'get')
    .done(function(data){      
      EditRefreshDiv.html(data);
    })
    .fail(function(){
      alertUser('failed to get edit form');
    });    
  
  });  

});

/* edit variant script */
$(function(){
  var editStockRefreshDiv = $('#div-edit-stock');
  var editSelectOption = $('.edit-stock-Btn');
  var toggleStock = $('#toggleStock');
  var url = '#';  

  editSelectOption.on('click',function(){
    editStockRefreshDiv.html('Processing form ...');
    if(toggleStock.is(':visible')){
        toggleStock.toggle('slow');
    }
    var pk = $(this).data('pk');
    url = $(this).data('href');
    dynamicData = {};
    dynamicData['template'] = 'edit_stock';    
    
    $('html, body').animate({
     scrollTop: $('#stock-tab').offset().top
    }, 1000);
    addProductDetails(dynamicData,url,'get')
    .done(function(data){      
      editStockRefreshDiv.html(data);
    })
    .fail(function(){
      alertUser('failed to get edit form');
    });    
  
  });  

});

/* add image script */
$(function(){
  var addImageBtn = $('.images-bt');
  var editImageRefreshDiv = $('#add-image-form-div');
  var loader = $('#myloader');
  // get template  
  addImageBtn.on('click',function(){
    loader.removeClass('hidden');
    var url = $(this).data('href');    
    dynamicData = {};
    dynamicData['url'] = url;
    addProductDetails(dynamicData,url,'get')
    .done(function(data){
      loader.addClass('hidden');
      editImageRefreshDiv.html(data);
    })
    .fail(function(){
      alertUser('failed to get edit form');
    });
  });
  // ./add get template
});