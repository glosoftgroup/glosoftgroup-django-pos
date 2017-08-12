$(function() {
  //add  product category 
  $('#add-new-category').on('click',function(){
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


  function notify(msg,color='bg-danger') {
          new PNotify({
              text: msg,
              addclass: color
          });
      }
   
  $('#modal_add_category_btn').on('click',function(){
        var cat_description = $('#cat_description').val();
        var cat_name = $('#cat_name').val();
        var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
        if(!cat_name){
          notify('add a valid category');
          return false;
        }

        // after validating category cat_name
        var url = $("#add-new-category").data('href');
        var modal = $("#add-new-category").attr('href');
        var posting = $.post( url, {
                              name:cat_name,
                              description:cat_description,
                              csrfmiddlewaretoken:csrf_token,
                            });
        posting.done(function( data ) {
//          $( "#category_field" ).empty().append( data );
          $( "#category_field" ).replaceWith( data );
          $(modal).modal('hide');
          notify('New category added successfully','bg-success');
        });
  });
  
});