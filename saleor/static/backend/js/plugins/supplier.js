
$(function() {
  //add  supplier
  $("body").on("click", "#add-supplier", function(){
    var url = $(this).data('href');
    var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
    var title_text = $(this).data('title');
    $('.modal-title').html(title_text);
    var modal = $(this).attr('href');
    $(modal).modal();

    var posting = $.get( url, {});

    posting.done(function( data ) {    
        $(".results" ).empty().append( data );
      });

  });  

 function notify(msg,color='bg-danger') {
          new PNotify({
              text: msg,
              addclass: color
          });
      } 

  //var url = $("#add-new-attribute").data('href');
  var attr_pk = 0
  
  // submit choice 
  $('#add_attrChoice_btn').on('click',function(){
    var attr_name = $('#attr_name').val();
    var value = $('#value').val();
    if(!attr_name){ 
      notify('add a valid attribute name');
      return false; 
    }  
    var url = $("#add-new-attribute").data('href');
    alert(url);
    var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();          
    var posting = $.post( url, {                
                value:value,                
                csrfmiddlewaretoken:csrf_token,
              });    
    posting.done(function(data) {        
        $('#add_value').empty().append( data );
        //$('#action').html('Add more Value');
      
      //$('#add_value').removeClass('hidden');
                 
      notify('New category added successfully','bg-success');
    });
    posting.fail(function() {
      notify('Error added successfully. Dublicates are not allowed','bg-danger');
    });
    //alert('sdfalsdf');
  });

  $('#add_attr_btn').on('click',function(){
    var attr_name = $('#attr_name').val();
    var value = $('#value').val();
    if(!attr_name){ 
      notify('add a valid attribute name');
      return false; 
    }        
    var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();          
    var posting = $.post( url, {
                name:attr_name,
                value:value,                
                csrfmiddlewaretoken:csrf_token,
              });    
    posting.done(function(data) {
      if(attr_pk == 0){
        attr_pk = parseInt(data);
        url = url+attr_pk+'/';
        $('#action').html('Add Value');
      }else{
        $('#add_value').empty().append( data );
        $('#action').html('Add more Value');
      }
      $('#add_value').removeClass('hidden');
      $('#attr_name').attr('disabled','disabled');            
      notify('New category added successfully','bg-success');
    });
    posting.fail(function() {
      notify('Error added successfully. Dublicates are not allowed','bg-danger');
    });
    //alert('sdfalsdf');
  });
  
});