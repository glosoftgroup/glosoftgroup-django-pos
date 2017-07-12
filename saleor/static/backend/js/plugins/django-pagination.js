 $(document).ready(function() {

    var total_pages;
    var visiblePages = $('.list-size').val();   
    localStorage.setItem('visiblePages', parseInt(visiblePages));

    var search_text = $('.search_sku').val();

    var pages_url = $('#pages_url').val();
    var data_url  = $('#data_url').val();

    function getVisiblePages(){
     	var visiblePages = $('.list-size').val();   
        localStorage.setItem('visiblePages', parseInt(visiblePages));
        return localStorage.getItem('visiblePages');
    }

    function getSearchtext(){
    	var search_text = $('.search_sku').val();
        localStorage.setItem('search_text', search_text);
        return localStorage.getItem('search_text');
    } 

    function getPages(){     
      var url = pages_url;    
      var posting = $.get( 
    	url,
    	 {
    	 	track:'onpageload',
    	 	page:1, 
        	size:localStorage.getItem('visiblePages'),
        	search_text:getSearchtext(),
    	 } );

    posting.done(function( data ){        
        localStorage.setItem('total_pages', parseInt(data));
     });    
    return  localStorage.getItem('total_pages');    
    }        

    var $pagination = $('#pagination-demo');
    var defaultOpts = {
        //totalPages: localStorage.getItem('total_pages'),
        visiblePages: 3,
        onPageClick: function (event, page) {
            $('#pag_nav').text('Page ' + page + ' of '+localStorage.getItem('total_pages'));
            $.get(data_url,
            	{
            	 track:'onPageClick',
            	 page:page, 
            	 size:localStorage.getItem('visiblePages'),
            	 search_text:getSearchtext(),
            	},function(data){
                $('#stock_content').html(data);
                });
        }
    };
    $pagination.twbsPagination(defaultOpts);
	
    // on list size change
    $('.list-size').on('change', function(){
        var visiblePages = $(this).val();
        var ts = visiblePages;        
        var search_text = getSearchtext();
        $('#stock_content').html('<td colspan="6"><div class="text-bold text-center"><i class="icon-spinner2 spinner"></i>Loading stock ....</div></td>');
        $.ajax({ url: data_url,
                type: 'GET',
                data: {page:1, size:getVisiblePages()}, 
                async:false,success: 
                function(data){
              $('#stock_content').html(data);
        }});        
        // changecontent        
        // $.get(data_url,
        // 	{
        // 		page:1, 
        // 		size:3,//getVisiblePages(),
        // 		search_text:getSearchtext()
        // 	},function(data){            
        //     $('#stock_content').html(data);
        // });
        
        //$('#pagination-demo').addClass('hidden');

        // destroy and create new pagination
        
    });

    //change content
    function changecontent(){
    	$.get(data_url,
        	{
        		page:1, 
        		size:getVisiblePages(),
        		search_text:getSearchtext()
        	},function(data){
            $('#stock_content').html(data);
        });
    }
    // change total_pages
    function changeTotalPages(){
    	$.ajax({ url: pages_url,type: 'GET',
        	data: {
        		track:'onchangesize',
        		size:getVisiblePages(),
        		select_size:'select_size',
        		search_text:getSearchtext()
        	},async:false,success: function(data){
           
           localStorage.setItem('total_pages',parseInt(data));         
           
        } });
    }
   // destroy and create new pagination
   function createNewPagination(){   
        var totalPages = getPages();        
        var currentPage = $pagination.twbsPagination('getCurrentPage');
        $pagination.twbsPagination('destroy');
        $pagination.twbsPagination($.extend({}, defaultOpts, {
                startPage: currentPage,
                totalPages: totalPages
            }));
          }

	  var delay = (function(){
      var timer = 0;
      return function(callback, ms){
        clearTimeout (timer);
        timer = setTimeout(callback, ms);
      };
    })();
    $('.search_sku').keyup(function() {
    	delay(function(){
        var search_text = $('.search_sku').val();
        var url = data_url;
        changecontent();
        changeTotalPages();
        createNewPagination();
	    }, 1000 );
	});  

  });

