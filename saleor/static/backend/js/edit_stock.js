/* ------------------------------------------------------------------------------
*
*  # edit variant scripts
*
*  Specific JS code additions for ps254 backend pages
*
*  Version: 1.0
*  Latest update: Sept 15, 2017
*
* ---------------------------------------------------------------------------- */

$(function(){
  var editStockRefreshDiv = $('#div-edit-stock');  
  var editStockBtn = $('#editStockBtn');
  var url = '#';
  var invoice_number = $("#id_invoice_number");
  var variant = $('#id_variant');
  var cost_price = $('#id_cost_price');
  var location = $('#id_location');
  var quantity = $('#id_quantity');
  var low_stock_threshold = $('#reorder-threshold');  

  editStockBtn.on('click',function(){   
    var url = $(this).data('contenturl');
    var refreshUrl = $(this).data('refreshstockurl')+"?tab=stock";
    
    dynamicData = {};
    dynamicData['location'] = location.val();
    if(cost_price.val()){
      dynamicData['cost_price'] = cost_price.val();
    }
    if(!variant.val()){
      alertUser('Variant field required','bg-warning','Variant required!');
      return false;
    }else{
      dynamicData['variant'] = variant.val();
    }
    if(!quantity.val()){
      alertUser('quantity field required','bg-warning','Quantity required!');
      return false;
    }else{
      dynamicData['quantity'] = quantity.val();
    }       
    if(low_stock_threshold.val()){
      dynamicData['low_stock_threshold'] = low_stock_threshold.val();
    }   
    if(!invoice_number.val()){
      alertUser('Invoice number field required','bg-warning','Invoice Number!');
      return false;
    }else{
      dynamicData['invoice_number'] = invoice_number.val();
    }    
    
    dynamicData['template'] = 'edit_stock';    

    addProductDetails(dynamicData,url,'post')
    .done(function(data){
      alertUser('Product Stock updated successfully');
      $('#div-edit-variant').slideUp();      
      window.location.href = refreshUrl;
    })
    .fail(function(data){
      alertUser('update failed','bg-danger','Ooops!');
    });    
  
  });

});

