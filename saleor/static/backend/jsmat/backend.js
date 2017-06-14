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


  $('.modal-trigger').on('click', function (e) {
    let that = this;  
    var url = $(this).data('href') 
    var prompt_text = $(this).data('title');
    var modal = $(this).attr('href');
    
    $('.modal-title').html(prompt_text);
    $(modal).modal();
    $('.delete_form').attr('action',url);
    
   
  });


});
