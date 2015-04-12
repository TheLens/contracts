window.downloadFile = function (sUrl) {

    //iOS devices do not support downloading. We have to inform user about this.
    if (/(iP)/g.test(navigator.userAgent)) {
        alert('Your device does not support files downloading. Please try again in desktop browser.');
        return false;
    }

    //If in Chrome or Safari - download via virtual link click
    if (window.downloadFile.isChrome || window.downloadFile.isSafari) {
        //Creating new link node.
        var link = document.createElement('a');
        link.href = sUrl;

        if (link.download !== undefined) {
            //Set HTML5 download attribute. This will prevent file from opening if supported.
            var fileName = sUrl.substring(sUrl.lastIndexOf('/') + 1, sUrl.length);
            link.download = fileName;
        }

        //Dispatching click event.
        if (document.createEvent) {
            var e = document.createEvent('MouseEvents');
            e.initEvent('click', true, true);
            link.dispatchEvent(e);
            return true;
        }
    }

    // Force file download (whether supported by server).
    if (sUrl.indexOf('?') === -1) {
        sUrl += '?download';
    }

    window.open(sUrl, '_self');
    return true;
};

window.downloadFile.isChrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
window.downloadFile.isSafari = navigator.userAgent.toLowerCase().indexOf('safari') > -1;

function resetVendor(){
    $("#vendors").val($("#vendors").find('option:first').val());
}

function resetOfficers(){
    $("#officers").val($("#officers").find('option:first').val());
}

function setupDocList(){
	$(".contractpreview").first().addClass("selected");
	$(".contractpreview").on("click", function(event) {
	$(".contractpreview").removeClass("selected");
		var attr = $(this).attr('id');
		$("#"+attr).addClass("selected");
	});
}

$(window).load(function() {
    setupDocList();
    $(".hide").removeClass("hide");
    $("#advanced_search").click(function(){
        var display = $(".advancedsearch").css("display");
        if (display==="none"){
            $(".advancedsearch").fadeIn(200);
            $(".advancedsearch").css("display", "block");
        }else{
            $(".advancedsearch").css("display", "none");
        }
        $("#advanced_search").remove();
    });
    $("#vendors").children().first().attr("value", "");
    $("#departments").children().first().attr("value", "");
    $("#officers").children().first().attr("value", "");

});

$(document).ready(function() {

    var runsearch = true;

    $("#DV-container").children().first().children().first().addClass('selected-viewer');

    $(".contractpreview").first().addClass("selected");

    $(document).keypress(function(e) {
        if (e.which == 13) {
            post_search();
        }
    });

	$( window ).resize(function() {
		setHeader();
	});

    $("#flip").click(function(){
        $("#panel").slideToggle("slow");
    });
    setHeader();
    setHandlers();
});

function validate(){
    if($('#vendors :selected').length>1){
        alert("You can only search one vendor at a time");
        $("#doclist").html("");
        return false;
    }
    if($('#departments :selected').length>1){
        alert("You can only search one department at a time");
        $("#doclist").html("");
        return false;
    }
    if($('#officers :selected').length>1){
        alert("You can only search one officer at a time");
        $("#doclist").html("");
        return false;
    }
    return true;
}

function buildSearch(){

    var searchQuery = $("#textbox").val();
    var selectedvendor = $('#vendors :selected').first().attr("value")!="" && $('#vendors :selected').first().attr("value") != undefined;
    if (selectedvendor) {
        searchQuery = searchQuery + " vendor:\"" + $('#vendors :selected').first().text() + "\"";
    }

    var selecteddeps = $('#departments :selected').first().attr("value")!="" && $('#departments :selected').first().attr("value") != undefined;
    if (selecteddeps) {
        searchQuery = searchQuery + " department:\"" + $('#departments :selected').first().text() + "\"";
    }

    var selectedofficers = $('#officers :selected').first().attr("value")!="" && $('#officers :selected').first().attr("value") != undefined;
    if (selectedofficers) {
        searchQuery = searchQuery + " officers:\"" + $('#officers :selected').first().text() + "\"";
    }

    searchQuery = searchQuery.replace(/^and /, ""); //remove and space if it starts the string

    offset = $("#pagination").attr("data-offset");

    searchQuery += "&&offset:" + offset;

    return searchQuery;
}

function resetUI(){
    $('#DV-container').html("");
    $("#searchresults-container").html("");
    $("#doclist").html("");
}

function openDetail(id){
    var win = window.open('http://' + window.location.host +  '/contracts/contract/' + id, '_blank');
    if(win){
        win.focus();
    }else{
        alert('Please allow popups for this site to see the contract in a new window');
    }
}

function setHandlers(){
    $("#next").on("click", function(e) {
        next();
    });

    $("#previous").on("click", function(e) {
        previous();
    });

    $('.contractpreview').hover(
       function(){ $(this).addClass('selected');},
       function(){ $(this).removeClass('selected');}
    );

    $("#search_button").on("click", function() {
        post_search();
    });

    $(".contractpreview").on("click", function(event) {
        var hit = this.id;
        $(".selected").removeClass("selected");
        $("#" + hit).addClass("selected");
        openDetail(this.id);
    });

    $(".open_button").on("click", function(event) {
        event.stopPropagation();
        var toopen = $(this).parents(".contractpreview").attr("id");
        openDetail(toopen);
    });

    $(".download_button").on("click", function(event) {
        event.stopPropagation();
        downloadFile("http://" + window.location.host + "/contracts/download/" + $(this).parents(".contractpreview").attr("id"));
    });

}

function handlePost(data){
	$("#contract_results").html(data);
	setupDocList();
	results = $("#pagination").attr("data-total");
	if (results>0){
		id = $(".contractpreview").first().attr("id");
	}
	setHandlers();
}

function post_back(query){
    $.post("next?" + query, function(data, status) {
         handlePost(data);
    });
}

function previous(){
    searchQuery = "query=" + $("#pagination").attr("data-query") + "&offset=" + (parseInt($("#pagination").attr("data-offset")) - 1);
    resetUI();
    post_back(searchQuery);
}

function next(){
    searchQuery = "query=" + $("#pagination").attr("data-query") + "&offset=" + (parseInt($("#pagination").attr("data-offset")) + 1);
    resetUI();
    post_back(searchQuery);
}

function post_search() {

    var valid = validate();
    if (!valid){
        return;
    }

    searchQuery = buildSearch();
    resetUI();

    $("#results_status").html("Searching...");
    $("#nav_context").remove();
    $.post("search/" + searchQuery, function(data, status) {
        handlePost(data);
    });
}

function validate(){
    if($('#vendors :selected').length>1){
        alert("You can only search one vendor at a time");
        $("#doclist").html("");
        return false;
    }
    if($('#departments :selected').length>1){
        alert("You can only search one department at a time");
        $("#doclist").html("");
        return false;
    }
    if($('#officers :selected').length>1){
        alert("You can only search one officer at a time");
        $("#doclist").html("");
        return false;
    }
    return true;
}

function resetUI(){
    $('#DV-container').html("");
    $("#searchresults-container").html("");
    $("#doclist").html("");
}

function checkForChanges()
{
  if ($('.t402-elided').length>0) {
    setTimeout(checkForChanges, 1000);
    console.log('Trying again in .25 seconds.');
  }
  else {
   console.log('Survey completed or skipped. Adding in advancedsearch');
   var html = $("#blockOfStuff").html();
   $("#post_gcs").html(html);
   $("#advanced_search").on("click", function(){$("#advanced_search").remove();});
   if (($("#vendors").length)==1){
       $.post("vendors/all", function(data){$("#vendors").html(data);}); //fill the vendors block
   }
   if (($("#officers").length)==1){
       $.post("officers/all", function(data){$("#officers").html(data);}); //fill the officers block
   }
   if (($("#departments").length)==1){
       $.post("departments/all", function(data){$("#departments").html(data);}); //fill the officers block
   }
   $("#advanced_search").on("click", function(){
        var display = $(".advancedsearch").first().css("display");
        if (display=="none"){
            $(".advancedsearch").css("display","block");
        }
        else{
            $(".advancedsearch").css("display","none");
        }
  });
  }
}