
$(function() {
  //add  product attribute

  $('#add-new-attribute').on('click',function(){
  	var url = $('#link-pk').val(); //$(this).data('href');
  	var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
  	var title_text = $(this).data('title');
  	$('.modal-title').html(title_text);
  	var modal = $(this).attr('href');
    
  	$(modal).modal();
  	//get form
  	var posting = $.get( url, 
      {} 
      );

    posting.done(function( data ) {    
        $(".results" ).empty().append( data );
        // $('#modal_add_tax').modal('hide'); 
        //$('#modal_add_category').modal(); 
      });
    
      // end post
  });  

 function notify(msg,color='bg-danger') {
          new PNotify({
              text: msg,
              addclass: color
          });
      } 
  
  //var url = $("#add-new-attribute").data('href');
  var attr_pk = 0
  var url = $('#add-new-attribute').data('href');
  
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
    alert(attr_name);   
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
        $('#add_value').removeClass('hidden');
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