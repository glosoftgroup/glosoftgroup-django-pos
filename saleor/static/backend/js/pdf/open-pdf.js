/* *****************************
 * return: open pdf on new window
 * param: data : response from server with content application/pdf header
 * ******************************/
function openPdf(data){
     var file = new Blob([data], { type: 'application/pdf' });
     var fileURL = URL.createObjectURL(file);
     // Firefox 1.0+
     var isFirefox = typeof InstallTrigger !== 'undefined';
     if(isFirefox){
        window.open("data:application/pdf," + escape(data));
     }else{
         var win = window.open("",name="_top",replace=true);
         win.document.write();
         var style = " text-transform: uppercase;-moz-user-select: none;border: 1px solid transparent;padding: 0.375rem 1rem;font-size: 0.875rem;line-height: 1.5;border-radius: 0.25rem;touch-action: manipulation;text-decoration: none;box-sizing: border-box;color: #fff;background-color: #2A9FD6;display: inline-block;font-weight: 400;text-align: center;white-space: nowrap;vertical-align: middle;border-color: #2A9FD6;";

         win.document.write('<div style="padding:12px"><a id="btn-back" style="'+style+'" href="'+back_path+'" >Click to go Back</a></diV><iframe src="' + fileURL + '" frameborder="0" style="border:0; top:0px; left:0px; bottom:0px; right:0px; width:100%; height:100%;" allowfullscreen></iframe>');
     }

 }