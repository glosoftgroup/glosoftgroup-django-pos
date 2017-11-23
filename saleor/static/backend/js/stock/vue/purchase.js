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
})

new Vue({
    el:'#purchase-app',
    delimiters: ['${', '}'],
    data:{ name:'POS'},
});
new Vue({
    el:'#purchase-app2',
    delimiters: ['${', '}'],
    data:{ name:'POS'},
});

new Vue({
    el:'#purchase-app3',
    delimiters: ['${', '}'],
    data:{ name:'POS'},
});