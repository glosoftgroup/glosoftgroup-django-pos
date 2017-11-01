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
	var redirectSettingsUrl = $('.redirectUrls').data('redirecturl');
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

	/* end each check*/
  $('#form-category').validate({
    onkeyup: function(element) {$(element).valid()},
    rules:{
        company_name: {
          required:true,
          minlength:3
        },
        loyalty_point_equiv:{
          required:false,
          digits: true,
          minlength: 1
        }

    },
    messages:{
      company_name:{
        required: "please provide the business name",
        minlength: "name must be atleast 3 characters long"
      }
    },
    submitHandler: function() {
          var file = $('#image')[0].files[0];
          var f = document.getElementById('form-category');
          var formData = new FormData(f);
          if(file != ''){
            formData.append("image", file);
          }
          if (formData) {
                $.ajax({
                    url: updateSettingsUrl,
                    type: "POST",
                    data: formData,
                    processData: false,
                    contentType: false,
                    success:function(data){
                       console.log(data);
                       if(data=='success'){
                          alertUser('Settings Updated successfully');
                          //setTimeout(function(){ window.location.reload(true); }, 2000);
                       }else{
                          alertUser('Error Updating', 'bg-danger','Error');
                       }

                    },
                    error:function(error){
                      console.log(error);
                      $.jGrowl('Unsuccessful in updating settings', {
                          header: 'Error!',
                          theme: 'bg-danger'
                      });
                    }
                });
          }
      }
//    }
  });
});