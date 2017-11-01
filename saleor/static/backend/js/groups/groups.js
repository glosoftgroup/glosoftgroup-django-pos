$('#modal_detail .addUserBtn').on('click', function(){
    $('#modal_detail').modal('hide');
    var id = $('.cgroup_id').val();
    $( "#"+id+" td ul .modal_trigger_user" ).trigger( "click" );
});
$('#modal_users').on('hidden.bs.modal', function () {
    names = [];
});
//**@ users modal
    $('body').on('click', '.modal_trigger_user',function (e) {
         var url = $(this).data('href')
         var prompt_text = $(this).data('title');
         var username = $(this).data('name');
         var modal = $(this).data('ta');
         var id = $(this).data('id');
         $('#group-id').val(id);
         var user_url = $(this).data('users');
         $('#group_name').val(username);
         $('.del').attr('data-id', id);
         $('.del').attr('data-href', url);
         $('.modal-title').html(prompt_text);
         $(modal).modal();
         $('.delete_form').attr('action',url);
         var token = $(this).data('token');

          //*@ get group users
          $.ajax({
            type:"POST",
            url:user_url,
            data:{id:id, csrfmiddlewaretoken:token},
            async:false,
            success:function(data){
             if(typeof data !== 'undefined' && data.length >0){
                  names = data;
                   //*@ populate table
                    var table_body = $('#user_table tbody');
                    var parent = table_body.parent();
                    table_body.detach().empty().each(function(i, val){
                        for (var x = 0; x < remove_duplicates(names).length; x++){
                            $(this).append('<tr id="user-'+ remove_duplicates(names)[x].id +'"><td><img src="'+ remove_duplicates(names)[x].image +'" class="circle teal img-circle" style="width: 40px;height: 40px;">'+ '</td><td>'+ remove_duplicates(names)[x].name + '</td><td><a href="javascript:;" onClick="removeuser('+ remove_duplicates(names)[x].id +')" class="modal-trigger btn btn-default btn-sm del_array_item"><i class="icon-trash" style="font-size: 11px;" data-toggle="modal"></i> delete</a></td></tr');
                            if (x == remove_duplicates(names).length - 1){
                                $(this).appendTo(parent);
                            }
                        }
                    });
               }else{
                    $('#user_table tbody').empty().append('<tr><td colspan="3"><div class="alert bg-danger col-md-12">No users available</td></tr></div>')
               }

            },error:function(error){
              console.log(error);
              names = [];
            }
          });

    });

    //**@ users select
$('#add_user').on('click', function(e){
   var selected = $("#edit_users_multiple :selected").map(function() {
                      return {
                          id: parseInt($(this).val()),
                          name: $(this).data("name"),
                          image: $(this).data("image")
                      };
                  }).get();

    $.each(selected, function(i, val){
      names.indexOf(val) === -1 ? names.push(val) : console.log('already exists');
    });

    var table_body = $('#users_table_body');
    var parent = table_body.parent();

    table_body.detach().empty().each(function(i, val){
        for (var x = 0; x < remove_duplicates(names).length; x++){
            $(this).append('<tr id="user-'+ remove_duplicates(names)[x].id +'"><td><img src="'+ remove_duplicates(names)[x].image +'" class="circle teal img-circle" style="width: 40px;height: 40px;">'+ '</td><td>'+ remove_duplicates(names)[x].name + '</td><td><a href="javascript:;" onClick="removeuser('+ remove_duplicates(names)[x].id +')" class="modal-trigger btn btn-default btn-sm del_array_item"><i class="icon-trash" style="font-size: 11px;" data-toggle="modal"></i> remove</a></td></tr');
            if (x == remove_duplicates(names).length - 1){
                $(this).appendTo(parent);
            }
        }
    });

});

//**@ submit users details
$('body').on('click', '#modal_update_users',function(){
   var users = [];
   //**@ get list of users ids
       $.each(names, function(i, val){
          users.push(val.id);
       });

    //**@ id
    var g_id = $('#group-id').val();
    var g_name = $('#group_name').val();

    //**@ post
    $.ajax({
      url: $(this).data('url'),
      type: 'POST',
      data: {
             'users[]': users,
             'id': g_id ,
             'group_name': g_name,
             'csrfmiddlewaretoken':$(this).data('token')
      },
      async:false,
      success: function(data){
              $.jGrowl('group updated successfully', {
                  header: 'Well done!',
                  theme: 'bg-success'
              });
          //window.location.reload();
          users=[];
          names = [];
          $('#modal_users').modal('hide');
      }
      ,error:function(error){
      console.log(error);
            $.jGrowl('something went wrong somewhere', {
                  header: 'Oops!',
                  theme: 'bg-danger'
             });
      }
    });
});