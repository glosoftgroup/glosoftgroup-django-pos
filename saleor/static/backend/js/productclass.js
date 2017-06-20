$(function() {
  //add  product category 
  $('#add-new-type').on('click',function(){
  	var url = $(this).data('href');
  	var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
  	var title_text = $(this).data('title');
  	$('.modal-title').html(title_text);
  	var modal = $(this).attr('href');
  	$(modal).modal();
  	//get form
  	var posting = $.post( url, 
  		{csrfmiddlewaretoken:csrf_token } 
  		);
      // Put the results in a div
      posting.done(function( data ) {    
        $("#add_category_form" ).empty().append( data );
        $('#modal_add_tax').modal('hide'); 
        //$('#modal_add_category').modal(); 
      });
      // end post
  });

});