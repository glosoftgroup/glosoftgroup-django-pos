$ = jQuery;
function isInt(value) {
  return !isNaN(value) && (function(x) { return (x | 0) === x; })(parseFloat(value))
}
new Vue({
    el:'#stock-edit-app',
    delimiters: ['${', '}'],
    data:{
        name:'gPOS',
        job:'pos',
        amount:0,
        quantity:0,
        total:0,
        reorder:0,
        balance:0,
        paid:0,
        settle:0,
        temp_paid:0,
        price_override:0,
        wholesale_override: 0,
        Wholesale:'',
        minimum_price: 0
    },
    created: function () {
        // `this` points to the vm instance
        this.reorder = $('#reorder-threshold').val();
        this.total   = $('#id_total_cost').val();
        this.amount  = $('#id_cost_price').val();
        this.price_override = $('#id_price_override').val();
        this.wholesale_override = $('#id_wholesale_override').val();
        this.quantity = $('#id_quantity').val();
        this.paid    = $('#id_amount_paid').val();
        this.temp_paid   = $('#id_amount_paid').val();
        this.balance = this.total - this.paid;
    },
    methods:{
        getTotal:function(){
            this.total = this.quantity * this.amount;
            this.balance = this.total - this.paid;
            return true;
        },
        getAmount:function(){
            this.amount = this.total/this.quantity;
            this.balance = this.total - this.paid;
            return true;
        },
        getBalance:function(){
            if(isInt(this.paid)){
            this.balance = this.total - this.paid;
            }
        },
        settleBalance:function(){
            this.paid = this.temp_paid;
            this.getBalance();
            if(isInt(this.settle)){
             this.paid = parseInt(this.paid) + parseInt(this.settle);
             this.balance = parseInt(this.total) - parseInt(this.paid);
            }else{

            }

        }
    }
});