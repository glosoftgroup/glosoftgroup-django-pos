$(function() {

  function notify(msg,color='bg-danger') {
          new PNotify({
              text: msg,
              addclass: color
          });
      }
  //add  product type 
  $('#add-new-type').on('click',function(){
  	var url = $(this).data('href');
  	var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
  	var title_text = $(this).data('title');
  	$('.modal-title').html(title_text);
  	var modal = $(this).attr('href');
  	$(modal).modal();
    var posting = $.get( url,{} );
    posting.done(function( data ) {    
        $("#modal_type_results" ).html( data ); 
             
      });
    //window.open(url, "unicorn", "width=400, height=600, screenX=100"); 

  });

});