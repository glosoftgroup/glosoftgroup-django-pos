$ = jQuery;
function isInt(value) {
  return !isNaN(value) && (function(x) { return (x | 0) === x; })(parseFloat(value))
}

Vue.component('child', {
  // camelCase in JavaScript
  props: ['pk','balance'],
  data: {
    paid:0
  },
  template: '<a v-bind:data-name="balance" class="type-number" id="type-number" data-type="number" data-inputclass="form-control" v-bind:data-pk="pk" data-title="Enter Amount">Pay</a>'
});
var purchaseUrl = $('.pageUrl').data('purchaseurl');
new Vue({
    el:'#purchase-app',
    delimiters: ['${', '}'],
    data:{ name:'POS'},
});
new Vue({
    el:'#purchase-app2',
    delimiters: ['${', '}'],
    data:{ name:'POS'},
    created: function () {

    //var purchaseUrl = "{% url 'dashboard:update-stock-purchase-data' %}";
    var csrf = $("[name=csrfmiddlewaretoken]").val();
    var oldBalance = 0;
    var amountPaid = 0;

    //return formated status
    function getStatus(pay_status){
         if(pay_status == 'fully-paid'){
                return '<span class="text-success  icon-checkmark-circle"><i></i></span>';
            }else{
                return '<span class="badge badge-flat border-warning text-warning-600">Pending..</span>';
            }
    }

    // purchase stock update
    $('.type-numbercxx').editable({
        url: purchaseUrl,
        title: 'Amount settled',
        params: {
            csrfmiddlewaretoken: csrf
        },
        validate: function(value) {
            if($.trim(value) == '') {
                return 'This field is required';
            }
        },
        success: function(response, newValue) {
            selector = '#'+response.message;
            oldBalance = $(selector).find('.stock-balance').data('balance');
            amountPaid = $(selector).find('.stock-paid').data('paid');
            $(selector).find('.stock-paid').html(parseInt(amountPaid)+parseInt(newValue));
            $(selector).find('.stock-balance').html(parseInt(oldBalance)-parseInt(newValue));


            $(selector).find('.stock-status').html(getStatus(response.status));

        }
    });
    }
});

new Vue({
    el:'#purchase-app3',
    delimiters: ['${', '}'],
    data:{ name:'POS'},
});