function splitID(id) {
    var dnum = id.split("-")[0];
    var dname = id.replace(dnum + "-", "");
    return {
        docnumber: dnum,
        docname: dname
    };
}

function setupDocList(){
	$(".contractpreview").first().addClass("selected");
	$(".contractpreview").on("click", function(event) {
	$(".contractpreview").removeClass("selected");
		var attr = $(this).attr('id');
		loadDoc(attr);
		$("#"+attr).addClass("selected");
	});
}

$(window).load(function() {

    setupDocList()
    $(".chosen-select").chosen({
        max_selected_options: 1
    });
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

    $("#searchButton").on("click", function() {
        post_search();
    });

    $("#next").on("click", function() {
        next();
    });

    $("#flip").click(function(){
        $("#panel").slideToggle("slow");
            $(".chosen-select").chosen({
        max_selected_options: 1
        });
    });

	$("#advanced_search").click(function(){
		var display = $("#officers_chosen").css("display");
		if (display==="none"){
			$("#officers_chosen").fadeIn(200);
			$("#officers_chosen").css("display", "block");
		}else{
			$("#officers_chosen").css("display", "none");
		}
	});

});

function loadDoc(id) {

    var idparts = splitID(id);
    docnumber = idparts.docnumber;
    docname = idparts.docname;
    firstmention = "";
    var widthfactor = (7 / 10);
    var windowWidth = $(window).width();
    if (windowWidth < 750) {
        widthfactor = 1;
    }
    try {
        firsthtml = $(this).find(".page").html();
        firstmention = firsthtml.split(" ")[1];
    } catch (err) {
        firstmention = 1;
    }

    var width = $("#DV-container").width() ;
    var height = $("#display").height() ;
    firstmention = typeof firstmention !== 'undefined' ? firstmention : 1;

    $('#DV-container').html('<div id="DV-viewer-' + docnumber + '-' + docname + '"></div>');

    DV.load("//www.documentcloud.org/documents/" + docnumber + "-" + docname + ".js", {
        width: width,
        sidebar: false,
        text: true,
        pdf: false,
        page: firstmention,
        height: height,
        container: "#DV-viewer-" + docnumber + "-" + docname
    });
    $("#DV-container").children().first().addClass('selected-viewer');
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

function buildSearch(){

    var searchQuery = $("#textbox").val();
    var selectedvendors = $('#vendors :selected').length;
    if (selectedvendors == 1) {
        searchQuery = searchQuery + " vendor:\"" + $('#vendors :selected').first().text() + "\"";
    }

    var selecteddeps = $('#departments :selected').length;
    if (selecteddeps == 1) {
        searchQuery = searchQuery + " department:\"" + $('#departments :selected').first().text() + "\"";
    }

    var selectedofficers = $('#officers :selected').length;
    if (selectedofficers == 1) {
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


function previous(){
    searchQuery =  $("#pagination").attr("data-query") + "&&offset:" + $("#pagination").attr("data-offset");
    resetUI();
    $.post("previous/" + searchQuery, function(data, status) {
        $("#searchresults-container").html(data);
        $("#results_status").html("Fetching...");
        var hgt = $("#DV-container").height();
        $("#searchresults-container").css("height", hgt);
        empty = data.indexOf("<p>No contracts found.</p>") > -1; //if true, then no results found
        $("#projectid-1542-city-of-new-orleans-contracts").remove();
        //get the doc name and number of the first doc
        $("#doclist").html(data);

        setupDocList();

        results = $("#pagination").attr("data-total");
        var resultText = (results == 1) ? " result " : " results ";
        var querytext = results + resultText;
        $("#results_status").html(querytext);

        if (results>0){
            id = $(".contractpreview").first().attr("id");
            loadDoc(id);
        }

        $("#next").on("click", function(e) {
            next();
        });

        $("#previous").on("click", function(e) {
            previous();
        });
    });
}

function next(){
    searchQuery =  $("#pagination").attr("data-query") + "&&offset:" + $("#pagination").attr("data-offset");
    resetUI();
    $.post("next/" + searchQuery, function(data, status) {
        $("#searchresults-container").html(data);
        $("#results_status").html("Fetching...");
        var hgt = $("#DV-container").height();
        $("#searchresults-container").css("height", hgt);
        empty = data.indexOf("<p>No contracts found.</p>") > -1; //if true, then no results found
        $("#projectid-1542-city-of-new-orleans-contracts").remove();
        //get the doc name and number of the first doc
        $("#doclist").html(data);

        setupDocList();

        results = $("#pagination").attr("data-total");
        var resultText = (results == 1) ? " result " : " results ";
        var querytext = results + resultText;
        $("#results_status").html(querytext);

        if (results>0){
            id = $(".contractpreview").first().attr("id");
            loadDoc(id);
        }

        $("#next").on("click", function(e) {
            next();
        });
        $("#previous").on("click", function(e) {
            previous();
        });
    });
}

function post_search() {

    var valid = validate();
    if (!valid){
        return;
    }

    searchQuery = buildSearch();
    resetUI();

    $("#results_status").html("Searching...");

    $.post("search/" + searchQuery, function(data, status) {
        $("#searchresults-container").html(data);
        $("#results_status").html("Searching...");
        var hgt = $("#DV-container").height();
        $("#searchresults-container").css("height", hgt);
        empty = data.indexOf("<p>No contracts found.</p>") > -1; //if true, then no results found
        $("#projectid-1542-city-of-new-orleans-contracts").remove();
        //get the doc name and number of the first doc
        $("#doclist").html(data);

        setupDocList();

        results = $("#pagination").attr("data-total");
        var resultText = (results == 1) ? " result " : " results ";
        var querytext = results + resultText;
        $("#results_status").html(querytext);

        if (results>0){
            id = $(".contractpreview").first().attr("id");
            loadDoc(id);
        }

        $("#next").on("click", function(e) {
            next();
        });

    });
}