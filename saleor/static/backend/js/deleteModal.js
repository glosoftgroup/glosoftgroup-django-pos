$(function(){
  var succes_url = '';
$('.modal-trigger-delete').on('click', function (e) {         
         var url = $(this).data('href')
         var prompt_text = $(this).data('title');
         //var username = $(this).data('name');
         var modal = $(this).data('ta');
         var id = $(this).data('id');
         var tabname = $(this).data('tabname');
         succes_url = $(this).data('successurl')+tabname;

         $('#success_url').attr('value',success_url);
         $('.delete-this').attr('data-id', id);
         $('.delete-this').attr('data-href', url);
         $('.modal-title').html(prompt_text);
         $(modal).modal();
         $('.delete_form').attr('action',url);
      });

      /* clicked the submit button */
      $('.delete-this').on('click', function (e) {
          var f = document.getElementById('delform');
          var formData = new FormData(f);
          var id = $(this).data('id');
          var url = $(this).data('href');

          $.ajax({
              url: url,
              type: "POST",
              data: formData,
              processData: false,
              contentType: false,
              success:function(data){        
                $('#modal_delete_instance').modal('hide');
                $('#variant-row'+id).remove();            
                $.jGrowl('deleted successfully', {
                  header: 'Well done!',
                  theme: 'bg-success'
                });
                window.location.href =  succes_url;               
              },
              error:function(error){
                console.log(error);
                
              }
          });
      });
});