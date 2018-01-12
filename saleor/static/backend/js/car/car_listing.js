$ = jQuery;
var $pagination = $('.bootpag-callback');
var $modal = $('#modal_instance');
var date;

//vue
var parent = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       'name':'Book Listing',
       items:[],
       loader:true,
       totalPages:1,
       visiblePages:4,
       page_size:10,
       search:'',
       status:'all',
       exportType:'none',
       date: 'Select date'
    },
    methods:{
        deleteBooking: function(url,id){
            /* open delete modal and populate dynamic form attributes */
            $modal.modal();

            /* set dynamic form data */
            console.log(url);
            var prompt_text = $(this).data('title');
            $('.del').attr('data-id', id);
            $('.del').attr('data-href', url);
            $('.modal-title').html(prompt_text);
            $modal.modal();
            $('.delete_form').attr('action',url);
        },
        inputChangeEvent:function(){
            /* make api request on events filter */
            var self = this;
            if(this.date == 'Select date'){
                date = '';
            }else{ date = this.date; }
            console.log(this.date);
            this.$http.get($('.pageUrls').data('bookinglisturl')+'?page_size='+self.page_size+'&q='+this.search+'&status='+this.status+'&date='+date)
                .then(function(data){
                    data = JSON.parse(data.bodyText);
                    this.items = data.results;
                    this.totalPages = data.total_pages;
                }, function(error){
                    console.log(error.statusText);
            });
        },
        listItems:function(num){
        /* make api request when pagination pages are clicked */
            if(this.date == 'Select date'){
                date = '';
            }else{ date = this.date; }
            this.$http.get($('.pageUrls').data('bookinglisturl')+'?page='+num+'&page_size='+this.page_size+'&status='+this.status+'&date='+date)
                .then(function(data){
                    data = JSON.parse(data.bodyText);
                    this.items = data.results;
                    this.loader = false;
                }, function(error){
                    console.log(error.statusText);
            });
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
        pagination: function(val){
        /* include twbsPagination on vue app */
            var self=this ;
            /* restructure pagination */
            $('.bootpag-callback').twbsPagination({
                totalPages: parseInt(val),
                visiblePages: this.visiblePages,
                prev: '<span aria-hidden="true">&laquo;</span>',
                next: '<span aria-hidden="true">&raquo;</span>',
                onPageClick: function (event, page) {
                    $('.pages-nav').text('Page ' + page + ' of '+self.totalPages);
                }
            }).on('page',function(event,page){
                self.listItems(page);
            });
        }
    },
    mounted:function(){
    /* on page load populate items with api list response */
        this.$http.get($('.pageUrls').data('bookinglisturl'))
            .then(function(data){
                data = JSON.parse(data.bodyText);
                this.items = data.results;
                this.totalPages = data.total_pages;
                this.pagination(data.total_pages);
                this.loader = false;
            }, function(error){
                console.log(error.statusText);
        });

    },
    watch: {
    /* listen to app data changes and restructure pagination when page size changes */
        'date': function(val, oldVal){
            this.inputChangeEvent();
        },
    	'totalPages': function(val, oldVal){
            var self=this ;
            /* destroy pagination on page size change */
            $('.bootpag-callback').twbsPagination('destroy');

            /* restructure pagination */
            $('.bootpag-callback').twbsPagination({
                totalPages: parseInt(val),
                visiblePages: this.visiblePages,
                prev: '<span aria-hidden="true">&laquo;</span>',
                next: '<span aria-hidden="true">&raquo;</span>',
                onPageClick: function (event, page) {
                    $('.pages-nav').text('Page ' + page + ' of '+self.totalPages);
                }
            }).on('page',function(event,page){
                self.listItems(page);
            });
        }
    }

});

$('.daterange-single').daterangepicker({
        singleDatePicker: true,
        locale:{format: 'YYYY-MM-DD'},
        showDropdowns:true,
        autoUpdateInput:false,
        maxDate: new Date()
    },function(chosen_date) {
        parent.date = chosen_date.format('YYYY-MM-DD');
        $('.daterange-single').val(chosen_date.format('YYYY-MM-DD'));

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