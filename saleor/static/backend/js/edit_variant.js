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
  var editForm = $('#edit-varaints-here');
  var editButton = editForm.find('.editVariantBtn');
  var editvariantBtn = editForm.find('#editvariantBtn');
  var url = '#';
  var id_sku = editForm.find('#id_sku');
  var rprice = editForm.find('#id_price_override');
  var minimum_price = editForm.find('#id_minimum_price');
  var wprice = editForm.find('#id_wholesale_override');
  var variantSupplier = editForm.find('#id_variant_supplier');
  var dynamic_attrs = editForm.find('.dynamicxedit');
  

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
    // console.log(JSON.stringify(json));
    dynamicData['attributes'] = JSON.stringify(json);
    if(!id_sku.val()){
      alertUser('SKU field required','bg-warning','Variant SKU!');
      return false;
    }else{
      dynamicData['sku'] = id_sku.val();
    }

    if(variantSupplier.val()){
      dynamicData['variant_supplier'] = variantSupplier.val();
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

