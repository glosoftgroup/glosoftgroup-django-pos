$ = jQuery;
var $pagination = $('.bootpag-callback');
var $modal = $('#modal_instance');
var date;
var dynamicData = {};

function ajaxSky(dynamicData,url,method){
  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
  return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });
}
// alertUser
function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }

// global functions
function formatNumber(n, c, d, t){
	var c = isNaN(c = Math.abs(c)) ? 2 : c,
			d = d === undefined ? '.' : d,
			t = t === undefined ? ',' : t,
			s = n < 0 ? '-' : '',
			i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c))),
			j = (j = i.length) > 3 ? j % 3 : 0;
	return s + (j ? i.substr(0, j) + t : '') + i.substr(j).replace(/(\d{3})(?=\d)/g, '$1' + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : '');
};
//vue filters
Vue.filter('formatCurrency', function (value) {
  return formatNumber(value, 2, '.', ',');
})
//vue
var parent = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       'name':'Cart Listing',
       items:[],
       cartItems: [],
       paymentItems: [],
       paymentOptions: [],
       paymentHistory:[],
       loader:true,
       totalPages:1,
       visiblePages:4,
       page_size:10,
       search:'',
       supplier:'',
       show_balance: false,
       show_change: false,
       pending:false,
       status:'all',
       exportType:'none',
       date: 'Select date',
       //  payment
       amount_paid: 0,
       quantity:0,
       payment_option: '',
       balance:0,
       paid:0
    },
    methods:{
        getHistory: function(){
            /* on load populate payment options with api list response */
            this.$http.get($('.pageUrls').data('historyurl'))
                .then(function(data){
                    data = JSON.parse(data.bodyText);
                    this.paymentHistory = data.results;
                    this.loader = false;
                }, function(error){
                    console.log(error.statusText);
            });
        },
        completePurchase: function(){
           dynamicData = {};
           dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
           dynamicData['amount_paid'] = parent.Tendered;
           dynamicData['total_net'] = parent.Total;
           dynamicData['supplier'] = this.supplier;
           dynamicData['quantity'] = parent.Quantity;
           dynamicData['balance'] = this.getDue(parent.Total, parent.Tendered);
           dynamicData['item'] = JSON.stringify(this.cartItems);
           dynamicData['history'] = JSON.stringify(this.paymentItems);

           // send purchase data
           // *******************
           // csrf token
           ajaxSky(dynamicData,$('.pageUrls').data('updateurl'),'POST')
           .done(function(data){
               data = JSON.parse(data);
               parent.getHistory();
               parent.paid = data.results.amount_paid;
               parent.balance = data.results.balance;
               parent.updateStatus();
               // clear cart notify user
               parent.paymentItems = [];
               $('#payment-modal').modal('hide');
               alertUser('Payment Made successfully');

               //window.location.reload();
           })
           .fail(function(err){console.log(err);});
        },
        creditPurchase: function(){},
        openModal:function(){
            /* open modal */
            $('#payment-modal').modal();

        },
        addPayment: function(itemToAdd) {
              var found = false;
              // Check if the item was already added to cart
              // If so them add it to the qty field
              this.paymentItems.forEach(item => {
                if (item.id === itemToAdd.id) {
                  found = true;
                  item.qty += parseInt(itemToAdd.qty);
                }
              });

              if (found === false) {
                this.paymentItems.push(Vue.util.extend({}, itemToAdd));
              }

           itemToAdd.qty = 1;
        },
        inputChangeEvent:function(){
            /* make api request on events filter */
            var self = this;
            this.$http.get($('.pageUrls').data('listurl')+'?page_size='+self.page_size+'&q='+this.search+'&supplier='+this.supplier)
                .then(function(data){
                    data = JSON.parse(data.bodyText);
                    this.items = data.results;
                    this.totalPages = data.total_pages;
                }, function(error){
                    console.log(error.statusText);
            });
        },
        clearCart:function(){
            // clear cart array
            this.cartItems = [];

            // refresh items
            this.inputChangeEvent();
        },
        addToCart: function(itemToAdd) {
              var found = false;
              // Check if the item was already added to cart
              // If so them add it to the qty field
              this.cartItems.forEach(item => {
                if (item.id === itemToAdd.id) {
                  found = true;
                  item.qty += parseInt(itemToAdd.qty);
                  item.quantity = item.qty;
                }
              });

              if (found === false) {
                this.cartItems.push(Vue.util.extend({}, itemToAdd));
              }

           itemToAdd.qty = 1;
        },
        removePayment(index) {
          this.paymentItems.splice(index, 1)
        },
        removeItem(index) {
          this.cartItems.splice(index, 1)
        },
        exportItems:function(){
        /* take care  of excel and pdf exports on filter panel */
            if(this.exportType == 'excel'){
                JSONToCSVConvertor(this.items, "Booking Report", true);
            }
            if(this.exportType == 'pdf'){
                $("#printme").printThis({
                    debug: false, // show the iframe for debugging
                    importCSS: true, // import page CSS
                    importStyle: true, // import style tags
                    printContainer: true, // grab outer container as well as the contents of the selector
                    loadCSS: "my.css", // path to additional css file - us an array [] for multiple
                    pageTitle: "Room Booking Report", // add title to print page
                    removeInline: false, // remove all inline styles from print elements
                    printDelay: 333, // variable print delay
                    header: null, // prefix to html
                    formValues: true //preserve input/form values)
                });
            }
        },
        getDue: function(total,tendered){
            due = parseInt(total) - parseInt(tendered);
            if(due <= 0){
                this.show_change = true;
                this.show_balance = false;
                due = parseInt(tendered) - parseInt(total);
            }else{
                this.show_balance = true;
                this.show_change = false;
            }
            return due
        },
        updateStatus: function(){
            if(parseInt(this.balance) > 0){
                this.pending = true;
            }else{
                this.pending = false;
            }
        }
    },
    computed: {
        Total: function() {
          var total = $('#balance').val();
          return total;
        },
        Quantity: function() {
          var quantity = 0;
          this.cartItems.forEach(item => {
            quantity += parseInt(item.qty);
          });
          return quantity;
        },
        Tendered: function() {
            var tendered = 0;
            this.paymentItems.forEach(item=>{
                tendered += parseInt(item.tendered);
            });
            return tendered;
        }
    },
    created:function(){
        // preset supplier
        this.balance = $('#balance').val();
        this.paid = $('#amount_paid').val();
        this.updateStatus();

        /* on page load populate items with api list response */
        this.getHistory();
        /* on load populate payment options with api list response */
        this.$http.get($('.pageUrls').data('paymentlisturl'))
            .then(function(data){
                data = JSON.parse(data.bodyText);
                this.paymentOptions = data.results;
            }, function(error){
                console.log(error.statusText);
        });
    }

});


//convert csv to excel
function JSONToCSVConvertor(JSONData, ReportTitle, ShowLabel) {
    //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
    var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;

    var CSV = '';
    //Set Report title in first row or line

    CSV += ReportTitle + '\r\n\n';

    //This condition will generate the Label/Header
    if (ShowLabel) {
        var row = "";

        //This loop will extract the label from 1st index of on array
        for (var index in arrData[0]) {

            //Now convert each value to string and comma-seprated
            row += index + ',';
        }

        row = row.slice(0, -1);

        //append Label row with line break
        CSV += row + '\r\n';
    }

    //1st loop is to extract each row
    for (var i = 0; i < arrData.length; i++) {
        var row = "";

        //2nd loop will extract each column and convert it in string comma-seprated
        for (var index in arrData[i]) {
            row += '"' + arrData[i][index] + '",';
        }

        row.slice(0, row.length - 1);

        //add a line break after each row
        CSV += row + '\r\n';
    }

    if (CSV == '') {
        alert("Invalid data");
        return;
    }

    //Generate a file name
    var fileName = "MyReport_";
    //this will remove the blank-spaces from the title and replace it with an underscore
    fileName += ReportTitle.replace(/ /g,"_");

    //Initialize file format you want csv or xls
    var uri = 'data:text/csv;charset=utf-8,' + escape(CSV);

    // Now the little tricky part.
    // you can use either>> window.open(uri);
    // but this will not work in some browsers
    // or you will not get the correct file extension

    //this trick will generate a temp <a /> tag
    var link = document.createElement("a");
    link.href = uri;

    //set the visibility hidden so it will not effect on your web-layout
    link.style = "visibility:hidden";
    link.download = fileName + ".csv";

    //this part will append the anchor tag and remove it after automatic click
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}