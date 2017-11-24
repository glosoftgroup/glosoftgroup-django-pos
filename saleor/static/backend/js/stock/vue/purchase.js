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
});

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