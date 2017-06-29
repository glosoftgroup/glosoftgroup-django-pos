// search js
$(function() {
  
  $( "#submit_search_product").on('click',function() {   
      var search_product = $( "#search_product" ).val();
      var csrf_token = $('#csrf_token').val();      
      var url = $('#search_url').val();

      var where_toshow_loader = "#content-search";
      content_loader(where_toshow_loader); 
      var posting = $.post( url, {search_product:search_product,'csrfmiddlewaretoken': csrf_token} );
      // Put the results in a div
      posting.done(function( data ) {
      var block = $(where_toshow_loader).parent().parent().parent().parent().parent();   
      $(block).unblock();    
      $("#content-search").empty().append( data ); 
         
      });
    
   });
   $( "#main_search_box").on('click',function() {
      // set loader
      var where_toshow_loader = "#content";
      content_loader(where_toshow_loader);   
      var search_product = $( "#search_product_main" ).val();
      var csrf_token = $('#csrf_token').val();
      var url = $('#search_url_main').val(); 
      var posting = $.post( url, {search_product:search_product,'csrfmiddlewaretoken': csrf_token} );
      // Put the results in a div
      posting.done(function( data ) { 
      var block = $(where_toshow_loader).parent().parent().parent().parent().parent();   
      $(block).unblock();
      $("#content" ).empty().append( data );       
      $('.blockElement').attr('class','hidden');
      });
    
   });
   
   // content wait loader
   function content_loader(val) {   
    var block = $(val).parent().parent().parent().parent().parent();
    
        $(block).block({ 
            message: '<i class="icon-spinner2 spinner"></i><br><span class="align-center">Please wait</span>',
            overlayCSS: {
                backgroundColor: '#fff',
                opacity: 0.8,
                cursor: 'wait',
                'box-shadow': '0 0 0 1px #ddd'
            },
            css: {
                border: 0,
                padding: 0,
                backgroundColor: 'none'
            }
        });
   }   

});