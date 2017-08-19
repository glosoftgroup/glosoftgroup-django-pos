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

 	if(!sku){
 	  alertUser('Stock keeping unit required','bg-danger','SKU missing!');
 	  return false; 	  
 	}
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