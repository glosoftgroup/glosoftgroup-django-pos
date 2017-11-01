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
  var EditRefreshDiv = $('#div-edit-variant');
  var editButton = $('.editVariantBtn');
  var editvariantBtn = $('#editvariantBtn');
  var url = '#';
  var id_sku = $('#id_sku');
  var rprice = $('#id_price_override');
  var minimum_price = $('#id_minimum_price');
  var wprice = $('#id_wholesale_override');
  var dynamic_attrs = $('.dynamicxedit');

  

  editvariantBtn.on('click',function(){    
    var vpk = $(this).data('pk');
    var pk = $(this).data('productpk');
    var url = $(this).data('attrurl');
    var refreshUrl = $(this).data('refreshvurl')+"?tab=variants";
    var json = [];
    dynamicData = {};
    // map each varaint
    dynamicData['vpk'] = vpk;
    dynamicData['pk'] = pk;

    dynamic_attrs.map(function() {       
      var id = $(this).data('pk');      
      var value = $(this).val(); 
      if(id && value){        
        json.push({'id':id,'value':value});
      }
      return $(this).data('pk');
    }).get();  
    // ./mapping

    // validation    
    if ( json.length < 1) {      
      //alertUser('Please Select variants','bg-danger','Varaints Required!');
      //return false;
    }
    console.log(JSON.stringify(json));
    dynamicData['attributes'] = JSON.stringify(json);
    if(!id_sku.val()){
      alertUser('SKU field required','bg-warning','Variant SKU!');
      return false;
    }else{
      dynamicData['sku'] = id_sku.val();
    }
    if(wprice.val()){      
      dynamicData['wholesale'] = wprice.val();
    }
    if(!rprice.val()){
      alertUser('Retail Price field required','bg-warning','Field Error!');
      return false;
    }else{
      dynamicData['price'] = rprice.val();
    }
    if(!minimum_price.val()){
      alertUser('Minimum Price field required','bg-warning','Field Error!');
      return false;
    }else{
      dynamicData['minimum_price'] = minimum_price.val();
    }
    dynamicData['template'] = 'edit_variant';
    dynamicData['track'] = 'edit variant'

    addProductDetails(dynamicData,url,'post')
    .done(function(data){
      alertUser('Product Variant updated successfully');
      $('#div-edit-variant').slideUp();
      json = [];
      window.location.href = refreshUrl;
    })
    .fail(function(data){
      alertUser('update failed','bg-danger','Ooops!');
    });    
  
  });

});

