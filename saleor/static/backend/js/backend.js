/* ------------------------------------------------------------------------------
*
*  # commonjs scripts
*
*  Specific JS code additions for ps254 backend pages
*
*  Version: 1.0
*  Latest update: May 22, 2017
*
* ---------------------------------------------------------------------------- */

$(function() {  
  $('body').on('click','.modal-trigger', function (e) {
    let that = this;  
    var url = $(this).data('href'); 
    var prompt_text = $(this).data('title');
    var modal = $(this).attr('href');
    
    $('.modal-title').html(prompt_text);
    $(modal).modal();
    $('.delete_form').attr('action',url);   
  });

  $('#modal-product-variant-delete-btn').on('click', function (e) {
    let that = this;  
    var url = $(this).data('href'); 
    var prompt_text = $(this).data('title');
    var modal = $(this).attr('href');
    
    $('.modal-title').html(prompt_text);
    $(modal).modal();
    $('.delete_form').attr('action',url);   
  });
  
  // update modal content from ajax results
  $( ".modal-trigger-ajax").on('click',function() {        
    var url = $(this).data('href')
    var prompt_text = $(this).data('title');
    var modal = $(this).attr('href');
    var csrf_token = $(this).data('csrf_token')
    
    $('.modal-title').html(prompt_text);
    $(".results" ).empty().append('<span class="text-center" style="padding:23px">Loading...<i class=" icon-spinner"></i></span>');
    $(modal).modal();
      var posting = $.get( url, {'csrfmiddlewaretoken':csrf_token });
      // Put the results in a div
      posting.done(function( data ) {    
      $(".results" ).empty().append( data ); 
       
      });
    
   });

  $('#select-all-variants').click(function () {    
	  $(':checkbox.switch-actions').prop('checked', this.checked);    
	});
	$('#select-all-stock').click(function () {    
	  $(':checkbox.switch-stock').prop('checked', this.checked);    
	});
	
// end scripts
});
// end main function



