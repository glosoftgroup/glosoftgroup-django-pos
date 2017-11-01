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
  	
  });

});