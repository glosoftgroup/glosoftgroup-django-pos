/* ************************************
 *
 *  invoicing app
 *
 * ************************************
*/
$ = jQuery;
var modal = $('#payment-modal');
var dynamicData = {};

function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }

var parent = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       'name':'Invoicing',
       'date': null,
       'amount_paid':null,
       'payment_option':null,
       'description':null,
       'book':null,
       'invoice_number':null,
       paymentListUrl:null,
       total_paid:null,
       is_booked:false,
       is_active:true,
       balance:null,
       room_id:null,
       payments: []
    },
    methods:{
        openModal:function(){
            /* open modal */
            $('#payment-modal').modal();

        },
        addPayment:function(){
            var addPaymentUrl = $('.pageUrls').data('payurl');
            var form = document.getElementById('pay-form');
            var f = new FormData(form);

            this.$http.post(addPaymentUrl,f)
            .then(function(data){
                $('#payment-modal').modal('hide');
                this.populatePayment();
                data = JSON.parse(data.bodyText);
                this.balance = data.balance;
                this.total_paid = data.total_paid;
            }, function(error){
                console.log(error.statusText);
            });
        },
        checkOut:function(){
            if(parseInt(this.balance) > 0){
                alertUser('Clear balance to checkout','bg-warning','Clear Balance!');
                this.openModal();
                return false;
            }
            var checkOutUrl = $('.pageUrls').data('checkouturl');
            var form = document.getElementById('check-out-form');
            var f = new FormData(form);
            this.$http.post($('.pageUrls').data('checkouturl'), f)
            .then(function(data){
                this.deActivate();
                data = JSON.parse(data.bodyText);
            }, function(error){
                console.log(error.statusText);
            });
        },
        deActivate:function(){
            var form = document.getElementById('deactivate-form');
            var f = new FormData(form);
            this.$http.post($('.pageUrls').data('deactivateurl'), f)
            .then(function(data){
                data = JSON.parse(data.bodyText);
                this.is_active = false;
            }, function(error){
                console.log(error.statusText);
            });
        },
        populatePayment:function(){
            this.$http.get(this.paymentListUrl)
            .then(function(data){
                this.payments = JSON.parse(data.bodyText);
            }, function(error){
                console.log(error.statusText);
            });
        }
    },
    created:function(){
        $('.daterange-single').datepicker();
        $('#date').val(moment().format('YYYY-MM-DD'));
        this.date = moment().format('YYYY-MM-DD');
        this.paymentListUrl = $('.pageUrls').data('paylisturl');
        this.balance = $('#balance').val();
        this.total_paid = $('#total_paid').val();
        this.room_id = $('#room_id').val();

        this.populatePayment();

    }
});