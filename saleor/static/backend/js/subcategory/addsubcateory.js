/* ------------------------------------------------------------------------------
*
*  # subcateory js scripts
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
  
  var pageUrls = $('.pageUrls');
  var modalBtnD = $('#addNewvaraints');
  var addClassBtnD = $('#xaddClassBtnD');
  var modalIdD  = $('#xProductClass');
  var url      = pageUrls.data('attributes');
  var addClassUrl = pageUrls.data('addclassurlb');
  var addAttrUrl = pageUrls.data('addattrurl');
  var refrehsurl = pageUrls.data('refrehsurl');
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
  function addNewClassD(name,attributes) {
    var dynamicData = {};    
    //dynamicData["attributes"] = JSON.stringify(attributes);
    dynamicData["newclass"] = name;
    dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
    dynamicData['variants']= JSON.stringify(attributes);
    return $.ajax({
      url: addClassUrl,
      type: "post",
      data: dynamicData
    });
   }

function refreshList(){ 
     $.ajax({ url:refrehsurl, type: 'GET',data: {page:1, q:'', },success: function(data){
            $('#pagination-div').html(data);
     }});
}

  addClassBtnD.on('click',function(){
    var cname = $('#newvName').val();
    var attributes = getAttributesD.val();
    //var variants = getAttributesTwoD.val();
    if(!attributes){
      alertUser('Add attributes or variants!','bg-danger','Error!');
      return false;
    }
    if(!cname){
      alertUser('Sub category name required!','bg-danger','Error!');
      return false;
    }
    addNewClassD(cname,attributes)
    .done(function(data){
      alertUser('Attribute added successfully!');
      getAttributesD.parents('div').find('li.token').remove();
        $(".xgetAttributesD option[selected='']").remove();
        $('#newvName').val('');
      $('#toggle-div').slideUp('slow');     
      refreshList();
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
