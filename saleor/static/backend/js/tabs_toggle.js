$(function() {  
  var tabProductAdded = $('.tabProductAdded');
  // alertUser
  function alertUser(msg,status='bg-danger',header='Add product first!')
	{
	    $.jGrowl(msg, 
	    {header: header,theme: status});
	}
  // disable clicking
  tabProductAdded.addClass('disabled');
  tabProductAdded.removeAttr('data-toggle');
  $(".tabProductAdded").on("click", function(e) {
  if ($(this).hasClass("disabled")) {
    e.preventDefault();
    alertUser('Add product to enable this tabs')
    return false;
  }
 });
 // ********
 var id_name = $('#id_name')
 id_name.on('focusout',function(){
 	var dt = new Date();
    var time = dt.getHours() + "-" + dt.getMinutes() + "-" + dt.getSeconds();
    var nSku = id_name.val()+time+'x';
 	$('#idvariant-sku').val(nSku);
 });
 //***********
});