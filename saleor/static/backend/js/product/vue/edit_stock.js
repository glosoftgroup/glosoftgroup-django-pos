$ = jQuery;
new Vue({
    el:'#edit-area-app',
    delimiters: ['${', '}'],
    data:{
        name:'gPOS',
        job:'pos',
        amount:0,
        quantity:0,
        total:0,
        reorder:0
    },
    created: function () {
        // `this` points to the vm instance
        this.reorder = $('#reorder-threshold').val();
        this.total   = $('#id_total_cost').val();
        this.amount  = $('#id_cost_price').val();
        this.quantity = $('#id_quantity').val();
    },
    methods:{
        getTotal:function(){
            this.total = this.quantity * this.amount;
            return true;
        },
        getAmount:function(){
            this.amount = this.total/this.quantity;
            return true;
        }
    }
});