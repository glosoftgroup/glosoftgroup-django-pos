
new Vue({
    el:'#product-app',
    delimiters: ['${', '}'],
    data:{
        name:'gPOS',
        job:'pos',
        amount:0,
        quantity:0,
        total:0
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