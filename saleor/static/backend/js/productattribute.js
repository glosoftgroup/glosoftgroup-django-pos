
$(function() {
  //add  product attribute
  $('#add-new-attribute').on('click',function(){
  	var url = $(this).data('href');
  	var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
  	var title_text = $(this).data('title');
  	$('.modal-title').html(title_text);
  	var modal = $(this).attr('href');
  	$(modal).modal();
  	//get form
  	
      // end post
  });  

 function notify(msg,color='bg-danger') {
          new PNotify({
              text: msg,
              addclass: color
          });
      } 
  
  var url = $("#add-new-attribute").data('href');
  var attr_pk = 0 
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
      
      $('#attr_name').attr('disabled','disabled');            
      notify('New category added successfully','bg-success');
    });
    //alert('sdfalsdf');
  });
  
});