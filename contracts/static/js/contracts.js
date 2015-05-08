window.downloadFile = function (sUrl) {

    // iOS devices do not support downloading. We have to inform user about this.
    if (/(iP)/g.test(navigator.userAgent)) {
      alert('Your device does not support files downloading. Please try again in desktop browser.');
      return false;
    }

    // If in Chrome or Safari - download via virtual link click
    if (window.downloadFile.isChrome || window.downloadFile.isSafari) {
      // Creating new link node.
      var link = document.createElement('a');
      link.href = sUrl;

      if (link.download !== undefined) {
        // Set HTML5 download attribute. This will prevent file from opening if supported.
        var fileName = sUrl.substring(sUrl.lastIndexOf('/') + 1, sUrl.length);
        link.download = fileName;
      }

      // Dispatching click event.
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

function buildSearch(){
  var searchQuery = $("#text-box").val();

  var selectedvendor = $('#vendors :selected').first().attr("value") !== "" && $('#vendors :selected').first().attr("value") !== undefined;
  if (selectedvendor) {
    searchQuery = searchQuery + " vendor:\"" + $('#vendors :selected').first().text() + "\"";
  }

  var selecteddeps = $('#departments :selected').first().attr("value") !== "" && $('#departments :selected').first().attr("value") !== undefined;
  if (selecteddeps) {
    searchQuery = searchQuery + " department:\"" + $('#departments :selected').first().text() + "\"";
  }

  var selectedofficers = $('#officers :selected').first().attr("value") !== "" && $('#officers :selected').first().attr("value") !== undefined;
  if (selectedofficers) {
    searchQuery = searchQuery + " officers:\"" + $('#officers :selected').first().text() + "\"";
  }

  searchQuery = searchQuery.replace(/^and /, ""); //remove and space if it starts the string

  offset = $("#pagination").attr("data-offset");

  // searchQuery += "&&offset:" + offset;

  return searchQuery;
}

function setHandlers(){
  $("#next").on("click", function(e) {
    next();
  });

  $("#previous").on("click", function(e) {
    previous();
  });

  $("#search-button").on("click", function() {
    postSearch();
  });

  $(".contract-preview").on("click", function(event) {
    // window.location.href = '/contracts/contract/' + id;
  });

  $(".open-button").on("click", function(event) {
    event.stopPropagation();
    var id = $(this).parents(".contract-preview").attr("id");
    window.location.href = '/contracts/contract/' + id;
  });

  $(".download-button").on("click", function(event) {
    event.stopPropagation();
    downloadFile("http://" + window.location.host + "/contracts/download/" + $(this).parents(".contract-preview").attr("id"));
  });
}

function handlePost(data){
  $("#contract-results").html(data);
  results = $("#pagination").attr("data-total");
  if (results > 0){
    id = $(".contract-preview").first().attr("id");
  }
  setHandlers();
}

function previous() {
  searchQuery =  $("#pagination").attr("data-query") + "&&offset:" + $("#pagination").attr("data-offset");
  resetUI();
  $.post("previous/" + searchQuery, function(data, status) {
    handlePost(data);
    });
}

function next() {
  searchQuery =  $("#pagination").attr("data-query") + "&&offset:" + $("#pagination").attr("data-offset");
  resetUI();
  $.post("next/" + searchQuery, function(data, status) {
    handlePost(data);
  });
}

function postSearch() {
  searchQuery = buildSearch();
  console.log('searchQuery:', searchQuery);

  resetUI();
  console.log('resetUI');

  // $("#results-status").html("Searching...");
  // $("#nav-context").remove();
  $.ajax({
    type: 'POST',
    url: "search/" + searchQuery,
    // data: data,
    // contentType: ...,
    success: function(info) {
      console.log('info: ', info);
      handlePost(data);
    }
  });
}

function resetUI() {
  document.getElementById('DV-container').innerHTML = "";
  document.getElementById("search-results-container").innerHTML = "";
  document.getElementById("doc-list").innerHTML = "";
}

function checkForChanges() {
  if ($('.t402-elided').length > 0) {
    setTimeout(checkForChanges, 1000);
    console.log('Trying again in one second.');
  } else {
    console.log('Survey completed or skipped. Adding in advancedsearch');
    //var html = $("#blockOfStuff").html();
    //$("#post-gcs").html(html);
  }
}

$("#advanced-search").on("click", function() {
  var display = document.getElementById("filters").style.display;
  if (display === "block") {
    document.getElementById('filters').style.display = 'none';
    document.getElementById('advanced-search').innerHTML = 'Show advanced search <i class="fa fa-caret-down"></i>';
  } else {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = 'Hide advanced search <i class="fa fa-caret-up"></i>';
  }
});

$(document).ready(function() {
  var runsearch = true;

  $("#DV-container").children().first().children().first().addClass('selected-viewer');

  $(".contract-preview").first().addClass("selected");

  $(document).keypress(function(e) {
    if (e.which == 13) {
      postSearch();
    }
  });

  $("#flip").click(function() {
    $("#panel").slideToggle("slow");
  });

  setHandlers();
});

window.downloadFile.isChrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
window.downloadFile.isSafari = navigator.userAgent.toLowerCase().indexOf('safari') > -1;
