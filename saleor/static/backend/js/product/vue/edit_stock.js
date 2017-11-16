$ = jQuery;
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
        paid:0
    },
    created: function () {
        // `this` points to the vm instance
        this.reorder = $('#reorder-threshold').val();
        this.total   = $('#id_total_cost').val();
        this.amount  = $('#id_cost_price').val();
        this.quantity = $('#id_quantity').val();
        this.paid    = $('#id_amount_paid').val();
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
            this.balance = this.total - this.paid;
        }
    }
});