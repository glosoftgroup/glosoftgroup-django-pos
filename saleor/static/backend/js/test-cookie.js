$(function() {
    // Try creating a test cookie
    //$.cookie('test_cookie', true);
	Cookies.set('test_cookie', true);
	var ck = Cookies.get('test_cookie');
    // Check if it can be read...
    if (ck) {
        // Our test cookie worked!
        // So, just delete it, and everything will work fine
        Cookies.remove('test_cookie');
    } else {
        // Opera 8.0+
        var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
        // Firefox 1.0+
        var isFirefox = typeof InstallTrigger !== 'undefined';
        // Safari 3.0+ "[object HTMLElementConstructor]"
        var isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || safari.pushNotification);
        // Internet Explorer 6-11
        var isIE = /*@cc_on!@*/false || !!document.documentMode;
        // Edge 20+
        var isEdge = !isIE && !!window.StyleMedia;
        // Chrome 1+
        var isChrome = !!window.chrome && !!window.chrome.webstore;
        // Blink engine detection
        var isBlink = (isChrome || isOpera) && !!window.CSS;
        if(isFirefox == true){
            var url = '/instructions/firefox';
        }else if(isSafari == true){
            var url = '/instructions/safari';
        }else if(isIE == true){
            var url = '/instructions/ie';
        }else if(isEdge == true){
            var url = '/instructions/edge';
        }else if(isChrome == true){
            var url = '/instructions/chrome';
        }


        var html = '<div class="alert bg-info animated slideInDown text-center" style="margin:0 auto;z-index:111;">'+
           '<p id="cookie_warning" style="font-size:14px;">' +
            'This form requires cookies, which are disabled on your browser.' +
            '<br>Please enable cookies by following ' +
            '<a target="_blank" href="'+url+'" style="color:#333">' +
            'these instructions</a></p><p>If cookies have been enabled, pls refresh the page</p></div>';
        var my_form = $("form");
//        my_form.prepend(html);
        $('body').prepend(html)
        // Now disable all the form elements
        my_form.find(':input:not(:disabled)').prop('disabled', true);
    }
});

