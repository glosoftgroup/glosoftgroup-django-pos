 // alertUser
function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }
function updateSettings(dynamicData,url,method){
  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
  return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });

}
$(function() {
	var smsApiBtn = $('#sms_api_btn');
	var api_key = $('#api_key');
	var api_username = $('#api_username');
	var pageUrls   = $('.pageUrls');
	var updateSettingsUrl = pageUrls.data('updateurl');
	var dynamicData = {};

	smsApiBtn.on('click',function(){		
		var sms_username = api_username.val();
		var sms_api_key = api_key.val();
		if(!sms_username){
			alertUser('Username required','bg-danger','Error');
			return false;
		}else{
			dynamicData['sms_username'] = sms_username;
		}
		if(!sms_api_key){
			alertUser('Api key required','bg-danger','Error');
			return false;
		}else{
			dynamicData['sms_api_key'] = sms_api_key;
		}		

		updateSettings(dynamicData,updateSettingsUrl,'post')
		.done(function(data){
			alertUser('Settings Updated successfully');
		})
		.fail(function(){
			alertUser('Error occured','bg-danger','Ooops');
		}
		);
	});
});