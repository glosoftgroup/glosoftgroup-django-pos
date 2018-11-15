$ = jQuery;
var $pagination = $('.bootpag-callback');
var $modal = $('#modal_instance');
var $deleteModal = $('#modal_delete');
var date;

// global functions
function alertUser(msg,status='bg-success',header='Well done!')
    { $.jGrowl(msg,{header: header,theme: status}); }

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

Vue.filter('strLimiter', function (value) {
  if (!value) return ''
  value = value.toString()
  return value.slice(0, 55)+'...';
})
//vue
var parent = new Vue({
    el:"#vue-app",
    delimiters: ['${', '}'],
    data:{
       name: 'Listing',
       items: [],
       loader: true,
       totalPages: 1,
       visiblePages: 4,
       page_size: 10,
       search: '',
       status: 'all',
       exportType: 'none',
       date: 'Select date',
       deleteUrl: false,
       deleteId: false,
       wing_name: '',
       description: '',
       errors:false,
       showForm: false,
       updateUrl: ''
    },
    methods:{
        getInstance(url){
            var self = this;
            axios.defaults.xsrfHeaderName = "X-CSRFToken";
            axios.defaults.xsrfCookieName = 'csrftoken';

            axios.get(url)
            .then(function(response){
                self.wing_name = response.data.name;
                self.description = response.data.description;
                self.updateUrl = url;
                self.showForm = true;
                window.scrollTo(0, 0);
            })
            .catch(function(error){
                console.log(error);
            })
        },
        toggleForm(){
            console.log('opening form')
            this.showForm = !this.showForm;
        },
        validate(){
            this.errors = false;
        },
        addInstance(e){
            e.preventDefault();
            if(this.wing_name === ''){
                this.errors = true;
                return;
            }

            var self = this;
            var data = new FormData();
            data.append('name', this.wing_name);
            data.append('description', this.description);

            axios.defaults.xsrfHeaderName = "X-CSRFToken";
            axios.defaults.xsrfCookieName = 'csrftoken';

            if(this.updateUrl !== ''){
                // update
                axios.put(self.updateUrl, data)
                .then(function (response) {
                    alertUser('Data Updated successfully');
                    self.showForm = false;
                    self.wing_name = '';
                    self.description = '';
                    self.updateUrl = '';
                    self.inputChangeEvent();

                })
                .catch(function (error) {
                    console.log(error);
                    alertUser('Try a different name', 'bg-danger', 'Field error');
                });
            }else{
                // create
                axios.post($('.pageUrls').data('createurl'), data)
                .then(function (response) {
                    alertUser('Data created successfully');
                    self.showForm = false;
                    self.inputChangeEvent();
                    self.wing_name = '';
                    self.description = '';
                })
                .catch(function (error) {
                    console.log(error);
                    alertUser('Try a different name', 'bg-danger', 'Field error');
                });
            }

        },
        showMore: function(id,text){
            $('#'+id).html(text);
        },
        goTo: function(url){
            window.location.href = url;
        },
        deleteInstance: function(url,id){
            // open delete modal and set delete url
            // ___________________
            // var deleteUrl = this.deleteUrl;
            var self = this;
            if(url){
                $('#modal_delete').modal();
                self.deleteUrl = url;
                self.deleteId = id;
                return;
            }

            if(!self.deleteUrl){
                $('#modal_delete').modal();
                self.deleteUrl = url;
                self.deleteId = id;
                return;
            }else{
                axios.defaults.xsrfHeaderName = "X-CSRFToken"
                axios.defaults.xsrfCookieName = 'csrftoken'
                
                axios.delete(self.deleteUrl)
                .then(function (response) {
                    alertUser('Data deleted successfully');
                    // hide modal & remove item
                    $('#modal_delete').modal('hide');
                    // this.removeItem();
                    console.log($('#'+self.deleteId).html());
                    $('#'+self.deleteId).html('').remove();
                    self.deleteUrl = false;
                    self.deleteId = false;
                })
                .catch(function (error) {
                    console.log(error);
                });
                
            }
        },
        inputChangeEvent:function(){
            /* make api request on events filter */
            var self = this;
            if(this.date == 'Select date'){
                date = '';
            }else{ date = this.date; }
            this.$http.get($('.pageUrls').data('listurl')+'?page_size='+self.page_size+'&q='+this.search+'&status='+this.status+'&date='+date)
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
            this.$http.get($('.pageUrls').data('listurl')+'?page='+num+'&page_size='+this.page_size+'&status='+this.status+'&date='+date)
                .then(function(data){
                    data = JSON.parse(data.bodyText);
                    this.items = data.results;
                    this.loader = false;
                }, function(error){
                    console.log(error.statusText);
            });
        },
        removeItem(index) {
          this.items.splice(index, 1);
        },
        exportItems:function(){
        /* take care  of excel and pdf exports on filter panel */
            if(this.exportType == 'excel'){
                JSONToCSVConvertor(this.items, "Report", true);
            }
            if(this.exportType == 'pdf'){
                $("#printme").printThis({
                    debug: true, // show the iframe for debugging
                    importCSS: true, // import page CSS
                    importStyle: true, // import style tags
                    printContainer: true, // grab outer container as well as the contents of the selector
                    loadCSS: "my.css", // path to additional css file - us an array [] for multiple
                    pageTitle: "Report", // add title to print page
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
    $('#crud-form').removeClass('hidden');
    /* on page load populate items with api list response */
        this.$http.get($('.pageUrls').data('listurl'))
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
