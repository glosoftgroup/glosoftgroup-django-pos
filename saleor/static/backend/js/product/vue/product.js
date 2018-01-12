
new Vue({
    el:'#product-app',
    delimiters: ['${', '}'],
    data:{
        name:'gPOS',
        job:'pos',
        amount:0,
        quantity:0,
        total:0,
        paid:0,
        balance:0
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