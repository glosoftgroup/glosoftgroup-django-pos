$(function() {

  function notify(msg,color='bg-danger') {
          new PNotify({
              text: msg,
              addclass: color
          });
      }

  //add  product type 
  $('body').on('click', '#add-new-type', function(){
    $('#modal_type').modal();
     $('#modal_type .modal-title').html('Add Sub Category');
  	/*var url = $(this).data('href');
  	var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
  	var title_text = $(this).data('title');
  	$('.mt1').html(title_text);
  	$('.mt2').html('Add Attribute');

  	var modal = $(this).data('modal');
    var posting = $.get( url,{} );
    posting.done(function( data ) {    
        $("#modal_type_results" ).html( data ); 
        $(modal).modal();
      });*/

  });

});