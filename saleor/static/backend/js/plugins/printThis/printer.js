$(function () {
    $('#printBtn').click(function () {
        $("#printme").printThis(
            {
            debug: false, // show the iframe for debugging
            importCSS: true, // import page CSS
            importStyle: true, // import style tags
            printContainer: true, // grab outer container as well as the contents of the selector
            //loadCSS: "path/to/my.css", // path to additional css file - us an array [] for multiple
            pageTitle: "Printed Report", // add title to print page
            removeInline: false, // remove all inline styles from print elements
            printDelay: 333, // variable print delay
            header: null, // prefix to html
            formValues: true //preserve input/form values)
        });
    });

});